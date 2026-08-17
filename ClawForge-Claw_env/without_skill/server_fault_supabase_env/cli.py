from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from typing import Any

from .environment import ServerFaultSupabaseEnvironment


SERVER_FAULT_SUPABASE_SESSION_ID_ENV = "SERVER_FAULT_SUPABASE_SESSION_ID"
SERVER_FAULT_SUPABASE_STATE_ROOT_ENV = "SERVER_FAULT_SUPABASE_STATE_ROOT"
SERVER_FAULT_SUPABASE_SCENARIO_ID_ENV = "SERVER_FAULT_SUPABASE_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "server_fault_triage_q2_2026"
_HIDDEN_HELP_MARKERS = ("(create-session)", "(reset-session)", "==SUPPRESS==")


def _print_json(payload: dict[str, Any], *, exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


class ServerFaultSupabaseArgumentParser(argparse.ArgumentParser):
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
    return f"srv-{_utc_stamp()}-{random.randint(1000, 9999)}"


def _resolve_bound_session_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "session_id", None)
    if explicit:
        return explicit
    env_value = os.getenv(SERVER_FAULT_SUPABASE_SESSION_ID_ENV, "").strip()
    if env_value:
        return env_value
    raise ValueError(
        f"No active rollout session is bound. The trainer must set {SERVER_FAULT_SUPABASE_SESSION_ID_ENV} "
        "before agent commands run."
    )


def _resolve_scenario_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "scenario_id", None)
    if explicit:
        return explicit
    env_value = os.getenv(SERVER_FAULT_SUPABASE_SCENARIO_ID_ENV, "").strip()
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

    parser = ServerFaultSupabaseArgumentParser(description="Server fault Supabase training environment CLI.")
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

    list_incidents_cmd = subparsers.add_parser("list-incidents", help="List server fault incidents.", parents=[shared, agent_session])
    list_incidents_cmd.add_argument("--query", type=str, default="")
    list_incidents_cmd.add_argument("--category", type=str, default=None)
    list_incidents_cmd.add_argument("--severity", type=str, default=None)
    list_incidents_cmd.add_argument("--status", type=str, default=None)
    list_incidents_cmd.add_argument("--limit", type=int, default=None)

    get_incident_cmd = subparsers.add_parser("get-incident", help="Get incident details.", parents=[shared, agent_session])
    get_incident_cmd.add_argument("--incident-id", required=True, type=str)

    screen_cmd = subparsers.add_parser(
        "screen-risk-incidents",
        help="Screen UPS outage and service-down risk tickets.",
        parents=[shared, agent_session],
    )
    screen_cmd.add_argument("--categories", required=True, type=str, help="Comma-separated categories")
    screen_cmd.add_argument("--statuses", type=str, default="open,triaged", help="Comma-separated statuses")
    screen_cmd.add_argument("--severities", type=str, default="critical,high", help="Comma-separated severities")
    screen_cmd.add_argument("--limit", type=int, default=None)

    subparsers.add_parser("list-attachments", help="List supporting attachments.", parents=[shared, agent_session])

    read_attachment_cmd = subparsers.add_parser(
        "read-attachment",
        help="Read an attachment used by the scenario.",
        parents=[shared, agent_session],
    )
    read_attachment_cmd.add_argument("--attachment-path", required=True, type=str)

    remediate_cmd = subparsers.add_parser(
        "remediate-incident",
        help="Execute remediation logic for one incident.",
        parents=[shared, agent_session],
    )
    remediate_cmd.add_argument("--incident-id", required=True, type=str)
    remediate_cmd.add_argument("--remediation-mode", required=True, type=str)
    remediate_cmd.add_argument("--operator-note", required=True, type=str)

    batch_cmd = subparsers.add_parser(
        "batch-remediate",
        help="Execute remediation logic for multiple incidents.",
        parents=[shared, agent_session],
    )
    batch_cmd.add_argument("--incident-ids", required=True, type=str, help="Comma-separated incident ids")
    batch_cmd.add_argument("--remediation-mode", required=True, type=str)
    batch_cmd.add_argument("--operator-note", required=True, type=str)

    write_cmd = subparsers.add_parser(
        "write-supabase-resolution",
        help="Write a processed incident into the simulated Supabase memory table.",
        parents=[shared, agent_session],
    )
    write_cmd.add_argument("--incident-id", required=True, type=str)
    write_cmd.add_argument("--table-name", type=str, default="incident_resolutions")

    list_rows_cmd = subparsers.add_parser(
        "list-supabase-rows",
        help="List rows in the simulated Supabase memory table.",
        parents=[shared, agent_session],
    )
    list_rows_cmd.add_argument("--table-name", type=str, default=None)
    list_rows_cmd.add_argument("--incident-id", type=str, default=None)
    list_rows_cmd.add_argument("--limit", type=int, default=None)

    get_row_cmd = subparsers.add_parser(
        "get-supabase-row",
        help="Get one Supabase memory row.",
        parents=[shared, agent_session],
    )
    get_row_cmd.add_argument("--row-id", required=True, type=str)

    list_audit_cmd = subparsers.add_parser(
        "list-audit-logs",
        help="List audit logs for the rollout session.",
        parents=[shared, agent_session],
    )
    list_audit_cmd.add_argument("--action-type", type=str, default=None)
    list_audit_cmd.add_argument("--limit", type=int, default=None)

    get_audit_cmd = subparsers.add_parser(
        "get-audit-log",
        help="Get one audit log entry.",
        parents=[shared, agent_session],
    )
    get_audit_cmd.add_argument("--audit-id", required=True, type=str)

    subparsers.add_parser("session-summary", help="Show session progress and summary.", parents=[shared, agent_session])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = ServerFaultSupabaseEnvironment(data_root=args.data_root, state_root=args.state_root)

    try:
        if args.command == "list-scenarios":
            return _print_json({"status": "success", "data": env.list_scenarios()})

        if args.command in {"prepare-rollout", "create-session"}:
            session_id = getattr(args, "session_id", None) or os.getenv(SERVER_FAULT_SUPABASE_SESSION_ID_ENV, "").strip()
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
                    SERVER_FAULT_SUPABASE_SESSION_ID_ENV: session_id,
                    SERVER_FAULT_SUPABASE_STATE_ROOT_ENV: str(env.store.state_root),
                    SERVER_FAULT_SUPABASE_SCENARIO_ID_ENV: scenario_id,
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

        if args.command == "list-incidents":
            data = env.list_incidents(
                session_id,
                query=args.query,
                category=args.category,
                severity=args.severity,
                status=args.status,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-incident":
            data = env.get_incident(session_id, args.incident_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "screen-risk-incidents":
            categories = [item.strip() for item in args.categories.split(",") if item.strip()]
            statuses = [item.strip() for item in args.statuses.split(",") if item.strip()]
            severities = [item.strip() for item in args.severities.split(",") if item.strip()]
            data = env.screen_risk_incidents(
                session_id,
                categories=categories,
                statuses=statuses,
                severities=severities,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-attachments":
            data = env.list_attachments(session_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "read-attachment":
            data = env.read_attachment(session_id, args.attachment_path)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "remediate-incident":
            data = env.remediate_incident(
                session_id,
                args.incident_id,
                remediation_mode=args.remediation_mode,
                operator_note=args.operator_note,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "batch-remediate":
            incident_ids = [item.strip() for item in args.incident_ids.split(",") if item.strip()]
            data = env.batch_remediate(
                session_id,
                incident_ids,
                remediation_mode=args.remediation_mode,
                operator_note=args.operator_note,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "write-supabase-resolution":
            data = env.write_supabase_resolution(session_id, args.incident_id, table_name=args.table_name)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-supabase-rows":
            data = env.list_supabase_rows(
                session_id,
                table_name=args.table_name,
                incident_id=args.incident_id,
                limit=args.limit,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-supabase-row":
            data = env.get_supabase_row(session_id, args.row_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "list-audit-logs":
            data = env.list_audit_logs(session_id, action_type=args.action_type, limit=args.limit)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-audit-log":
            data = env.get_audit_log(session_id, args.audit_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "session-summary":
            return _print_json({"status": "success", "data": _agent_payload(env.session_summary(session_id))})

    except Exception as exc:
        return _print_json({"status": "error", "message": _agent_error_message(exc)}, exit_code=1)

    return _print_json({"status": "error", "message": f"Unknown command: {args.command}"}, exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
