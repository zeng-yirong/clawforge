"""Compatibility file editor tool with Anthropic-style commands."""

from pathlib import Path

from pydantic import BaseModel, Field

from uni_agent.tools.base import AbstractTool
from uni_agent.tools.registry import register_tool

DESCRIPTION = """
View, create, and edit files in the runtime workspace.
Use view to inspect files or directories, create to create a new file,
str_replace to replace one unique exact string, insert to insert text after a
line, and undo_edit to revert the last edit to the same file.
""".strip()


class StrReplaceEditorArguments(BaseModel):
    command: str = Field(
        description="Command to run.",
        json_schema_extra={"enum": ["view", "create", "str_replace", "insert", "undo_edit"]},
    )
    path: str = Field(description="Path to the file or directory.")
    file_text: str | None = Field(
        default=None,
        description="Content for the create command.",
    )
    old_str: str | None = Field(
        default=None,
        description="Exact unique string to replace for str_replace.",
    )
    new_str: str | None = Field(
        default=None,
        description="Replacement text for str_replace, or text to insert for insert.",
    )
    insert_line: int | None = Field(
        default=None,
        description="For insert, insert new_str after this 1-based line number. Use 0 to insert at file start.",
    )
    view_range: list[int] | None = Field(
        default=None,
        description="Optional [start, end] 1-based line range for view. Use end=-1 for EOF.",
    )


@register_tool("str_replace_editor")
class StrReplaceEditorTool(AbstractTool):
    @property
    def name(self) -> str:
        return "str_replace_editor"

    @property
    def local_path(self) -> Path:
        return Path(__file__).parent / "str_replace_editor"

    def get_tool_schema(self) -> dict:
        return self.build_tool_schema(
            description=DESCRIPTION,
            arguments_model=StrReplaceEditorArguments,
        )

    def get_install_command(self) -> str | None:
        return None
