import ast
import importlib.util
import re
import shlex
from pathlib import Path


class ActionPermissionError(Exception):
    pass


WORKSPACE_PATH_TOOL_NAMES = {
    "read",
    "write",
    "edit",
    "str_replace_editor",
    "uni-agent-ls",
    "uni-agent-grep",
    "uni-agent-find",
}
SHELL_CONTROL_TOKENS = {";", "&&", "||", "|", ">", ">>", "<", "<<", "&", "(", ")"}
SAFE_COMPOSITION_OPERATORS = {';', '&&', '||', '|'}
SAFE_REDIRECTION_OPERATORS = {'>', '>>', '<'}
UNSAFE_COMPOSITION_OPERATORS = {'&', '<<', '(', ')'}
PYTHON_COMMAND_NAMES = {"python", "python3", "python3.10", "python3.11", "python3.12"}
SAFE_PYTHON_OPTIONS = {"-u", "-B", "-I", "-S"}
PYTHON_MODULE_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*")
DANGEROUS_IMPORTS = {"subprocess", "shutil"}
SAFE_WORKSPACE_COMMANDS = {
    'cat',
    'cd',
    'cmp',
    'cp',
    'date',
    'diff',
    'du',
    'echo',
    'file',
    'find',
    'grep',
    'head',
    'ls',
    'mkdir',
    'printf',
    'pwd',
    'readlink',
    'realpath',
    'sha256sum',
    'stat',
    'tail',
    'tee',
    'touch',
    'tree',
    'wc',
}
DANGEROUS_SHELL_COMMANDS = {
    'chattr',
    'dd',
    'mv',
    'rename',
    'rm',
    'rmdir',
    'shred',
    'truncate',
    'unlink',
}
DANGEROUS_FIND_PREDICATES = {
    '-delete',
    '-exec',
    '-execdir',
    '-fprint',
    '-fprint0',
    '-fprintf',
    '-fls',
    '-ok',
    '-okdir',
}
DANGEROUS_CALLS = {
    "__import__",
    "compile",
    "eval",
    "exec",
    "os.remove",
    "os.unlink",
    "os.rmdir",
    "os.removedirs",
    "os.rename",
    "os.replace",
    "os.system",
    "os.popen",
    "os.chdir",
    "os.link",
    "os.symlink",
    "Path.unlink",
    "Path.rmdir",
    "Path.rename",
    "Path.replace",
    "pathlib.Path.unlink",
    "pathlib.Path.rmdir",
    "pathlib.Path.rename",
    "pathlib.Path.replace",
    "shutil.move",
    "shutil.rmtree",
    "subprocess.call",
    "subprocess.check_call",
    "subprocess.check_output",
    "subprocess.Popen",
    "subprocess.run",
}
PATH_ARG_CALLS = {
    "os.listdir",
    "os.makedirs",
    "os.mkdir",
    "os.path.exists",
    "os.path.isdir",
    "os.path.isfile",
    "os.scandir",
    "os.stat",
}


def split_action_command(command: str) -> list[str]:
    try:
        return shlex.split(command, posix=True)
    except ValueError as exc:
        raise ActionPermissionError(f"Unable to parse action command for permission checks: {exc}") from exc


def tool_name_from_tokens(tokens: list[str]) -> str | None:
    if len(tokens) < 2 or tokens[0] != "env":
        return None

    # ToolsManager emits `env <runtime_tool> ...`. Keep this tolerant of
    # harmless env assignments such as `env FOO=bar read ...`.
    for token in tokens[1:]:
        if "=" in token and not token.startswith("-"):
            continue
        return token
    return None


def _iter_path_arg_values(tokens: list[str]) -> list[str]:
    values: list[str] = []
    for idx, token in enumerate(tokens):
        if token == "--path":
            if idx + 1 >= len(tokens):
                raise ActionPermissionError("Missing value for --path.")
            values.append(tokens[idx + 1])
        elif token.startswith("--path="):
            values.append(token.split("=", 1)[1])
    return values


def _resolve_user_path(path_value: str, *, workspace: Path, cwd: Path) -> Path:
    path = Path(path_value).expanduser()
    if not path.is_absolute():
        path = cwd / path
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(workspace)
    except ValueError as exc:
        raise ActionPermissionError(
            f"Path access denied: {path_value!r} resolves to {resolved}, outside workspace {workspace}."
        ) from exc
    return resolved


def _require_workspace_paths(workspace: str | None, cwd: str | None) -> tuple[Path, Path]:
    if not workspace or not cwd:
        raise ActionPermissionError("Bash command denied: workspace and cwd are required for general commands.")
    workspace_path = Path(workspace).expanduser().resolve(strict=False)
    cwd_path = Path(cwd).expanduser().resolve(strict=False)
    try:
        cwd_path.relative_to(workspace_path)
    except ValueError as exc:
        raise ActionPermissionError(
            f"Bash command denied: current directory {cwd_path} is outside workspace {workspace_path}."
        ) from exc
    return workspace_path, cwd_path


def validate_workspace_tool_command(command: str, *, workspace: str, cwd: str) -> None:
    """Validate file-tool path arguments against a workspace root."""
    tokens = split_action_command(command)
    tool_name = tool_name_from_tokens(tokens)
    if tool_name not in WORKSPACE_PATH_TOOL_NAMES:
        return

    workspace_path = Path(workspace).expanduser().resolve(strict=False)
    cwd_path = Path(cwd).expanduser().resolve(strict=False)
    if not workspace_path:
        raise ActionPermissionError("Workspace restriction is enabled but workspace path is empty.")

    for path_value in _iter_path_arg_values(tokens):
        _resolve_user_path(path_value, workspace=workspace_path, cwd=cwd_path)


def _contains_shell_control(command: str) -> bool:
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError as exc:
        raise ActionPermissionError(f"Unable to parse bash command for permission checks: {exc}") from exc
    return any(token in SHELL_CONTROL_TOKENS for token in tokens)


def _contains_command_substitution(command: str) -> bool:
    in_single_quote = False
    in_double_quote = False
    escaped = False
    i = 0
    while i < len(command):
        ch = command[i]

        if escaped:
            escaped = False
            i += 1
            continue

        if ch == "\\" and not in_single_quote:
            escaped = True
            i += 1
            continue

        if ch == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
            i += 1
            continue

        if ch == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            i += 1
            continue

        # Shell command substitution is disabled outside single quotes.
        # Double quotes still allow both `...` and $(...) substitutions.
        if not in_single_quote:
            if ch == "`":
                return True
            if ch == "$" and i + 1 < len(command) and command[i + 1] == "(":
                return True

        i += 1

    return False


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _call_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    if isinstance(node, ast.Call):
        return _call_name(node.func)
    return None


def _constant_str(node: ast.AST | None) -> str | None:
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def _path_constructor_arg(node: ast.AST) -> str | None:
    if not isinstance(node, ast.Call):
        return None
    if _call_name(node.func) not in {"Path", "pathlib.Path"}:
        return None
    if not node.args:
        return None
    return _constant_str(node.args[0])


def _check_script_path(path_value: str, *, workspace: Path, cwd: Path, context: str) -> Path:
    resolved = _resolve_user_path(path_value, workspace=workspace, cwd=cwd)
    if context == "script" and (not resolved.is_file() or resolved.suffix != ".py"):
        raise ActionPermissionError(f"Bash command denied: Python script must be an existing .py file: {path_value!r}")
    return resolved


def _check_literal_script_path_arg(
    path_node: ast.AST | None,
    *,
    workspace: Path,
    cwd: Path,
    script_path: Path,
    call_name: str,
) -> None:
    path_value = _constant_str(path_node)
    if path_value is None:
        raise ActionPermissionError(
            f"Bash command denied: Python file paths must be string literals so they can be checked "
            f"({call_name} in {script_path})."
        )
    _resolve_user_path(path_value, workspace=workspace, cwd=cwd)


def _validate_python_file_call(
    node: ast.Call,
    *,
    workspace: Path,
    cwd: Path,
    script_path: Path,
) -> None:
    call_name = _call_name(node.func)
    if call_name in {"Path", "pathlib.Path"} and node.args:
        _check_literal_script_path_arg(
            node.args[0], workspace=workspace, cwd=cwd, script_path=script_path, call_name=call_name
        )
        return

    if call_name in {"open", "io.open"}:
        if not node.args:
            raise ActionPermissionError(f"Bash command denied: open() without path in {script_path}.")
        _check_literal_script_path_arg(
            node.args[0], workspace=workspace, cwd=cwd, script_path=script_path, call_name=call_name
        )
        return

    if call_name in PATH_ARG_CALLS and node.args:
        _check_literal_script_path_arg(
            node.args[0], workspace=workspace, cwd=cwd, script_path=script_path, call_name=call_name
        )
        return

    if isinstance(node.func, ast.Attribute) and node.func.attr == "open":
        path_value = _path_constructor_arg(node.func.value)
        if path_value is not None:
            _resolve_user_path(path_value, workspace=workspace, cwd=cwd)


def _validate_python_source(source: str, *, script_path: Path, workspace: Path, cwd: Path) -> None:
    try:
        tree = ast.parse(source, filename=str(script_path))
    except SyntaxError as exc:
        raise ActionPermissionError(f"Bash command denied: Python script has syntax errors: {exc}") from exc

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root in DANGEROUS_IMPORTS:
                    raise ActionPermissionError(f"Bash command denied: importing {root!r} is not allowed.")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".", 1)[0]
            if root in DANGEROUS_IMPORTS:
                raise ActionPermissionError(f"Bash command denied: importing {root!r} is not allowed.")
        elif isinstance(node, ast.Call):
            call_name = _call_name(node.func)
            if call_name in DANGEROUS_CALLS:
                raise ActionPermissionError(f"Bash command denied: dangerous Python call {call_name!r} is not allowed.")
            _validate_python_file_call(node, workspace=workspace, cwd=cwd, script_path=script_path)


def _validate_python_script_content(script_path: Path, *, workspace: Path, cwd: Path) -> None:
    try:
        source = script_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        source = script_path.read_text(encoding="utf-8", errors="replace")
    _validate_python_source(source, script_path=script_path, workspace=workspace, cwd=cwd)


def _validate_python_inline_code(source: str, *, workspace: Path, cwd: Path) -> None:
    if not source.strip():
        raise ActionPermissionError("Bash command denied: python -c code must not be empty.")
    _validate_python_source(source, script_path=Path("<python -c>"), workspace=workspace, cwd=cwd)


def _workspace_module_source(module_name: str, *, workspace: Path) -> Path | None:
    module_parts = module_name.split(".")
    module_path = workspace.joinpath(*module_parts)
    candidates = (module_path.with_suffix(".py"), module_path / "__main__.py")
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def _python_module_source(module_name: str) -> Path:
    try:
        spec = importlib.util.find_spec(module_name)
    except (ImportError, ModuleNotFoundError, ValueError) as exc:
        raise ActionPermissionError(f"Bash command denied: unable to resolve Python module {module_name!r}.") from exc

    origin = spec.origin if spec is not None else None
    if not origin or origin in {"built-in", "frozen"}:
        raise ActionPermissionError(
            f"Bash command denied: Python module {module_name!r} has no inspectable source file."
        )

    module_path = Path(origin).resolve()
    if module_path.suffix != ".py" or not module_path.is_file():
        raise ActionPermissionError(
            f"Bash command denied: Python module {module_name!r} must have an inspectable .py source file."
        )
    return module_path


def _validate_python_module_args(tokens: list[str], *, workspace: Path, cwd: Path) -> None:
    options_done = False
    for token in tokens:
        if token == "--":
            options_done = True
            continue
        if not options_done and token.startswith("-") and token != "-":
            continue
        _resolve_workspace_shell_path(token, workspace=workspace, cwd=cwd)


def _validate_python_module(
    module_name: str,
    module_args: list[str],
    *,
    workspace: Path,
    cwd: Path,
) -> None:
    if not PYTHON_MODULE_RE.fullmatch(module_name):
        raise ActionPermissionError(f"Bash command denied: invalid Python module name {module_name!r}.")

    module_path = _workspace_module_source(module_name, workspace=workspace)
    if module_path is None:
        module_path = _python_module_source(module_name)
    _validate_python_script_content(module_path, workspace=workspace, cwd=cwd)
    _validate_python_module_args(module_args, workspace=workspace, cwd=cwd)


def _validate_python_command(tokens: list[str], *, workspace: Path, cwd: Path) -> None:
    script_token: str | None = None
    idx = 1
    while idx < len(tokens):
        token = tokens[idx]
        if token in SAFE_PYTHON_OPTIONS:
            idx += 1
            continue
        if token == "-c":
            if idx + 1 >= len(tokens):
                raise ActionPermissionError("Bash command denied: python -c requires a code string.")
            if idx + 2 != len(tokens):
                raise ActionPermissionError("Bash command denied: python -c must not receive additional arguments.")
            _validate_python_inline_code(tokens[idx + 1], workspace=workspace, cwd=cwd)
            return
        if token.startswith("-c"):
            raise ActionPermissionError("Bash command denied: use python -c followed by one quoted code string.")
        if token == "-m":
            if idx + 1 >= len(tokens):
                raise ActionPermissionError("Bash command denied: python -m requires a module name.")
            _validate_python_module(tokens[idx + 1], tokens[idx + 2 :], workspace=workspace, cwd=cwd)
            return
        if token.startswith("-m"):
            raise ActionPermissionError("Bash command denied: use python -m followed by a module name.")
        if token.startswith("-"):
            raise ActionPermissionError(f"Bash command denied: Python option {token!r} is not allowed.")
        script_token = token
        break

    if not script_token:
        raise ActionPermissionError("Bash command denied: Python command must execute a workspace .py script.")
    script_path = _check_script_path(script_token, workspace=workspace, cwd=cwd, context="script")
    _validate_python_script_content(script_path, workspace=workspace, cwd=cwd)


def _resolve_workspace_shell_path(path_value: str, *, workspace: Path, cwd: Path) -> None:
    if path_value == '-':
        return
    if '$' in path_value or path_value.startswith('~'):
        raise ActionPermissionError(
            f'Bash command denied: shell-expanded path {path_value!r} is not allowed.'
        )
    _resolve_user_path(path_value, workspace=workspace, cwd=cwd)


def _simple_command_operands(tokens: list[str]) -> list[str]:
    operands: list[str] = []
    options_done = False
    for token in tokens[1:]:
        if token == '--':
            options_done = True
            continue
        if not options_done and token.startswith('-') and token != '-':
            continue
        operands.append(token)
    return operands


def _validate_path_operands(tokens: list[str], *, workspace: Path, cwd: Path) -> None:
    for operand in _simple_command_operands(tokens):
        _resolve_workspace_shell_path(operand, workspace=workspace, cwd=cwd)


def _validate_cd_command(tokens: list[str], *, workspace: Path, cwd: Path) -> None:
    if len(tokens) != 2 or tokens[1].startswith('-'):
        raise ActionPermissionError('Bash command denied: cd requires exactly one workspace-relative path.')
    _resolve_workspace_shell_path(tokens[1], workspace=workspace, cwd=cwd)


def _validate_find_command(tokens: list[str], *, workspace: Path, cwd: Path) -> None:
    if any(token in DANGEROUS_FIND_PREDICATES for token in tokens):
        raise ActionPermissionError('Bash command denied: find execution or write predicates are not allowed.')

    idx = 1
    while idx < len(tokens):
        token = tokens[idx]
        if token == '--':
            idx += 1
            break
        if token == '-L':
            raise ActionPermissionError('Bash command denied: find -L is not allowed.')
        if token in {'-H', '-P'} or token.startswith('-O') or token.startswith('-D'):
            idx += 2 if token == '-D' else 1
            continue
        break

    while idx < len(tokens):
        token = tokens[idx]
        if token.startswith('-') or token == '!':
            break
        _resolve_workspace_shell_path(token, workspace=workspace, cwd=cwd)
        idx += 1


def _validate_grep_command(tokens: list[str], *, workspace: Path, cwd: Path) -> None:
    option_values = {
        '-A',
        '-B',
        '-C',
        '-e',
        '-f',
        '-m',
        '--after-context',
        '--before-context',
        '--binary-files',
        '--context',
        '--exclude',
        '--exclude-dir',
        '--file',
        '--include',
        '--max-count',
        '--regexp',
    }
    pattern_seen = False
    options_done = False
    idx = 1
    while idx < len(tokens):
        token = tokens[idx]
        if token == '--':
            options_done = True
            idx += 1
            continue
        if not options_done and (token == '-R' or token == '--dereference-recursive' or token.startswith('-R')):
            raise ActionPermissionError('Bash command denied: grep recursive symlink traversal is not allowed.')
        if not options_done and token.startswith('-') and token != '-':
            option_name = token.split('=', 1)[0]
            if option_name in option_values:
                if '=' in token:
                    if option_name in {'-f', '--file'}:
                        _resolve_workspace_shell_path(token.split('=', 1)[1], workspace=workspace, cwd=cwd)
                    idx += 1
                    continue
                if idx + 1 >= len(tokens):
                    raise ActionPermissionError(f'Bash command denied: grep option {token!r} requires a value.')
                if option_name in {'-f', '--file'}:
                    _resolve_workspace_shell_path(tokens[idx + 1], workspace=workspace, cwd=cwd)
                idx += 2
                continue
            idx += 1
            continue
        if not pattern_seen:
            pattern_seen = True
        else:
            _resolve_workspace_shell_path(token, workspace=workspace, cwd=cwd)
        idx += 1


def _validate_safe_workspace_command(tokens: list[str], *, workspace: Path, cwd: Path) -> None:
    command_name = Path(tokens[0]).name
    if command_name in DANGEROUS_SHELL_COMMANDS:
        raise ActionPermissionError(f'Bash command denied: dangerous command {command_name!r} is not allowed.')
    if command_name not in SAFE_WORKSPACE_COMMANDS:
        raise ActionPermissionError(
            'Bash command denied. Only configured environment CLI commands, safe workspace commands, '
            'and safe workspace Python scripts are allowed.'
        )

    if command_name == 'cd':
        _validate_cd_command(tokens, workspace=workspace, cwd=cwd)
    elif command_name == 'find':
        _validate_find_command(tokens, workspace=workspace, cwd=cwd)
    elif command_name == 'grep':
        _validate_grep_command(tokens, workspace=workspace, cwd=cwd)
    elif command_name == 'ls':
        if any(token == '--dereference' or token == '-L' or token.startswith('-') and 'L' in token[1:] for token in tokens[1:]):
            raise ActionPermissionError('Bash command denied: ls symlink dereferencing is not allowed.')
        _validate_path_operands(tokens, workspace=workspace, cwd=cwd)
    elif command_name in {'pwd', 'echo', 'printf'}:
        return
    else:
        _validate_path_operands(tokens, workspace=workspace, cwd=cwd)


def _validate_safe_general_bash_command(tokens: list[str], *, workspace: str | None, cwd: str | None) -> None:
    if not tokens:
        raise ActionPermissionError("Bash command denied: empty command.")

    command_name = Path(tokens[0]).name
    if command_name in PYTHON_COMMAND_NAMES:
        workspace_path, cwd_path = _require_workspace_paths(workspace, cwd)
        _validate_python_command(tokens, workspace=workspace_path, cwd=cwd_path)
        return

    workspace_path, cwd_path = _require_workspace_paths(workspace, cwd)
    _validate_safe_workspace_command(tokens, workspace=workspace_path, cwd=cwd_path)


def _shell_tokens(command: str) -> list[str]:
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        return list(lexer)
    except ValueError as exc:
        raise ActionPermissionError(f"Unable to parse bash command for permission checks: {exc}") from exc


def _validate_command_segment(
    tokens: list[str],
    *,
    allowed_prefixes: list[str],
    blocked_subcommands: set[str],
    workspace: str | None,
    cwd: str | None,
) -> None:
    if not tokens:
        raise ActionPermissionError("Bash command denied: empty command segment.")
    if "=" in tokens[0] and not tokens[0].startswith("-"):
        raise ActionPermissionError("Bash command denied: environment variable assignments are not allowed.")

    for prefix in allowed_prefixes:
        prefix_tokens = split_action_command(prefix)
        if prefix_tokens and tokens[: len(prefix_tokens)] == prefix_tokens:
            subcommand = tokens[len(prefix_tokens)] if len(tokens) > len(prefix_tokens) else ""
            if subcommand in blocked_subcommands:
                raise ActionPermissionError(f"Bash command denied: CLI subcommand {subcommand!r} is not allowed.")
            return

    _validate_safe_general_bash_command(tokens, workspace=workspace, cwd=cwd)


def _is_standalone_python_inline_command(command: str) -> bool:
    try:
        tokens = split_action_command(command)
    except ActionPermissionError:
        return False
    if not tokens or Path(tokens[0]).name not in PYTHON_COMMAND_NAMES:
        return False

    idx = 1
    while idx < len(tokens):
        token = tokens[idx]
        if token in SAFE_PYTHON_OPTIONS:
            idx += 1
            continue
        return token == "-c" and idx + 2 == len(tokens)
    return False


def _validate_composed_bash_command(
    command: str,
    *,
    allowed_prefixes: list[str],
    blocked_subcommands: list[str],
    workspace: str | None,
    cwd: str | None,
) -> None:
    if _contains_command_substitution(command):
        raise ActionPermissionError("Bash command denied: command substitution is not allowed.")
    if ("\n" in command or "\r" in command) and not _is_standalone_python_inline_command(command):
        raise ActionPermissionError("Bash command denied: multi-line commands are not allowed.")

    tokens = _shell_tokens(command)
    if not tokens:
        raise ActionPermissionError("Bash command denied: empty command.")

    workspace_path: Path | None = None
    cwd_path: Path | None = None

    def require_workspace_paths() -> tuple[Path, Path]:
        nonlocal workspace_path, cwd_path
        if workspace_path is None or cwd_path is None:
            workspace_path, cwd_path = _require_workspace_paths(workspace, cwd)
        return workspace_path, cwd_path

    if any(token in SAFE_COMPOSITION_OPERATORS | SAFE_REDIRECTION_OPERATORS for token in tokens):
        require_workspace_paths()

    segments: list[list[str]] = []
    current: list[str] = []
    idx = 0
    while idx < len(tokens):
        token = tokens[idx]
        if token in UNSAFE_COMPOSITION_OPERATORS:
            raise ActionPermissionError(f"Bash command denied: shell operator {token!r} is not allowed.")
        if token in SAFE_COMPOSITION_OPERATORS:
            if not current:
                raise ActionPermissionError("Bash command denied: empty command segment.")
            segments.append(current)
            current = []
            idx += 1
            continue
        if token in SAFE_REDIRECTION_OPERATORS:
            if not current or idx + 1 >= len(tokens):
                raise ActionPermissionError("Bash command denied: invalid redirection.")
            target = tokens[idx + 1]
            if target in SHELL_CONTROL_TOKENS:
                raise ActionPermissionError("Bash command denied: invalid redirection target.")
            workspace_root, current_dir = require_workspace_paths()
            _resolve_user_path(target, workspace=workspace_root, cwd=current_dir)
            idx += 2
            continue
        if token and all(char in "&|<>()" for char in token):
            raise ActionPermissionError(f"Bash command denied: shell operator {token!r} is not allowed.")
        current.append(token)
        idx += 1

    if not current:
        raise ActionPermissionError("Bash command denied: empty command segment.")
    segments.append(current)

    blocked = set(blocked_subcommands)
    for segment in segments:
        _validate_command_segment(
            segment,
            allowed_prefixes=allowed_prefixes,
            blocked_subcommands=blocked,
            workspace=workspace,
            cwd=cwd,
        )


def validate_no_shell_composition(command: str) -> None:
    if _contains_command_substitution(command):
        raise ActionPermissionError("Bash command denied: command substitution is not allowed.")
    if _contains_shell_control(command):
        raise ActionPermissionError("Bash command denied: shell control operators are not allowed.")


def validate_restricted_bash_command(
    command: str,
    *,
    allowed_prefixes: list[str],
    blocked_subcommands: list[str],
    workspace: str | None = None,
    cwd: str | None = None,
) -> None:
    """Allow safe CLI/Python command compositions confined to the workspace."""
    _validate_composed_bash_command(
        command,
        allowed_prefixes=allowed_prefixes,
        blocked_subcommands=blocked_subcommands,
        workspace=workspace,
        cwd=cwd,
    )