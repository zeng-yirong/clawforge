from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from typing import Any

from .environment import MailClientEnvironment

MAIL_CLIENT_SESSION_ID_ENV = "MAIL_CLIENT_SESSION_ID"
MAIL_CLIENT_SCENARIO_ID_ENV = "MAIL_CLIENT_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "email_inbox_automation"
_HIDDEN_HELP_MARKERS = ("(create-session)", "(reset-session)", "==SUPPRESS==")


def _print_json(payload: dict[str, Any], *, exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


class MailClientArgumentParser(argparse.ArgumentParser):
    def format_help(self) -> str:
        help_text = super().format_help()
        lines = [
            line
            for line in help_text.splitlines()
            if not any(marker in line for marker in _HIDDEN_HELP_MARKERS)
        ]
        return "\n".join(lines) + ("\n" if help_text.endswith("\n") else "")


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _generate_session_id() -> str:
    return f"mc-{_utc_stamp()}-{random.randint(1000, 9999)}"


def _resolve_bound_session_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "session_id", None)
    if explicit:
        return explicit

    env_value = os.getenv(MAIL_CLIENT_SESSION_ID_ENV, "").strip()
    if env_value:
        return env_value

    raise ValueError(
        f"No active rollout session is bound. The trainer must set {MAIL_CLIENT_SESSION_ID_ENV} "
        "before agent commands run."
    )


def _resolve_scenario_id(args: argparse.Namespace) -> str:
    scenario_id = getattr(args, "scenario_id", None)
    if scenario_id:
        return scenario_id

    env_value = os.getenv(MAIL_CLIENT_SCENARIO_ID_ENV, "").strip()
    if env_value:
        return env_value

    return DEFAULT_SCENARIO_ID


def _agent_payload(data: dict[str, Any]) -> dict[str, Any]:
    filtered = dict(data)
    filtered.pop("session_id", None)
    filtered.pop("state_root", None)
    return filtered


def _agent_error_message(exc: Exception) -> str:
    message = str(exc)
    if message.startswith("Session not found:"):
        return "No active rollout state was found. The trainer must prepare the rollout session first."
    if message.startswith("Timed out waiting for session lock:"):
        return "The rollout session is busy. Retry the command."
    return message


def build_parser() -> argparse.ArgumentParser:
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--data-root", type=str, default=None, help="Override the environment data directory.")
    shared.add_argument("--state-root", type=str, default=None, help="Override the session state directory.")

    agent_session = argparse.ArgumentParser(add_help=False)
    agent_session.add_argument("--session-id", type=str, default=None, help=argparse.SUPPRESS)

    parser = MailClientArgumentParser(description="Mail client automation training environment CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True, metavar="command")

    subparsers.add_parser("list-scenarios", help="List available scenarios.", parents=[shared])

    prepare = subparsers.add_parser(
        "prepare-rollout",
        aliases=["create-session"],
        help=argparse.SUPPRESS,
        parents=[shared],
    )
    prepare.add_argument("--session-id", type=str, default=None, help=argparse.SUPPRESS)
    prepare.add_argument("--scenario-id", type=str, default=None)
    prepare.add_argument("--show-bindings", action="store_true")
    prepare.add_argument("--show-task", action="store_true")
    prepare.add_argument("--overwrite", action="store_true")

    subparsers.add_parser(
        "reset-rollout",
        aliases=["reset-session"],
        help=argparse.SUPPRESS,
        parents=[shared, agent_session],
    )

    subparsers.add_parser("task", help="Show the task prompt and workspace summary.", parents=[shared, agent_session])

    list_emails = subparsers.add_parser("list-emails", help="List emails in the inbox.", parents=[shared, agent_session])
    list_emails.add_argument("--query", type=str, default="")
    list_emails.add_argument("--folder", type=str, default=None)
    list_emails.add_argument("--label", type=str, default=None)
    list_emails.add_argument("--unread-only", action="store_true")
    list_emails.add_argument("--limit", type=int, default=None)

    read_email = subparsers.add_parser("read-email", help="Open an email and mark it as read.", parents=[shared, agent_session])
    read_email.add_argument("--email-id", required=True, type=str)

    read_attachment = subparsers.add_parser("read-attachment", help="Read an attachment and mark it as opened.", parents=[shared, agent_session])
    read_attachment.add_argument("--attachment-id", required=True, type=str)

    classify = subparsers.add_parser("classify-email", help="Classify an email into a folder with labels.", parents=[shared, agent_session])
    classify.add_argument("--email-id", required=True, type=str)
    classify.add_argument("--folder", required=True, type=str)
    classify.add_argument("--labels", required=True, type=str, help="Comma-separated labels")

    archive = subparsers.add_parser("archive-email", help="Archive an email.", parents=[shared, agent_session])
    archive.add_argument("--email-id", required=True, type=str)

    delete = subparsers.add_parser("delete-email", help="Move an email to trash.", parents=[shared, agent_session])
    delete.add_argument("--email-id", required=True, type=str)

    list_todos = subparsers.add_parser("list-todos", help="List TODO items.", parents=[shared, agent_session])
    list_todos.add_argument("--completed-only", action="store_true")
    list_todos.add_argument("--pending-only", action="store_true")
    list_todos.add_argument("--priority", type=str, default=None)
    list_todos.add_argument("--limit", type=int, default=None)

    create_todo = subparsers.add_parser("create-todo", help="Create a new TODO item from an email.", parents=[shared, agent_session])
    create_todo.add_argument("--source-email-id", required=True, type=str)
    create_todo.add_argument("--title", required=True, type=str)
    create_todo.add_argument("--description", required=True, type=str)
    create_todo.add_argument("--priority", type=str, default="normal")
    create_todo.add_argument("--due-date", type=str, default=None)

    complete_todo = subparsers.add_parser("complete-todo", help="Mark a TODO item as completed.", parents=[shared, agent_session])
    complete_todo.add_argument("--todo-id", required=True, type=str)

    list_replies = subparsers.add_parser("list-replies", help="List sent replies.", parents=[shared, agent_session])
    list_replies.add_argument("--target-email-id", type=str, default=None)
    list_replies.add_argument("--limit", type=int, default=None)

    create_reply = subparsers.add_parser("create-reply", help="Send a reply to an email.", parents=[shared, agent_session])
    create_reply.add_argument("--target-email-id", required=True, type=str)
    create_reply.add_argument("--content", required=True, type=str)

    subparsers.add_parser("session-summary", help="Show session progress and summary.", parents=[shared, agent_session])

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = MailClientEnvironment(data_root=args.data_root, state_root=args.state_root)

    try:
        if args.command == "list-scenarios":
            return _print_json({"status": "success", "data": env.list_scenarios()})
        if args.command in {"prepare-rollout", "create-session"}:
            session_id = getattr(args, "session_id", None) or os.getenv(MAIL_CLIENT_SESSION_ID_ENV, "").strip()
            session_id = session_id or _generate_session_id()
            scenario_id = _resolve_scenario_id(args)
            env.create_session(session_id, scenario_id, overwrite=args.overwrite)
            payload = {
                "session_id": session_id,
                "scenario_id": scenario_id,
                "state_root": str(env.store.state_root),
            }
            if args.show_bindings:
                payload["bindings"] = {
                    MAIL_CLIENT_SESSION_ID_ENV: session_id,
                    "MAIL_CLIENT_STATE_ROOT": str(env.store.state_root),
                    MAIL_CLIENT_SCENARIO_ID_ENV: scenario_id,
                }
            if args.show_task:
                payload["task"] = _agent_payload(env.get_task(session_id))
            return _print_json({"status": "success", "data": payload})

        session_id = _resolve_bound_session_id(args)

        if args.command in {"reset-rollout", "reset-session"}:
            data = env.reset_session(session_id)
            return _print_json({"status": "success", "data": _agent_payload(data)})
        if args.command == "task":
            return _print_json({"status": "success", "data": _agent_payload(env.get_task(session_id))})
        if args.command == "list-emails":
            data = env.list_emails(
                session_id,
                query=args.query,
                folder=args.folder,
                label=args.label,
                unread_only=args.unread_only,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "read-email":
            data = env.read_email(session_id, args.email_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "read-attachment":
            data = env.read_attachment(session_id, args.attachment_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "classify-email":
            labels = [l.strip() for l in args.labels.split(",")]
            data = env.classify_email(session_id, args.email_id, args.folder, labels)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "archive-email":
            data = env.archive_email(session_id, args.email_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "delete-email":
            data = env.delete_email(session_id, args.email_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "list-todos":
            data = env.list_todos(
                session_id,
                completed_only=args.completed_only,
                pending_only=args.pending_only,
                priority=args.priority,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "create-todo":
            data = env.create_todo(
                session_id,
                source_email_id=args.source_email_id,
                title=args.title,
                description=args.description,
                priority=args.priority,
                due_date=args.due_date,
            )
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "complete-todo":
            data = env.complete_todo(session_id, args.todo_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "list-replies":
            data = env.list_replies(
                session_id,
                target_email_id=args.target_email_id,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "create-reply":
            data = env.create_reply(
                session_id,
                target_email_id=args.target_email_id,
                content=args.content,
            )
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "session-summary":
            return _print_json({"status": "success", "data": _agent_payload(env.session_summary(session_id))})
    except Exception as exc:
        return _print_json({"status": "error", "message": _agent_error_message(exc)}, exit_code=1)

    return _print_json({"status": "error", "message": f"Unknown command: {args.command}"}, exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
