"""Edit file contents in the runtime workspace."""

from pathlib import Path

from pydantic import BaseModel, Field

from uni_agent.tools.base import AbstractTool
from uni_agent.tools.registry import register_tool

DESCRIPTION = """
Edit a file by replacing an existing string with a new string.
By default the old string must match exactly once.
Use replace_all=true to replace every occurrence.
""".strip()


class EditArguments(BaseModel):
    path: str = Field(description="Path to the file to edit.")
    old_str: str = Field(description="Exact text to replace in the file.")
    new_str: str = Field(description="Replacement text.")
    replace_all: bool = Field(
        default=False,
        description="Whether to replace all occurrences instead of requiring a unique match.",
    )


@register_tool("edit")
class EditTool(AbstractTool):
    @property
    def name(self) -> str:
        return "edit"

    @property
    def local_path(self) -> Path:
        return Path(__file__).parent / "edit"

    def get_tool_schema(self) -> dict:
        return self.build_tool_schema(
            description=DESCRIPTION,
            arguments_model=EditArguments,
        )

    def get_install_command(self) -> str | None:
        return None
