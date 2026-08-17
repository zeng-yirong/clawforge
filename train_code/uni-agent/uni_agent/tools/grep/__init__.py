"""Search workspace file contents with a regular expression."""

from pathlib import Path

from pydantic import BaseModel, Field

from uni_agent.tools.base import AbstractTool
from uni_agent.tools.registry import register_tool

DESCRIPTION = """
Search workspace file contents with a regular expression.
Returns matching lines with file paths and line numbers.
Use glob to limit which files are searched.
""".strip()


class GrepArguments(BaseModel):
    pattern: str = Field(description="Regular expression to search for in file contents.")
    path: str = Field(
        default=".",
        description="Directory or file path to search from. Defaults to the current workspace directory.",
    )
    glob: str = Field(
        default="**/*",
        description="Glob pattern that filters which files are searched, relative to path.",
    )
    case_sensitive: bool = Field(
        default=True,
        description="Whether the regular expression match is case-sensitive.",
    )
    max_results: int = Field(
        default=200,
        description="Maximum number of matching lines to return.",
    )


@register_tool("grep")
class GrepTool(AbstractTool):
    @property
    def name(self) -> str:
        return "grep"

    @property
    def runtime_name(self) -> str:
        return "uni-agent-grep"

    @property
    def local_path(self) -> Path:
        return Path(__file__).parent / "grep"

    def get_tool_schema(self) -> dict:
        return self.build_tool_schema(
            description=DESCRIPTION,
            arguments_model=GrepArguments,
        )

    def get_install_command(self) -> str | None:
        return None
