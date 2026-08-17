from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .environment import ExpenseEnvironment

_HIDDEN_HELP_MARKERS = ("prepare-rollout", "reset-rollout", "evaluate", "==SUPPRESS==")


def _get_data_root() -> Path:
    return Path(__file__).parent / "data"


def _get_state_root() -> Path:
    default = Path.home() / ".expense_state"
    return Path(os.environ.get("EXPENSE_STATE_ROOT", default))


def _get_session_id() -> str | None:
    return os.environ.get("EXPENSE_SESSION_ID")


class ExpenseArgumentParser(argparse.ArgumentParser):
    def format_help(self) -> str:
        help_text = super().format_help()
        lines = [
            line
            for line in help_text.splitlines()
            if not any(marker in line for marker in _HIDDEN_HELP_MARKERS)
        ]
        return "\n".join(lines) + ("\n" if help_text.endswith("\n") else "")

    def exit(self, status=0, message=None):
        if message:
            print(json.dumps({"status": "error", "message": message}, ensure_ascii=False), file=sys.stderr)
        sys.exit(status)


def main():
    base_parser = ExpenseArgumentParser(add_help=False)
    base_parser.add_argument("--session-id", dest="session_id", default=None, help=argparse.SUPPRESS)

    main_parser = ExpenseArgumentParser(description="Expense Management CLI")
    sub = main_parser.add_subparsers(dest="command", metavar="")

    hidden = ExpenseArgumentParser(add_help=False)
    hidden.add_argument("--show-bindings", action="store_true")
    hidden.add_argument("--scenario-id", dest="scenario_id")
    hidden.add_argument("--session-id", dest="session_id", default=None, help=argparse.SUPPRESS)

    list_sc = sub.add_parser("list-scenarios", parents=[base_parser], help="List available scenarios")
    list_sc.set_defaults(func=lambda args, env: {"status": "success", "data": {"scenarios": env.repo.list_scenarios()}})

    prep = sub.add_parser("prepare-rollout", parents=[hidden], help=argparse.SUPPRESS)
    prep.set_defaults(func=lambda args, env: env.prepare_rollout(args.scenario_id, show_bindings=args.show_bindings))

    reset = sub.add_parser("reset-rollout", parents=[hidden], help=argparse.SUPPRESS)
    reset.set_defaults(func=lambda args, env: env.reset_rollout(args.session_id or _get_session_id()))

    load_pol = sub.add_parser("load-policy", parents=[base_parser], help="Load travel policy")
    load_pol.add_argument("--tier", default=None)
    load_pol.set_defaults(func=lambda args, env: _execute(env, args.session_id, "load_policy", tier=args.tier))

    calc_bud = sub.add_parser("calculate-budget", parents=[base_parser], help="Calculate expense budget")
    calc_bud.add_argument("--tier", default=None)
    calc_bud.add_argument("--destination", default=None)
    calc_bud.add_argument("--duration-days", dest="duration_days", type=int, default=None)
    calc_bud.set_defaults(func=lambda args, env: _execute(env, args.session_id, "calculate_budget", tier=args.tier, destination=args.destination, duration_days=args.duration_days))

    load_con = sub.add_parser("load-consumption", parents=[base_parser], help="Load consumption records")
    load_con.add_argument("--trip-id", dest="trip_id", required=True)
    load_con.set_defaults(func=lambda args, env: _execute(env, args.session_id, "load_consumption", trip_id=args.trip_id))

    gen_ana = sub.add_parser("generate-analysis", parents=[base_parser], help="Generate budget vs actual analysis")
    gen_ana.set_defaults(func=lambda args, env: _execute(env, args.session_id, "generate_analysis"))

    exp_rep = sub.add_parser("export-report", parents=[base_parser], help="Export expense report")
    exp_rep.set_defaults(func=lambda args, env: _execute(env, args.session_id, "export_report"))

    summary_p = sub.add_parser("session-summary", parents=[base_parser], help="Get session summary")
    summary_p.set_defaults(func=lambda args, env: {"status": "success", "data": env.get_session_summary(args.session_id or _get_session_id())})

    eval_p = sub.add_parser("evaluate", parents=[base_parser], help=argparse.SUPPRESS)
    eval_p.set_defaults(func=lambda args, env: {"status": "success", "data": env.get_reward(args.session_id or _get_session_id())})

    args = main_parser.parse_args()

    data_root = _get_data_root()
    state_root = _get_state_root()
    env = ExpenseEnvironment(data_root, state_root)

    if not args.command:
        main_parser.print_help()
        return

    try:
        result = args.func(args, env)
    except Exception as e:
        result = {"status": "error", "message": str(e)}

    print(json.dumps(result, ensure_ascii=False))


def _execute(env: ExpenseEnvironment, session_id: str | None, action_type: str, **kwargs) -> dict:
    sid = session_id or _get_session_id()
    if not sid:
        return {"status": "error", "message": "No session bound"}
    session = env.store.load_session(sid)
    if not session:
        return {"status": "error", "message": f"Session {sid} not found"}
    action_idx = session["meta"]["action_index"]
    result = env.execute_action(sid, action_type, action_idx, **kwargs)
    return {"status": "success", "data": result}


if __name__ == "__main__":
    main()
