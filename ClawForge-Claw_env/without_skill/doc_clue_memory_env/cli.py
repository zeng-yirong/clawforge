from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from typing import Any

from .environment import DocumentClueMemoryEnvironment


DOC_CLUE_MEMORY_SESSION_ID_ENV = "DOC_CLUE_MEMORY_SESSION_ID"
DOC_CLUE_MEMORY_STATE_ROOT_ENV = "DOC_CLUE_MEMORY_STATE_ROOT"
DOC_CLUE_MEMORY_SCENARIO_ID_ENV = "DOC_CLUE_MEMORY_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "tech_solution_signal_trace_q2_2026"
_HIDDEN_HELP_MARKERS = ("(create-session)", "(reset-session)", "==SUPPRESS==")


def _print_json(payload: dict[str, Any], *, exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


class DocClueMemoryArgumentParser(argparse.ArgumentParser):
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
    return f"doc-{_utc_stamp()}-{random.randint(1000, 9999)}"


def _resolve_bound_session_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "session_id", None)
    if explicit:
        return explicit

    env_value = os.getenv(DOC_CLUE_MEMORY_SESSION_ID_ENV, "").strip()
    if env_value:
        return env_value

    raise ValueError(
        f"No active rollout session is bound. The trainer must set {DOC_CLUE_MEMORY_SESSION_ID_ENV} "
        "before agent commands run."
    )


def _resolve_scenario_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "scenario_id", None)
    if explicit:
        return explicit

    env_value = os.getenv(DOC_CLUE_MEMORY_SCENARIO_ID_ENV, "").strip()
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

    parser = DocClueMemoryArgumentParser(description="Document clue memory training environment CLI.")
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

    list_reports_cmd = subparsers.add_parser("list-reports", help="List industry reports.", parents=[shared, agent_session])
    list_reports_cmd.add_argument("--query", type=str, default="")
    list_reports_cmd.add_argument("--sector", type=str, default=None)
    list_reports_cmd.add_argument("--limit", type=int, default=None)

    get_report_cmd = subparsers.add_parser("get-report", help="Get full report content.", parents=[shared, agent_session])
    get_report_cmd.add_argument("--report-id", required=True, type=str)

    list_presentations_cmd = subparsers.add_parser(
        "list-presentations",
        help="List presentation samples.",
        parents=[shared, agent_session],
    )
    list_presentations_cmd.add_argument("--query", type=str, default="")
    list_presentations_cmd.add_argument("--owner", type=str, default=None)
    list_presentations_cmd.add_argument("--limit", type=int, default=None)

    get_presentation_cmd = subparsers.add_parser(
        "get-presentation",
        help="Get full presentation notes.",
        parents=[shared, agent_session],
    )
    get_presentation_cmd.add_argument("--presentation-id", required=True, type=str)

    list_media_cmd = subparsers.add_parser(
        "list-media-samples",
        help="List media copy memory samples.",
        parents=[shared, agent_session],
    )
    list_media_cmd.add_argument("--query", type=str, default="")
    list_media_cmd.add_argument("--channel", type=str, default=None)
    list_media_cmd.add_argument("--limit", type=int, default=None)

    get_media_cmd = subparsers.add_parser(
        "get-media-sample",
        help="Get one media sample.",
        parents=[shared, agent_session],
    )
    get_media_cmd.add_argument("--sample-id", required=True, type=str)

    search_cmd = subparsers.add_parser(
        "search-library",
        help="Search across reports, presentations, and media samples.",
        parents=[shared, agent_session],
    )
    search_cmd.add_argument("--query", required=True, type=str)
    search_cmd.add_argument("--source-type", type=str, default=None)
    search_cmd.add_argument("--limit", type=int, default=None)

    subparsers.add_parser("list-attachments", help="List supporting attachments.", parents=[shared, agent_session])

    read_attachment_cmd = subparsers.add_parser(
        "read-attachment",
        help="Read an attachment used by the scenario.",
        parents=[shared, agent_session],
    )
    read_attachment_cmd.add_argument("--attachment-path", required=True, type=str)

    save_clue_cmd = subparsers.add_parser(
        "save-clue-list",
        help="Save a clue list into the environment temporary records.",
        parents=[shared, agent_session],
    )
    save_clue_cmd.add_argument("--solution-id", required=True, type=str)
    save_clue_cmd.add_argument("--solution-name", required=True, type=str)
    save_clue_cmd.add_argument("--document-ids", required=True, type=str, help="Comma-separated document ids")
    save_clue_cmd.add_argument("--clues-json", required=True, type=str, help="JSON array of clue strings")
    save_clue_cmd.add_argument("--summary", required=True, type=str)
    save_clue_cmd.add_argument("--confidence", type=str, default="medium")

    list_temp_cmd = subparsers.add_parser(
        "list-temp-records",
        help="List saved temporary records.",
        parents=[shared, agent_session],
    )
    list_temp_cmd.add_argument("--record-type", type=str, default=None)
    list_temp_cmd.add_argument("--limit", type=int, default=None)

    get_temp_cmd = subparsers.add_parser(
        "get-temp-record",
        help="Get one saved temporary record.",
        parents=[shared, agent_session],
    )
    get_temp_cmd.add_argument("--record-id", required=True, type=str)

    subparsers.add_parser("session-summary", help="Show session progress and summary.", parents=[shared, agent_session])

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = DocumentClueMemoryEnvironment(data_root=args.data_root, state_root=args.state_root)

    try:
        if args.command == "list-scenarios":
            return _print_json({"status": "success", "data": env.list_scenarios()})

        if args.command in {"prepare-rollout", "create-session"}:
            session_id = getattr(args, "session_id", None) or os.getenv(DOC_CLUE_MEMORY_SESSION_ID_ENV, "").strip()
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
                    DOC_CLUE_MEMORY_SESSION_ID_ENV: session_id,
                    DOC_CLUE_MEMORY_STATE_ROOT_ENV: str(env.store.state_root),
                    DOC_CLUE_MEMORY_SCENARIO_ID_ENV: scenario_id,
                }
            if args.show_task:
                payload["task"] = _agent_payload(env.get_task(session_id))
            return _print_json({"status": "success", "data": payload})

        session_id = _resolve_bound_session_id(args)

        if args.command in {"reset-rollout", "reset-session"}:
            data = env.reset_session(session_id)
            return _print_json({"status": "success", "data": _agent_payload(data)})

        if args.command == "task":
            return _print_json({"status": "success", "data": _agent_payload(env.view_task(session_id)["data"])})

        if args.command == "list-reports":
            data = env.list_reports(session_id, query=args.query, sector=args.sector, limit=args.limit)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-report":
            data = env.get_report(session_id, args.report_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-presentations":
            data = env.list_presentations(session_id, query=args.query, owner=args.owner, limit=args.limit)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-presentation":
            data = env.get_presentation(session_id, args.presentation_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-media-samples":
            data = env.list_media_samples(session_id, query=args.query, channel=args.channel, limit=args.limit)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-media-sample":
            data = env.get_media_sample(session_id, args.sample_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "search-library":
            data = env.search_library(
                session_id,
                query=args.query,
                source_type=args.source_type,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-attachments":
            data = env.list_attachments(session_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "read-attachment":
            data = env.read_attachment(session_id, args.attachment_path)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "save-clue-list":
            document_ids = [item.strip() for item in args.document_ids.split(",") if item.strip()]
            clues = json.loads(args.clues_json)
            data = env.save_clue_list(
                session_id,
                solution_id=args.solution_id,
                solution_name=args.solution_name,
                document_ids=document_ids,
                clues=clues,
                summary=args.summary,
                confidence=args.confidence,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-temp-records":
            data = env.list_temp_records(session_id, record_type=args.record_type, limit=args.limit)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-temp-record":
            data = env.get_temp_record(session_id, args.record_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "session-summary":
            return _print_json({"status": "success", "data": _agent_payload(env.session_summary(session_id))})

    except Exception as exc:
        return _print_json({"status": "error", "message": _agent_error_message(exc)}, exit_code=1)

    return _print_json({"status": "error", "message": f"Unknown command: {args.command}"}, exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
