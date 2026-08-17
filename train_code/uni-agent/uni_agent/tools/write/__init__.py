"""Write file contents into the runtime workspace."""

from pathlib import Path

from pydantic import BaseModel, Field

from uni_agent.tools.base import AbstractTool
from uni_agent.tools.registry import register_tool

DESCRIPTION = """
Write text content to a file in the runtime workspace.
Creates parent directories when needed.
Use append=true to append instead of overwriting.
""".strip()


class WriteArguments(BaseModel):
    path: str = Field(description="Path to the file to write.")
    content: str = Field(description="Text content to write into the file.")
    append: bool = Field(
        default=False,
        description="Whether to append to the file instead of overwriting it.",
    )


@register_tool("write")
class WriteTool(AbstractTool):
    @property
    def name(self) -> str:
        return "write"

    @property
    def local_path(self) -> Path:
        return Path(__file__).parent / "write"

    def get_tool_schema(self) -> dict:
        return self.build_tool_schema(
            description=DESCRIPTION,
            arguments_model=WriteArguments,
        )

    def get_install_command(self) -> str | None:
        return None
