from __future__ import annotations

import argparse
import os
import sys

from without_skill._shared.cli_utils import HiddenCommandArgumentParser, agent_error_message, agent_payload, generate_session_id, print_json, resolve_bound_session_id, resolve_scenario_id
from .environment import OnboardingAssetAccessEnvironment


SESSION_ENV = "ONBOARDING_ASSET_ACCESS_SESSION_ID"
STATE_ENV = "ONBOARDING_ASSET_ACCESS_STATE_ROOT"
SCENARIO_ENV = "ONBOARDING_ASSET_ACCESS_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "onboarding_asset_access_q2_2026"


def build_parser() -> argparse.ArgumentParser:
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--data-root", default=None)
    shared.add_argument("--state-root", default=None)
    agent_session = argparse.ArgumentParser(add_help=False)
    agent_session.add_argument("--session-id", default=None, help=argparse.SUPPRESS)
    parser = HiddenCommandArgumentParser(description="Onboarding asset access environment CLI.")
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
    lc = subparsers.add_parser("list-contracts", parents=[shared, agent_session]); lc.add_argument("--status", default=None)
    gc = subparsers.add_parser("get-contract", parents=[shared, agent_session]); gc.add_argument("--employee-id", required=True)
    em = subparsers.add_parser("create-email-profile", parents=[shared, agent_session]); em.add_argument("--employee-id", required=True)
    sa = subparsers.add_parser("assign-system-access", parents=[shared, agent_session]); sa.add_argument("--employee-id", required=True); sa.add_argument("--pack-id", required=True)
    ae = subparsers.add_parser("allocate-equipment", parents=[shared, agent_session]); ae.add_argument("--employee-id", required=True); ae.add_argument("--asset-tag", required=True)
    wm = subparsers.add_parser("post-welcome-message", parents=[shared, agent_session]); wm.add_argument("--employee-id", required=True)
    subparsers.add_parser("session-summary", parents=[shared, agent_session])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = OnboardingAssetAccessEnvironment(data_root=args.data_root, state_root=args.state_root)
    try:
        if args.command == "list-scenarios":
            return print_json({"status": "success", "data": env.list_scenarios()})
        if args.command in {"prepare-rollout", "create-session"}:
            session_id = getattr(args, "session_id", None) or os.getenv(SESSION_ENV, "").strip() or generate_session_id("onboard")
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
        if args.command == "list-contracts":
            return print_json({"status": "success", "data": env.list_contracts(session_id, status=args.status)["data"]})
        if args.command == "get-contract":
            return print_json({"status": "success", "data": env.get_contract(session_id, args.employee_id)["data"]})
        if args.command == "create-email-profile":
            return print_json({"status": "success", "data": env.create_email_profile(session_id, args.employee_id)["data"]})
        if args.command == "assign-system-access":
            return print_json({"status": "success", "data": env.assign_system_access(session_id, args.employee_id, args.pack_id)["data"]})
        if args.command == "allocate-equipment":
            return print_json({"status": "success", "data": env.allocate_equipment(session_id, args.employee_id, args.asset_tag)["data"]})
        if args.command == "post-welcome-message":
            return print_json({"status": "success", "data": env.post_welcome_message(session_id, args.employee_id)["data"]})
        if args.command == "session-summary":
            return print_json({"status": "success", "data": agent_payload(env.session_summary(session_id))})
    except Exception as exc:
        return print_json({"status": "error", "message": agent_error_message(exc)}, exit_code=1)
    return print_json({"status": "error", "message": f"Unknown command: {args.command}"}, exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
