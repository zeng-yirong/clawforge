"""CLI for sensor monitoring environment."""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from typing import Any

from .environment import SensorMonitorEnvironment

SENSOR_SESSION_ID_ENV = "SENSOR_SESSION_ID"
SENSOR_SCENARIO_ID_ENV = "SENSOR_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "sensor_monitoring"
_HIDDEN_HELP_MARKERS = ("prepare-rollout", "reset-rollout", "evaluate", "(create-session)", "(reset-session)", "==SUPPRESS==")


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _generate_session_id() -> str:
    return f"se-{_utc_stamp()}-{random.randint(1000, 9999)}"


def _print_json(payload: dict[str, Any], *, exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


class SensorArgumentParser(argparse.ArgumentParser):
    """Custom argument parser for sensor monitoring CLI."""

    def format_help(self) -> str:
        help_text = super().format_help()
        lines = [
            line
            for line in help_text.splitlines()
            if not any(marker in line for marker in _HIDDEN_HELP_MARKERS)
        ]
        return "\n".join(lines) + ("\n" if help_text.endswith("\n") else "")


def _resolve_bound_session_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "session_id", None)
    if explicit:
        return explicit

    env_value = os.getenv(SENSOR_SESSION_ID_ENV, "").strip()
    if env_value:
        return env_value

    raise ValueError(
        f"No active rollout session is bound. The trainer must set {SENSOR_SESSION_ID_ENV} "
        "before agent commands run."
    )


def _resolve_scenario_id(args: argparse.Namespace) -> str:
    scenario_id = getattr(args, "scenario_id", None)
    if scenario_id:
        return scenario_id

    env_value = os.getenv(SENSOR_SCENARIO_ID_ENV, "").strip()
    if env_value:
        return env_value

    return DEFAULT_SCENARIO_ID


def _resolve_state_root(args: argparse.Namespace) -> str | None:
    return getattr(args, "state_root", None)


def build_parser() -> argparse.ArgumentParser:
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--data-root", type=str, default=None, help="Override the environment data directory.")
    shared.add_argument("--state-root", type=str, default=None, help="Override the session state directory.")

    agent_session = argparse.ArgumentParser(add_help=False)
    agent_session.add_argument("--session-id", type=str, default=None, help=argparse.SUPPRESS)

    parser = SensorArgumentParser(
        description="Sensor Monitoring Environment CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    prepare_parser = subparsers.add_parser(
        "prepare-rollout",
        aliases=["create-session"],
        help=argparse.SUPPRESS,
        parents=[shared],
    )
    prepare_parser.add_argument("--session-id", type=str, default=None, help=argparse.SUPPRESS)
    prepare_parser.add_argument("--scenario-id", type=str, default=None)
    prepare_parser.add_argument("--show-bindings", action="store_true")
    prepare_parser.add_argument("--overwrite", action="store_true")

    subparsers.add_parser(
        "reset-rollout",
        aliases=["reset-session"],
        help=argparse.SUPPRESS,
        parents=[shared, agent_session],
    )

    reset_parser = subparsers.add_parser("reset", help="Reset environment", parents=[shared])
    reset_parser.add_argument("--scenario-id", type=str, default=None)

    sensors_parser = subparsers.add_parser("sensors", help="Sensor data commands", parents=[shared, agent_session])
    sensors_subparsers = sensors_parser.add_subparsers(dest="subcommand", help="Sensor commands")
    list_parser = sensors_subparsers.add_parser("list", help="List all sensors")
    list_parser.add_argument("--type", help="Filter by sensor type")
    list_parser.add_argument("--location", help="Filter by location ID")
    read_parser = sensors_subparsers.add_parser("read", help="Read sensor data")
    read_parser.add_argument("sensor_id", help="Sensor ID to read")
    read_parser.add_argument("--timestamp", help="Timestamp for historical data")
    sensors_subparsers.add_parser("thresholds", help="Get sensor thresholds").add_argument("sensor_id", help="Sensor ID")
    st_parser = sensors_subparsers.add_parser("set-threshold", help="Set sensor threshold")
    st_parser.add_argument("sensor_id", help="Sensor ID")
    st_parser.add_argument("low", type=float, help="Low threshold")
    st_parser.add_argument("high", type=float, help="High threshold")
    stats_parser = sensors_subparsers.add_parser("stats", help="Get sensor statistics")
    stats_parser.add_argument("sensor_id", help="Sensor ID")
    stats_parser.add_argument("--start", required=True, help="Start time")
    stats_parser.add_argument("--end", required=True, help="End time")

    monitoring_parser = subparsers.add_parser("monitoring", help="Monitoring commands", parents=[shared, agent_session])
    monitoring_subparsers = monitoring_parser.add_subparsers(dest="subcommand", help="Monitoring commands")
    check_parser = monitoring_subparsers.add_parser("check", help="Check for anomalies")
    check_parser.add_argument("--sensor-id", help="Sensor ID to check")
    check_parser.add_argument("--severity", help="Filter by severity")
    monitoring_subparsers.add_parser("acknowledge", help="Acknowledge anomaly").add_argument("anomaly_id", help="Anomaly ID")
    res_parser = monitoring_subparsers.add_parser("resolve", help="Resolve anomaly")
    res_parser.add_argument("anomaly_id", help="Anomaly ID")
    res_parser.add_argument("--resolution", required=True, help="Resolution notes")
    monitoring_subparsers.add_parser("summary", help="Get monitoring summary")

    alerts_parser = subparsers.add_parser("alerts", help="Alert management commands", parents=[shared, agent_session])
    alerts_subparsers = alerts_parser.add_subparsers(dest="subcommand", help="Alert commands")
    create_alert = alerts_subparsers.add_parser("create", help="Create an alert")
    create_alert.add_argument("--type", required=True, help="Alert type")
    create_alert.add_argument("--severity", required=True, help="Severity")
    create_alert.add_argument("--title", required=True, help="Title")
    create_alert.add_argument("--description", required=True, help="Description")
    create_alert.add_argument("--sensor-id", required=True, help="Sensor ID")
    create_alert.add_argument("--location-id", required=True, help="Location ID")
    create_alert.add_argument("--anomaly-id", help="Linked anomaly ID")
    alerts_subparsers.add_parser("acknowledge", help="Acknowledge alert").add_argument("alert_id", help="Alert ID")
    res_alert = alerts_subparsers.add_parser("resolve", help="Resolve alert")
    res_alert.add_argument("alert_id", help="Alert ID")
    res_alert.add_argument("--resolution", required=True, help="Resolution")
    list_alerts = alerts_subparsers.add_parser("list", help="List alerts")
    list_alerts.add_argument("--status", help="Filter by status")
    list_alerts.add_argument("--severity", help="Filter by severity")
    list_alerts.add_argument("--type", help="Filter by type")
    list_alerts.add_argument("--limit", type=int, help="Result limit")
    active_alerts = alerts_subparsers.add_parser("active", help="Get active alerts")
    active_alerts.add_argument("--severity", help="Filter by severity")
    active_alerts.add_argument("--type", help="Filter by type")

    reports_parser = subparsers.add_parser("reports", help="Report generation commands", parents=[shared, agent_session])
    reports_subparsers = reports_parser.add_subparsers(dest="subcommand", help="Report commands")
    hourly_rep = reports_subparsers.add_parser("hourly", help="Generate hourly report")
    hourly_rep.add_argument("--location", help="Location ID")
    hourly_rep.add_argument("--type", help="Sensor type")
    daily_rep = reports_subparsers.add_parser("daily", help="Generate daily report")
    daily_rep.add_argument("--location", help="Location ID")
    daily_rep.add_argument("--type", help="Sensor type")
    monthly_rep = reports_subparsers.add_parser("monthly", help="Generate monthly report")
    monthly_rep.add_argument("--location", help="Location ID")
    monthly_rep.add_argument("--type", help="Sensor type")
    anomaly_rep = reports_subparsers.add_parser("anomaly", help="Generate anomaly report")
    anomaly_rep.add_argument("--start", help="Start time")
    anomaly_rep.add_argument("--end", help="End time")
    anomaly_rep.add_argument("--severity", help="Severity filter")
    energy_rep = reports_subparsers.add_parser("energy", help="Generate energy report")
    energy_rep.add_argument("--location", help="Location ID")
    energy_rep.add_argument("--start", help="Start time")
    energy_rep.add_argument("--end", help="End time")

    trends_parser = subparsers.add_parser("trends", help="Trend analysis commands", parents=[shared, agent_session])
    trends_subparsers = trends_parser.add_subparsers(dest="subcommand", help="Trend commands")
    analyze = trends_subparsers.add_parser("analyze", help="Analyze trend for sensor")
    analyze.add_argument("sensor_id", help="Sensor ID")
    analyze.add_argument("--start", help="Start time")
    analyze.add_argument("--end", help="End time")
    mov_avg = trends_subparsers.add_parser("moving-average", help="Calculate moving average")
    mov_avg.add_argument("sensor_id", help="Sensor ID")
    mov_avg.add_argument("--window", type=int, default=5, help="Window size")
    mov_avg.add_argument("--start", help="Start time")
    mov_avg.add_argument("--end", help="End time")
    season = trends_subparsers.add_parser("seasonality", help="Detect seasonality")
    season.add_argument("sensor_id", help="Sensor ID")
    season.add_argument("--period", type=int, default=24, help="Expected period in hours")
    trend_sum = trends_subparsers.add_parser("summary", help="Get trend summary")
    trend_sum.add_argument("--location", help="Location ID")
    trend_sum.add_argument("--type", help="Sensor type")

    notifications_parser = subparsers.add_parser("notifications", help="Notification commands", parents=[shared, agent_session])
    notif_subparsers = notifications_parser.add_subparsers(dest="subcommand", help="Notification commands")
    create_notif = notif_subparsers.add_parser("create", help="Create notification")
    create_notif.add_argument("--type", required=True, help="Notification type")
    create_notif.add_argument("--recipient", required=True, help="Recipient name")
    create_notif.add_argument("--contact", required=True, help="Recipient contact")
    create_notif.add_argument("--subject", required=True, help="Subject")
    create_notif.add_argument("--body", required=True, help="Body")
    create_notif.add_argument("--priority", default="normal", help="Priority")
    create_notif.add_argument("--linked-alerts", help="Comma-separated alert IDs")
    notif_subparsers.add_parser("send", help="Send notification").add_argument("notification_id", help="Notification ID")
    compose = notif_subparsers.add_parser("compose-anomaly", help="Compose anomaly alert notification")
    compose.add_argument("--recipient", required=True, help="Recipient name")
    compose.add_argument("--contact", required=True, help="Recipient contact")
    compose.add_argument("--anomaly-id", required=True, help="Anomaly ID")
    list_notif = notif_subparsers.add_parser("list", help="List notifications")
    list_notif.add_argument("--status", help="Filter by status")
    list_notif.add_argument("--type", help="Filter by type")
    list_notif.add_argument("--priority", help="Filter by priority")
    list_notif.add_argument("--limit", type=int, help="Result limit")
    notif_subparsers.add_parser("stats", help="Get notification statistics")

    subparsers.add_parser("evaluate", help=argparse.SUPPRESS, parents=[shared, agent_session])
    subparsers.add_parser("info", help="Show environment info", parents=[shared, agent_session])

    return parser


def _run_sensors(args: argparse.Namespace, env: SensorMonitorEnvironment) -> int:
    env.reset()
    if args.subcommand == "list":
        result = env.execute_action("read_all_sensors_current", sensor_type=args.type, location_id=args.location)
    elif args.subcommand == "read":
        result = env.execute_action("read_sensor_data", sensor_id=args.sensor_id, timestamp=args.timestamp)
    elif args.subcommand == "thresholds":
        result = env.execute_action("get_sensor_thresholds", sensor_id=args.sensor_id)
    elif args.subcommand == "set-threshold":
        result = env.execute_action("set_sensor_threshold", sensor_id=args.sensor_id, threshold_low=args.low, threshold_high=args.high)
    elif args.subcommand == "stats":
        result = env.execute_action("get_sensor_stats", sensor_id=args.sensor_id, start_time=args.start, end_time=args.end)
    else:
        return 1
    _print_json(result)
    return 0


def _run_monitoring(args: argparse.Namespace, env: SensorMonitorEnvironment) -> int:
    env.reset()
    if args.subcommand == "check":
        result = env.execute_action("check_anomalies", sensor_id=args.sensor_id, severity=args.severity)
    elif args.subcommand == "acknowledge":
        result = env.execute_action("acknowledge_anomaly", anomaly_id=args.anomaly_id)
    elif args.subcommand == "resolve":
        result = env.execute_action("resolve_anomaly", anomaly_id=args.anomaly_id, resolution=args.resolution)
    elif args.subcommand == "summary":
        result = env.execute_action("get_monitoring_summary")
    else:
        return 1
    _print_json(result)
    return 0


def _run_alerts(args: argparse.Namespace, env: SensorMonitorEnvironment) -> int:
    env.reset()
    linked_alert_ids = None
    if args.subcommand == "create" and args.linked_alerts:
        linked_alert_ids = args.linked_alerts.split(",")

    if args.subcommand == "create":
        result = env.execute_action(
            "create_alert",
            alert_type=args.type,
            severity=args.severity,
            title=args.title,
            description=args.description,
            sensor_id=args.sensor_id,
            location_id=args.location_id,
            linked_anomaly_id=args.anomaly_id
        )
    elif args.subcommand == "acknowledge":
        result = env.execute_action("acknowledge_alert", alert_id=args.alert_id)
    elif args.subcommand == "resolve":
        result = env.execute_action("resolve_alert", alert_id=args.alert_id, resolution=args.resolution)
    elif args.subcommand == "list":
        result = env.execute_action(
            "list_alerts",
            status=args.status,
            severity=args.severity,
            alert_type=args.type,
            limit=args.limit
        )
    elif args.subcommand == "active":
        result = env.execute_action("get_active_alerts", severity=args.severity, alert_type=args.type)
    else:
        return 1
    _print_json(result)
    return 0


def _run_reports(args: argparse.Namespace, env: SensorMonitorEnvironment) -> int:
    env.reset()
    if args.subcommand == "hourly":
        result = env.execute_action("generate_hourly_report", location_id=args.location, sensor_type=args.type)
    elif args.subcommand == "daily":
        result = env.execute_action("generate_daily_report", location_id=args.location, sensor_type=args.type)
    elif args.subcommand == "monthly":
        result = env.execute_action("generate_monthly_report", location_id=args.location, sensor_type=args.type)
    elif args.subcommand == "anomaly":
        result = env.execute_action("generate_anomaly_report", start_time=args.start, end_time=args.end, severity=args.severity)
    elif args.subcommand == "energy":
        result = env.execute_action("generate_energy_report", location_id=args.location, start_time=args.start, end_time=args.end)
    else:
        return 1
    _print_json(result)
    return 0


def _run_trends(args: argparse.Namespace, env: SensorMonitorEnvironment) -> int:
    env.reset()
    if args.subcommand == "analyze":
        result = env.execute_action("analyze_trend", sensor_id=args.sensor_id, start_time=args.start, end_time=args.end)
    elif args.subcommand == "moving-average":
        result = env.execute_action(
            "calculate_moving_average",
            sensor_id=args.sensor_id,
            window_size=args.window,
            start_time=args.start,
            end_time=args.end
        )
    elif args.subcommand == "seasonality":
        result = env.execute_action("detect_seasonality", sensor_id=args.sensor_id, expected_period_hours=args.period)
    elif args.subcommand == "summary":
        result = env.execute_action("get_trend_summary", location_id=args.location, sensor_type=args.type)
    else:
        return 1
    _print_json(result)
    return 0


def _run_notifications(args: argparse.Namespace, env: SensorMonitorEnvironment) -> int:
    env.reset()
    linked_alert_ids = None
    if args.subcommand == "create" and args.linked_alerts:
        linked_alert_ids = args.linked_alerts.split(",")

    if args.subcommand == "create":
        result = env.execute_action(
            "create_notification",
            notification_type=args.type,
            recipient_name=args.recipient,
            recipient_contact=args.contact,
            subject=args.subject,
            body=args.body,
            priority=args.priority,
            linked_alert_ids=linked_alert_ids
        )
    elif args.subcommand == "send":
        result = env.execute_action("send_notification", notification_id=args.notification_id)
    elif args.subcommand == "compose-anomaly":
        result = env.execute_action(
            "compose_anomaly_alert_notification",
            recipient_name=args.recipient,
            recipient_contact=args.contact,
            anomaly_id=args.anomaly_id
        )
    elif args.subcommand == "list":
        result = env.execute_action(
            "list_notifications",
            status=args.status,
            notification_type=args.type,
            priority=args.priority,
            limit=args.limit
        )
    elif args.subcommand == "stats":
        result = env.execute_action("get_notification_stats")
    else:
        return 1
    _print_json(result)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    state_root = _resolve_state_root(args)
    scenario_id = _resolve_scenario_id(args)
    env = SensorMonitorEnvironment(
        scenario_id=scenario_id,
        config={"state_root": state_root} if state_root else None
    )

    try:
        if args.command in {"prepare-rollout", "create-session"}:
            session_id = getattr(args, "session_id", None) or os.getenv(SENSOR_SESSION_ID_ENV, "").strip()
            session_id = session_id or _generate_session_id()
            scenario_id = _resolve_scenario_id(args)
            env.reset()
            payload = {
                "session_id": env._current_session_id,
                "scenario_id": scenario_id,
                "state_root": str(env.store.state_root),
            }
            if getattr(args, "show_bindings", False):
                payload["bindings"] = {
                    SENSOR_SESSION_ID_ENV: env._current_session_id,
                    "SENSOR_STATE_ROOT": str(env.store.state_root),
                    SENSOR_SCENARIO_ID_ENV: scenario_id,
                }
            return _print_json({"status": "success", "data": payload})

        session_id = _resolve_bound_session_id(args)

        if args.command in {"reset-rollout", "reset-session"}:
            env.reset()
            return _print_json({"status": "success", "data": {"session_id": env._current_session_id}})
        elif args.command == "reset":
            env.reset()
            return _print_json({"status": "success", "data": {"session_id": env._current_session_id}})
        elif args.command == "sensors":
            return _run_sensors(args, env)
        elif args.command == "monitoring":
            return _run_monitoring(args, env)
        elif args.command == "alerts":
            return _run_alerts(args, env)
        elif args.command == "reports":
            return _run_reports(args, env)
        elif args.command == "trends":
            return _run_trends(args, env)
        elif args.command == "notifications":
            return _run_notifications(args, env)
        elif args.command == "evaluate":
            env.reset()
            return _print_json(env.evaluate_session())
        elif args.command == "info":
            env.reset()
            return _print_json({
                "scenario_id": env.scenario_id,
                "available_actions": env.get_available_actions()
            })
        else:
            parser.print_help()
            return 1
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
