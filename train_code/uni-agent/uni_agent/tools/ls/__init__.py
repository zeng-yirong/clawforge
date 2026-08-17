"""List workspace directory contents."""

from pathlib import Path

from pydantic import BaseModel, Field

from uni_agent.tools.base import AbstractTool
from uni_agent.tools.registry import register_tool

DESCRIPTION = """
List directory contents in the workspace.
Shows files and directories in sorted order.
Use recursive=true to descend into subdirectories.
""".strip()


class LsArguments(BaseModel):
    path: str = Field(
        default=".",
        description="Directory path to list. Defaults to the current workspace directory.",
    )
    recursive: bool = Field(
        default=False,
        description="Whether to recursively list subdirectories.",
    )
    show_hidden: bool = Field(
        default=False,
        description="Whether to include hidden files and directories.",
    )
    max_depth: int = Field(
        default=2,
        description="Maximum recursion depth below the top-level directory when recursive=true.",
    )
    max_entries: int = Field(
        default=500,
        description="Maximum number of entries to return.",
    )


@register_tool("ls")
class LsTool(AbstractTool):
    @property
    def name(self) -> str:
        return "ls"

    @property
    def runtime_name(self) -> str:
        return "uni-agent-ls"

    @property
    def local_path(self) -> Path:
        return Path(__file__).parent / "ls"

    def get_tool_schema(self) -> dict:
        return self.build_tool_schema(
            description=DESCRIPTION,
            arguments_model=LsArguments,
        )

    def get_install_command(self) -> str | None:
        return None
