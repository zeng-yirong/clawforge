"""CLI for security monitoring environment."""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from typing import Any

from .environment import SecurityMonitorEnvironment
from .repository import DatasetRepository
from .store import SessionStore

SECURITY_SESSION_ID_ENV = "SECURITY_SESSION_ID"
SECURITY_SCENARIO_ID_ENV = "SECURITY_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "intrusion_response"
_HIDDEN_HELP_MARKERS = ("prepare-rollout", "reset-rollout", "evaluate", "(create-session)", "(reset-session)", "==SUPPRESS==")


def _print_json(payload: dict[str, Any], *, exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


class SecurityArgumentParser(argparse.ArgumentParser):
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
    return f"sec-{_utc_stamp()}-{random.randint(1000, 9999)}"


def _resolve_bound_session_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "session_id", None)
    if explicit:
        return explicit

    env_value = os.getenv(SECURITY_SESSION_ID_ENV, "").strip()
    if env_value:
        return env_value

    raise ValueError(
        f"No active rollout session is bound. The trainer must set {SECURITY_SESSION_ID_ENV} "
        "before agent commands run."
    )


def _resolve_scenario_id(args: argparse.Namespace) -> str:
    scenario_id = getattr(args, "scenario_id", None)
    if scenario_id:
        return scenario_id

    env_value = os.getenv(SECURITY_SCENARIO_ID_ENV, "").strip()
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


def cmd_doors(parser: argparse.ArgumentParser) -> None:
    subparsers = parser.add_subparsers(dest="subcommand", help="Door commands")

    list_parser = subparsers.add_parser("list", help="List all doors")
    list_parser.add_argument("--verbose", action="store_true", help="Verbose output")

    lock_parser = subparsers.add_parser("lock", help="Lock a door")
    lock_parser.add_argument("door_id", help="Door ID to lock")

    unlock_parser = subparsers.add_parser("unlock", help="Unlock a door")
    unlock_parser.add_argument("door_id", help="Door ID to unlock")

    lock_all_parser = subparsers.add_parser("lock-all", help="Lock all doors")
    lock_all_parser.add_argument("--zone", help="Filter by zone ID")


def cmd_zones(parser: argparse.ArgumentParser) -> None:
    subparsers = parser.add_subparsers(dest="subcommand", help="Zone commands")

    list_parser = subparsers.add_parser("list", help="List all zones")

    arm_parser = subparsers.add_parser("arm", help="Arm a zone")
    arm_parser.add_argument("zone_id", help="Zone ID to arm")

    disarm_parser = subparsers.add_parser("disarm", help="Disarm a zone")
    disarm_parser.add_argument("zone_id", help="Zone ID to disarm")

    arm_all_parser = subparsers.add_parser("arm-all", help="Arm all zones")

    sensors_parser = subparsers.add_parser("sensors", help="Check zone sensors")
    sensors_parser.add_argument("zone_id", help="Zone ID to check")


def cmd_alerts(parser: argparse.ArgumentParser) -> None:
    subparsers = parser.add_subparsers(dest="subcommand", help="Alert commands")

    check_parser = subparsers.add_parser("check", help="Check for intrusion")

    create_parser = subparsers.add_parser("create", help="Create an alert")
    create_parser.add_argument("--type", required=True, help="Alert type")
    create_parser.add_argument("--zone", required=True, help="Zone ID")
    create_parser.add_argument("--description", required=True, help="Description")
    create_parser.add_argument("--severity", required=True, help="Severity")
    create_parser.add_argument("--source", required=True, help="Source")

    ack_parser = subparsers.add_parser("acknowledge", help="Acknowledge an alert")
    ack_parser.add_argument("alert_id", help="Alert ID")

    resolve_parser = subparsers.add_parser("resolve", help="Resolve an alert")
    resolve_parser.add_argument("alert_id", help="Alert ID")
    resolve_parser.add_argument("--resolution", required=True, help="Resolution")

    list_parser = subparsers.add_parser("list", help="List alerts")
    list_parser.add_argument("--status", help="Filter by status")


def cmd_emergency(parser: argparse.ArgumentParser) -> None:
    subparsers = parser.add_subparsers(dest="subcommand", help="Emergency commands")

    dial_parser = subparsers.add_parser("dial", help="Dial emergency")
    dial_parser.add_argument("--type", required=True, help="Call type (police/fire/ambulance)")
    dial_parser.add_argument("--description", required=True, help="Description")
    dial_parser.add_argument("--location", required=True, help="Location")

    list_parser = subparsers.add_parser("list", help="List emergency calls")
    list_parser.add_argument("--query", help="Search query")
    list_parser.add_argument("--call-type", help="Filter by call type")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--limit", type=int, default=10, help="Result limit")

    contacts_parser = subparsers.add_parser("contacts", help="Get emergency contacts")


def cmd_evidence(parser: argparse.ArgumentParser) -> None:
    subparsers = parser.add_subparsers(dest="subcommand", help="Evidence commands")

    save_parser = subparsers.add_parser("save", help="Save evidence")
    save_parser.add_argument("--type", required=True, help="Evidence type")
    save_parser.add_argument("--description", required=True, help="Description")
    save_parser.add_argument("--source", required=True, help="Source")
    save_parser.add_argument("--metadata", help="Metadata JSON")

    snapshot_parser = subparsers.add_parser("snapshot", help="Capture camera snapshot")
    snapshot_parser.add_argument("--camera", required=True, help="Camera ID")
    snapshot_parser.add_argument("--zone", required=True, help="Zone ID")

    clip_parser = subparsers.add_parser("clip", help="Capture motion clip")
    clip_parser.add_argument("--camera", required=True, help="Camera ID")
    clip_parser.add_argument("--zone", required=True, help="Zone ID")
    clip_parser.add_argument("--duration", type=int, default=30, help="Duration in seconds")


def cmd_notifications(parser: argparse.ArgumentParser) -> None:
    subparsers = parser.add_subparsers(dest="subcommand", help="Notification commands")

    create_parser = subparsers.add_parser("create", help="Create notification")
    create_parser.add_argument("--type", required=True, help="Notification type")
    create_parser.add_argument("--recipient", required=True, help="Recipient name")
    create_parser.add_argument("--contact", required=True, help="Recipient contact")
    create_parser.add_argument("--subject", required=True, help="Subject")
    create_parser.add_argument("--body", required=True, help="Body")
    create_parser.add_argument("--priority", default="normal", help="Priority")

    send_parser = subparsers.add_parser("send", help="Send notification")
    send_parser.add_argument("notification_id", help="Notification ID")

    compose_parser = subparsers.add_parser("compose", help="Compose intrusion notification")
    compose_parser.add_argument("--recipient", required=True, help="Recipient name")
    compose_parser.add_argument("--contact", required=True, help="Recipient contact")
    compose_parser.add_argument("--alert-id", required=True, help="Alert ID")

    list_parser = subparsers.add_parser("list", help="List pending notifications")


def build_parser() -> argparse.ArgumentParser:
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--data-root", type=str, default=None, help="Override the environment data directory.")
    shared.add_argument("--state-root", type=str, default=None, help="Override the session state directory.")

    agent_session = argparse.ArgumentParser(add_help=False)
    agent_session.add_argument("--session-id", type=str, default=None, help=argparse.SUPPRESS)

    parser = SecurityArgumentParser(description="Security monitoring training environment CLI.")
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
    prepare.add_argument("--overwrite", action="store_true")

    subparsers.add_parser(
        "reset-rollout",
        aliases=["reset-session"],
        help=argparse.SUPPRESS,
        parents=[shared, agent_session],
    )

    reset_parser = subparsers.add_parser("reset", help="Reset environment", parents=[shared, agent_session])

    status_parser = subparsers.add_parser("status", help="Get security status", parents=[shared, agent_session])

    doors_parser = subparsers.add_parser("doors", help="Door control commands", parents=[shared, agent_session])
    cmd_doors(doors_parser)

    zones_parser = subparsers.add_parser("zones", help="Zone management commands", parents=[shared, agent_session])
    cmd_zones(zones_parser)

    alerts_parser = subparsers.add_parser("alerts", help="Alert management commands", parents=[shared, agent_session])
    cmd_alerts(alerts_parser)

    emergency_parser = subparsers.add_parser("emergency", help="Emergency call commands", parents=[shared, agent_session])
    cmd_emergency(emergency_parser)

    evidence_parser = subparsers.add_parser("evidence", help="Evidence capture commands", parents=[shared, agent_session])
    cmd_evidence(evidence_parser)

    notifications_parser = subparsers.add_parser("notifications", help="Notification commands", parents=[shared, agent_session])
    cmd_notifications(notifications_parser)

    evaluate_parser = subparsers.add_parser("evaluate", help=argparse.SUPPRESS, parents=[shared, agent_session])

    closed_loop_parser = subparsers.add_parser("closed-loop", help="Run closed-loop response", parents=[shared, agent_session])

    info_parser = subparsers.add_parser("info", help="Show environment info", parents=[shared, agent_session])

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    
    repository = DatasetRepository(data_root=args.data_root) if args.data_root else None
    store = SessionStore(state_root=args.state_root) if args.state_root else None
    config = {"state_root": args.state_root} if args.state_root else None
    env = SecurityMonitorEnvironment(scenario_id=_resolve_scenario_id(args), repository=repository, store=store, config=config)

    try:
        if args.command == "list-scenarios":
            return _print_json({"status": "success", "data": env.repository.list_scenarios()})

        if args.command in {"prepare-rollout", "create-session"}:
            session_id = getattr(args, "session_id", None) or os.getenv(SECURITY_SESSION_ID_ENV, "").strip()
            session_id = session_id or _generate_session_id()
            scenario_id = _resolve_scenario_id(args)
            env.reset()
            env.store.create_session(session_id, env.store.load_session(env._current_session_id), overwrite=args.overwrite)
            payload = {
                "session_id": session_id,
                "scenario_id": scenario_id,
                "state_root": str(env.store.state_root),
            }
            if args.show_bindings:
                payload["bindings"] = {
                    SECURITY_SESSION_ID_ENV: session_id,
                    "SECURITY_STATE_ROOT": str(env.store.state_root),
                    SECURITY_SCENARIO_ID_ENV: scenario_id,
                }
            return _print_json({"status": "success", "data": payload})

        session_id = _resolve_bound_session_id(args)
        if session_id is None:
            return _print_json({"status": "error", "message": "Session ID could not be resolved"}, exit_code=1)

        env._current_session_id = session_id
        env._initialized = True

        if args.command in {"reset-rollout", "reset-session"}:
            data = env.reset()
            env.store.create_session(session_id, env.store.load_session(env._current_session_id), overwrite=True)
            return _print_json({"status": "success", "data": _agent_payload(data)})

        if args.command == "reset":
            data = env.reset()
            env.store.create_session(session_id, env.store.load_session(env._current_session_id), overwrite=True)
            return _print_json({"status": "success", "data": _agent_payload(data)})

        if args.command == "status":
            data = env.get_security_status()
            return _print_json({"status": "success", "data": data})

        if args.command == "doors":
            if args.subcommand == "list":
                result = env.execute_action("get_all_doors_status")
                return _print_json({"status": "success", "data": result})
            elif args.subcommand == "lock":
                result = env.execute_action("lock_door", door_id=args.door_id)
                return _print_json({"status": "success", "data": result})
            elif args.subcommand == "unlock":
                result = env.execute_action("unlock_door", door_id=args.door_id)
                return _print_json({"status": "success", "data": result})
            elif args.subcommand == "lock-all":
                result = env.execute_action("lock_all_doors", zone_id=args.zone)
                return _print_json({"status": "success", "data": result})

        if args.command == "zones":
            if args.subcommand == "list":
                session = env.get_state()
                zones = session.get("zones", {})
                return _print_json({"status": "success", "data": zones})
            elif args.subcommand == "arm":
                result = env.execute_action("arm_zone", zone_id=args.zone_id)
                return _print_json({"status": "success", "data": result})
            elif args.subcommand == "disarm":
                result = env.execute_action("disarm_zone", zone_id=args.zone_id)
                return _print_json({"status": "success", "data": result})
            elif args.subcommand == "arm-all":
                result = env.execute_action("arm_all_zones")
                return _print_json({"status": "success", "data": result})
            elif args.subcommand == "sensors":
                result = env.execute_action("check_zone_sensors", zone_id=args.zone_id)
                return _print_json({"status": "success", "data": result})

        if args.command == "alerts":
            if args.subcommand == "check":
                result = env.execute_action("check_intrusion_detected")
                return _print_json({"status": "success", "data": result})
            elif args.subcommand == "create":
                result = env.execute_action(
                    "create_alert",
                    alert_type=args.type,
                    zone_id=args.zone,
                    description=args.description,
                    severity=args.severity,
                    source=args.source
                )
                return _print_json({"status": "success", "data": result})
            elif args.subcommand == "acknowledge":
                result = env.execute_action("acknowledge_alert", alert_id=args.alert_id)
                return _print_json({"status": "success", "data": result})
            elif args.subcommand == "resolve":
                result = env.execute_action("resolve_alert", alert_id=args.alert_id, resolution=args.resolution)
                return _print_json({"status": "success", "data": result})
            elif args.subcommand == "list":
                session = env.get_state()
                alerts = session.get("alerts", [])
                if args.status:
                    alerts = [a for a in alerts if a.get("status") == args.status]
                return _print_json({"status": "success", "data": alerts})

        if args.command == "emergency":
            if args.subcommand == "dial":
                result = env.execute_action(
                    "dial_emergency",
                    call_type=args.type,
                    description=args.description,
                    location=args.location
                )
                return _print_json({"status": "success", "data": result})
            elif args.subcommand == "list":
                result = env.execute_action(
                    "list_emergency_calls",
                    query=args.query,
                    call_type=args.call_type,
                    status=args.status,
                    limit=args.limit
                )
                return _print_json({"status": "success", "data": result})
            elif args.subcommand == "contacts":
                result = env.execute_action("get_emergency_contacts")
                return _print_json({"status": "success", "data": result})

        if args.command == "evidence":
            metadata = {}
            if args.subcommand == "save" and args.metadata:
                metadata = json.loads(args.metadata)

            if args.subcommand == "save":
                result = env.execute_action(
                    "save_evidence",
                    evidence_type=args.type,
                    description=args.description,
                    source=args.source,
                    metadata=metadata
                )
                return _print_json({"status": "success", "data": result})
            elif args.subcommand == "snapshot":
                result = env.execute_action(
                    "capture_camera_snapshot",
                    camera_id=args.camera,
                    zone_id=args.zone
                )
                return _print_json({"status": "success", "data": result})
            elif args.subcommand == "clip":
                result = env.execute_action(
                    "capture_motion_clip",
                    camera_id=args.camera,
                    zone_id=args.zone,
                    duration_seconds=args.duration
                )
                return _print_json({"status": "success", "data": result})

        if args.command == "notifications":
            if args.subcommand == "create":
                result = env.execute_action(
                    "create_notification",
                    notification_type=args.type,
                    recipient_name=args.recipient,
                    recipient_contact=args.contact,
                    subject=args.subject,
                    body=args.body,
                    priority=args.priority
                )
                return _print_json({"status": "success", "data": result})
            elif args.subcommand == "send":
                result = env.execute_action("send_notification", notification_id=args.notification_id)
                return _print_json({"status": "success", "data": result})
            elif args.subcommand == "compose":
                result = env.execute_action(
                    "compose_intrusion_notification",
                    recipient_name=args.recipient,
                    recipient_contact=args.contact,
                    alert_id=args.alert_id
                )
                return _print_json({"status": "success", "data": result})
            elif args.subcommand == "list":
                result = env.execute_action("list_pending_notifications")
                return _print_json({"status": "success", "data": result})

        if args.command == "evaluate":
            result = env.evaluate_response()
            return _print_json({"status": "success", "data": result})

        if args.command == "closed-loop":
            result = env.run_closed_loop_response()
            return _print_json({"status": "success", "data": result})

        if args.command == "info":
            return _print_json({
                "status": "success",
                "data": {
                    "scenario_id": env.scenario_id,
                    "available_actions": env.get_available_actions()
                }
            })

    except Exception as exc:
        return _print_json({"status": "error", "message": _agent_error_message(exc)}, exit_code=1)

    return _print_json({"status": "error", "message": f"Unknown command: {args.command}"}, exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
