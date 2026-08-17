"""Find workspace files with a glob pattern."""

from pathlib import Path

from pydantic import BaseModel, Field

from uni_agent.tools.base import AbstractTool
from uni_agent.tools.registry import register_tool

DESCRIPTION = """
Find files in the workspace using a glob pattern.
Returns matching paths relative to the search root.
Use include_dirs=true when you also want matching directories.
""".strip()


class FindArguments(BaseModel):
    glob: str = Field(description="Glob pattern to match, such as `**/*.py` or `docs/*.md`.")
    path: str = Field(
        default=".",
        description="Directory to search from. Defaults to the current workspace directory.",
    )
    include_dirs: bool = Field(
        default=False,
        description="Whether matching directories should also be returned.",
    )
    max_results: int = Field(
        default=500,
        description="Maximum number of matching paths to return.",
    )


@register_tool("find")
class FindTool(AbstractTool):
    @property
    def name(self) -> str:
        return "find"

    @property
    def runtime_name(self) -> str:
        return "uni-agent-find"

    @property
    def local_path(self) -> Path:
        return Path(__file__).parent / "find"

    def get_tool_schema(self) -> dict:
        return self.build_tool_schema(
            description=DESCRIPTION,
            arguments_model=FindArguments,
        )

    def get_install_command(self) -> str | None:
        return None
