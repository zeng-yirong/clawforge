from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from typing import Any

from .environment import CRMEnvironment

CRM_SESSION_ID_ENV = "CRM_SESSION_ID"
CRM_SCENARIO_ID_ENV = "CRM_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "crm_contact_management"
_HIDDEN_HELP_MARKERS = ("(create-session)", "(reset-session)", "==SUPPRESS==")


def _print_json(payload: dict[str, Any], *, exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


class CRMArgumentParser(argparse.ArgumentParser):
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
    return f"crm-{_utc_stamp()}-{random.randint(1000, 9999)}"


def _resolve_bound_session_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "session_id", None)
    if explicit:
        return explicit

    env_value = os.getenv(CRM_SESSION_ID_ENV, "").strip()
    if env_value:
        return env_value

    raise ValueError(
        f"No active rollout session is bound. The trainer must set {CRM_SESSION_ID_ENV} "
        "before agent commands run."
    )


def _resolve_scenario_id(args: argparse.Namespace) -> str:
    scenario_id = getattr(args, "scenario_id", None)
    if scenario_id:
        return scenario_id

    env_value = os.getenv(CRM_SCENARIO_ID_ENV, "").strip()
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

    parser = CRMArgumentParser(description="CRM training environment CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True, metavar="command")

    subparsers.add_parser("list-scenarios", help="List available scenarios.", parents=[shared])

    prepare = subparsers.add_parser("prepare-rollout", aliases=["create-session"], help=argparse.SUPPRESS, parents=[shared])
    prepare.add_argument("--session-id", type=str, default=None, help=argparse.SUPPRESS)
    prepare.add_argument("--scenario-id", type=str, default=None)
    prepare.add_argument("--show-bindings", action="store_true")
    prepare.add_argument("--show-task", action="store_true")
    prepare.add_argument("--overwrite", action="store_true")

    subparsers.add_parser("reset-rollout", aliases=["reset-session"], help=argparse.SUPPRESS, parents=[shared, agent_session])

    subparsers.add_parser("task", help="Show the task prompt and workspace summary.", parents=[shared, agent_session])

    list_contacts = subparsers.add_parser("list-contacts", help="List contacts with optional filters.", parents=[shared, agent_session])
    list_contacts.add_argument("--query", type=str, default="")
    list_contacts.add_argument("--folder", type=str, default=None)
    list_contacts.add_argument("--contact-type", type=str, default=None)
    list_contacts.add_argument("--tag", type=str, default=None)
    list_contacts.add_argument("--limit", type=int, default=None)

    get_contact = subparsers.add_parser("get-contact", help="Get contact details.", parents=[shared, agent_session])
    get_contact.add_argument("--contact-id", required=True, type=str)

    classify = subparsers.add_parser("classify-contact", help="Classify contact into folder with tags.", parents=[shared, agent_session])
    classify.add_argument("--contact-id", required=True, type=str)
    classify.add_argument("--folder", required=True, type=str)
    classify.add_argument("--tags", required=True, type=str, help="Comma-separated tags")

    add_tags = subparsers.add_parser("add-tags", help="Add tags to contact.", parents=[shared, agent_session])
    add_tags.add_argument("--contact-id", required=True, type=str)
    add_tags.add_argument("--tags", required=True, type=str, help="Comma-separated tags")

    remove_tags = subparsers.add_parser("remove-tags", help="Remove tags from contact.", parents=[shared, agent_session])
    remove_tags.add_argument("--contact-id", required=True, type=str)
    remove_tags.add_argument("--tags", required=True, type=str, help="Comma-separated tags")

    archive = subparsers.add_parser("archive-contact", help="Archive a contact.", parents=[shared, agent_session])
    archive.add_argument("--contact-id", required=True, type=str)

    search = subparsers.add_parser("search-contacts", help="Search contacts by various criteria.", parents=[shared, agent_session])
    search.add_argument("--name-query", type=str, default="")
    search.add_argument("--email-query", type=str, default="")
    search.add_argument("--company-id", type=str, default=None)
    search.add_argument("--tag", type=str, default=None)
    search.add_argument("--folder", type=str, default=None)

    list_reminders = subparsers.add_parser("list-reminders", help="List reminders.", parents=[shared, agent_session])
    list_reminders.add_argument("--contact-id", type=str, default=None)
    list_reminders.add_argument("--reminder-type", type=str, default=None)
    list_reminders.add_argument("--upcoming-only", action="store_true")
    list_reminders.add_argument("--limit", type=int, default=None)

    create_reminder = subparsers.add_parser("create-birthday-reminder", help="Create birthday reminder for contact.", parents=[shared, agent_session])
    create_reminder.add_argument("--contact-id", required=True, type=str)
    create_reminder.add_argument("--days-before", type=int, default=7)

    enable_reminder = subparsers.add_parser("enable-reminder", help="Enable a reminder.", parents=[shared, agent_session])
    enable_reminder.add_argument("--reminder-id", required=True, type=str)

    disable_reminder = subparsers.add_parser("disable-reminder", help="Disable a reminder.", parents=[shared, agent_session])
    disable_reminder.add_argument("--reminder-id", required=True, type=str)

    list_tags = subparsers.add_parser("list-tags", help="List available tag definitions.", parents=[shared, agent_session])
    list_tags.add_argument("--category", type=str, default=None)

    create_tag = subparsers.add_parser("get-or-create-tag", help="Get or create a tag.", parents=[shared, agent_session])
    create_tag.add_argument("--tag-name", required=True, type=str)

    subparsers.add_parser("session-summary", help="Show session progress and summary.", parents=[shared, agent_session])

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = CRMEnvironment(data_root=args.data_root, state_root=args.state_root)

    try:
        if args.command == "list-scenarios":
            return _print_json({"status": "success", "data": env.list_scenarios()})

        if args.command in {"prepare-rollout", "create-session"}:
            session_id = getattr(args, "session_id", None) or os.getenv(CRM_SESSION_ID_ENV, "").strip()
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
                    CRM_SESSION_ID_ENV: session_id,
                    "CRM_STATE_ROOT": str(env.store.state_root),
                    CRM_SCENARIO_ID_ENV: scenario_id,
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

        if args.command == "list-contacts":
            data = env.list_contacts(
                session_id, query=args.query, folder=args.folder, contact_type=args.contact_type, tag=args.tag, limit=args.limit
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-contact":
            data = env.get_contact(session_id, args.contact_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "classify-contact":
            tags = [t.strip() for t in args.tags.split(",")]
            data = env.classify_contact(session_id, args.contact_id, args.folder, tags)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "add-tags":
            tags = [t.strip() for t in args.tags.split(",")]
            data = env.add_tags(session_id, args.contact_id, tags)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "remove-tags":
            tags = [t.strip() for t in args.tags.split(",")]
            data = env.remove_tags(session_id, args.contact_id, tags)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "archive-contact":
            data = env.archive_contact(session_id, args.contact_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "search-contacts":
            data = env.search_contacts(
                session_id,
                name_query=args.name_query,
                email_query=args.email_query,
                company_id=args.company_id,
                tag=args.tag,
                folder=args.folder,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-reminders":
            data = env.list_reminders(
                session_id, contact_id=args.contact_id, reminder_type=args.reminder_type, upcoming_only=args.upcoming_only, limit=args.limit
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "create-birthday-reminder":
            data = env.create_birthday_reminder(session_id, args.contact_id, args.days_before)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "enable-reminder":
            data = env.enable_reminder(session_id, args.reminder_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "disable-reminder":
            data = env.disable_reminder(session_id, args.reminder_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-tags":
            data = env.list_tags(session_id, category=args.category)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-or-create-tag":
            data = env.get_or_create_tag(session_id, args.tag_name)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "session-summary":
            return _print_json({"status": "success", "data": _agent_payload(env.session_summary(session_id))})

    except Exception as exc:
        return _print_json({"status": "error", "message": _agent_error_message(exc)}, exit_code=1)

    return _print_json({"status": "error", "message": f"Unknown command: {args.command}"}, exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
