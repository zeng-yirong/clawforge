from __future__ import annotations

import json
import logging
import os

import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import datasets
import numpy as np

from verl.tools.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema, ToolResponse
from verl.utils.dataset import RLHFDataset
from verl.utils.rollout_trace import rollout_trace_op

from nanoclaw_recipe.common import (
    NanoclawTaskSpec,
    copy_task_bundle as common_copy_task_bundle,
    discover_tasks as common_discover_tasks,
    normalize_task_ids as common_normalize_task_ids,
    score_summary as common_score_summary,
)

logger = logging.getLogger(__name__)

DEFAULT_TEMP_ROOT = "/tmp/verl_nanoclaw_workspaces"
DEFAULT_TOOL_NAMES = (
    "list_dir",
    "read_file",
    "write_file",
    "edit_file",
    "apply_patch",
    "grep",
    "find",
    "mkdir",
    "bash",
)

MAX_BASH_OUTPUT_CHARS = 8000
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


@dataclass(frozen=True, slots=True)
class NanoclawTaskSpec:
    task_id: str
    base_tasks: Path
    task_dir: Path
    prompt_path: Path
    env_builder_path: Path
    verifier_path: Path | None
    input_layout: str = "legacy"
    manifest_path: Path | None = None


class WorkspaceSetupError(RuntimeError):
    def __init__(self, message: str, state: dict[str, Any]):
        super().__init__(message)
        self.state = state


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def bool_config(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def float_config(value: Any, default: float) -> float:
    if value is None:
        return default
    return float(value)


def int_config(value: Any, default: int) -> int:
    if value is None:
        return default
    return int(value)


def plain_container(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): plain_container(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain_container(item) for item in value]
    return value


def normalize_task_ids(raw_task_ids: Any) -> set[str] | None:
    return common_normalize_task_ids(raw_task_ids)


def safe_name(raw_name: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", raw_name).strip("._")
    return safe or "task"


def json_dumps(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def discover_tasks(base_tasks: Path, *, task_glob: str, task_ids: set[str] | None) -> list[NanoclawTaskSpec]:
    return common_discover_tasks(base_tasks, task_glob=task_glob, task_ids=task_ids)


def discover_legacy_tasks(
    base_tasks: Path, *, tasks_root: Path, task_glob: str, task_ids: set[str] | None
) -> list[NanoclawTaskSpec]:

    script_root = find_script_root(base_tasks)
    specs: list[NanoclawTaskSpec] = []
    for task_dir in sorted(path for path in tasks_root.glob(task_glob) if path.is_dir()):
        task_id = task_dir.name
        if task_ids is not None and task_id not in task_ids:
            continue

        env_builder_path = task_dir / "env_builder.py"
        if not env_builder_path.is_file():
            continue

        prompt_path = find_prompt_path(tasks_root, task_dir, task_id)
        verifier_path = find_verifier_path(script_root, task_id) if script_root is not None else None
        specs.append(
            NanoclawTaskSpec(
                task_id=task_id,
                base_tasks=base_tasks,
                task_dir=task_dir,
                prompt_path=prompt_path,
                env_builder_path=env_builder_path,
                verifier_path=verifier_path,
                input_layout="legacy",
            )
        )

    if task_ids is not None:
        found_task_ids = {spec.task_id for spec in specs}
        missing_task_ids = sorted(task_ids - found_task_ids)
        if missing_task_ids:
            raise FileNotFoundError(f"requested task ids not found or missing env_builder.py: {missing_task_ids}")
    if not specs:
        raise FileNotFoundError(f"no task directories matched {task_glob!r} under {tasks_root}")
    return specs


def discover_flat_tasks(base_tasks: Path, *, task_glob: str, task_ids: set[str] | None) -> list[NanoclawTaskSpec]:
    if not base_tasks.is_dir():
        raise FileNotFoundError(f"Nanoclaw data directory not found: {base_tasks}")

    if (base_tasks / "env_builder.py").is_file():
        task_dirs = [base_tasks]
    else:
        task_dirs = sorted(path for path in base_tasks.glob(task_glob) if path.is_dir())

    specs: list[NanoclawTaskSpec] = []
    for task_dir in task_dirs:
        manifest_files, manifest_path, manifest_task_id = read_manifest(task_dir)
        task_id = manifest_task_id or task_dir.name
        if task_ids is not None and task_id not in task_ids:
            continue

        env_builder_path = resolve_manifest_file(task_dir, manifest_files, "env_builder") or task_dir / "env_builder.py"
        if not env_builder_path.is_file():
            continue

        prompt_path = find_prompt_path(base_tasks, task_dir, task_id, manifest_files=manifest_files)
        verifier_path = find_verifier_path(None, task_id, task_dir=task_dir, manifest_files=manifest_files)
        specs.append(
            NanoclawTaskSpec(
                task_id=task_id,
                base_tasks=base_tasks,
                task_dir=task_dir,
                prompt_path=prompt_path,
                env_builder_path=env_builder_path,
                verifier_path=verifier_path,
                input_layout="flat",
                manifest_path=manifest_path,
            )
        )

    if task_ids is not None:
        found_task_ids = {spec.task_id for spec in specs}
        missing_task_ids = sorted(task_ids - found_task_ids)
        if missing_task_ids:
            raise FileNotFoundError(f"requested task ids not found or missing env_builder.py: {missing_task_ids}")
    if not specs:
        raise FileNotFoundError(f"no flat Nanoclaw task directories matched {task_glob!r} under {base_tasks}")
    return specs


def read_manifest(task_dir: Path) -> tuple[dict[str, str], Path | None, str | None]:
    manifest_path = task_dir / "manifest.json"
    if not manifest_path.is_file():
        return {}, None, None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as manifest_exc:
        raise ValueError(f"failed to read Nanoclaw manifest {manifest_path}: {manifest_exc}") from manifest_exc

    files = manifest.get("files") if isinstance(manifest, dict) else None
    manifest_files = {str(key): str(value) for key, value in files.items()} if isinstance(files, dict) else {}
    task_id = manifest.get("task_id") if isinstance(manifest, dict) else None
    return manifest_files, manifest_path, str(task_id) if task_id else None


def resolve_manifest_file(task_dir: Path, manifest_files: dict[str, str] | None, key: str) -> Path | None:
    if not manifest_files:
        return None
    relative_path = manifest_files.get(key)
    if not relative_path:
        return None
    candidate = (task_dir / relative_path).expanduser()
    return candidate if candidate.is_file() else None


TASK_BUNDLE_IGNORE = shutil.ignore_patterns(
    "workspace_before",
    "workspace_after",
    "workplace_before",
    "workplace_after",
    "__pycache__",
    ".runner_home",
    ".runner_tmp",
    ".nanoclaw_python_patch",
)


def make_result_dir(task_config: dict[str, Any], *, request_id: str, task_id: str, temp_root: Path) -> Path:
    rollout_step = optional_int(task_config.get("rollout_step"))
    rollout_n = optional_int(task_config.get("rollout_n"))
    if rollout_step is None or rollout_n is None:
        return Path(tempfile.mkdtemp(prefix=f"{safe_name(task_id)}_{safe_name(request_id)[:12]}_", dir=str(temp_root)))

    step_dir = temp_root / f"step_{rollout_step}"
    result_dir = step_dir / f"{safe_name(task_id)}_sample_{rollout_n}"
    if result_dir.exists():
        if bool_config(task_config.get("strict_result_dir"), False):
            raise FileExistsError(
                "canonical Nanoclaw result directory already exists in strict mode: "
                f"task_id={task_id!r}, rollout_step={rollout_step}, rollout_n={rollout_n}, "
                f"path={result_dir}, request_id={request_id}"
            )
        result_dir = step_dir / f"{result_dir.name}_{safe_name(request_id)[:8]}"
    result_dir.mkdir(parents=True, exist_ok=False)
    return result_dir


def copy_task_bundle(task_config: dict[str, Any], result_dir: Path) -> None:
    common_copy_task_bundle(task_config, result_dir)


def find_script_root(base_tasks: Path) -> Path | None:
    for dirname in ("scrips", "scripts"):
        candidate = base_tasks / dirname
        if candidate.is_dir():
            return candidate
    return None


def find_prompt_path(
    tasks_root: Path,
    task_dir: Path,
    task_id: str,
    *,
    manifest_files: dict[str, str] | None = None,
) -> Path:
    manifest_prompt = resolve_manifest_file(task_dir, manifest_files, "prompt")
    candidates = (
        manifest_prompt,
        tasks_root / "prompts" / f"{task_id}.md",
        task_dir / "prompts.md",
        task_dir / "prompt.md",
        task_dir / "task.md",
    )
    for candidate in candidates:
        if candidate is not None and candidate.is_file():
            return candidate
    raise FileNotFoundError(
        f"prompt file not found for {task_id}; tried: " + ", ".join(str(path) for path in candidates)
    )


def find_verifier_path(
    script_root: Path | None,
    task_id: str,
    *,
    task_dir: Path | None = None,
    manifest_files: dict[str, str] | None = None,
) -> Path | None:
    candidates: list[Path | None] = [resolve_manifest_file(task_dir, manifest_files, "verifier") if task_dir else None]
    if task_dir is not None:
        candidates.extend((task_dir / "workplace_verifier.py", task_dir / "verify_workplace.py"))
    if script_root is not None:
        candidates.extend(
            (
                script_root / task_id / "verify_workplace.py",
                script_root / f"{task_id}.py",
                script_root / "verify_workplace.py",
            )
        )
    for candidate in candidates:
        if candidate is not None and candidate.is_file():
            return candidate
    return None


def build_system_prompt(*, max_steps: Any, allow_bash: bool) -> str:
    bash_line = "The restricted bash tool is available." if allow_bash else "The bash tool is disabled."
    max_steps_line = f"The rollout should finish within about {max_steps} assistant turns." if max_steps else ""
    return "\n".join(
        line
        for line in (
            "You are solving a Nanoclaw workspace task inside VERL multi-turn RL.",
            "A fresh per-rollout workspace is prepared automatically before the first workspace tool call.",
            "All tool paths must be relative to that workspace. Do not use absolute paths or '..'.",
            "Inspect files before editing them, make the smallest correct changes, then stop with a final answer.",
            "The verifier scores the final workspace, not your final prose answer.",
            "For large files, do not read the whole file first. Use bash commands such as find, ls -lh, wc -l, wc -c, head, tail, grep, and sed -n to inspect targeted parts.",
            "For structured or large data, write and run a small Python script inside the workspace to compute the answer.",
            "Prefer finalizing once the requested files are written; do not repeatedly re-check the same evidence.",
            bash_line,
            max_steps_line,
            "Use Qwen3-Coder XML tool calls, for example:",
            "<tool_call>",
            "<function=read_file>",
            "<parameter=path>",
            "relative/file.txt",
            "</parameter>",
            "</function>",
            "</tool_call>",
        )
        if line
    )


def build_initial_messages(prompt_text: str, *, max_steps: Any, allow_bash: bool) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": build_system_prompt(max_steps=max_steps, allow_bash=allow_bash)},
        {
            "role": "user",
            "content": (
                "Solve this task by using the workspace tools to inspect and modify files. "
                "Only provide a final answer after the requested workspace changes are complete.\n\n"
                f"Task:\n{prompt_text}"
            ),
        },
    ]


def task_config_from_spec(spec: NanoclawTaskSpec, config: Any) -> dict[str, Any]:
    temp_root = str(Path(str(config.get("nanoclaw_temp_root", DEFAULT_TEMP_ROOT))).expanduser())
    return {
        "task_id": spec.task_id,
        "base_tasks": str(spec.base_tasks),
        "task_dir": str(spec.task_dir),
        "prompt_path": str(spec.prompt_path),
        "env_builder_path": str(spec.env_builder_path),
        "verifier_path": str(spec.verifier_path) if spec.verifier_path is not None else None,
        "input_layout": spec.input_layout,
        "manifest_path": str(spec.manifest_path) if spec.manifest_path is not None else None,
        "temp_root": temp_root,
        "cleanup_workspace": bool_config(config.get("nanoclaw_cleanup_workspaces", True), True),
        "keep_failed_workspace": bool_config(config.get("nanoclaw_keep_failed_workspaces", False), False),
        "env_builder_timeout": float_config(config.get("nanoclaw_env_builder_timeout", 120.0), 120.0),
        "verifier_timeout": float_config(config.get("nanoclaw_verifier_timeout", 300.0), 300.0),
        "reward_score_mode": str(config.get("nanoclaw_reward_score_mode", "ratio")),
        "missing_verifier_score": float_config(config.get("nanoclaw_missing_verifier_score", 0.0), 0.0),
        "setup_failure_score": float_config(config.get("nanoclaw_setup_failure_score", 0.0), 0.0),
        "allow_bash": bool_config(config.get("nanoclaw_allow_bash", True), True),
        "save_workspace_before": bool_config(config.get("nanoclaw_save_workspace_before", False), False),
        "strict_result_dir": bool_config(config.get("nanoclaw_strict_result_dir", False), False),
    }


def build_tools_kwargs(task_config: dict[str, Any], tool_names: tuple[str, ...]) -> dict[str, Any]:
    create_kwargs = {"nanoclaw": task_config}
    tools_kwargs = {"_nanoclaw": create_kwargs}
    for tool_name in tool_names:
        tools_kwargs[tool_name] = {"create_kwargs": create_kwargs}
    return tools_kwargs


class CustomRLHFDataset(RLHFDataset):
    def _download(self, use_origin_parquet: bool = False):
        source_files = self.original_data_files if use_origin_parquet else self.data_files
        resolved_files = [str(Path(str(data_file)).expanduser().resolve()) for data_file in source_files]
        if use_origin_parquet:
            self.original_data_files = resolved_files
        else:
            self.data_files = resolved_files

    def _read_files_and_tokenize(self):
        task_glob = str(self.config.get("nanoclaw_task_glob", "data_*"))
        task_ids = normalize_task_ids(self.config.get("nanoclaw_task_ids", None))
        raw_tool_names = self.config.get("nanoclaw_tool_names", DEFAULT_TOOL_NAMES)
        tool_names = tuple(str(tool_name) for tool_name in raw_tool_names)
        max_steps = self.config.get("nanoclaw_max_steps", None)

        rows: list[dict[str, Any]] = []
        for base_tasks_str in self.data_files:
            base_tasks = Path(base_tasks_str).expanduser().resolve()
            specs = discover_tasks(base_tasks, task_glob=task_glob, task_ids=task_ids)
            for spec in specs:
                task_config = task_config_from_spec(spec, self.config)
                prompt_text = spec.prompt_path.read_text(encoding="utf-8")
                tools_kwargs = build_tools_kwargs(task_config, tool_names)
                index = len(rows)
                rows.append(
                    {
                        self.prompt_key: build_initial_messages(
                            prompt_text,
                            max_steps=max_steps,
                            allow_bash=bool_config(task_config.get("allow_bash"), True),
                        ),
                        "data_source": f"nanoclaw/{spec.task_id}",
                        "reward_model": {"style": "rule", "ground_truth": task_config},
                        "extra_info": {
                            "index": index,
                            "task_id": spec.task_id,
                            "nanoclaw_task": task_config,
                            "tools_kwargs": tools_kwargs,
                            "tool_selection": list(tool_names),
                        },
                        "agent_name": "tool_agent",
                    }
                )

        if not rows:
            raise FileNotFoundError(f"no Nanoclaw tasks discovered from data files: {self.data_files}")

        self.dataframe = datasets.Dataset.from_list(rows)
        total = len(self.dataframe)
        print(f"nanoclaw dataset len: {total}")

        if self.max_samples > 0 and self.max_samples < total:
            if self.shuffle:
                rng_args = (self.seed,) if self.seed is not None else ()
                random_generator = np.random.default_rng(*rng_args)
                indices = random_generator.choice(total, size=self.max_samples, replace=False)
            else:
                indices = np.arange(self.max_samples)
            self.dataframe = self.dataframe.select(indices.tolist())
            print(f"selected {self.max_samples} nanoclaw samples out of {total}")

        self.dataframe = self.maybe_filter_out_long_prompts(self.dataframe)



VERIFIER_SITECUSTOMIZE = '''
from __future__ import annotations

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
'''


def ensure_verifier_sitecustomize(workspace: Path) -> Path:
    patch_dir = workspace.resolve() / ".nanoclaw_python_patch"
    patch_dir.mkdir(parents=True, exist_ok=True)
    sitecustomize_path = patch_dir / "sitecustomize.py"
    if not sitecustomize_path.exists():
        sitecustomize_path.write_text(VERIFIER_SITECUSTOMIZE, encoding="utf-8")
    return patch_dir


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


def run_env_builder(env_builder_path: Path, workspace: Path, *, timeout: float) -> dict[str, Any]:
    started_at = time.time()
    try:
        runner_code = (
            "import runpy, sys\n"
            "namespace = runpy.run_path(sys.argv[1], run_name='__nanoclaw_env_builder__')\n"
            "build_env = namespace.get('build_env')\n"
            "if callable(build_env):\n"
            "    build_env()\n"
        )
        process = subprocess.run(
            [sys.executable, "-c", runner_code, str(env_builder_path)],
            cwd=workspace,
            text=True,
            capture_output=True,
            env=workspace_subprocess_env(workspace),
            timeout=timeout,
            check=False,
        )
        result = {
            "returncode": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "elapsed_seconds": round(time.time() - started_at, 3),
        }
    except subprocess.TimeoutExpired as timeout_exc:
        result = {
            "returncode": None,
            "stdout": timeout_exc.stdout or "",
            "stderr": timeout_exc.stderr or "",
            "elapsed_seconds": round(time.time() - started_at, 3),
            "error": f"env_builder.py timed out after {timeout:g}s",
        }
        raise RuntimeError(result["error"]) from timeout_exc

    if process.returncode != 0:
        raise RuntimeError(
            f"env_builder.py failed for {env_builder_path} with code {process.returncode}\n"
            f"stdout:\n{process.stdout}\n\nstderr:\n{process.stderr}"
        )
    return result


def prepare_workspace(task_config: dict[str, Any], *, request_id: str, source: str) -> dict[str, Any]:
    task_id = str(task_config.get("task_id") or "unknown_task")
    temp_root = Path(str(task_config.get("temp_root") or DEFAULT_TEMP_ROOT)).expanduser().resolve()
    temp_root.mkdir(parents=True, exist_ok=True)

    result_dir = make_result_dir(task_config, request_id=request_id, task_id=task_id, temp_root=temp_root)
    workspace_after = result_dir / "workspace_after"
    workspace_before = result_dir / "workspace_before"
    save_workspace_before = bool_config(task_config.get("save_workspace_before"), False)
    workspace_after.mkdir(parents=True, exist_ok=False)

    env_builder_path = Path(str(task_config["env_builder_path"])).expanduser().resolve()
    prompt_path = Path(str(task_config["prompt_path"])).expanduser().resolve()
    verifier_path = Path(str(task_config["verifier_path"])).expanduser().resolve() if task_config.get("verifier_path") else None

    state: dict[str, Any] = {
        "task_id": task_id,
        "status": "initializing",
        "source": source,
        "result_dir": str(result_dir),
        "workspace_after": str(workspace_after),
        "workspace_before": str(workspace_before) if save_workspace_before else None,
        "save_workspace_before": save_workspace_before,
        "base_tasks": task_config.get("base_tasks"),
        "task_dir": task_config.get("task_dir"),
        "prompt_path": str(prompt_path),
        "env_builder_path": str(env_builder_path),
        "verifier_path": str(verifier_path) if verifier_path is not None else None,
        "original_verifier_path": str(verifier_path) if verifier_path is not None else None,
        "created_at": utc_now(),
        "rollout_step": task_config.get("rollout_step"),
        "rollout_sample_index": task_config.get("rollout_sample_index"),
        "rollout_n": task_config.get("rollout_n"),
        "validate": task_config.get("validate"),
        "cleanup_workspace": bool_config(task_config.get("cleanup_workspace"), True),
        "keep_failed_workspace": bool_config(task_config.get("keep_failed_workspace"), False),
        "task_config": task_config,
        "tool_call_count": 0,
    }

    try:
        copy_task_bundle(task_config, result_dir)

        env_result = run_env_builder(
            env_builder_path,
            workspace_after,
            timeout=float_config(task_config.get("env_builder_timeout"), 120.0),
        )
        state["env_builder"] = env_result
        if save_workspace_before:
            shutil.copytree(workspace_after, workspace_before, ignore=TASK_BUNDLE_IGNORE)
        state["status"] = "ready"
    except Exception as setup_exc:
        state["status"] = "setup_failed"
        state["setup_error"] = f"{type(setup_exc).__name__}: {setup_exc}"
        write_runtime_metadata(state)
        raise WorkspaceSetupError(state["setup_error"], state) from setup_exc

    write_runtime_metadata(state)
    return state


def write_runtime_metadata(state: dict[str, Any]) -> None:
    result_dir = Path(str(state["result_dir"]))
    metadata_path = result_dir / "nanoclaw_metadata.json"
    metadata_path.write_text(json_dumps(state) + "\n", encoding="utf-8")


def resolve_workspace_path(workspace: Path, relative_path: str) -> Path:
    raw_path = str(relative_path or ".").strip() or "."
    candidate_path = Path(raw_path)
    if candidate_path.is_absolute():
        raise ValueError(f"absolute paths are not allowed: {relative_path}")
    if any(part == ".." for part in candidate_path.parts):
        raise ValueError(f"parent path '..' is not allowed: {relative_path}")
    resolved_path = (workspace / candidate_path).resolve()
    workspace_resolved = workspace.resolve()
    if resolved_path != workspace_resolved and workspace_resolved not in resolved_path.parents:
        raise ValueError(f"path escapes workspace: {relative_path}")
    return resolved_path


def relative_workspace_path(workspace: Path, path: Path) -> str:
    workspace_resolved = workspace.resolve()
    path_resolved = path.resolve()
    if path_resolved == workspace_resolved:
        return "."
    return path_resolved.relative_to(workspace_resolved).as_posix()


def require_string(parameters: dict[str, Any], key: str) -> str:
    value = parameters.get(key)
    if not isinstance(value, str):
        raise ValueError(f"field {key!r} must be a string")
    return value


def require_path_like(parameters: dict[str, Any]) -> str:
    value = parameters.get("path", parameters.get("filename"))
    if not isinstance(value, str):
        raise ValueError("field 'path' must be a string")
    return value


def list_dir(workspace: Path, relative_path: str, *, limit: int) -> str:
    path = resolve_workspace_path(workspace, relative_path)
    if not path.exists():
        return "Error: path not found."
    if path.is_file():
        return json_dumps(
            {
                "path": relative_workspace_path(workspace, path),
                "entries": [{"path": relative_workspace_path(workspace, path), "type": "file"}],
                "truncated": False,
            }
        )

    entries = []
    truncated = False
    for entry_index, child_path in enumerate(sorted(path.iterdir())):
        if entry_index >= limit:
            truncated = True
            break
        entries.append(
            {
                "path": relative_workspace_path(workspace, child_path),
                "type": "dir" if child_path.is_dir() else "file",
            }
        )
    return json_dumps({"path": relative_workspace_path(workspace, path), "entries": entries, "truncated": truncated})


def list_dir_recursive(workspace: Path, relative_path: str, *, limit: int) -> str:
    path = resolve_workspace_path(workspace, relative_path)
    if not path.exists():
        return "Error: path not found."
    if path.is_file():
        return list_dir(workspace, relative_path, limit=limit)

    entries = []
    truncated = False
    for entry_index, child_path in enumerate(sorted(path.rglob("*"))):
        if entry_index >= limit:
            truncated = True
            break
        entries.append(
            {
                "path": relative_workspace_path(workspace, child_path),
                "type": "dir" if child_path.is_dir() else "file",
            }
        )
    return json_dumps({"path": relative_workspace_path(workspace, path), "entries": entries, "truncated": truncated})


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
    return "Success: file written."


def edit_file(workspace: Path, relative_path: str, old_text: str, new_text: str, *, replace_all: bool) -> str:
    if old_text == "":
        return "Error: old_text must not be empty."
    path = resolve_workspace_path(workspace, relative_path)
    if not path.is_file():
        return f"Error: path is not a file: {relative_path}"
    content = path.read_text(encoding="utf-8", errors="replace")
    occurrences = content.count(old_text)
    if occurrences == 0:
        return "Error: target text not found."
    if not replace_all and occurrences != 1:
        return "Error: target text matched multiple locations. Pass replace_all=true or provide more specific old_text."
    updated = content.replace(old_text, new_text) if replace_all else content.replace(old_text, new_text, 1)
    path.write_text(updated, encoding="utf-8")
    changed = occurrences if replace_all else 1
    return f"Success: applied {changed} edit(s)."


def make_dir(workspace: Path, relative_path: str) -> str:
    path = resolve_workspace_path(workspace, relative_path)
    path.mkdir(parents=True, exist_ok=True)
    return f"Success: directory exists: {relative_path}."


def parse_patch_changes(parameters: dict[str, Any]) -> list[Any]:
    raw_changes = parameters.get("changes", parameters.get("changes_json"))
    if raw_changes is None:
        raise ValueError("field 'changes_json' must contain a JSON array of edit objects")
    if isinstance(raw_changes, str):
        raw_changes = json.loads(raw_changes)
    if not isinstance(raw_changes, list):
        raise ValueError("patch changes must be a list")
    return raw_changes


def apply_workspace_patch(workspace: Path, changes: list[Any]) -> str:
    if not changes:
        return "Error: no changes provided."
    results: list[str] = []
    for change_index, change in enumerate(changes, start=1):
        if not isinstance(change, dict):
            return f"Error: change #{change_index} must be an object."
        try:
            result = edit_file(
                workspace,
                require_path_like(change),
                require_string(change, "old_text"),
                require_string(change, "new_text"),
                replace_all=bool_config(change.get("replace_all", False), False),
            )
        except Exception as patch_exc:
            return f"Error: {type(patch_exc).__name__}: {patch_exc} (change #{change_index})"
        if result.startswith("Error:"):
            return f"{result} (change #{change_index})"
        results.append(f"change #{change_index}: {result}")
    return "Success: patch applied.\n" + "\n".join(results)


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
    for file_index, path in enumerate(sorted(path for path in workspace.glob(raw_pattern) if path.is_file())):
        if file_index >= limit:
            truncated = True
            break
        files.append(relative_workspace_path(workspace, path))
    return json_dumps({"files": files, "truncated": truncated})


def grep_workspace(workspace: Path, pattern: str, glob_pattern: Any, *, limit: int) -> str:
    try:
        compiled_pattern = re.compile(pattern)
    except re.error as regex_exc:
        return f"Error: invalid regex: {regex_exc}"

    raw_glob = str(glob_pattern or "**/*").strip() or "**/*"
    validation_error = validate_glob_pattern(raw_glob)
    if validation_error is not None:
        return f"Error: {validation_error}."

    matches: list[dict[str, Any]] = []
    for path in sorted(path for path in workspace.glob(raw_glob) if path.is_file()):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        relative_path = relative_workspace_path(workspace, path)
        for line_number, line in enumerate(text.splitlines(), start=1):
            if not compiled_pattern.search(line):
                continue
            if len(matches) >= limit:
                return json_dumps({"matches": matches, "truncated": True})
            matches.append({"path": relative_path, "line": line_number, "text": line})
    return json_dumps({"matches": matches, "truncated": False})


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
    validation_error = validate_python_script_text(code)
    if validation_error is not None:
        return f"Error: unsafe python code: {validation_error}"
    script_path = workspace / f".verl_nanoclaw_python_{uuid.uuid4().hex}.py"
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
        except subprocess.TimeoutExpired as timeout_exc:
            output = format_process_output(timeout_exc.stdout, timeout_exc.stderr)
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


def execute_bash(workspace: Path, *, command: str | None, script: str | None, script_path: str | None, timeout: float) -> str:
    provided = [value is not None and value.strip() != "" for value in (command, script, script_path)]
    if sum(provided) != 1:
        return "Error: provide exactly one of command, script, or path for bash execution."

    temp_script_path: Path | None = None
    command_text_for_status = command or script or script_path or ""
    try:
        if script is not None and script.strip():
            validation_error = validate_bash_text(workspace, script)
            if validation_error is not None:
                return validation_error
            temp_script_path = workspace / f".verl_nanoclaw_bash_{uuid.uuid4().hex}.sh"
            temp_script_path.write_text(script, encoding="utf-8")
            argv = ["bash", "--noprofile", "--norc", str(temp_script_path.name)]
        elif script_path is not None and script_path.strip():
            resolved_script_path = resolve_workspace_path(workspace, script_path)
            if not resolved_script_path.is_file():
                return f"Error: bash script does not exist: {script_path}"
            if resolved_script_path.suffix == ".py":
                validation_error = validate_python_script_text(resolved_script_path.read_text(encoding="utf-8", errors="replace"))
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
        except subprocess.TimeoutExpired as timeout_exc:
            output = format_process_output(timeout_exc.stdout, timeout_exc.stderr)
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
    except ValueError as parse_exc:
        return f"invalid command syntax: {parse_exc}"
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
    except ValueError as parse_exc:
        return f"invalid command syntax: {parse_exc}"
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
            return validate_python_script_text(argv[index + 1])
        if argument.startswith("-c") and len(argument) > 2:
            return validate_python_script_text(argument[2:])
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
    return validate_python_script_text(script_path.read_text(encoding="utf-8", errors="replace"))


def find_parent_directory_literal(code: str) -> str | None:
    for match in re.finditer(r"(['\"])(.*?)\1", code, flags=re.DOTALL):
        literal = match.group(2).replace("\\", "/")
        if ".." in literal.split("/"):
            return match.group(0)
    return None


def validate_python_script_text(code: str) -> str | None:
    lowered = code.lower()
    parent_literal = find_parent_directory_literal(code)
    if parent_literal is not None:
        return f"parent-directory path literal is not allowed in python scripts run by bash: {parent_literal}"
    absolute_match = ABSOLUTE_PATH_LITERAL.search(code)
    if absolute_match:
        return f"absolute path literal is not allowed in python scripts run by bash: {absolute_match.group(0)}"
    for pattern in DANGEROUS_PYTHON_PATTERNS:
        if pattern in lowered:
            return f"forbidden python pattern {pattern!r}"
    return None


def bash_path_operands(argv: list[str]) -> list[str]:
    command_name = argv[0]
    args = argv[1:]
    if command_name in {"pwd", "which"} or command_name in {"echo", "printf", "true", "false", "test", "["}:
        return []
    if command_name == "grep":
        operands = list(
            iter_operands(
                args,
                options_with_values={
                    "-e",
                    "--regexp",
                    "-f",
                    "--file",
                    "-m",
                    "--max-count",
                    "-A",
                    "-B",
                    "-C",
                    "--after-context",
                    "--before-context",
                    "--context",
                    "--include",
                    "--exclude",
                    "--exclude-dir",
                },
            )
        )
        uses_pattern_option = any(argument in {"-e", "--regexp", "-f", "--file"} or argument.startswith("-e") for argument in args)
        return operands if uses_pattern_option else operands[1:]
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
    resolved_path = candidate_path.resolve() if candidate_path.is_absolute() else (workspace / candidate_path).resolve()
    if resolved_path != workspace_resolved and workspace_resolved not in resolved_path.parents:
        return f"path escapes workspace: {operand}"
    return None


class NanoclawWorkspaceTool(BaseTool):
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> tuple[ToolResponse, float, dict]:
        agent_data = kwargs.get("agent_data")
        if agent_data is None:
            return ToolResponse(text="Error: NanoclawWorkspaceTool requires agent_data."), 0.0, {}

        try:
            state = self._ensure_workspace(agent_data)
        except WorkspaceSetupError as setup_error:
            return ToolResponse(text=f"Error: failed to initialize Nanoclaw workspace: {setup_error}"), 0.0, {}
        except Exception as setup_exc:
            return ToolResponse(text=f"Error: failed to initialize Nanoclaw workspace: {type(setup_exc).__name__}: {setup_exc}"), 0.0, {}

        if state.get("status") != "ready":
            return ToolResponse(text=f"Error: workspace is not ready: {state.get('setup_error', state.get('status'))}"), 0.0, {}

        workspace = Path(str(state["workspace_after"]))
        try:
            observation = self._dispatch(workspace, plain_container(parameters), state)
        except Exception as tool_exc:
            observation = f"Error: {type(tool_exc).__name__}: {tool_exc}"

        self._record_tool_event(state, self.name, parameters, observation)
        return ToolResponse(text=observation), 0.0, {"nanoclaw_tool": self.name}

    def _ensure_workspace(self, agent_data: Any) -> dict[str, Any]:
        existing_state = agent_data.extra_fields.get("nanoclaw")
        if isinstance(existing_state, dict) and existing_state.get("workspace_after"):
            return existing_state

        task_config = self._task_config_from_agent(agent_data)
        request_id = str(getattr(agent_data, "request_id", uuid.uuid4().hex))
        try:
            state = prepare_workspace(task_config, request_id=request_id, source="tool")
        except WorkspaceSetupError as setup_error:
            agent_data.extra_fields["nanoclaw"] = setup_error.state
            raise
        agent_data.extra_fields["nanoclaw"] = state
        return state

    def _task_config_from_agent(self, agent_data: Any) -> dict[str, Any]:
        tools_kwargs = plain_container(getattr(agent_data, "tools_kwargs", {}) or {})
        candidates = []
        current_tool_kwargs = tools_kwargs.get(self.name, {})
        if isinstance(current_tool_kwargs, dict):
            candidates.append(current_tool_kwargs.get("create_kwargs", current_tool_kwargs))
        shared_kwargs = tools_kwargs.get("_nanoclaw", {})
        if isinstance(shared_kwargs, dict):
            candidates.append(shared_kwargs)
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            if isinstance(candidate.get("nanoclaw"), dict):
                return candidate["nanoclaw"]
            if "task_id" in candidate and "env_builder_path" in candidate:
                return candidate
        raise ValueError("missing Nanoclaw task metadata in tools_kwargs")

    def _dispatch(self, workspace: Path, parameters: dict[str, Any], state: dict[str, Any]) -> str:
        if self.name == "list_dir":
            relative_path = str(parameters.get("path") or ".")
            limit = int_config(parameters.get("limit"), int_config(self.config.get("list_limit"), 200))
            if bool_config(parameters.get("recursive", False), False):
                return list_dir_recursive(workspace, relative_path, limit=limit)
            return list_dir(workspace, relative_path, limit=limit)
        if self.name == "read_file":
            limit = int_config(parameters.get("limit"), int_config(self.config.get("read_limit"), 20000))
            return read_file(workspace, require_path_like(parameters), limit=limit)
        if self.name == "write_file":
            return write_file(workspace, require_path_like(parameters), require_string(parameters, "content"))
        if self.name == "edit_file":
            return edit_file(
                workspace,
                require_path_like(parameters),
                require_string(parameters, "old_text"),
                require_string(parameters, "new_text"),
                replace_all=bool_config(parameters.get("replace_all", False), False),
            )
        if self.name == "apply_patch":
            return apply_workspace_patch(workspace, parse_patch_changes(parameters))
        if self.name == "grep":
            limit = int_config(parameters.get("limit"), int_config(self.config.get("grep_limit"), 200))
            return grep_workspace(workspace, require_string(parameters, "pattern"), parameters.get("glob", "**/*"), limit=limit)
        if self.name == "find":
            limit = int_config(parameters.get("limit"), int_config(self.config.get("find_limit"), 200))
            return find_workspace_files(workspace, parameters.get("pattern", "**/*"), limit=limit)
        if self.name == "mkdir":
            return make_dir(workspace, require_path_like(parameters))
        if self.name == "bash":
            task_config = state.get("task_config", {}) if isinstance(state.get("task_config"), dict) else {}
            allow_bash = bool_config(task_config.get("allow_bash", self.config.get("allow_bash", True)), True)
            if not allow_bash:
                return "Error: bash tool is disabled for this Nanoclaw task."
            timeout = float_config(parameters.get("timeout"), float_config(self.config.get("bash_timeout"), 20.0))
            return execute_bash(
                workspace,
                command=parameters.get("command"),
                script=parameters.get("script"),
                script_path=parameters.get("path", parameters.get("script_path")),
                timeout=timeout,
            )
        return f"Error: unsupported Nanoclaw tool: {self.name}"

    def _record_tool_event(self, state: dict[str, Any], tool_name: str, parameters: dict[str, Any], observation: str) -> None:
        state["tool_call_count"] = int(state.get("tool_call_count", 0)) + 1
        state["updated_at"] = utc_now()
        result_dir = Path(str(state["result_dir"]))
        event = {
            "time": state["updated_at"],
            "tool": tool_name,
            "parameters": truncate_for_log(plain_container(parameters), limit=1000),
            "observation": truncate_for_log(observation, limit=2000),
        }
        with (result_dir / "tool_events.jsonl").open("a", encoding="utf-8") as event_file:
            event_file.write(json.dumps(event, ensure_ascii=False) + "\n")
        write_runtime_metadata(state)


def truncate_for_log(value: Any, *, limit: int) -> Any:
    if isinstance(value, str):
        return value if len(value) <= limit else value[:limit] + "...(truncated)"
    if isinstance(value, dict):
        return {key: truncate_for_log(item, limit=limit) for key, item in value.items()}
    if isinstance(value, list):
        return [truncate_for_log(item, limit=limit) for item in value]
    return value


def run_verifier(
    *,
    verifier_path: Path,
    workspace_after: Path,
    timeout: float,
    mock_api_base: str | None = None,
    mock_api_key: str | None = None,
    mock_model_name: str | None = None,
    mock_api_timeout: float | None = None,
    mock_api_connect_timeout: float | None = None,
) -> dict[str, Any]:
    started_at = time.time()
    env = workspace_subprocess_env(workspace_after)
    if mock_api_base:
        env["MOCK_API_BASE"] = mock_api_base
    if mock_api_key:
        env["MOCK_API_KEY"] = mock_api_key
    if mock_model_name:
        env["MOCK_MODEL_NAME"] = mock_model_name
    if mock_api_timeout is not None:
        env["MOCK_API_TIMEOUT"] = str(mock_api_timeout)
    if mock_api_connect_timeout is not None:
        env["MOCK_API_CONNECT_TIMEOUT"] = str(mock_api_connect_timeout)

    print(
        "[nanoclaw_verifier_start] "
        f"verifier={verifier_path} "
        f"workspace={workspace_after} "
        f"timeout={timeout} "
        f"mock_api_base={env.get('MOCK_API_BASE')} "
        f"mock_model_name={env.get('MOCK_MODEL_NAME')} "
        f"mock_api_timeout={env.get('MOCK_API_TIMEOUT')} "
        f"mock_api_connect_timeout={env.get('MOCK_API_CONNECT_TIMEOUT')}",
        flush=True,
    )

    try:
        process = subprocess.run(
            [sys.executable, str(verifier_path), str(workspace_after)],
            cwd=verifier_path.parent,
            text=True,
            capture_output=True,
            env=env,
            timeout=timeout,
            check=False,
        )
        result: dict[str, Any] = {
            "status": "completed" if process.returncode == 0 else "failed",
            "returncode": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "elapsed_seconds": round(time.time() - started_at, 3),
        }
    except subprocess.TimeoutExpired as timeout_exc:
        result = {
            "status": "failed",
            "returncode": None,
            "stdout": timeout_exc.stdout or "",
            "stderr": timeout_exc.stderr or "",
            "elapsed_seconds": round(time.time() - started_at, 3),
            "error": f"verifier timed out after {timeout:g}s",
        }

    score_candidates = [
        workspace_after / "workplace_score.json",
        verifier_path.parent / "workplace_score.json",
    ]
    result["workplace_score_path"] = None
    result["workplace_score_source"] = None
    for score_path in score_candidates:
        if not score_path.is_file():
            continue
        try:
            result["workplace_score"] = json.loads(score_path.read_text(encoding="utf-8"))
            result["workplace_score_path"] = str(score_path)
            result["workplace_score_source"] = "workspace_after" if score_path.parent == workspace_after else "verifier_cwd"
            if score_path.parent != workspace_after:
                print(
                    "[nanoclaw_score_path_fallback] "
                    f"expected={workspace_after / 'workplace_score.json'} "
                    f"actual={score_path}",
                    flush=True,
                )
            break
        except json.JSONDecodeError as json_exc:
            result["workplace_score_error"] = str(json_exc)
            result["workplace_score_path"] = str(score_path)
            result["workplace_score_source"] = "workspace_after" if score_path.parent == workspace_after else "verifier_cwd"
            break
    result["score_summary"] = score_summary(result.get("workplace_score"))
    return result


def score_summary(workplace_score: Any) -> dict[str, Any]:
    return common_score_summary(workplace_score)


def choose_reward_score(verifier_result: dict[str, Any], *, mode: str, fallback_score: float) -> float:
    summary = verifier_result.get("score_summary") or {}
    raw_score = summary.get("score")
    ratio = summary.get("score_ratio")
    passed = summary.get("passed")

    if mode == "raw" and isinstance(raw_score, (int, float)):
        return float(raw_score)
    if mode == "binary":
        if isinstance(passed, bool):
            return 1.0 if passed else 0.0
        return 1.0 if verifier_result.get("returncode") == 0 else fallback_score
    if isinstance(ratio, (int, float)):
        return float(ratio)
    if isinstance(raw_score, (int, float)):
        return float(raw_score)
    if isinstance(passed, bool):
        return 1.0 if passed else 0.0
    return fallback_score


def compute_assistant_turn_penalty(runtime_state: dict[str, Any], task_config: dict[str, Any], raw_penalty: Any) -> tuple[float, int, float]:
    penalty_per_turn = float_config(raw_penalty, float_config(task_config.get("assistant_turn_penalty"), 0.0))
    assistant_turns = int_config(runtime_state.get("rollout_assistant_turns"), 0)
    penalty = max(0.0, penalty_per_turn) * max(0, assistant_turns)
    return penalty_per_turn, assistant_turns, penalty


def load_conversation_events(runtime_state: dict[str, Any]) -> list[dict[str, Any]]:
    result_dir = runtime_state.get("result_dir")
    if not result_dir:
        return []
    conversation_path = Path(str(result_dir)) / "conversation_history.json"
    if not conversation_path.is_file():
        return []
    try:
        payload = json.loads(conversation_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    events = payload.get("events") if isinstance(payload, dict) else None
    if not isinstance(events, list):
        return []
    return [event for event in events if isinstance(event, dict)]


def canonical_json_key(value: Any) -> str:
    try:
        return json.dumps(plain_container(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    except Exception:
        return repr(value)


def compute_duplicate_tool_call_penalty(
    events: list[dict[str, Any]],
    task_config: dict[str, Any],
    raw_penalty: Any,
) -> tuple[float, int, float]:
    penalty_per_extra = float_config(raw_penalty, float_config(task_config.get("duplicate_tool_call_penalty"), 0.0))
    if penalty_per_extra <= 0:
        return penalty_per_extra, 0, 0.0
    counts: Counter[str] = Counter()
    for event in events:
        if event.get("type") != "tool":
            continue
        key = canonical_json_key(
            {
                "tool": event.get("tool"),
                "arguments": event.get("arguments"),
                "response": event.get("response"),
                "result": event.get("result"),
            }
        )
        counts[key] += 1
    duplicate_count = sum(count - 1 for count in counts.values() if count > 1)
    penalty = max(0.0, penalty_per_extra) * duplicate_count
    return penalty_per_extra, duplicate_count, penalty


def normalized_repeat_text(text: Any) -> str:
    value = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n[ \t]+", "\n", value)
    return value.strip()


def consecutive_chunk_repeat_count(chunks: list[str], min_chars: int) -> int:
    extra_repeats = 0
    chunk_index = 0
    while chunk_index < len(chunks):
        current_chunk = chunks[chunk_index]
        if len(current_chunk) < min_chars:
            chunk_index += 1
            continue
        run_length = 1
        next_index = chunk_index + 1
        while next_index < len(chunks) and chunks[next_index] == current_chunk:
            run_length += 1
            next_index += 1
        if run_length > 1:
            extra_repeats += run_length - 1
        chunk_index = next_index
    return extra_repeats


def continuous_separator_repeat_count(text: str, min_chars: int) -> int:
    for separator in ("</think>", "\n\n", "\n"):
        if separator not in text:
            continue
        chunks = [normalized_repeat_text(part) for part in text.split(separator)]
        chunks = [chunk for chunk in chunks if chunk]
        extra_repeats = consecutive_chunk_repeat_count(chunks, min_chars)
        if extra_repeats:
            return extra_repeats
    return 0


def continuous_token_repeat_count(text: str, min_chars: int, max_unit_tokens: int = 512) -> int:
    token_matches = list(re.finditer(r"\S+", text))
    token_count = len(token_matches)
    if token_count < 2:
        return 0

    tokens = [match.group(0) for match in token_matches]
    max_unit_tokens = min(max_unit_tokens, token_count // 2)
    best_extra_repeats = 0
    for unit_token_count in range(1, max_unit_tokens + 1):
        start_token_index = 0
        while start_token_index + 2 * unit_token_count <= token_count:
            unit_start_char = token_matches[start_token_index].start()
            unit_end_char = token_matches[start_token_index + unit_token_count - 1].end()
            if unit_end_char - unit_start_char < min_chars:
                start_token_index += 1
                continue

            first_unit = tokens[start_token_index : start_token_index + unit_token_count]
            next_start = start_token_index + unit_token_count
            if first_unit != tokens[next_start : next_start + unit_token_count]:
                start_token_index += 1
                continue

            run_length = 2
            next_start += unit_token_count
            while next_start + unit_token_count <= token_count and first_unit == tokens[next_start : next_start + unit_token_count]:
                run_length += 1
                next_start += unit_token_count
            best_extra_repeats = max(best_extra_repeats, run_length - 1)
            start_token_index += run_length * unit_token_count
    return best_extra_repeats


def repeated_block_count(text: Any, min_chars: int, min_consecutive_repeats: int = 2) -> int:
    normalized = normalized_repeat_text(text)
    min_consecutive_repeats = max(2, min_consecutive_repeats)
    if len(normalized) < min_chars * min_consecutive_repeats:
        return 0

    separator_repeats = continuous_separator_repeat_count(normalized, min_chars)
    if separator_repeats >= min_consecutive_repeats - 1:
        return separator_repeats

    token_repeats = continuous_token_repeat_count(normalized, min_chars)
    return token_repeats if token_repeats >= min_consecutive_repeats - 1 else 0


def compute_repeated_response_penalty(
    events: list[dict[str, Any]],
    task_config: dict[str, Any],
    raw_penalty: Any,
    raw_min_chars: Any,
    raw_min_consecutive_repeats: Any = None,
) -> tuple[float, int, int, int, float]:
    penalty_per_repeat = float_config(raw_penalty, float_config(task_config.get("repeated_response_penalty"), 0.0))
    min_chars = max(1, int_config(raw_min_chars, int_config(task_config.get("repeated_response_min_chars"), 200)))
    min_consecutive_repeats = max(2, int_config(raw_min_consecutive_repeats, int_config(task_config.get("repeated_response_min_consecutive_repeats"), 2)))
    if penalty_per_repeat <= 0:
        return penalty_per_repeat, 0, min_chars, min_consecutive_repeats, 0.0
    repeat_count = 0
    for event in events:
        if event.get("type") == "assistant":
            repeat_count += repeated_block_count(event.get("content"), min_chars, min_consecutive_repeats)
    penalty = max(0.0, penalty_per_repeat) * repeat_count
    return penalty_per_repeat, repeat_count, min_chars, min_consecutive_repeats, penalty


def compute_behavior_penalties(
    runtime_state: dict[str, Any],
    task_config: dict[str, Any],
    *,
    assistant_turn_penalty: Any,
    duplicate_tool_call_penalty: Any,
    repeated_response_penalty: Any,
    repeated_response_min_chars: Any,
    repeated_response_min_consecutive_repeats: Any = None,
    reward_score_before_penalty: Any = None,
    turn_penalty_only_positive_score: Any = None,
) -> dict[str, Any]:
    penalty_per_turn, assistant_turns, turn_penalty = compute_assistant_turn_penalty(
        runtime_state,
        task_config,
        assistant_turn_penalty,
    )
    only_positive_turn_penalty = bool_config(
        turn_penalty_only_positive_score,
        bool_config(
            task_config.get("turn_penalty_only_positive_score"),
            bool_config(os.environ.get("NANOCLAW_TURN_PENALTY_ONLY_POSITIVE_SCORE"), False),
        ),
    )
    skipped_turn_penalty = False
    numeric_base_score = (
        float(reward_score_before_penalty) if isinstance(reward_score_before_penalty, (int, float)) else None
    )
    if only_positive_turn_penalty and (numeric_base_score is None or numeric_base_score <= 0.0):
        turn_penalty = 0.0
        skipped_turn_penalty = True
    events = load_conversation_events(runtime_state)
    duplicate_penalty_per_extra, duplicate_tool_call_count, duplicate_tool_penalty = compute_duplicate_tool_call_penalty(
        events,
        task_config,
        duplicate_tool_call_penalty,
    )
    (
        repeated_penalty_per_repeat,
        repeated_response_count,
        repeated_min_chars,
        repeated_min_consecutive_repeats,
        repeated_penalty,
    ) = compute_repeated_response_penalty(
        events,
        task_config,
        repeated_response_penalty,
        repeated_response_min_chars,
        repeated_response_min_consecutive_repeats,
    )
    total_penalty = turn_penalty + duplicate_tool_penalty + repeated_penalty
    return {
        "nanoclaw_assistant_turns": assistant_turns,
        "nanoclaw_assistant_turn_penalty_per_turn": penalty_per_turn,
        "nanoclaw_turn_penalty_only_positive_score": only_positive_turn_penalty,
        "nanoclaw_assistant_turn_penalty_skipped_non_positive_score": skipped_turn_penalty,
        "nanoclaw_assistant_turn_penalty": turn_penalty,
        "nanoclaw_duplicate_tool_call_count": duplicate_tool_call_count,
        "nanoclaw_duplicate_tool_call_penalty_per_extra": duplicate_penalty_per_extra,
        "nanoclaw_duplicate_tool_call_penalty": duplicate_tool_penalty,
        "nanoclaw_repeated_response_count": repeated_response_count,
        "nanoclaw_repeated_response_min_chars": repeated_min_chars,
        "nanoclaw_repeated_response_min_consecutive_repeats": repeated_min_consecutive_repeats,
        "nanoclaw_repeated_response_penalty_per_repeat": repeated_penalty_per_repeat,
        "nanoclaw_repeated_response_penalty": repeated_penalty,
        "nanoclaw_total_behavior_penalty": total_penalty,
    }


def cleanup_workspace(result_dir: str | None) -> str | None:
    if not result_dir:
        return None
    try:
        shutil.rmtree(result_dir)
        return None
    except FileNotFoundError:
        return None
    except Exception as cleanup_exc:
        return f"{type(cleanup_exc).__name__}: {cleanup_exc}"


def extract_task_and_runtime(extra_info: Any, ground_truth: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    extra_info = plain_container(extra_info or {})
    ground_truth = plain_container(ground_truth or {})
    runtime_state = extra_info.get("nanoclaw") if isinstance(extra_info.get("nanoclaw"), dict) else {}
    runtime_state = dict(runtime_state or {})
    for key in (
        "rollout_termination_reason",
        "rollout_final_answer",
        "rollout_assistant_turns",
        "rollout_user_turns",
        "rollout_tool_call_count",
        "rollout_response_tokens",
    ):
        if key in extra_info and key not in runtime_state:
            runtime_state[key] = extra_info[key]
    task_config = extra_info.get("nanoclaw_task") if isinstance(extra_info.get("nanoclaw_task"), dict) else {}
    if not task_config and isinstance(ground_truth, dict):
        task_config = ground_truth
    if not task_config and isinstance(runtime_state.get("task_config"), dict):
        task_config = runtime_state["task_config"]
    if task_config:
        task_config = dict(task_config)
        rollout_mapping = {
            "rollout_step": "rollout_step",
            "rollout_sample_index": "rollout_sample_index",
            "rollout_n": "rollout_n",
            "rollout_index": "rollout_n",
            "validate": "validate",
        }
        for source_key, target_key in rollout_mapping.items():
            if task_config.get(target_key) is None and extra_info.get(source_key) is not None:
                task_config[target_key] = extra_info[source_key]
    return task_config or {}, runtime_state or {}


def compute_final_answer_bonus(
    runtime_state: dict[str, Any],
    task_config: dict[str, Any],
    solution_str: str,
    *,
    enabled: Any = None,
    score: Any = None,
) -> dict[str, Any]:
    bonus_enabled = bool_config(
        enabled,
        bool_config(
            task_config.get("final_answer_bonus_enable"),
            bool_config(os.environ.get("NANOCLAW_FINAL_ANSWER_BONUS_ENABLE"), False),
        ),
    )
    bonus_score = float_config(
        score,
        float_config(
            task_config.get("final_answer_bonus_score"),
            float_config(os.environ.get("NANOCLAW_FINAL_ANSWER_BONUS_SCORE"), 0.0),
        ),
    )
    termination_reason = str(runtime_state.get("rollout_termination_reason") or "")

    # New rollouts provide the exact last assistant message. For older saved
    # rollouts, fall back to solution_str only when the agent terminated by
    # emitting a non-tool assistant response.
    if "rollout_final_answer" in runtime_state:
        final_answer = runtime_state.get("rollout_final_answer")
    elif termination_reason == "completed_no_tool_call":
        final_answer = solution_str
    else:
        final_answer = None

    has_final_answer = (
        termination_reason == "completed_no_tool_call"
        and isinstance(final_answer, str)
        and bool(final_answer.strip())
    )
    awarded_bonus = bonus_score if bonus_enabled and has_final_answer else 0.0
    return {
        "nanoclaw_has_final_answer": has_final_answer,
        "nanoclaw_final_answer_bonus_enabled": bonus_enabled,
        "nanoclaw_final_answer_bonus_score": bonus_score,
        "nanoclaw_final_answer_bonus_awarded": awarded_bonus,
    }


def tail_text(text: Any, *, limit: int = 800) -> str:
    if text is None:
        return ""
    value = str(text).strip()
    if len(value) <= limit:
        return value
    return "...(tail)" + value[-limit:]


REWARD_LOG_LOCK = threading.Lock()
REWARD_LOG_COUNTERS: Counter[str] = Counter()


def compact_reward_details(workplace_score: Any, *, limit: int = 20) -> list[dict[str, Any]]:
    if not isinstance(workplace_score, dict):
        return []
    details = workplace_score.get("details")
    if not isinstance(details, list):
        return []
    compact_details = []
    for item in details[:limit]:
        if isinstance(item, dict):
            compact_details.append(
                {
                    "item": item.get("item"),
                    "score": item.get("score"),
                    "max_score": item.get("max_score"),
                    "passed": item.get("passed"),
                    "reason": tail_text(item.get("reason"), limit=240),
                }
            )
    return compact_details


def reward_issue_kind(result: dict[str, Any], verifier_result: dict[str, Any]) -> str:
    if result.get("nanoclaw_status") in {"setup_failed", "missing_verifier", "no_workspace"}:
        return str(result.get("nanoclaw_status"))
    if verifier_result.get("error"):
        return "verifier_timeout" if "timed out" in str(verifier_result.get("error")) else "verifier_error"
    if verifier_result.get("workplace_score_error"):
        return "score_json_error"
    returncode = result.get("nanoclaw_returncode")
    if returncode not in (0, None):
        return "verifier_exception"
    if result.get("nanoclaw_raw_score") is None or result.get("nanoclaw_max_score") is None:
        return "score_schema_missing"
    if result.get("nanoclaw_score_ratio") == 0:
        return "zero_score"
    if result.get("nanoclaw_passed") is True:
        return "passed"
    return "partial_score"


def reward_logs_dir(runtime_state: dict[str, Any]) -> Path | None:
    result_dir = runtime_state.get("result_dir")
    if not result_dir:
        return None
    root = Path(str(result_dir)).parent / "_reward_logs"
    root.mkdir(parents=True, exist_ok=True)
    return root


def write_reward_debug_files(
    result: dict[str, Any],
    *,
    runtime_state: dict[str, Any],
    verifier_result: dict[str, Any],
    issue_kind: str,
    compact_details: list[dict[str, Any]],
    stdout_tail: str,
    stderr_tail: str,
) -> None:
    root = reward_logs_dir(runtime_state)
    if root is None:
        return
    task_id = safe_name(str(result.get("nanoclaw_task_id") or "unknown"))
    result_dir = Path(str(runtime_state.get("result_dir", ""))).name or uuid.uuid4().hex
    reward_record = {
        "time": utc_now(),
        "task_id": result.get("nanoclaw_task_id"),
        "issue_kind": issue_kind,
        "score": result.get("score"),
        "has_final_answer": result.get("nanoclaw_has_final_answer"),
        "final_answer_bonus_enabled": result.get("nanoclaw_final_answer_bonus_enabled"),
        "final_answer_bonus_score": result.get("nanoclaw_final_answer_bonus_score"),
        "final_answer_bonus_awarded": result.get("nanoclaw_final_answer_bonus_awarded"),
        "raw_score": result.get("nanoclaw_raw_score"),
        "max_score": result.get("nanoclaw_max_score"),
        "score_ratio": result.get("nanoclaw_score_ratio"),
        "passed": result.get("nanoclaw_passed"),
        "status": result.get("nanoclaw_status"),
        "returncode": result.get("nanoclaw_returncode"),
        "error": result.get("nanoclaw_error") or verifier_result.get("error") or verifier_result.get("workplace_score_error"),
        "result_dir": result.get("nanoclaw_result_dir") or runtime_state.get("result_dir"),
        "workspace_after": result.get("nanoclaw_workspace_after") or runtime_state.get("workspace_after"),
        "verifier_path": runtime_state.get("verifier_path"),
        "workplace_score_path": verifier_result.get("workplace_score_path"),
        "workplace_score_source": verifier_result.get("workplace_score_source"),
        "details": compact_details,
        "stdout_tail": stdout_tail,
        "stderr_tail": stderr_tail,
    }
    sample_path = root / f"{task_id}__{safe_name(result_dir)}.reward.json"
    sample_path.write_text(json_dumps(reward_record) + "\n", encoding="utf-8")
    with REWARD_LOG_LOCK:
        REWARD_LOG_COUNTERS["total"] += 1
        REWARD_LOG_COUNTERS[f"issue/{issue_kind}"] += 1
        if isinstance(result.get("score"), (int, float)):
            REWARD_LOG_COUNTERS["score_sum_x1000"] += int(round(float(result["score"]) * 1000))
        stats_record = {
            "time": utc_now(),
            "task_id": result.get("nanoclaw_task_id"),
            "issue_kind": issue_kind,
            "score": result.get("score"),
            "has_final_answer": result.get("nanoclaw_has_final_answer"),
            "final_answer_bonus_awarded": result.get("nanoclaw_final_answer_bonus_awarded"),
            "raw_score": result.get("nanoclaw_raw_score"),
            "max_score": result.get("nanoclaw_max_score"),
            "score_ratio": result.get("nanoclaw_score_ratio"),
            "passed": result.get("nanoclaw_passed"),
            "status": result.get("nanoclaw_status"),
            "returncode": result.get("nanoclaw_returncode"),
            "sample_log": str(sample_path),
        }
        with (root / "reward_events.jsonl").open("a", encoding="utf-8") as event_file:
            event_file.write(json_dumps(stats_record) + "\n")
        total = REWARD_LOG_COUNTERS["total"]
        summary = {
            "time": utc_now(),
            "total": total,
            "mean_score": round(REWARD_LOG_COUNTERS["score_sum_x1000"] / max(total, 1) / 1000, 6),
            "issues": {key.removeprefix("issue/"): value for key, value in REWARD_LOG_COUNTERS.items() if key.startswith("issue/")},
        }
        (root / "reward_stats.json").write_text(json_dumps(summary) + "\n", encoding="utf-8")


def log_reward_result(result: dict[str, Any], *, runtime_state: dict[str, Any] | None = None, verifier_result: dict[str, Any] | None = None) -> dict[str, Any]:
    runtime_state = runtime_state or {}
    verifier_result = verifier_result or {}
    stdout_tail = tail_text(verifier_result.get("stdout"))
    stderr_tail = tail_text(verifier_result.get("stderr"))
    verifier_error = verifier_result.get("error") or verifier_result.get("workplace_score_error")
    compact_details = compact_reward_details(verifier_result.get("workplace_score"))
    issue_kind = reward_issue_kind(result, verifier_result)
    try:
        write_reward_debug_files(
            result,
            runtime_state=runtime_state,
            verifier_result=verifier_result,
            issue_kind=issue_kind,
            compact_details=compact_details,
            stdout_tail=stdout_tail,
            stderr_tail=stderr_tail,
        )
    except Exception as log_exc:
        print(f"[nanoclaw_reward_log_error] task={result.get('nanoclaw_task_id')} error={type(log_exc).__name__}: {log_exc}", flush=True)

    summary_bits = [
        f"task={result.get('nanoclaw_task_id')}",
        f"score={result.get('score')}",
        f"raw={result.get('nanoclaw_raw_score')}/{result.get('nanoclaw_max_score')}",
        f"ratio={result.get('nanoclaw_score_ratio')}",
        f"passed={result.get('nanoclaw_passed')}",
        f"status={result.get('nanoclaw_status')}",
        f"final={result.get('nanoclaw_has_final_answer')}",
        f"final_bonus={result.get('nanoclaw_final_answer_bonus_awarded')}",
        f"rc={result.get('nanoclaw_returncode')}",
        f"issue={issue_kind}",
        f"dir={Path(str(runtime_state.get('result_dir'))).name if runtime_state.get('result_dir') else None}",
    ]
    if verifier_error:
        summary_bits.append(f"err={tail_text(verifier_error, limit=180)}")
    if stderr_tail:
        summary_bits.append(f"stderr={tail_text(stderr_tail, limit=240)}")
    print("[nanoclaw_reward] " + " ".join(summary_bits), flush=True)
    if os.environ.get("NANOCLAW_REWARD_PRINT_DETAILS", "0").strip().lower() in {"1", "true", "yes", "on"} and compact_details:
        print(
            f"[nanoclaw_reward_details] task={result.get('nanoclaw_task_id')} "
            f"details={json.dumps(compact_details, ensure_ascii=False)}",
            flush=True,
        )
    return result


def compute_score(
    data_source: str,
    solution_str: str,
    ground_truth: Any,
    extra_info: dict[str, Any],
    cleanup_workspaces: bool | None = None,
    keep_failed_workspaces: bool | None = None,
    verifier_timeout: float | None = None,
    reward_score_mode: str | None = None,
    require_final_answer: bool | None = None,
    final_answer_bonus_enable: bool | None = None,
    final_answer_bonus_score: float | None = None,
    assistant_turn_penalty: float | None = None,
    turn_penalty_only_positive_score: bool | None = None,
    duplicate_tool_call_penalty: float | None = None,
    repeated_response_penalty: float | None = None,
    repeated_response_min_chars: int | None = None,
    repeated_response_min_consecutive_repeats: int | None = None,
    score_uninitialized_workspace: bool = True,
    mock_api_base: str | None = None,
    mock_api_key: str | None = None,
    mock_model_name: str | None = None,
    mock_api_timeout: float | None = None,
    mock_api_connect_timeout: float | None = None,
    **kwargs,
) -> dict[str, Any]:
    task_config, runtime_state = extract_task_and_runtime(extra_info, ground_truth)
    task_id = str(task_config.get("task_id") or runtime_state.get("task_id") or data_source)
    fallback_score = float_config(task_config.get("setup_failure_score"), 0.0)
    created_for_reward = False
    final_answer_bonus = compute_final_answer_bonus(
        runtime_state,
        task_config,
        solution_str,
        enabled=final_answer_bonus_enable,
        score=final_answer_bonus_score,
    )
    awarded_final_answer_bonus = final_answer_bonus["nanoclaw_final_answer_bonus_awarded"]
    if bool_config(require_final_answer, bool_config(task_config.get("require_final_answer"), False)):
        termination_reason = str(runtime_state.get("rollout_termination_reason") or "")
        if termination_reason != "completed_no_tool_call":
            behavior_penalties = compute_behavior_penalties(
                runtime_state,
                task_config,
                assistant_turn_penalty=assistant_turn_penalty,
                duplicate_tool_call_penalty=duplicate_tool_call_penalty,
                repeated_response_penalty=repeated_response_penalty,
                repeated_response_min_chars=repeated_response_min_chars,
                repeated_response_min_consecutive_repeats=repeated_response_min_consecutive_repeats,
                reward_score_before_penalty=0.0,
                turn_penalty_only_positive_score=turn_penalty_only_positive_score,
            )
            reward_score_before_penalty = 0.0
            reward_score = reward_score_before_penalty - behavior_penalties["nanoclaw_total_behavior_penalty"]
            cleanup_error = None
            should_cleanup = bool_config(cleanup_workspaces, bool_config(task_config.get("cleanup_workspace"), True))
            if should_cleanup:
                cleanup_error = cleanup_workspace(runtime_state.get("result_dir"))
            return log_reward_result(
                {
                    "score": reward_score,
                    "nanoclaw_task_id": task_id,
                    "nanoclaw_status": "missing_final_answer",
                    "nanoclaw_error": f"rollout did not finish with final answer; termination_reason={termination_reason or '<missing>'}",
                    "nanoclaw_returncode": None,
                    "nanoclaw_raw_score": None,
                    "nanoclaw_max_score": None,
                    "nanoclaw_score_ratio": None,
                    "nanoclaw_passed": False,
                    "nanoclaw_result_dir": None if should_cleanup else runtime_state.get("result_dir"),
                    "nanoclaw_workspace_after": None if should_cleanup else runtime_state.get("workspace_after"),
                    "nanoclaw_created_for_reward": created_for_reward,
                    "nanoclaw_cleanup_error": cleanup_error,
                    "nanoclaw_reward_score_before_final_answer_bonus": reward_score_before_penalty,
                    "nanoclaw_reward_score_before_behavior_penalty": reward_score_before_penalty,
                    **final_answer_bonus,
                    **behavior_penalties,
                },
                runtime_state=runtime_state,
            )

    if runtime_state.get("status") == "setup_failed":
        cleanup_error = None
        should_cleanup = bool_config(cleanup_workspaces, bool_config(task_config.get("cleanup_workspace"), True))
        if should_cleanup:
            cleanup_error = cleanup_workspace(runtime_state.get("result_dir"))
        return log_reward_result(
            {
                "score": fallback_score + awarded_final_answer_bonus,
                "nanoclaw_task_id": task_id,
                "nanoclaw_status": "setup_failed",
                "nanoclaw_error": runtime_state.get("setup_error"),
                "nanoclaw_cleanup_error": cleanup_error,
                "nanoclaw_reward_score_before_final_answer_bonus": fallback_score,
                **final_answer_bonus,
            },
            runtime_state=runtime_state,
        )

    if not runtime_state.get("workspace_after"):
        if not score_uninitialized_workspace:
            return log_reward_result(
                {
                    "score": fallback_score + awarded_final_answer_bonus,
                    "nanoclaw_task_id": task_id,
                    "nanoclaw_status": "no_workspace",
                    "nanoclaw_error": "model did not initialize the Nanoclaw workspace via tools",
                    "nanoclaw_reward_score_before_final_answer_bonus": fallback_score,
                    **final_answer_bonus,
                },
                runtime_state=runtime_state,
            )
        try:
            runtime_state = prepare_workspace(task_config, request_id=f"reward_{uuid.uuid4().hex}", source="reward")
            created_for_reward = True
        except WorkspaceSetupError as setup_error:
            cleanup_error = cleanup_workspace(setup_error.state.get("result_dir"))
            return log_reward_result(
                {
                    "score": fallback_score + awarded_final_answer_bonus,
                    "nanoclaw_task_id": task_id,
                    "nanoclaw_status": "setup_failed",
                    "nanoclaw_error": str(setup_error),
                    "nanoclaw_cleanup_error": cleanup_error,
                    "nanoclaw_reward_score_before_final_answer_bonus": fallback_score,
                    **final_answer_bonus,
                },
                runtime_state=setup_error.state,
            )

    verifier_path_value = runtime_state.get("verifier_path") or task_config.get("verifier_path")
    if verifier_path_value and not Path(str(verifier_path_value)).expanduser().is_file():
        fallback_verifier_path = runtime_state.get("original_verifier_path") or task_config.get("verifier_path")
        if fallback_verifier_path and Path(str(fallback_verifier_path)).expanduser().is_file():
            print(
                "[nanoclaw_verifier_path_fallback] "
                f"task={task_id} missing={verifier_path_value} fallback={fallback_verifier_path}",
                flush=True,
            )
            verifier_path_value = fallback_verifier_path
    if not verifier_path_value:
        missing_score = float_config(task_config.get("missing_verifier_score"), 0.0)
        cleanup_error = None
        should_cleanup = bool_config(cleanup_workspaces, bool_config(task_config.get("cleanup_workspace"), True))
        if should_cleanup:
            cleanup_error = cleanup_workspace(runtime_state.get("result_dir"))
        return log_reward_result(
            {
                "score": missing_score + awarded_final_answer_bonus,
                "nanoclaw_task_id": task_id,
                "nanoclaw_status": "missing_verifier",
                "nanoclaw_error": "verifier_path is not configured for this task",
                "nanoclaw_cleanup_error": cleanup_error,
                "nanoclaw_reward_score_before_final_answer_bonus": missing_score,
                **final_answer_bonus,
            },
            runtime_state=runtime_state,
        )

    verifier_result = run_verifier(
        verifier_path=Path(str(verifier_path_value)).expanduser().resolve(),
        workspace_after=Path(str(runtime_state["workspace_after"])).expanduser().resolve(),
        timeout=float_config(verifier_timeout, float_config(task_config.get("verifier_timeout"), 300.0)),
        mock_api_base=mock_api_base or kwargs.get("reward_router_address"),
        mock_api_key=mock_api_key,
        mock_model_name=mock_model_name,
        mock_api_timeout=float_config(mock_api_timeout, float_config(os.environ.get("MOCK_API_TIMEOUT"), 60.0)),
        mock_api_connect_timeout=float_config(
            mock_api_connect_timeout, float_config(os.environ.get("MOCK_API_CONNECT_TIMEOUT"), 10.0)
        ),
    )
    score_mode = str(reward_score_mode or task_config.get("reward_score_mode") or "ratio")
    reward_score = choose_reward_score(verifier_result, mode=score_mode, fallback_score=fallback_score)
    reward_score_before_final_answer_bonus = reward_score
    reward_score += awarded_final_answer_bonus
    behavior_penalties = compute_behavior_penalties(
        runtime_state,
        task_config,
        assistant_turn_penalty=assistant_turn_penalty,
        duplicate_tool_call_penalty=duplicate_tool_call_penalty,
        repeated_response_penalty=repeated_response_penalty,
        repeated_response_min_chars=repeated_response_min_chars,
        repeated_response_min_consecutive_repeats=repeated_response_min_consecutive_repeats,
        reward_score_before_penalty=reward_score,
        turn_penalty_only_positive_score=turn_penalty_only_positive_score,
    )
    reward_score_before_penalty = reward_score
    reward_score = reward_score - behavior_penalties["nanoclaw_total_behavior_penalty"]
    passed = verifier_result.get("score_summary", {}).get("passed")

    should_cleanup = bool_config(cleanup_workspaces, bool_config(task_config.get("cleanup_workspace"), True))
    keep_failed = bool_config(keep_failed_workspaces, bool_config(task_config.get("keep_failed_workspace"), False))
    if keep_failed and passed is not True:
        should_cleanup = False
    cleanup_error = cleanup_workspace(runtime_state.get("result_dir")) if should_cleanup else None

    summary = verifier_result.get("score_summary", {})
    result = {
        "score": reward_score,
        "nanoclaw_task_id": task_id,
        "nanoclaw_status": verifier_result.get("status"),
        "nanoclaw_returncode": verifier_result.get("returncode"),
        "nanoclaw_raw_score": summary.get("score"),
        "nanoclaw_max_score": summary.get("max_score"),
        "nanoclaw_score_ratio": summary.get("score_ratio"),
        "nanoclaw_passed": passed,
        "nanoclaw_result_dir": None if should_cleanup else runtime_state.get("result_dir"),
        "nanoclaw_workspace_after": None if should_cleanup else runtime_state.get("workspace_after"),
        "nanoclaw_created_for_reward": created_for_reward,
        "nanoclaw_cleanup_error": cleanup_error,
        "nanoclaw_reward_score_before_final_answer_bonus": reward_score_before_final_answer_bonus,
        "nanoclaw_reward_score_before_behavior_penalty": reward_score_before_penalty,
        **final_answer_bonus,
        **behavior_penalties,
    }
    return log_reward_result(result, runtime_state=runtime_state, verifier_result=verifier_result)
