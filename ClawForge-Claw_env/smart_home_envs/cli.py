from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from typing import Any

from .environment import SmartHomeEnvironment

SMART_HOME_SESSION_ID_ENV = "SMART_HOME_SESSION_ID"
SMART_HOME_STATE_ROOT_ENV = "SMART_HOME_STATE_ROOT"
SMART_HOME_SCENARIO_ID_ENV = "SMART_HOME_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "energy_aware_climate"
_HIDDEN_HELP_MARKERS = ("==SUPPRESS==",)


def _print_json(payload: dict[str, Any], *, exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


class SmartHomeArgumentParser(argparse.ArgumentParser):
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
    return f"smh-{_utc_stamp()}-{random.randint(1000, 9999)}"


def _resolve_bound_session_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "session_id", None)
    if explicit:
        return explicit

    env_value = os.getenv(SMART_HOME_SESSION_ID_ENV, "").strip()
    if env_value:
        return env_value

    raise ValueError(
        f"No active rollout session is bound. The trainer must set {SMART_HOME_SESSION_ID_ENV} "
        "before agent commands run."
    )


def _resolve_scenario_id(args: argparse.Namespace) -> str:
    scenario_id = getattr(args, "scenario_id", None)
    if scenario_id:
        return scenario_id

    env_value = os.getenv(SMART_HOME_SCENARIO_ID_ENV, "").strip()
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

    parser = SmartHomeArgumentParser(description="Smart home energy-aware climate control environment CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True, metavar="command")

    subparsers.add_parser("list-scenarios", help="List available scenarios.", parents=[shared])

    prepare = subparsers.add_parser(
        "prepare-rollout",
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
        help=argparse.SUPPRESS,
        parents=[shared, agent_session],
    )

    subparsers.add_parser("task", help="Show the task prompt and workspace summary.", parents=[shared, agent_session])

    get_weather = subparsers.add_parser("get-weather", help="Get current weather information.", parents=[shared, agent_session])
    get_weather.add_argument("--timestamp", type=str, default=None)

    analyze_weather_comfort = subparsers.add_parser("analyze-weather-comfort", help="Analyze weather comfort level.", parents=[shared, agent_session])
    analyze_weather_comfort.add_argument("--temperature", type=float, required=True)
    analyze_weather_comfort.add_argument("--humidity", type=float, required=True)

    get_weather_forecast = subparsers.add_parser("get-weather-forecast", help="Get weather forecast.", parents=[shared, agent_session])
    get_weather_forecast.add_argument("--hours-ahead", type=int, default=24)

    check_extreme_weather = subparsers.add_parser("check-extreme-weather", help="Check for extreme weather conditions.", parents=[shared, agent_session])

    get_electricity_rate = subparsers.add_parser("get-electricity-rate", help="Get current electricity rate.", parents=[shared, agent_session])
    get_electricity_rate.add_argument("--timestamp", type=str, default=None)

    get_daily_rate_schedule = subparsers.add_parser("get-daily-rate-schedule", help="Get daily electricity rate schedule.", parents=[shared, agent_session])

    get_optimal_window = subparsers.add_parser("get-optimal-window", help="Get optimal operation window for device.", parents=[shared, agent_session])
    get_optimal_window.add_argument("--duration-hours", type=float, required=True)
    get_optimal_window.add_argument("--preferred-start", type=str, default=None)

    check_cost_saving = subparsers.add_parser("check-cost-saving", help="Check cost saving opportunities.", parents=[shared, agent_session])
    check_cost_saving.add_argument("--device-type", type=str, required=True)
    check_cost_saving.add_argument("--current-setting", type=str, required=True)

    get_user_health = subparsers.add_parser("get-user-health", help="Get user health profile.", parents=[shared, agent_session])
    get_user_health.add_argument("--user-id", type=str, required=True)

    analyze_health_conflicts = subparsers.add_parser("analyze-health-conflicts", help="Analyze health-comfort conflicts.", parents=[shared, agent_session])
    analyze_health_conflicts.add_argument("--user-id", type=str, required=True)
    analyze_health_conflicts.add_argument("--current-temp", type=float, required=True)
    analyze_health_conflicts.add_argument("--current-humidity", type=float, required=True)

    get_health_recommendations = subparsers.add_parser("get-health-recommendations", help="Get health-based recommendations.", parents=[shared, agent_session])
    get_health_recommendations.add_argument("--user-id", type=str, required=True)

    check_health_alerts = subparsers.add_parser("check-health-alerts", help="Check health alerts.", parents=[shared, agent_session])
    check_health_alerts.add_argument("--user-id", type=str, required=True)
    check_health_alerts.add_argument("--current-temp", type=float, required=True)
    check_health_alerts.add_argument("--current-humidity", type=float, required=True)

    get_device_status = subparsers.add_parser("get-device-status", help="Get device status.", parents=[shared, agent_session])
    get_device_status.add_argument("--device-id", type=str, required=True)

    get_all_devices = subparsers.add_parser("get-all-devices", help="Get all devices.", parents=[shared, agent_session])

    get_devices_by_type = subparsers.add_parser("get-devices-by-type", help="Get devices by type.", parents=[shared, agent_session])
    get_devices_by_type.add_argument("--device-type", type=str, required=True)

    set_ac = subparsers.add_parser("set-air-conditioner", help="Set air conditioner settings.", parents=[shared, agent_session])
    set_ac.add_argument("--device-id", type=str, required=True)
    set_ac.add_argument("--temperature", type=float, required=True)
    set_ac.add_argument("--mode", type=str, default="auto")
    set_ac.add_argument("--fan-speed", type=str, default="auto")

    set_humidifier = subparsers.add_parser("set-humidifier", help="Set humidifier settings.", parents=[shared, agent_session])
    set_humidifier.add_argument("--device-id", type=str, required=True)
    set_humidifier.add_argument("--humidity-level", type=int, required=True)
    set_humidifier.add_argument("--mode", type=str, default="auto")

    set_smart_plug = subparsers.add_parser("set-smart-plug", help="Set smart plug state.", parents=[shared, agent_session])
    set_smart_plug.add_argument("--device-id", type=str, required=True)
    set_smart_plug.add_argument("--power-state", type=lambda x: x.lower() == "true", required=True)

    turn_off = subparsers.add_parser("turn-off-device", help="Turn off a device.", parents=[shared, agent_session])
    turn_off.add_argument("--device-id", type=str, required=True)

    calculate_power = subparsers.add_parser("calculate-power-consumption", help="Calculate device power consumption.", parents=[shared, agent_session])
    calculate_power.add_argument("--device-id", type=str, required=True)
    calculate_power.add_argument("--hours", type=float, required=True)

    get_recommended_temp = subparsers.add_parser("get-recommended-temperature", help="Get recommended temperature based on conditions.", parents=[shared, agent_session])
    get_recommended_temp.add_argument("--current-temp", type=float, default=None)
    get_recommended_temp.add_argument("--current-humidity", type=float, default=None)
    get_recommended_temp.add_argument("--user-health-priority", action="store_true")

    subparsers.add_parser("session-summary", help="Show session progress and summary.", parents=[shared, agent_session])

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = SmartHomeEnvironment(data_root=args.data_root, state_root=args.state_root)

    try:
        if args.command == "list-scenarios":
            return _print_json({"status": "success", "data": env.list_scenarios()})

        if args.command == "prepare-rollout":
            session_id = getattr(args, "session_id", None) or os.getenv(SMART_HOME_SESSION_ID_ENV, "").strip()
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
                    SMART_HOME_SESSION_ID_ENV: session_id,
                    SMART_HOME_STATE_ROOT_ENV: str(env.store.state_root),
                    SMART_HOME_SCENARIO_ID_ENV: scenario_id,
                }
            if args.show_task:
                payload["task"] = _agent_payload(env.get_task(session_id))
            return _print_json({"status": "success", "data": payload})

        session_id = _resolve_bound_session_id(args)

        if args.command == "reset-rollout":
            data = env.reset_session(session_id)
            return _print_json({"status": "success", "data": _agent_payload(data)})

        if args.command == "task":
            return _print_json({"status": "success", "data": _agent_payload(env.get_task(session_id))})

        if args.command == "get-weather":
            data = env.get_weather(session_id, timestamp=args.timestamp)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "analyze-weather-comfort":
            data = env.analyze_weather_comfort(session_id, args.temperature, args.humidity)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-weather-forecast":
            data = env.get_weather_forecast(session_id, hours_ahead=args.hours_ahead)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "check-extreme-weather":
            data = env.check_extreme_weather(session_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-electricity-rate":
            data = env.get_electricity_rate(session_id, timestamp=args.timestamp)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-daily-rate-schedule":
            data = env.get_daily_rate_schedule(session_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-optimal-window":
            data = env.get_optimal_operation_window(session_id, args.duration_hours, args.preferred_start)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "check-cost-saving":
            current_setting = json.loads(args.current_setting) if isinstance(args.current_setting, str) else args.current_setting
            data = env.check_cost_saving_opportunity(session_id, args.device_type, current_setting)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-user-health":
            data = env.get_user_health_profile(session_id, args.user_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "analyze-health-conflicts":
            data = env.analyze_health_comfort_conflicts(session_id, args.user_id, args.current_temp, args.current_humidity)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-health-recommendations":
            data = env.get_health_based_recommendations(session_id, args.user_id, {})
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "check-health-alerts":
            data = env.check_health_alerts(session_id, args.user_id, args.current_temp, args.current_humidity)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-device-status":
            data = env.get_device_status(session_id, args.device_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-all-devices":
            data = env.get_all_devices(session_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-devices-by-type":
            data = env.get_devices_by_type(session_id, args.device_type)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "set-air-conditioner":
            data = env.set_air_conditioner(session_id, args.device_id, args.temperature, args.mode, args.fan_speed)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "set-humidifier":
            data = env.set_humidifier(session_id, args.device_id, args.humidity_level, args.mode)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "set-smart-plug":
            data = env.set_smart_plug(session_id, args.device_id, args.power_state)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "turn-off-device":
            data = env.turn_off_device(session_id, args.device_id)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "calculate-power-consumption":
            data = env.calculate_device_power_consumption(session_id, args.device_id, args.hours)
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "get-recommended-temperature":
            data = env.calculate_recommended_temperature(
                session_id,
                current_temp=args.current_temp,
                current_humidity=args.current_humidity,
                user_health_priority=args.user_health_priority,
            )
            return _print_json({"status": "success", "data": data["data"]})

        if args.command == "session-summary":
            return _print_json({"status": "success", "data": _agent_payload(env.session_summary(session_id))})

    except Exception as exc:
        return _print_json({"status": "error", "message": _agent_error_message(exc)}, exit_code=1)

    return _print_json({"status": "error", "message": f"Unknown command: {args.command}"}, exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
