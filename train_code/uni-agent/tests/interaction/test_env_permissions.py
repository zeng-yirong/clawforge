import pytest

from uni_agent.interaction.permissions import (
    ActionPermissionError,
    validate_no_shell_composition,
    validate_restricted_bash_command,
    validate_workspace_tool_command,
)


def test_workspace_tool_paths_must_stay_inside_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "data").mkdir()

    validate_workspace_tool_command(
        "env read --path data/input.json",
        workspace=str(workspace),
        cwd=str(workspace),
    )
    validate_workspace_tool_command(
        "env uni-agent-grep --pattern Jane --path data",
        workspace=str(workspace),
        cwd=str(workspace),
    )

    with pytest.raises(ActionPermissionError, match="outside workspace"):
        validate_workspace_tool_command(
            "env read --path ../secret.txt",
            workspace=str(workspace),
            cwd=str(workspace),
        )

    with pytest.raises(ActionPermissionError, match="outside workspace"):
        validate_workspace_tool_command(
            f"env write --path '{(tmp_path / 'outside.txt').as_posix()}' --content nope",
            workspace=str(workspace),
            cwd=str(workspace),
        )


def test_restricted_bash_allows_direct_env_cli_commands_only():
    allowed = ["python -m claw_envs.smart_home_envs.cli", "python -m smart_home_envs.cli"]

    validate_restricted_bash_command(
        "python -m claw_envs.smart_home_envs.cli get-all-devices",
        allowed_prefixes=allowed,
        blocked_subcommands=["prepare-rollout", "reset-rollout"],
    )
    validate_restricted_bash_command(
        'python -m smart_home_envs.cli set-air-conditioner --device-id AC_001 --mode "eco; night"',
        allowed_prefixes=allowed,
        blocked_subcommands=["prepare-rollout", "reset-rollout"],
    )

    with pytest.raises(ActionPermissionError, match="Allowed command prefix"):
        validate_restricted_bash_command(
            "cat /etc/passwd",
            allowed_prefixes=allowed,
            blocked_subcommands=["prepare-rollout", "reset-rollout"],
        )

    with pytest.raises(ActionPermissionError, match="shell control"):
        validate_restricted_bash_command(
            "python -m claw_envs.smart_home_envs.cli task && cat /etc/passwd",
            allowed_prefixes=allowed,
            blocked_subcommands=["prepare-rollout", "reset-rollout"],
        )

    with pytest.raises(ActionPermissionError, match="not allowed"):
        validate_restricted_bash_command(
            "python -m claw_envs.smart_home_envs.cli prepare-rollout",
            allowed_prefixes=allowed,
            blocked_subcommands=["prepare-rollout", "reset-rollout"],
        )

    with pytest.raises(ActionPermissionError, match="command substitution"):
        validate_restricted_bash_command(
            'python -m claw_envs.smart_home_envs.cli task --note "$(cat /etc/passwd)"',
            allowed_prefixes=allowed,
            blocked_subcommands=["prepare-rollout", "reset-rollout"],
        )


def test_tool_commands_cannot_append_shell_operations():
    validate_no_shell_composition("env write --path notes.txt --content 'a && b'")

    with pytest.raises(ActionPermissionError, match="shell control"):
        validate_no_shell_composition("env read --path data && cat /etc/passwd")

    with pytest.raises(ActionPermissionError, match="command substitution"):
        validate_no_shell_composition('env write --path notes.txt --content "$(cat /etc/passwd)"')
