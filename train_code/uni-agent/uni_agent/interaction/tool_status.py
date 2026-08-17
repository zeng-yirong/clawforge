from typing import Literal


ToolStatus = Literal["ok", "timeout", "syntax_error", "permission_error", "command_error", "skipped"]

_FINISH_TOOL_NAMES = frozenset({"finish", "submit"})


def command_status_from_exit_code(tool_name: str, exit_code: int) -> tuple[ToolStatus, bool]:
    """Map a tool process exit code to interaction status and finish accounting."""
    success = exit_code == 0
    status: ToolStatus = "ok" if success else "command_error"
    should_mark_finished = success and tool_name in _FINISH_TOOL_NAMES
    return status, should_mark_finished