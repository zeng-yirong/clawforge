import json

from claw_envs.post_mails.cli import POST_MAILS_SESSION_ID_ENV, build_parser, main


def _run_cli(argv: list[str], capsys) -> tuple[int, dict]:
    exit_code = main(argv)
    captured = capsys.readouterr()
    return exit_code, json.loads(captured.out)


def test_help_hides_session_management_details() -> None:
    help_text = build_parser().format_help()

    assert "--session-id" not in help_text
    assert "create-session" not in help_text
    assert "reset-session" not in help_text
    assert "prepare-rollout" not in help_text
    assert "reset-rollout" not in help_text


def test_task_requires_bound_rollout_session(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.delenv(POST_MAILS_SESSION_ID_ENV, raising=False)

    exit_code, payload = _run_cli(["task", "--state-root", str(tmp_path)], capsys)

    assert exit_code == 1
    assert payload["status"] == "error"
    assert POST_MAILS_SESSION_ID_ENV in payload["message"]


def test_prepare_rollout_binds_agent_commands_without_session_arg(tmp_path, monkeypatch, capsys) -> None:
    exit_code, prepared = _run_cli(
        [
            "prepare-rollout",
            "--state-root",
            str(tmp_path),
            "--scenario-id",
            "orbital_launch",
            "--show-bindings",
            "--show-task",
        ],
        capsys,
    )

    assert exit_code == 0
    assert prepared["status"] == "success"

    data = prepared["data"]
    session_id = data["session_id"]
    assert session_id
    assert data["bindings"][POST_MAILS_SESSION_ID_ENV] == session_id
    assert "session_id" not in data["task"]

    monkeypatch.setenv(POST_MAILS_SESSION_ID_ENV, session_id)

    exit_code, task_payload = _run_cli(["task", "--state-root", str(tmp_path)], capsys)

    assert exit_code == 0
    assert task_payload["status"] == "success"
    assert task_payload["data"]["scenario_id"] == "orbital_launch"
    assert "session_id" not in task_payload["data"]
