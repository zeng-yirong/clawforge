"""Execute bash command tool."""

from pathlib import Path

from pydantic import BaseModel, Field

from uni_agent.tools.base import AbstractTool
from uni_agent.tools.registry import register_tool

DESCRIPTION = """
Execute a bash command in the terminal.
""".strip()


class ExecuteBashArguments(BaseModel):
    command: str = Field(description="The command to execute.")


@register_tool("execute_bash")
class ExecuteBashTool(AbstractTool):
    @property
    def name(self) -> str:
        return "execute_bash"

    @property
    def local_path(self) -> Path:
        return Path(__file__).parent / "execute_bash"

    def get_tool_schema(self) -> dict:
        return self.build_tool_schema(
            description=DESCRIPTION,
            arguments_model=ExecuteBashArguments,
        )

    def get_install_command(self) -> str:
        return None
