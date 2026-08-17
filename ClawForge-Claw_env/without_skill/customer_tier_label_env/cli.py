from __future__ import annotations

import argparse
import os
import sys

from without_skill._shared.cli_utils import HiddenCommandArgumentParser, agent_error_message, agent_payload, generate_session_id, print_json, resolve_bound_session_id, resolve_scenario_id
from .environment import CustomerTierLabelEnvironment


SESSION_ENV = "CUSTOMER_TIER_LABEL_SESSION_ID"
STATE_ENV = "CUSTOMER_TIER_LABEL_STATE_ROOT"
SCENARIO_ENV = "CUSTOMER_TIER_LABEL_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "customer_tier_labeling_q2_2026"


def build_parser() -> argparse.ArgumentParser:
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--data-root", type=str, default=None)
    shared.add_argument("--state-root", type=str, default=None)
    agent_session = argparse.ArgumentParser(add_help=False)
    agent_session.add_argument("--session-id", type=str, default=None, help=argparse.SUPPRESS)
    parser = HiddenCommandArgumentParser(description="Customer tier label training environment CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list-scenarios", parents=[shared])
    prepare = subparsers.add_parser("prepare-rollout", aliases=["create-session"], parents=[shared], help=argparse.SUPPRESS)
    prepare.add_argument("--session-id", type=str, default=None, help=argparse.SUPPRESS)
    prepare.add_argument("--scenario-id", type=str, default=None)
    prepare.add_argument("--show-bindings", action="store_true")
    prepare.add_argument("--show-task", action="store_true")
    prepare.add_argument("--overwrite", action="store_true")
    subparsers.add_parser("reset-rollout", aliases=["reset-session"], parents=[shared, agent_session], help=argparse.SUPPRESS)
    subparsers.add_parser("task", parents=[shared, agent_session])
    list_customers_cmd = subparsers.add_parser("list-customers", parents=[shared, agent_session])
    list_customers_cmd.add_argument("--query", type=str, default="")
    list_customers_cmd.add_argument("--industry", type=str, default=None)
    list_customers_cmd.add_argument("--risk-level", type=str, default=None)
    list_customers_cmd.add_argument("--limit", type=int, default=None)
    get_customer_cmd = subparsers.add_parser("get-customer", parents=[shared, agent_session])
    get_customer_cmd.add_argument("--customer-id", required=True, type=str)
    metrics_cmd = subparsers.add_parser("get-customer-metrics", parents=[shared, agent_session])
    metrics_cmd.add_argument("--customer-id", required=True, type=str)
    read_attachment_cmd = subparsers.add_parser("read-attachment", parents=[shared, agent_session])
    read_attachment_cmd.add_argument("--attachment-path", required=True, type=str)
    update_cmd = subparsers.add_parser("update-customer-labels", parents=[shared, agent_session])
    update_cmd.add_argument("--customer-id", required=True, type=str)
    subparsers.add_parser("list-update-logs", parents=[shared, agent_session])
    get_update_cmd = subparsers.add_parser("get-update-log", parents=[shared, agent_session])
    get_update_cmd.add_argument("--update-id", required=True, type=str)
    subparsers.add_parser("session-summary", parents=[shared, agent_session])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = CustomerTierLabelEnvironment(data_root=args.data_root, state_root=args.state_root)
    try:
        if args.command == "list-scenarios":
            return print_json({"status": "success", "data": env.list_scenarios()})
        if args.command in {"prepare-rollout", "create-session"}:
            session_id = getattr(args, "session_id", None) or os.getenv(SESSION_ENV, "").strip() or generate_session_id("tier-label")
            scenario_id = resolve_scenario_id(args, SCENARIO_ENV, DEFAULT_SCENARIO_ID)
            env.create_session(session_id, scenario_id, overwrite=args.overwrite)
            payload = {"session_id": session_id, "scenario_id": scenario_id, "state_root": str(env.store.state_root)}
            if args.show_bindings:
                payload["bindings"] = {SESSION_ENV: session_id, STATE_ENV: str(env.store.state_root), SCENARIO_ENV: scenario_id}
            if args.show_task:
                payload["task"] = agent_payload(env.get_task(session_id))
            return print_json({"status": "success", "data": payload})
        session_id = resolve_bound_session_id(args, SESSION_ENV)
        if args.command in {"reset-rollout", "reset-session"}:
            return print_json({"status": "success", "data": agent_payload(env.reset_session(session_id))})
        if args.command == "task":
            return print_json({"status": "success", "data": agent_payload(env.view_task(session_id)["data"])})
        if args.command == "list-customers":
            return print_json({"status": "success", "data": env.list_customers(session_id, query=args.query, industry=args.industry, risk_level=args.risk_level, limit=args.limit)["data"]})
        if args.command == "get-customer":
            return print_json({"status": "success", "data": env.get_customer(session_id, args.customer_id)["data"]})
        if args.command == "get-customer-metrics":
            return print_json({"status": "success", "data": env.get_customer_metrics(session_id, args.customer_id)["data"]})
        if args.command == "read-attachment":
            return print_json({"status": "success", "data": env.read_attachment(session_id, args.attachment_path)["data"]})
        if args.command == "update-customer-labels":
            return print_json({"status": "success", "data": env.update_customer_labels(session_id, args.customer_id)["data"]})
        if args.command == "list-update-logs":
            return print_json({"status": "success", "data": env.list_update_logs(session_id)["data"]})
        if args.command == "get-update-log":
            return print_json({"status": "success", "data": env.get_update_log(session_id, args.update_id)["data"]})
        if args.command == "session-summary":
            return print_json({"status": "success", "data": agent_payload(env.session_summary(session_id))})
    except Exception as exc:
        return print_json({"status": "error", "message": agent_error_message(exc)}, exit_code=1)
    return print_json({"status": "error", "message": f"Unknown command: {args.command}"}, exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
