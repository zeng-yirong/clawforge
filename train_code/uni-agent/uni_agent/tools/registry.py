# ruff: noqa
"""Tool registry for concrete AbstractTool implementations and their schema/install hooks."""

from uni_agent.tools.base import AbstractTool


TOOL_REGISTRY: dict[str, type[AbstractTool]] = {}


def register_tool(name: str) -> type[AbstractTool]:
    """Decorator to register a tool class with a given name."""

    def decorator(cls: type[AbstractTool]) -> type[AbstractTool]:
        if name in TOOL_REGISTRY and TOOL_REGISTRY[name] != cls:
            raise ValueError(f"Tool {name} has already been registered: {TOOL_REGISTRY[name]} vs {cls}")
        TOOL_REGISTRY[name] = cls
        return cls

    return decorator


def get_tool(name: str) -> AbstractTool:
    """Get a tool instance by name."""
    if name not in TOOL_REGISTRY:
        raise ValueError(f"Unknown tool: {name}")
    return TOOL_REGISTRY[name]()
