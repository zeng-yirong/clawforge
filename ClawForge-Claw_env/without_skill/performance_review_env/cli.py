from __future__ import annotations

import argparse
import os
import sys

from without_skill._shared.cli_utils import HiddenCommandArgumentParser, agent_error_message, agent_payload, generate_session_id, print_json, resolve_bound_session_id, resolve_scenario_id
from .environment import PerformanceReviewEnvironment


SESSION_ENV = "PERFORMANCE_REVIEW_SESSION_ID"
STATE_ENV = "PERFORMANCE_REVIEW_STATE_ROOT"
SCENARIO_ENV = "PERFORMANCE_REVIEW_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "performance_review_engineering_q2_2026"


def build_parser() -> argparse.ArgumentParser:
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--data-root", default=None)
    shared.add_argument("--state-root", default=None)
    agent_session = argparse.ArgumentParser(add_help=False)
    agent_session.add_argument("--session-id", default=None, help=argparse.SUPPRESS)
    parser = HiddenCommandArgumentParser(description="Performance review environment CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list-scenarios", parents=[shared])
    prepare = subparsers.add_parser("prepare-rollout", aliases=["create-session"], parents=[shared], help=argparse.SUPPRESS)
    prepare.add_argument("--session-id", default=None, help=argparse.SUPPRESS)
    prepare.add_argument("--scenario-id", default=None)
    prepare.add_argument("--show-bindings", action="store_true")
    prepare.add_argument("--show-task", action="store_true")
    prepare.add_argument("--overwrite", action="store_true")
    subparsers.add_parser("reset-rollout", aliases=["reset-session"], parents=[shared, agent_session], help=argparse.SUPPRESS)
    subparsers.add_parser("task", parents=[shared, agent_session])
    list_emp = subparsers.add_parser("list-employees", parents=[shared, agent_session])
    list_emp.add_argument("--department", default=None)
    list_emp.add_argument("--limit", type=int, default=None)
    get_emp = subparsers.add_parser("get-employee", parents=[shared, agent_session])
    get_emp.add_argument("--employee-id", required=True)
    out_cmd = subparsers.add_parser("get-output-ledger", parents=[shared, agent_session])
    out_cmd.add_argument("--employee-id", required=True)
    rule_cmd = subparsers.add_parser("get-scoring-rule", parents=[shared, agent_session])
    rule_cmd.add_argument("--role-code", required=True)
    gen_cmd = subparsers.add_parser("generate-performance-profile", parents=[shared, agent_session])
    gen_cmd.add_argument("--employee-id", required=True)
    subparsers.add_parser("list-performance-profiles", parents=[shared, agent_session])
    get_prof = subparsers.add_parser("get-performance-profile", parents=[shared, agent_session])
    get_prof.add_argument("--profile-id", required=True)
    subparsers.add_parser("session-summary", parents=[shared, agent_session])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = PerformanceReviewEnvironment(data_root=args.data_root, state_root=args.state_root)
    try:
        if args.command == "list-scenarios":
            return print_json({"status": "success", "data": env.list_scenarios()})
        if args.command in {"prepare-rollout", "create-session"}:
            session_id = getattr(args, "session_id", None) or os.getenv(SESSION_ENV, "").strip() or generate_session_id("perf-review")
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
        if args.command == "list-employees":
            return print_json({"status": "success", "data": env.list_employees(session_id, department=args.department, limit=args.limit)["data"]})
        if args.command == "get-employee":
            return print_json({"status": "success", "data": env.get_employee(session_id, args.employee_id)["data"]})
        if args.command == "get-output-ledger":
            return print_json({"status": "success", "data": env.get_output_ledger(session_id, args.employee_id)["data"]})
        if args.command == "get-scoring-rule":
            return print_json({"status": "success", "data": env.get_scoring_rule(session_id, args.role_code)["data"]})
        if args.command == "generate-performance-profile":
            return print_json({"status": "success", "data": env.generate_performance_profile(session_id, args.employee_id)["data"]})
        if args.command == "list-performance-profiles":
            return print_json({"status": "success", "data": env.list_performance_profiles(session_id)["data"]})
        if args.command == "get-performance-profile":
            return print_json({"status": "success", "data": env.get_performance_profile(session_id, args.profile_id)["data"]})
        if args.command == "session-summary":
            return print_json({"status": "success", "data": agent_payload(env.session_summary(session_id))})
    except Exception as exc:
        return print_json({"status": "error", "message": agent_error_message(exc)}, exit_code=1)
    return print_json({"status": "error", "message": f"Unknown command: {args.command}"}, exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
