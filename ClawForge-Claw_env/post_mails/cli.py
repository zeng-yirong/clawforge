from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from typing import Any

from .environment import PostMailsEnvironment

POST_MAILS_SESSION_ID_ENV = "POST_MAILS_SESSION_ID"
POST_MAILS_SCENARIO_ID_ENV = "POST_MAILS_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "orbital_launch"
_HIDDEN_HELP_MARKERS = ("(create-session)", "(reset-session)", "==SUPPRESS==")


def _print_json(payload: dict[str, Any], *, exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


class PostMailsArgumentParser(argparse.ArgumentParser):
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
    return f"pm-{_utc_stamp()}-{random.randint(1000, 9999)}"


def _resolve_bound_session_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "session_id", None)
    if explicit:
        return explicit

    env_value = os.getenv(POST_MAILS_SESSION_ID_ENV, "").strip()
    if env_value:
        return env_value

    raise ValueError(
        f"No active rollout session is bound. The trainer must set {POST_MAILS_SESSION_ID_ENV} "
        "before agent commands run."
    )


def _resolve_scenario_id(args: argparse.Namespace) -> str:
    scenario_id = getattr(args, "scenario_id", None)
    if scenario_id:
        return scenario_id

    env_value = os.getenv(POST_MAILS_SCENARIO_ID_ENV, "").strip()
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

    parser = PostMailsArgumentParser(description="Post-mails training environment CLI.")
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

    list_emails = subparsers.add_parser("list-emails", help="List inbox items.", parents=[shared, agent_session])
    list_emails.add_argument("--query", type=str, default="")
    list_emails.add_argument("--folder", type=str, default=None)
    list_emails.add_argument("--unread-only", action="store_true")
    list_emails.add_argument("--limit", type=int, default=None)

    read_email = subparsers.add_parser(
        "read-email",
        help="Open an email and mark it as read.",
        parents=[shared, agent_session],
    )
    read_email.add_argument("--email-id", required=True, type=str)

    read_attachment = subparsers.add_parser(
        "read-attachment",
        help="Read an attachment and mark it as opened.",
        parents=[shared, agent_session],
    )
    read_attachment.add_argument("--attachment-id", required=True, type=str)

    list_posts = subparsers.add_parser("list-posts", help="List X and Reddit posts.", parents=[shared, agent_session])
    list_posts.add_argument("--query", type=str, default="")
    list_posts.add_argument("--platform", type=str, default=None)
    list_posts.add_argument("--needs-response-only", action="store_true")
    list_posts.add_argument("--limit", type=int, default=None)

    view_post = subparsers.add_parser(
        "view-post",
        help="View a full post thread, including replies.",
        parents=[shared, agent_session],
    )
    view_post.add_argument("--post-id", required=True, type=str)

    publish = subparsers.add_parser("publish-post", help="Publish a new X or Reddit post.", parents=[shared, agent_session])
    publish.add_argument("--platform", required=True, type=str)
    publish.add_argument("--content", required=True, type=str)
    publish.add_argument("--title", type=str, default=None)
    publish.add_argument("--community", type=str, default=None)
    publish.add_argument("--author", type=str, default=None)

    reply = subparsers.add_parser("reply-post", help="Reply to a post.", parents=[shared, agent_session])
    reply.add_argument("--post-id", required=True, type=str)
    reply.add_argument("--content", required=True, type=str)
    reply.add_argument("--author", type=str, default=None)

    subparsers.add_parser(
        "session-summary",
        help="Show session progress and summary.",
        parents=[shared, agent_session],
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = PostMailsEnvironment(data_root=args.data_root, state_root=args.state_root)

    try:
        if args.command == "list-scenarios":
            return _print_json({"status": "success", "data": env.list_scenarios()})
        if args.command in {"prepare-rollout", "create-session"}:
            session_id = getattr(args, "session_id", None) or os.getenv(POST_MAILS_SESSION_ID_ENV, "").strip()
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
                    POST_MAILS_SESSION_ID_ENV: session_id,
                    "POST_MAILS_STATE_ROOT": str(env.store.state_root),
                    POST_MAILS_SCENARIO_ID_ENV: scenario_id,
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
        if args.command == "list-posts":
            data = env.list_posts(
                session_id,
                query=args.query,
                platform=args.platform,
                needs_response_only=args.needs_response_only,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "view-post":
            data = env.view_post(session_id, args.post_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "publish-post":
            data = env.publish_post(
                session_id,
                platform=args.platform,
                content=args.content,
                title=args.title,
                community=args.community,
                author=args.author,
            )
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "reply-post":
            data = env.reply_to_post(
                session_id,
                post_id=args.post_id,
                content=args.content,
                author=args.author,
            )
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "session-summary":
            return _print_json({"status": "success", "data": _agent_payload(env.session_summary(session_id))})
    except Exception as exc:
        return _print_json({"status": "error", "message": _agent_error_message(exc)}, exit_code=1)

    return _print_json({"status": "error", "message": f"Unknown command: {args.command}"}, exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
