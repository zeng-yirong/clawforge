from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from typing import Any

from .environment import ExcelDataEnvironment

EXCEL_DATA_SESSION_ID_ENV = "EXCEL_DATA_SESSION_ID"
EXCEL_DATA_SCENARIO_ID_ENV = "EXCEL_DATA_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "sales_data_processing"
_HIDDEN_HELP_MARKERS = ("(create-session)", "(reset-session)", "==SUPPRESS==")


def _print_json(payload: dict[str, Any], *, exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


class ExcelDataArgumentParser(argparse.ArgumentParser):
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
    return f"ed-{_utc_stamp()}-{random.randint(1000, 9999)}"


def _resolve_bound_session_id(args: argparse.Namespace) -> str:
    explicit = getattr(args, "session_id", None)
    if explicit:
        return explicit

    env_value = os.getenv(EXCEL_DATA_SESSION_ID_ENV, "").strip()
    if env_value:
        return env_value

    raise ValueError(
        f"No active rollout session is bound. The trainer must set {EXCEL_DATA_SESSION_ID_ENV} "
        "before agent commands run."
    )


def _resolve_scenario_id(args: argparse.Namespace) -> str:
    scenario_id = getattr(args, "scenario_id", None)
    if scenario_id:
        return scenario_id

    env_value = os.getenv(EXCEL_DATA_SCENARIO_ID_ENV, "").strip()
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

    parser = ExcelDataArgumentParser(description="Excel-data training environment CLI.")
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

    list_raw = subparsers.add_parser("list-raw-data", help="List available raw datasets.", parents=[shared, agent_session])
    
    read_raw = subparsers.add_parser("read-raw-data", help="Read raw dataset info.", parents=[shared, agent_session])
    read_raw.add_argument("--data-id", required=True, type=str)

    deduplicate = subparsers.add_parser("deduplicate", help="Remove duplicate transactions.", parents=[shared, agent_session])
    deduplicate.add_argument("--data-id", required=True, type=str)
    deduplicate.add_argument("--key-column", type=str, default="transaction_id")

    fill_missing = subparsers.add_parser("fill-missing", help="Fill missing customer data.", parents=[shared, agent_session])
    fill_missing.add_argument("--data-id", required=True, type=str)

    subparsers.add_parser("get-cleaned-data", help="Get cleaned deduplicated data.", parents=[shared, agent_session])
    subparsers.add_parser("get-data-summary", help="Get data summary.", parents=[shared, agent_session])

    create_pivot = subparsers.add_parser("create-pivot", help="Create a custom pivot table.", parents=[shared, agent_session])
    create_pivot.add_argument("--row-dimensions", required=True, type=str, help="Comma-separated dimension columns")
    create_pivot.add_argument("--value-column", required=True, type=str)
    create_pivot.add_argument("--aggregation", type=str, default="sum")

    subparsers.add_parser("create-pivot-category-region", help="Create pivot by category and region.", parents=[shared, agent_session])
    subparsers.add_parser("create-pivot-salesperson", help="Create pivot by salesperson.", parents=[shared, agent_session])
    subparsers.add_parser("create-pivot-city", help="Create pivot by city.", parents=[shared, agent_session])
    subparsers.add_parser("get-pivots", help="List all created pivot tables.", parents=[shared, agent_session])

    create_bar = subparsers.add_parser("create-bar-chart", help="Create a bar chart.", parents=[shared, agent_session])
    create_bar.add_argument("--chart-id", required=True, type=str)
    create_bar.add_argument("--title", required=True, type=str)
    create_bar.add_argument("--x-axis", required=True, type=str)
    create_bar.add_argument("--y-axis", required=True, type=str)
    create_bar.add_argument("--aggregation", type=str, default="sum")

    create_pie = subparsers.add_parser("create-pie-chart", help="Create a pie chart.", parents=[shared, agent_session])
    create_pie.add_argument("--chart-id", required=True, type=str)
    create_pie.add_argument("--title", required=True, type=str)
    create_pie.add_argument("--label-column", required=True, type=str)
    create_pie.add_argument("--value-column", required=True, type=str)
    create_pie.add_argument("--aggregation", type=str, default="sum")

    create_line = subparsers.add_parser("create-line-chart", help="Create a line chart.", parents=[shared, agent_session])
    create_line.add_argument("--chart-id", required=True, type=str)
    create_line.add_argument("--title", required=True, type=str)
    create_line.add_argument("--x-axis", required=True, type=str)
    create_line.add_argument("--y-axis", required=True, type=str)
    create_line.add_argument("--aggregation", type=str, default="sum")

    create_col = subparsers.add_parser("create-column-chart", help="Create a column chart.", parents=[shared, agent_session])
    create_col.add_argument("--chart-id", required=True, type=str)
    create_col.add_argument("--title", required=True, type=str)
    create_col.add_argument("--x-axis", required=True, type=str)
    create_col.add_argument("--y-axis", required=True, type=str)
    create_col.add_argument("--aggregation", type=str, default="sum")

    subparsers.add_parser("get-charts", help="List all created charts.", parents=[shared, agent_session])
    subparsers.add_parser("get-chart", help="Get a specific chart.", parents=[shared, agent_session])
    subparsers.add_parser("get-chart-details", help="Get chart details.", parents=[shared, agent_session])

    create_formula = subparsers.add_parser("create-formula", help="Create a calculation formula.", parents=[shared, agent_session])
    create_formula.add_argument("--name", required=True, type=str)
    create_formula.add_argument("--expression", required=True, type=str)
    create_formula.add_argument("--description", type=str, default="")

    subparsers.add_parser("create-total-revenue", help="Create total revenue formula.", parents=[shared, agent_session])
    subparsers.add_parser("create-average-order", help="Create average order value formula.", parents=[shared, agent_session])
    subparsers.add_parser("create-total-transactions", help="Create total transactions formula.", parents=[shared, agent_session])
    subparsers.add_parser("get-formulas", help="List all created formulas.", parents=[shared, agent_session])

    subparsers.add_parser(
        "session-summary",
        help="Show session progress and summary.",
        parents=[shared, agent_session],
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = ExcelDataEnvironment(data_root=args.data_root, state_root=args.state_root)

    try:
        if args.command == "list-scenarios":
            return _print_json({"status": "success", "data": env.list_scenarios()})
        if args.command in {"prepare-rollout", "create-session"}:
            session_id = getattr(args, "session_id", None) or os.getenv(EXCEL_DATA_SESSION_ID_ENV, "").strip()
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
                    EXCEL_DATA_SESSION_ID_ENV: session_id,
                    "EXCEL_DATA_STATE_ROOT": str(env.store.state_root),
                    EXCEL_DATA_SCENARIO_ID_ENV: scenario_id,
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
        if args.command == "list-raw-data":
            data = env.list_raw_datasets(session_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "read-raw-data":
            data = env.read_raw_dataset(session_id, args.data_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "deduplicate":
            data = env.deduplicate(session_id, args.data_id, args.key_column)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "fill-missing":
            data = env.fill_missing(session_id, args.data_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "get-cleaned-data":
            data = env.get_cleaned_data(session_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "get-data-summary":
            data = env.get_data_summary(session_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "create-pivot":
            dims = [d.strip() for d in args.row_dimensions.split(",")]
            data = env.create_pivot(session_id, dims, args.value_column, args.aggregation)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "create-pivot-category-region":
            data = env.create_pivot_category_region(session_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "create-pivot-salesperson":
            data = env.create_pivot_salesperson(session_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "create-pivot-city":
            data = env.create_pivot_city(session_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "get-pivots":
            data = env.get_all_pivots(session_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "create-bar-chart":
            data = env.create_bar_chart(session_id, args.chart_id, args.title, args.x_axis, args.y_axis, args.aggregation)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "create-pie-chart":
            data = env.create_pie_chart(session_id, args.chart_id, args.title, args.label_column, args.value_column, args.aggregation)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "create-line-chart":
            data = env.create_line_chart(session_id, args.chart_id, args.title, args.x_axis, args.y_axis, args.aggregation)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "create-column-chart":
            data = env.create_column_chart(session_id, args.chart_id, args.title, args.x_axis, args.y_axis, args.aggregation)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "get-charts":
            data = env.get_all_charts(session_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "get-chart":
            data = env.get_chart(session_id, args.chart_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "create-formula":
            data = env.create_formula(session_id, args.name, args.expression, args.description)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "create-total-revenue":
            data = env.create_total_revenue(session_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "create-average-order":
            data = env.create_average_order_value(session_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "create-total-transactions":
            data = env.create_total_transactions(session_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "get-formulas":
            data = env.get_all_formulas(session_id)
            return _print_json({"status": "success", "data": data["data"]})
        if args.command == "session-summary":
            return _print_json({"status": "success", "data": _agent_payload(env.session_summary(session_id))})
    except Exception as exc:
        return _print_json({"status": "error", "message": _agent_error_message(exc)}, exit_code=1)

    return _print_json({"status": "error", "message": f"Unknown command: {args.command}"}, exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
