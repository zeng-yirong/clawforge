from uni_agent.interaction.tool_schemas import OpenAIFunctionCallSchema, OpenAIFunctionToolCall
from uni_agent.interaction.tools_manager import ToolsManager, ToolsManagerConfig


def test_new_file_tools_are_registered_in_schema_list() -> None:
    manager = ToolsManager(
        ToolsManagerConfig(
            tools=[
                {"name": "read"},
                {"name": "write"},
                {"name": "edit"},
                {"name": "str_replace_editor"},
                {"name": "grep"},
                {"name": "find"},
                {"name": "ls"},
            ]
        )
    )

    schema_names = [schema["function"]["name"] for schema in manager.tools_schemas]
    assert schema_names == ["read", "write", "edit", "str_replace_editor", "grep", "find", "ls"]


def test_generic_tool_commands_use_env_prefix_to_avoid_bash_builtin_collisions() -> None:
    manager = ToolsManager(ToolsManagerConfig(tools=[{"name": "read"}]))
    tool_call = OpenAIFunctionToolCall(
        id="call_1",
        function=OpenAIFunctionCallSchema(name="read", arguments={"path": "/tmp/demo.txt"}),
    )

    assert manager.get_tool_bash_command(tool_call) == "env read --path /tmp/demo.txt"


def test_workspace_tools_use_runtime_aliases_for_installation_and_execution() -> None:
    manager = ToolsManager(ToolsManagerConfig(tools=[{"name": "grep"}, {"name": "find"}, {"name": "ls"}]))

    grep_call = OpenAIFunctionToolCall(
        id="call_1",
        function=OpenAIFunctionCallSchema(name="grep", arguments={"pattern": "foo", "path": "."}),
    )
    find_call = OpenAIFunctionToolCall(
        id="call_2",
        function=OpenAIFunctionCallSchema(name="find", arguments={"glob": "**/*.py", "path": "."}),
    )
    ls_call = OpenAIFunctionToolCall(
        id="call_3",
        function=OpenAIFunctionCallSchema(name="ls", arguments={"path": "."}),
    )

    assert manager.get_tool_bash_command(grep_call) == "env uni-agent-grep --pattern foo --path ."
    assert manager.get_tool_bash_command(find_call) == "env uni-agent-find --glob '**/*.py' --path ."
    assert manager.get_tool_bash_command(ls_call) == "env uni-agent-ls --path ."


def test_str_replace_editor_command_argument_is_positional() -> None:
    manager = ToolsManager(ToolsManagerConfig(tools=[{"name": "str_replace_editor"}]))
    tool_call = OpenAIFunctionToolCall(
        id="call_1",
        function=OpenAIFunctionCallSchema(
            name="str_replace_editor",
            arguments={"command": "view", "path": "notes.txt", "view_range": [1, 20]},
        ),
    )

    assert manager.get_tool_bash_command(tool_call) == (
        "env str_replace_editor view --path notes.txt --view_range '[1, 20]'"
    )
