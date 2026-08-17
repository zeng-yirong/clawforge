"""Read file contents from the runtime workspace."""

from pathlib import Path

from pydantic import BaseModel, Field

from uni_agent.tools.base import AbstractTool
from uni_agent.tools.registry import register_tool

DESCRIPTION = """
Read a file from the runtime workspace.
Optionally read only a selected line range.
If the path points to a directory, list its non-hidden entries.
""".strip()


class ReadArguments(BaseModel):
    path: str = Field(description="Path to the file or directory to read.")
    start_line: int | None = Field(
        default=None,
        description="Optional 1-based first line to show when reading a file. Defaults to 1.",
    )
    end_line: int | None = Field(
        default=None,
        description="Optional 1-based last line to show when reading a file. Use -1 to read to the end.",
    )


@register_tool("read")
class ReadTool(AbstractTool):
    @property
    def name(self) -> str:
        return "read"

    @property
    def local_path(self) -> Path:
        return Path(__file__).parent / "read"

    def get_tool_schema(self) -> dict:
        return self.build_tool_schema(
            description=DESCRIPTION,
            arguments_model=ReadArguments,
        )

    def get_install_command(self) -> str | None:
        return None
