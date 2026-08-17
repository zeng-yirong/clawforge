def __getattr__(name: str):
    if name in {"AgentEnv", "AgentEnvConfig"}:
        from .env import AgentEnv, AgentEnvConfig

        return {"AgentEnv": AgentEnv, "AgentEnvConfig": AgentEnvConfig}[name]
    if name == "AgentInteraction":
        from .interaction import AgentInteraction

        return AgentInteraction
    if name in {"AgentChatModel", "OpenAICompatibleChatModel"}:
        from .model import AgentChatModel, OpenAICompatibleChatModel

        return {"AgentChatModel": AgentChatModel, "OpenAICompatibleChatModel": OpenAICompatibleChatModel}[name]
    if name in {"ToolsManager", "ToolsManagerConfig"}:
        from .tools_manager import ToolsManager, ToolsManagerConfig

        return {"ToolsManager": ToolsManager, "ToolsManagerConfig": ToolsManagerConfig}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AgentInteraction",
    "AgentEnvConfig",
    "AgentEnv",
    "AgentChatModel",
    "OpenAICompatibleChatModel",
    "ToolsManagerConfig",
    "ToolsManager",
]
