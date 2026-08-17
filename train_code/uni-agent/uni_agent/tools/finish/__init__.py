"""Finish tool definition."""

from pathlib import Path

from pydantic import BaseModel, Field

from uni_agent.tools.base import AbstractTool
from uni_agent.tools.registry import register_tool

DESCRIPTION = """
Finish the task and output the final answer.
Always call this tool when you are ready to end the interaction.
""".strip()


class FinishArguments(BaseModel):
    answer: str = Field(description="Final answer to return to the user.")


@register_tool("finish")
class FinishTool(AbstractTool):
    @property
    def name(self) -> str:
        return "finish"

    @property
    def local_path(self) -> Path:
        return Path(__file__).parent / "finish"

    def get_tool_schema(self) -> dict:
        return self.build_tool_schema(
            description=DESCRIPTION,
            arguments_model=FinishArguments,
        )

    def get_install_command(self) -> str | None:
        return None
