# ruff: noqa
"""
Scaffold tools.
"""

from pydantic import BaseModel

from .edit import EditTool
from .execute_bash import ExecuteBashTool
from .find import FindTool
from .finish import FinishTool
from .grep import GrepTool
from .ls import LsTool
from .read import ReadTool
from .registry import AbstractTool, get_tool
from .str_replace_editor import StrReplaceEditorTool
from .write import WriteTool


class ToolConfig(BaseModel):
    name: str

    def get_tool(self) -> AbstractTool:
        """Return a tool instance (for env.install_tools / init_for_interaction)."""
        return get_tool(self.name)


__all__ = [
    "ToolConfig",
    "EditTool",
    "ExecuteBashTool",
    "FinishTool",
    "FindTool",
    "GrepTool",
    "LsTool",
    "ReadTool",
    "StrReplaceEditorTool",
    "WriteTool",
]
