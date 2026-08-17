from __future__ import annotations

import argparse
import os
import sys

from without_skill._shared.cli_utils import HiddenCommandArgumentParser, agent_error_message, agent_payload, generate_session_id, parse_csv_list, print_json, resolve_bound_session_id, resolve_scenario_id
from .environment import ExperimentDiffRecordEnvironment


SESSION_ENV = "EXPERIMENT_DIFF_RECORD_SESSION_ID"
STATE_ENV = "EXPERIMENT_DIFF_RECORD_STATE_ROOT"
SCENARIO_ENV = "EXPERIMENT_DIFF_RECORD_SCENARIO_ID"
DEFAULT_SCENARIO_ID = "experiment_diff_record_q2_2026"


def build_parser() -> argparse.ArgumentParser:
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--data-root", default=None)
    shared.add_argument("--state-root", default=None)
    agent_session = argparse.ArgumentParser(add_help=False)
    agent_session.add_argument("--session-id", default=None, help=argparse.SUPPRESS)
    parser = HiddenCommandArgumentParser(description="Experiment diff record environment CLI.")
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
    subparsers.add_parser("list-experiment-batches", parents=[shared, agent_session])
    get_batch = subparsers.add_parser("get-batch", parents=[shared, agent_session])
    get_batch.add_argument("--batch-id", required=True)
    gen = subparsers.add_parser("generate-diff-record", parents=[shared, agent_session])
    gen.add_argument("--batch-ids", required=True)
    subparsers.add_parser("list-records", parents=[shared, agent_session])
    get_record = subparsers.add_parser("get-record", parents=[shared, agent_session])
    get_record.add_argument("--record-id", required=True)
    subparsers.add_parser("session-summary", parents=[shared, agent_session])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = ExperimentDiffRecordEnvironment(data_root=args.data_root, state_root=args.state_root)
    try:
        if args.command == "list-scenarios":
            return print_json({"status": "success", "data": env.list_scenarios()})
        if args.command in {"prepare-rollout", "create-session"}:
            session_id = getattr(args, "session_id", None) or os.getenv(SESSION_ENV, "").strip() or generate_session_id("exp-diff")
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
        if args.command == "list-experiment-batches":
            return print_json({"status": "success", "data": env.list_experiment_batches(session_id)["data"]})
        if args.command == "get-batch":
            return print_json({"status": "success", "data": env.get_batch(session_id, args.batch_id)["data"]})
        if args.command == "generate-diff-record":
            return print_json({"status": "success", "data": env.generate_diff_record(session_id, batch_ids=parse_csv_list(args.batch_ids))["data"]})
        if args.command == "list-records":
            return print_json({"status": "success", "data": env.list_records(session_id)["data"]})
        if args.command == "get-record":
            return print_json({"status": "success", "data": env.get_record(session_id, args.record_id)["data"]})
        if args.command == "session-summary":
            return print_json({"status": "success", "data": agent_payload(env.session_summary(session_id))})
    except Exception as exc:
        return print_json({"status": "error", "message": agent_error_message(exc)}, exit_code=1)
    return print_json({"status": "error", "message": f"Unknown command: {args.command}"}, exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
