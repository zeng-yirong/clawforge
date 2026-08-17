from __future__ import annotations

import json
import os

import re
import shlex
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

from .types import ToolResult


DANGEROUS_PYTHON_PATTERNS = (
    "rm -",
    "rmtree",
    "unlink",
    "remove(",
    "removedirs",
    "rmdir",
    "os.system",
    "os.popen",
    "subprocess",
    "shutil",
    "send2trash",
    "__import__",
    "eval(",
    "exec(",
    "compile(",
    "socket",
    "httpx",
    "requests",
    "urllib",
)
ABSOLUTE_PATH_LITERAL = re.compile(r"[\"']/(?:[^\"']*)[\"']")
MAX_BASH_OUTPUT_CHARS = 4000
BASH_CONTROL_SPLIT = re.compile(r"\s*(?:&&|\|\||;|\n)\s*")
BASH_PIPE_SPLIT = re.compile(r"\s*\|\s*")
BASH_UNSUPPORTED_TOKENS = ("`", "<(", ">(")
BASH_PARENT_PATH_RE = re.compile(r"(?<![\w.-])\.\.(?:/|$)")
BASH_BACKGROUND_RE = re.compile(r"(?<![&])&(?![&])")
BASH_COMMANDS_WITH_PATH_OPERANDS = {
    "cat",
    "head",
    "tail",
    "wc",
    "ls",
    "mkdir",
    "touch",
    "rm",
    "cp",
    "mv",
    "chmod",
}
BASH_ALLOWED_COMMANDS = BASH_COMMANDS_WITH_PATH_OPERANDS | {
    "pwd",
    "echo",
    "printf",
    "true",
    "false",
    "test",
    "[",
    "set",
    "grep",
    "find",
    "sort",
    "uniq",
    "cut",
    "bash",
    "sh",
    "python",
    "python3",
    "which",
    "awk",
    "sed",
    "tr",
    "basename",
    "dirname",
}


VERIFIER_SITECUSTOMIZE = r"""
import os

import builtins
import csv

builtins.null = None
builtins.true = True
builtins.false = False

_original_dict_writer = csv.DictWriter

class _NanoclawCompatDictWriter(_original_dict_writer):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("extrasaction", "ignore")
        super().__init__(*args, **kwargs)

csv.DictWriter = _NanoclawCompatDictWriter


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _int_env(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _float_env(name: str, default: float) -> float:
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _patch_openai_no_thinking() -> None:
    try:
        from openai.resources.chat.completions.completions import Completions
    except Exception:
        try:
            from openai.resources.chat.completions import Completions
        except Exception as exc:
            if _bool_env("NANOCLAW_PATCH_LOG", False):
                print(f"[nanoclaw_no_thinking_patch_error] import_openai_completions {type(exc).__name__}: {exc}", flush=True)
            return

    original_create = Completions.create

    def nanoclaw_no_thinking_create(self, *args, **kwargs):
        max_tokens = _int_env("NANOCLAW_FORCE_MAX_TOKENS", 50)
        request_timeout = _float_env("MOCK_API_TIMEOUT", 1800.0)
        extra_body = dict(kwargs.get("extra_body") or {})
        chat_template_kwargs = dict(extra_body.get("chat_template_kwargs") or {})
        chat_template_kwargs["enable_thinking"] = False
        extra_body["chat_template_kwargs"] = chat_template_kwargs
        kwargs["extra_body"] = extra_body
        kwargs["max_tokens"] = max_tokens
        kwargs.pop("max_completion_tokens", None)
        kwargs["timeout"] = request_timeout
        return original_create(self, *args, **kwargs)

    Completions.create = nanoclaw_no_thinking_create
    if _bool_env("NANOCLAW_PATCH_LOG", False):
        print(
            "[nanoclaw_no_thinking_patch] openai chat completions force enable_thinking=False max_tokens="
            f"{_int_env('NANOCLAW_FORCE_MAX_TOKENS', 50)} timeout={_float_env('MOCK_API_TIMEOUT', 1800.0)}",
            flush=True,
        )


if _bool_env("NANOCLAW_FORCE_NO_THINKING", True):
    _patch_openai_no_thinking()
"""

def ensure_verifier_sitecustomize(workspace: Path) -> Path:
    patch_dir = workspace.resolve() / ".nanoclaw_python_patch"
    patch_dir.mkdir(parents=True, exist_ok=True)
    sitecustomize_path = patch_dir / "sitecustomize.py"
    if not sitecustomize_path.exists():
        sitecustomize_path.write_text(VERIFIER_SITECUSTOMIZE, encoding="utf-8")
    return patch_dir


def execute_actions(
    actions: list[dict[str, Any]],
    workspace: Path,
    *,
    args: Any,
    step: int,
) -> tuple[list[dict[str, Any]], str, bool, str | None]:
    action_events: list[dict[str, Any]] = []
    observations: list[str] = []
    final_answer: str | None = None
    is_final = False

    for index, action in enumerate(actions, start=1):
        result = execute_action(action, workspace, args=args, step=step)
        action_name = str(action.get("action") or action.get("tool") or "<missing>")
        action_events.append(
            {
                "index": index,
                "action": action,
                "observation": result.observation,
                "is_final": result.is_final,
            }
        )
        observations.append(f"Tool result {index} ({action_name}):\n{result.observation}")
        if result.is_final:
            is_final = True
            final_answer = result.final_answer
            break

    return action_events, "\n\n".join(observations), is_final, final_answer


def execute_action(action: dict[str, Any], workspace: Path, *, args: Any, step: int) -> ToolResult:
    action_name = str(action.get("action", "")).strip()
    try:
        if action_name in {"list_dir", "ls"}:
            path = str(action.get("path") or ".")
            if bool(action.get("recursive", False)):
                return ToolResult(list_dir_recursive(workspace, path, limit=args.list_limit))
            return ToolResult(list_dir(workspace, path, limit=args.list_limit))
        if action_name in {"read_file", "read"}:
            return ToolResult(read_file(workspace, require_path_like(action), limit=args.read_limit))
        if action_name in {"write_file", "write"}:
            return ToolResult(write_file(workspace, require_path_like(action), require_string(action, "content")))
        if action_name in {"edit_file", "edit"}:
            return ToolResult(
                edit_file(
                    workspace,
                    require_path_like(action),
                    require_string(action, "old_text"),
                    require_string(action, "new_text"),
                    replace_all=bool(action.get("replace_all", False)),
                )
            )
        if action_name == "apply_patch":
            changes = action.get("changes")
            if not isinstance(changes, list):
                return ToolResult("Error: 'changes' must be a list.")
            return ToolResult(apply_workspace_patch(workspace, changes))
        if action_name == "grep":
            return ToolResult(
                grep_workspace(
                    workspace,
                    require_string(action, "pattern"),
                    action.get("glob"),
                    limit=args.list_limit,
                )
            )
        if action_name == "find":
            return ToolResult(find_workspace_files(workspace, action.get("pattern"), limit=args.list_limit))
        if action_name in {"memory_search", "memory_get", "memory_append"}:
            return ToolResult("Error: memory is disabled in this local no-memory runner.")
        if action_name in {"exec", "execute_dangerous_command", "bash"}:
            return ToolResult(
                execute_bash(
                    workspace,
                    command=str(action.get("command", "")) if action.get("command") is not None else None,
                    script=str(action.get("script", "")) if action.get("script") is not None else None,
                    script_path=str(action.get("script_path", action.get("path", ""))) if (action.get("script_path") is not None or action.get("path") is not None) else None,
                    step=step,
                    timeout=float(getattr(args, "bash_timeout", 20.0)),
                )
            )
        if action_name == "ask_human_for_confirmation":
            command = str(action.get("command", ""))
            return ToolResult(f"Human response: Reject (auto). Command not approved: {command}")
        if action_name == "mkdir":
            return ToolResult(make_dir(workspace, require_string(action, "path")))
        if action_name == "run_python":
            if not args.allow_python_tool:
                return ToolResult("Error: run_python is disabled. Use read/write/edit/apply_patch actions instead.")
            return ToolResult(run_python(workspace, require_string(action, "code"), step=step, timeout=args.python_timeout))
        if action_name == "finish":
            return ToolResult(
                observation="Finished.",
                is_final=True,
                final_answer=str(action.get("answer") or ""),
            )
        if not action_name:
            return ToolResult("Error: missing action field.")
        return ToolResult(f"Error: Unknown tool '{action_name}'.")
    except Exception as exc:
        return ToolResult(f"Error while executing {action_name or '<missing>'}: {type(exc).__name__}: {exc}")


def require_string(action: dict[str, Any], key: str) -> str:
    value = action.get(key)
    if not isinstance(value, str):
        raise ValueError(f"field {key!r} must be a string")
    return value


def require_path_like(action: dict[str, Any]) -> str:
    value = action.get("path", action.get("filename"))
    if not isinstance(value, str):
        raise ValueError("field 'path' must be a string")
    return value


def resolve_workspace_path(workspace: Path, relative_path: str) -> Path:
    raw_path = relative_path.strip() or "."
    candidate_path = Path(raw_path)
    if candidate_path.is_absolute():
        raise ValueError(f"absolute paths are not allowed: {relative_path}")
    if any(part == ".." for part in candidate_path.parts):
        raise ValueError(f"parent path '..' is not allowed: {relative_path}")
    resolved = (workspace / candidate_path).resolve()
    workspace_resolved = workspace.resolve()
    if resolved != workspace_resolved and workspace_resolved not in resolved.parents:
        raise ValueError(f"path escapes workspace: {relative_path}")
    return resolved


def relative_workspace_path(workspace: Path, path: Path) -> str:
    workspace_resolved = workspace.resolve()
    path_resolved = path.resolve()
    if path_resolved == workspace_resolved:
        return "."
    return path_resolved.relative_to(workspace_resolved).as_posix()


def json_dumps(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def list_dir(workspace: Path, relative_path: str, *, limit: int) -> str:
    path = resolve_workspace_path(workspace, relative_path)
    if not path.exists():
        return "Error: path not found."
    if path.is_file():
        return json_dumps(
            {
                "path": relative_workspace_path(workspace, path),
                "entries": [
                    {
                        "path": relative_workspace_path(workspace, path),
                        "type": "file",
                    }
                ],
                "truncated": False,
            }
        )

    entries = []
    truncated = False
    for index, child in enumerate(sorted(path.iterdir())):
        if index >= limit:
            truncated = True
            break
        entries.append(
            {
                "path": relative_workspace_path(workspace, child),
                "type": "dir" if child.is_dir() else "file",
            }
        )
    return json_dumps(
        {
            "path": relative_workspace_path(workspace, path),
            "entries": entries,
            "truncated": truncated,
        }
    )


def list_dir_recursive(workspace: Path, relative_path: str, *, limit: int) -> str:
    path = resolve_workspace_path(workspace, relative_path)
    if not path.exists():
        return "Error: path not found."
    if path.is_file():
        return list_dir(workspace, relative_path, limit=limit)

    entries = []
    truncated = False
    for index, child in enumerate(sorted(path.rglob("*"))):
        if index >= limit:
            truncated = True
            break
        entries.append(
            {
                "path": relative_workspace_path(workspace, child),
                "type": "dir" if child.is_dir() else "file",
            }
        )
    return json_dumps(
        {
            "path": relative_workspace_path(workspace, path),
            "entries": entries,
            "truncated": truncated,
        }
    )


def read_file(workspace: Path, relative_path: str, *, limit: int) -> str:
    path = resolve_workspace_path(workspace, relative_path)
    if not path.exists():
        return f"Error: file does not exist: {relative_path}"
    if not path.is_file():
        return f"Error: path is not a file: {relative_path}"
    content = path.read_text(encoding="utf-8", errors="replace")
    if len(content) > limit:
        return content[:limit] + f"\n... truncated after {limit} characters"
    return content


def write_file(workspace: Path, relative_path: str, content: str) -> str:
    path = resolve_workspace_path(workspace, relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "Success: File written."


def edit_file(
    workspace: Path,
    relative_path: str,
    old_text: str,
    new_text: str,
    *,
    replace_all: bool,
) -> str:
    path = resolve_workspace_path(workspace, relative_path)
    content = path.read_text(encoding="utf-8")
    occurrences = content.count(old_text)
    if occurrences == 0:
        return "Error: target text not found."
    if not replace_all and occurrences != 1:
        return "Error: target text matched multiple locations. Pass replace_all=true or provide more specific old_text."
    updated = content.replace(old_text, new_text) if replace_all else content.replace(old_text, new_text, 1)
    path.write_text(updated, encoding="utf-8")
    changed = occurrences if replace_all else 1
    return f"Success: Applied {changed} edit(s)."


def make_dir(workspace: Path, relative_path: str) -> str:
    path = resolve_workspace_path(workspace, relative_path)
    path.mkdir(parents=True, exist_ok=True)
    return f"Success: directory exists: {relative_path}."


def apply_workspace_patch(workspace: Path, changes: list[Any]) -> str:
    if not changes:
        return "Error: no changes provided."
    results: list[str] = []
    for index, change in enumerate(changes, start=1):
        if not isinstance(change, dict):
            return f"Error: change #{index} must be an object."
        try:
            result = edit_file(
                workspace,
                require_path_like(change),
                require_string(change, "old_text"),
                require_string(change, "new_text"),
                replace_all=bool(change.get("replace_all", False)),
            )
        except Exception as exc:
            return f"Error: {type(exc).__name__}: {exc} (change #{index})"
        if result.startswith("Error:"):
            return f"{result} (change #{index})"
        results.append(f"change #{index}: {result}")
    return "Success: Patch applied.\n" + "\n".join(results)


def validate_glob_pattern(raw_pattern: str) -> str | None:
    glob_path = Path(raw_pattern)
    if glob_path.is_absolute() or any(part == ".." for part in glob_path.parts):
        return "glob must stay inside the workspace"
    return None


def find_workspace_files(workspace: Path, pattern: Any, *, limit: int) -> str:
    raw_pattern = str(pattern or "**/*").strip() or "**/*"
    validation_error = validate_glob_pattern(raw_pattern)
    if validation_error is not None:
        return f"Error: {validation_error}."

    files = []
    truncated = False
    for index, path in enumerate(sorted(path for path in workspace.glob(raw_pattern) if path.is_file())):
        if index >= limit:
            truncated = True
            break
        files.append(relative_workspace_path(workspace, path))
    return json_dumps({"files": files, "truncated": truncated})


def grep_workspace(workspace: Path, pattern: str, glob_pattern: Any, *, limit: int) -> str:
    try:
        regex = re.compile(pattern)
    except re.error as exc:
        return f"Error: invalid regex: {exc}"

    raw_glob = str(glob_pattern or "**/*").strip() or "**/*"
    validation_error = validate_glob_pattern(raw_glob)
    if validation_error is not None:
        return f"Error: {validation_error}."

    matches: list[dict[str, Any]] = []
    truncated = False
    for path in sorted(path for path in workspace.glob(raw_glob) if path.is_file()):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        relative = relative_workspace_path(workspace, path)
        for line_number, line in enumerate(text.splitlines(), start=1):
            if not regex.search(line):
                continue
            if len(matches) >= limit:
                truncated = True
                return json_dumps({"matches": matches, "truncated": truncated})
            matches.append({"path": relative, "line": line_number, "text": line})
    return json_dumps({"matches": matches, "truncated": truncated})


def execute_bash(
    workspace: Path,
    *,
    command: str | None,
    script: str | None,
    script_path: str | None,
    step: int,
    timeout: float,
) -> str:
    provided = [value is not None and value.strip() != "" for value in (command, script, script_path)]
    if sum(provided) != 1:
        return "Error: provide exactly one of command, script, or script_path/path for bash execution."

    temp_script_path: Path | None = None
    command_text_for_status = command or script or script_path or ""
    try:
        if script is not None and script.strip():
            validation_error = validate_bash_text(workspace, script)
            if validation_error is not None:
                return validation_error
            temp_script_path = workspace / f".vllm_nanoclaw_bash_step_{step}.sh"
            temp_script_path.write_text(script, encoding="utf-8")
            argv = ["bash", "--noprofile", "--norc", str(temp_script_path.name)]
        elif script_path is not None and script_path.strip():
            resolved_script_path = resolve_workspace_path(workspace, script_path)
            if not resolved_script_path.is_file():
                return f"Error: bash script does not exist: {script_path}"
            if resolved_script_path.suffix == ".py":
                validation_error = validate_python_tool_code(resolved_script_path.read_text(encoding="utf-8", errors="replace"))
                if validation_error is not None:
                    return f"Error: unsafe python script: {validation_error}"
                argv = ["python3", script_path]
            else:
                script_content = resolved_script_path.read_text(encoding="utf-8", errors="replace")
                validation_error = validate_shell_script_path_operands(workspace, script_content)
                if validation_error is not None:
                    return validation_error
                argv = ["bash", "--noprofile", "--norc", script_path]
        else:
            raw_command = command or ""
            python_inline = parse_python_inline_command(raw_command)
            if python_inline is not None:
                return execute_python_code(workspace, python_inline[0], python_inline[1], timeout=timeout)
            validation_error = validate_bash_text(workspace, raw_command)
            if validation_error is not None:
                return validation_error
            argv = ["bash", "--noprofile", "--norc", "-c", raw_command]

        try:
            process = subprocess.run(
                argv,
                cwd=workspace,
                text=True,
                capture_output=True,
                env=workspace_subprocess_env(workspace),
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            output = format_process_output(stdout, stderr)
            return f"Error: bash timed out after {timeout:g}s\n{output}"
    finally:
        if temp_script_path is not None:
            try:
                temp_script_path.unlink()
            except FileNotFoundError:
                pass

    output = format_process_output(process.stdout, process.stderr)
    if len(output) > MAX_BASH_OUTPUT_CHARS:
        output = output[:MAX_BASH_OUTPUT_CHARS] + "\n...(truncated)"
    if process.returncode != 0:
        if is_nonfatal_grep_no_match(process.returncode, command_text_for_status, process.stderr):
            return output
        return f"Error: bash exited with code {process.returncode}\n{output}"
    return output


def parse_python_inline_command(command_text: str) -> tuple[str, str] | None:
    heredoc_match = re.fullmatch(
        r"\s*(python3?|python)\s+<<\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2\s*\n(.*)\n\3\s*",
        command_text,
        flags=re.DOTALL,
    )
    if heredoc_match is not None:
        return heredoc_match.group(1), heredoc_match.group(4)

    try:
        argv = shlex.split(command_text)
    except ValueError:
        return None
    if not argv or argv[0] not in {"python", "python3"}:
        return None
    for index, argument in enumerate(argv[1:], start=1):
        if argument == "-c":
            return (argv[0], argv[index + 1]) if index + 1 < len(argv) else None
        if argument.startswith("-c") and len(argument) > 2:
            return argv[0], argument[2:]
    return None


def execute_python_code(workspace: Path, python_executable: str, code: str, *, timeout: float) -> str:
    validation_error = validate_python_tool_code(code)
    if validation_error is not None:
        return f"Error: unsafe python code: {validation_error}"
    script_path = workspace / f".vllm_nanoclaw_python_{uuid.uuid4().hex}.py"
    script_path.write_text(code, encoding="utf-8")
    try:
        try:
            process = subprocess.run(
                [python_executable, str(script_path.name)],
                cwd=workspace,
                text=True,
                capture_output=True,
                env=workspace_subprocess_env(workspace),
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            output = format_process_output(exc.stdout, exc.stderr)
            return f"Error: python timed out after {timeout:g}s\n{output}"
    finally:
        try:
            script_path.unlink()
        except FileNotFoundError:
            pass

    output = format_process_output(process.stdout, process.stderr)
    if len(output) > MAX_BASH_OUTPUT_CHARS:
        output = output[:MAX_BASH_OUTPUT_CHARS] + "\n...(truncated)"
    if process.returncode != 0:
        return f"Error: python exited with code {process.returncode}\n{output}"
    return output


def is_nonfatal_grep_no_match(returncode: int, command_text: str, stderr: str | bytes | None) -> bool:
    stderr_text = stderr.decode() if isinstance(stderr, bytes) else (stderr or "")
    return returncode == 1 and "grep" in command_text and not stderr_text.strip()


def format_process_output(stdout: str | bytes | None, stderr: str | bytes | None) -> str:
    stdout_text = stdout.decode() if isinstance(stdout, bytes) else (stdout or "")
    stderr_text = stderr.decode() if isinstance(stderr, bytes) else (stderr or "")
    output_parts = []
    if stdout_text.strip():
        output_parts.append(stdout_text.strip())
    if stderr_text.strip():
        output_parts.append(f"[stderr]\n{stderr_text.strip()}")
    return "\n\n".join(output_parts) if output_parts else "(no output)"


def validate_shell_script_path_operands(workspace: Path, text: str) -> str | None:
    unsupported_error = validate_unsupported_bash_syntax(text)
    if unsupported_error is not None:
        return unsupported_error
    for line_number, raw_line in enumerate(text.splitlines() or [text], start=1):
        stripped_line = raw_line.strip()
        if not stripped_line or stripped_line.startswith("#") or stripped_line.startswith("#!"):
            continue
        for raw_segment in BASH_CONTROL_SPLIT.split(stripped_line):
            segment = raw_segment.strip()
            if not segment:
                continue
            try:
                tokens = split_bash_segment(segment)
            except ValueError:
                continue
            for token in tokens:
                if token.startswith("../") or token == ".." or "/../" in token:
                    return f"Error: unsafe bash at line {line_number}: path escapes workspace: {token}"
    return None


def validate_bash_text(workspace: Path, text: str) -> str | None:
    if not text.strip():
        return "Error: empty bash command/script."
    unsupported_error = validate_unsupported_bash_syntax(text)
    if unsupported_error is not None:
        return unsupported_error
    return None


def validate_unsupported_bash_syntax(text: str) -> str | None:
    if BASH_BACKGROUND_RE.search(text):
        return "Error: unsupported bash syntax '&'. Background jobs are not allowed."
    for token in BASH_UNSUPPORTED_TOKENS:
        if token in text:
            return f"Error: unsupported bash syntax {token!r}. Process substitution and backticks are not allowed."
    normalized = text.replace("\\\n", " ")
    if BASH_PARENT_PATH_RE.search(normalized):
        return "Error: unsupported bash path escape. Parent-directory paths are not allowed."
    return None


def split_bash_segment(segment: str) -> list[str]:
    lexer = shlex.shlex(segment, posix=True, punctuation_chars="><")
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


def strip_output_redirections(workspace: Path, argv: list[str]) -> tuple[list[str], str | None]:
    stripped: list[str] = []
    index = 0
    while index < len(argv):
        token = argv[index]
        if token in {">", ">>"}:
            if index + 1 >= len(argv):
                return [], "missing output path after redirection"
            target = argv[index + 1]
            path_error = validate_workspace_operand(workspace, target)
            if path_error is not None:
                return [], path_error
            index += 2
            continue
        if token in {"<", "<<", "<<<", "<>"}:
            if index + 1 >= len(argv):
                return [], "missing input path or heredoc marker after redirection"
            target = argv[index + 1]
            if token == "<":
                path_error = validate_workspace_operand(workspace, target)
                if path_error is not None:
                    return [], path_error
            index += 2
            continue
        stripped.append(token)
        index += 1
    return stripped, None


def validate_bash_pipeline(workspace: Path, segment: str) -> str | None:
    try:
        tokens = split_bash_segment(segment)
    except ValueError as exc:
        return f"invalid command syntax: {exc}"
    if not tokens:
        return None
    if "||" in tokens:
        return "unsupported bash syntax '||'. Use separate commands instead"
    if tokens[0] == "|" or tokens[-1] == "|":
        return "empty command in pipeline"

    current: list[str] = []
    for token in tokens:
        if token == "|":
            segment_error = validate_bash_argv(workspace, current)
            if segment_error is not None:
                return segment_error
            current = []
        else:
            current.append(token)
    return validate_bash_argv(workspace, current)


def is_shell_assignment(token: str) -> bool:
    name, sep, _ = token.partition("=")
    return bool(sep) and bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name))


def validate_bash_argv(workspace: Path, raw_argv: list[str]) -> str | None:
    if not raw_argv:
        return "empty command in pipeline"

    argv, redirection_error = strip_output_redirections(workspace, raw_argv)
    if redirection_error is not None:
        return redirection_error
    if not argv:
        return "empty command after redirection parsing"

    command_name = argv[0]
    if is_shell_assignment(command_name):
        return None
    if command_name not in BASH_ALLOWED_COMMANDS:
        return f"command {command_name!r} is not allowed. Allowed commands: {', '.join(sorted(BASH_ALLOWED_COMMANDS))}"
    if command_name in {"bash", "sh"}:
        return validate_nested_bash_script(workspace, argv)
    if command_name in {"python", "python3"}:
        return validate_python_command(workspace, argv)
    if command_name == "set":
        return validate_set_command(argv)

    for operand in bash_path_operands(argv):
        path_error = validate_workspace_operand(workspace, operand)
        if path_error is not None:
            return path_error
    return None


def validate_bash_segment(workspace: Path, segment: str) -> str | None:
    try:
        raw_argv = split_bash_segment(segment)
    except ValueError as exc:
        return f"invalid command syntax: {exc}"
    return validate_bash_argv(workspace, raw_argv)


def validate_set_command(argv: list[str]) -> str | None:
    for argument in argv[1:]:
        if not argument.startswith("-") and not argument.startswith("+"):
            return "set only supports shell option flags in this restricted runner"
    return None


def validate_nested_bash_script(workspace: Path, argv: list[str]) -> str | None:
    operands = list(iter_operands(argv[1:]))
    if not operands:
        return "bash/sh requires a script path in this restricted runner"
    if operands[0] in {"-c", "--command"} or any(argument in {"-c", "--command"} for argument in argv[1:]):
        return "bash/sh -c is not allowed inside restricted bash; use the bash tool command field instead"
    script_operand = operands[0]
    path_error = validate_workspace_operand(workspace, script_operand)
    if path_error is not None:
        return path_error
    script_path = resolve_workspace_path(workspace, script_operand)
    if not script_path.is_file():
        return f"bash script does not exist: {script_operand}"
    return validate_shell_script_path_operands(workspace, script_path.read_text(encoding="utf-8", errors="replace"))


def validate_python_command(workspace: Path, argv: list[str]) -> str | None:
    if any(argument == "-m" or argument.startswith("-m") for argument in argv[1:]):
        return "python -m is not allowed inside restricted bash"
    for index, argument in enumerate(argv[1:], start=1):
        if argument == "-c":
            if index + 1 >= len(argv):
                return "python -c requires code"
            return validate_python_tool_code(argv[index + 1])
        if argument.startswith("-c") and len(argument) > 2:
            return validate_python_tool_code(argument[2:])
    operands = list(iter_operands(argv[1:]))
    if not operands:
        return "python requires a workspace script path in this restricted runner"
    script_operand = operands[0]
    if script_operand == "-":
        return "python stdin execution is only supported through python << EOF in the bash command field"
    path_error = validate_workspace_operand(workspace, script_operand)
    if path_error is not None:
        return path_error
    script_path = resolve_workspace_path(workspace, script_operand)
    if not script_path.is_file():
        return f"python script does not exist: {script_operand}"
    return validate_python_tool_code(script_path.read_text(encoding="utf-8", errors="replace"))


def bash_path_operands(argv: list[str]) -> list[str]:
    command_name = argv[0]
    args = argv[1:]
    if command_name in {"pwd", "which"} or command_name in {"echo", "printf", "true", "false", "test", "["}:
        return []
    if command_name == "grep":
        operands = list(iter_operands(args, options_with_values={"-e", "--regexp", "-f", "--file", "-m", "--max-count", "-A", "-B", "-C", "--after-context", "--before-context", "--context", "--include", "--exclude", "--exclude-dir"}))
        uses_explicit_pattern_option = any(argument in {"-e", "--regexp", "-f", "--file"} or argument.startswith("-e") for argument in args)
        return operands if uses_explicit_pattern_option else operands[1:]
    if command_name == "find":
        operands: list[str] = []
        iterator = iter(args)
        for argument in iterator:
            if argument == "--":
                continue
            if argument.startswith("-") or argument in {"!", "(", ")"}:
                if argument in {"-name", "-path", "-type", "-maxdepth", "-mindepth", "-size", "-mtime", "-newer"}:
                    next(iterator, None)
                continue
            operands.append(argument)
        return operands[:1]
    if command_name == "cut":
        return list(iter_operands(args, options_with_values={"-b", "-c", "-d", "-f", "--bytes", "--characters", "--delimiter", "--fields"}))
    if command_name == "sed":
        operands = list(iter_operands(args, options_with_values={"-e", "--expression", "-f", "--file"}))
        uses_script_option = any(argument in {"-e", "--expression", "-f", "--file"} or argument.startswith("-e") for argument in args)
        return operands if uses_script_option else operands[1:]
    if command_name == "awk":
        operands = list(iter_operands(args, options_with_values={"-f", "--file", "-v"}))
        uses_script_file = any(argument in {"-f", "--file"} for argument in args)
        return operands if uses_script_file else operands[1:]
    if command_name == "tr":
        return []
    if command_name in {"basename", "dirname"}:
        return list(iter_operands(args))[:1]
    if command_name in {"head", "tail"}:
        return list(iter_operands(args, options_with_values={"-n", "--lines", "-c", "--bytes"}))
    if command_name == "chmod":
        operands = list(iter_operands(args))
        return operands[1:]
    return list(iter_operands(args))


def iter_operands(args: list[str], *, options_with_values: set[str] | None = None) -> list[str]:
    options_with_values = options_with_values or set()
    operands: list[str] = []
    skip_next = False
    after_double_dash = False
    for argument in args:
        if skip_next:
            skip_next = False
            continue
        if not after_double_dash and argument == "--":
            after_double_dash = True
            continue
        if not after_double_dash and argument.startswith("-") and argument != "-":
            option_name = argument.split("=", 1)[0]
            if option_name in options_with_values and "=" not in argument:
                skip_next = True
            continue
        operands.append(argument)
    return operands


def validate_workspace_operand(workspace: Path, operand: str) -> str | None:
    if operand in {"", "-"}:
        return None
    if operand.startswith("~"):
        return f"path {operand!r} is not allowed: '~' expansion is disabled"

    candidate_path = Path(operand)
    workspace_resolved = workspace.resolve()
    resolved = candidate_path.resolve() if candidate_path.is_absolute() else (workspace / candidate_path).resolve()
    if resolved != workspace_resolved and workspace_resolved not in resolved.parents:
        return f"path escapes workspace: {operand}"
    return None


def run_python(workspace: Path, code: str, *, step: int, timeout: float) -> str:
    safety_error = validate_python_tool_code(code)
    if safety_error is not None:
        return f"Error: blocked unsafe Python code: {safety_error}"

    script_path = workspace / f".vllm_nanoclaw_step_{step}.py"
    script_path.write_text(code, encoding="utf-8")
    try:
        try:
            process = subprocess.run(
                [sys.executable, str(script_path.name)],
                cwd=workspace,
                text=True,
                capture_output=True,
                env=workspace_subprocess_env(workspace),
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            output_parts = []
            if stdout:
                output_parts.append(str(stdout).strip())
            if stderr:
                output_parts.append(f"[stderr]\n{str(stderr).strip()}")
            output = "\n\n".join(output_parts) if output_parts else "(no output)"
            return f"Error: Python timed out after {timeout:g}s\n{output}"
    finally:
        try:
            script_path.unlink()
        except FileNotFoundError:
            pass

    output_parts = []
    if process.stdout.strip():
        output_parts.append(process.stdout.strip())
    if process.stderr.strip():
        output_parts.append(f"[stderr]\n{process.stderr.strip()}")
    output = "\n\n".join(output_parts) if output_parts else "(no output)"
    if process.returncode != 0:
        return f"Error: Python exited with code {process.returncode}\n{output}"
    return output


def find_parent_directory_literal(code: str) -> str | None:
    for match in re.finditer(r"(['\"])(.*?)\1", code, flags=re.DOTALL):
        literal = match.group(2).replace("\\", "/")
        if ".." in literal.split("/"):
            return match.group(0)
    return None


def validate_python_tool_code(code: str) -> str | None:
    lowered = code.lower()
    parent_literal = find_parent_directory_literal(code)
    if parent_literal is not None:
        return f"parent-directory path literal is not allowed: {parent_literal}"
    absolute_match = ABSOLUTE_PATH_LITERAL.search(code)
    if absolute_match:
        return f"absolute path literal is not allowed: {absolute_match.group(0)}"
    for pattern in DANGEROUS_PYTHON_PATTERNS:
        if pattern in lowered:
            return f"forbidden pattern {pattern!r}"
    return None


def workspace_subprocess_env(workspace: Path) -> dict[str, str]:
    workspace_resolved = workspace.resolve()
    home_dir = workspace_resolved / ".runner_home"
    tmp_dir = workspace_resolved / ".runner_tmp"
    home_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env.pop("BASH_ENV", None)
    env.pop("ENV", None)
    env["HOME"] = str(home_dir)
    env["TMPDIR"] = str(tmp_dir)
    env["TEMP"] = str(tmp_dir)
    env["TMP"] = str(tmp_dir)
    env["PWD"] = str(workspace_resolved)
    env["PYTHONNOUSERSITE"] = "1"
    env["NANOCLAW_WORKSPACE"] = str(workspace_resolved)
    patch_dir = ensure_verifier_sitecustomize(workspace_resolved)
    env["PYTHONPATH"] = f"{patch_dir}{os.pathsep}{env.get('PYTHONPATH', '')}" if env.get("PYTHONPATH") else str(patch_dir)
    env.setdefault("NANOCLAW_FORCE_NO_THINKING", "1")
    env.setdefault("NANOCLAW_FORCE_MAX_TOKENS", "50")
    return env
