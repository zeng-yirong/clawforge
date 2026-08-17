from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from typing import Any

from .environment import SchedulingEnvironment

SCHEDULING_SESSION_ID_ENV = "SCHEDULING_SESSION_ID"
SCHEDULING_STATE_ROOT_ENV = "SCHEDULING_STATE_ROOT"
SCHEDULING_SCENARIO_ID_ENV = "SCHEDULING_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "device_scheduling"
_HIDDEN_HELP_MARKERS = ("(create-session)", "(reset-session)", "==SUPPRESS==")


def _print_json(payload: dict[str, Any], *, exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


class SchedulingArgumentParser(argparse.ArgumentParser):
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
    return f"sched-{_utc_stamp()}-{random.randint(1000, 9999)}"


def _resolve_bound_session_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "session_id", None)
    if explicit:
        return explicit

    env_value = os.getenv(SCHEDULING_SESSION_ID_ENV, "").strip()
    if env_value:
        return env_value

    raise ValueError(
        f"No active rollout session is bound. The trainer must set {SCHEDULING_SESSION_ID_ENV} "
        "before agent commands run."
    )


def _resolve_scenario_id(args: argparse.Namespace) -> str:
    scenario_id = getattr(args, "scenario_id", None)
    if scenario_id:
        return scenario_id

    env_value = os.getenv(SCHEDULING_SCENARIO_ID_ENV, "").strip()
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

    parser = SchedulingArgumentParser(description="Scheduling environment CLI.")
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

    list_devices = subparsers.add_parser("list-devices", help="List all devices.", parents=[shared, agent_session])
    list_devices.add_argument("--type", type=str, default=None)

    get_device = subparsers.add_parser("get-device", help="Get device status.", parents=[shared, agent_session])
    get_device.add_argument("--device-id", required=True, type=str)

    turn_on = subparsers.add_parser("turn-on-device", help="Turn on a device.", parents=[shared, agent_session])
    turn_on.add_argument("--device-id", required=True, type=str)

    turn_off = subparsers.add_parser("turn-off-device", help="Turn off a device.", parents=[shared, agent_session])
    turn_off.add_argument("--device-id", required=True, type=str)

    control_light = subparsers.add_parser("control-light", help="Control a light.", parents=[shared, agent_session])
    control_light.add_argument("--device-id", required=True, type=str)
    control_light.add_argument("--action", required=True, choices=["on", "off"])
    control_light.add_argument("--brightness", type=int, default=None)

    control_ac = subparsers.add_parser("control-ac", help="Control AC.", parents=[shared, agent_session])
    control_ac.add_argument("--device-id", required=True, type=str)
    control_ac.add_argument("--action", required=True, choices=["on", "off"])
    control_ac.add_argument("--temperature", type=float, default=None)
    control_ac.add_argument("--mode", type=str, default=None)

    control_humidifier = subparsers.add_parser("control-humidifier", help="Control humidifier.", parents=[shared, agent_session])
    control_humidifier.add_argument("--device-id", required=True, type=str)
    control_humidifier.add_argument("--action", required=True, choices=["on", "off"])
    control_humidifier.add_argument("--humidity", type=int, default=None)

    control_plug = subparsers.add_parser("control-plug", help="Control smart plug.", parents=[shared, agent_session])
    control_plug.add_argument("--device-id", required=True, type=str)
    control_plug.add_argument("--action", required=True, choices=["on", "off"])

    list_schedules = subparsers.add_parser("list-schedules", help="List all schedules.", parents=[shared, agent_session])
    list_schedules.add_argument("--enabled", type=str, default=None)

    get_schedule = subparsers.add_parser("get-schedule", help="Get schedule details.", parents=[shared, agent_session])
    get_schedule.add_argument("--schedule-id", required=True, type=str)

    create_schedule = subparsers.add_parser("create-schedule", help="Create a new schedule.", parents=[shared, agent_session])
    create_schedule.add_argument("--name", required=True, type=str)
    create_schedule.add_argument("--device-id", required=True, type=str)
    create_schedule.add_argument("--action", required=True, choices=["on", "off"])
    create_schedule.add_argument("--time", required=True, type=str)
    create_schedule.add_argument("--repeat", required=True, choices=["once", "daily", "weekly", "custom"])
    create_schedule.add_argument("--days", type=str, default=None)
    create_schedule.add_argument("--start", type=str, default=None)
    create_schedule.add_argument("--end", type=str, default=None)

    enable_schedule = subparsers.add_parser("enable-schedule", help="Enable a schedule.", parents=[shared, agent_session])
    enable_schedule.add_argument("--schedule-id", required=True, type=str)

    disable_schedule = subparsers.add_parser("disable-schedule", help="Disable a schedule.", parents=[shared, agent_session])
    disable_schedule.add_argument("--schedule-id", required=True, type=str)

    delete_schedule = subparsers.add_parser("delete-schedule", help="Delete a schedule.", parents=[shared, agent_session])
    delete_schedule.add_argument("--schedule-id", required=True, type=str)

    execute_tasks = subparsers.add_parser("execute-tasks", help="Execute scheduled tasks.", parents=[shared, agent_session])
    execute_tasks.add_argument("--time", type=str, default=None)

    upcoming_tasks = subparsers.add_parser("upcoming-tasks", help="Get upcoming tasks.", parents=[shared, agent_session])
    upcoming_tasks.add_argument("--limit", type=int, default=10)

    task_history = subparsers.add_parser("task-history", help="Get execution history.", parents=[shared, agent_session])
    task_history.add_argument("--schedule-id", type=str, default=None)
    task_history.add_argument("--limit", type=int, default=50)

    subparsers.add_parser("scheduling-status", help="Get scheduling status.", parents=[shared, agent_session])

    subparsers.add_parser("session-summary", help="Show session progress and summary.", parents=[shared, agent_session])

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = SchedulingEnvironment(scenario_id=_resolve_scenario_id(args))

    try:
        if args.command == "list-scenarios":
            return _print_json({"status": "success", "data": {"scenarios": [{"scenario_id": DEFAULT_SCENARIO_ID, "title": "Device Scheduling"}]}})

        if args.command in {"prepare-rollout", "create-session"}:
            session_id = getattr(args, "session_id", None) or os.getenv(SCHEDULING_SESSION_ID_ENV, "").strip()
            session_id = session_id or _generate_session_id()
            scenario_id = _resolve_scenario_id(args)
            env.reset()
            payload = {
                "session_id": env._current_session_id,
                "scenario_id": scenario_id,
                "state_root": str(env.store.state_root),
            }
            if args.show_bindings:
                payload["bindings"] = {
                    SCHEDULING_SESSION_ID_ENV: env._current_session_id,
                    SCHEDULING_STATE_ROOT_ENV: str(env.store.state_root),
                    SCHEDULING_SCENARIO_ID_ENV: scenario_id,
                }
            if args.show_task:
                payload["task"] = {"scenario_id": scenario_id, "task_prompt": "Manage device scheduling and automation"}
            return _print_json({"status": "success", "data": payload})

        session_id = _resolve_bound_session_id(args)

        if args.command in {"reset-rollout", "reset-session"}:
            env.reset()
            return _print_json({"status": "success", "data": {"session_id": env._current_session_id, "status": "reset"}})

        if args.command == "task":
            return _print_json({"status": "success", "data": {"scenario_id": env.scenario_id, "task_prompt": "Manage device scheduling and automation"}})

        if args.command == "list-devices":
            result = env.execute_action("get_all_devices", device_type=args.type)
            return _print_json({"status": "success", "data": result})

        if args.command == "get-device":
            result = env.execute_action("get_device_status", device_id=args.device_id)
            return _print_json({"status": "success", "data": result})

        if args.command == "turn-on-device":
            result = env.execute_action("turn_on_device", device_id=args.device_id)
            return _print_json({"status": "success", "data": result})

        if args.command == "turn-off-device":
            result = env.execute_action("turn_off_device", device_id=args.device_id)
            return _print_json({"status": "success", "data": result})

        if args.command == "control-light":
            result = env.execute_action("control_light", device_id=args.device_id, action=args.action, brightness=args.brightness)
            return _print_json({"status": "success", "data": result})

        if args.command == "control-ac":
            result = env.execute_action("control_ac", device_id=args.device_id, action=args.action, temperature=args.temperature, mode=args.mode)
            return _print_json({"status": "success", "data": result})

        if args.command == "control-humidifier":
            result = env.execute_action("control_humidifier", device_id=args.device_id, action=args.action, humidity_level=args.humidity)
            return _print_json({"status": "success", "data": result})

        if args.command == "control-plug":
            result = env.execute_action("control_smart_plug", device_id=args.device_id, action=args.action)
            return _print_json({"status": "success", "data": result})

        if args.command == "list-schedules":
            enabled_filter = None
            if args.enabled:
                enabled_filter = args.enabled.lower() == "true"
            result = env.execute_action("list_schedules", enabled=enabled_filter)
            return _print_json({"status": "success", "data": result})

        if args.command == "get-schedule":
            result = env.execute_action("get_schedule", schedule_id=args.schedule_id)
            return _print_json({"status": "success", "data": result})

        if args.command == "create-schedule":
            days_of_week = None
            if args.days:
                days_of_week = [int(d) for d in args.days.split(",")]
            result = env.execute_action(
                "create_schedule",
                schedule_name=args.name,
                device_id=args.device_id,
                action=args.action,
                time_spec=args.time,
                repeat_type=args.repeat,
                days_of_week=days_of_week,
                start_date=args.start,
                end_date=args.end
            )
            return _print_json({"status": "success", "data": result})

        if args.command == "enable-schedule":
            result = env.execute_action("enable_schedule", schedule_id=args.schedule_id)
            return _print_json({"status": "success", "data": result})

        if args.command == "disable-schedule":
            result = env.execute_action("disable_schedule", schedule_id=args.schedule_id)
            return _print_json({"status": "success", "data": result})

        if args.command == "delete-schedule":
            result = env.execute_action("delete_schedule", schedule_id=args.schedule_id)
            return _print_json({"status": "success", "data": result})

        if args.command == "execute-tasks":
            result = env.execute_action("execute_scheduled_tasks", current_time=args.time)
            return _print_json({"status": "success", "data": result})

        if args.command == "upcoming-tasks":
            result = env.execute_action("get_next_scheduled_tasks", limit=args.limit)
            return _print_json({"status": "success", "data": result})

        if args.command == "task-history":
            result = env.execute_action("get_task_execution_history", schedule_id=args.schedule_id, limit=args.limit)
            return _print_json({"status": "success", "data": result})

        if args.command == "scheduling-status":
            result = env.get_scheduling_status()
            return _print_json({"status": "success", "data": result})

        if args.command == "session-summary":
            result = env.session_summary()
            return _print_json({"status": "success", "data": result})

    except Exception as exc:
        return _print_json({"status": "error", "message": _agent_error_message(exc)}, exit_code=1)

    return _print_json({"status": "error", "message": f"Unknown command: {args.command}"}, exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
