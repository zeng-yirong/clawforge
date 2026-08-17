from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .environment import NaviEnvironment

_HIDDEN_HELP_MARKERS = ("prepare-rollout", "reset-rollout", "evaluate", "==SUPPRESS==")


def _get_data_root() -> Path:
    return Path(__file__).parent / "data"


def _get_state_root() -> Path:
    default = Path.home() / ".car_navi_state"
    return Path(os.environ.get("CAR_NAVI_STATE_ROOT", default))


def _get_session_id() -> str | None:
    return os.environ.get("CAR_NAVI_SESSION_ID")


class NaviArgumentParser(argparse.ArgumentParser):
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
    base_parser = NaviArgumentParser(add_help=False)
    base_parser.add_argument("--session-id", dest="session_id", default=None, help=argparse.SUPPRESS)

    main_parser = NaviArgumentParser(description="Car Navigation CLI")
    sub = main_parser.add_subparsers(dest="command", metavar="")

    hidden = NaviArgumentParser(add_help=False)
    hidden.add_argument("--show-bindings", action="store_true")
    hidden.add_argument("--scenario-id", dest="scenario_id")
    hidden.add_argument("--session-id", dest="session_id", default=None, help=argparse.SUPPRESS)

    list_sc = sub.add_parser("list-scenarios", parents=[base_parser], help="List available scenarios")
    list_sc.set_defaults(func=lambda args, env: {"status": "success", "data": {"scenarios": env.repo.list_scenarios()}})

    prep = sub.add_parser("prepare-rollout", parents=[hidden], help=argparse.SUPPRESS)
    prep.set_defaults(func=lambda args, env: env.prepare_rollout(args.scenario_id, show_bindings=args.show_bindings))

    reset = sub.add_parser("reset-rollout", parents=[hidden], help=argparse.SUPPRESS)
    reset.set_defaults(func=lambda args, env: env.reset_rollout(args.session_id or _get_session_id()))

    search_p = sub.add_parser("search-poi", parents=[base_parser], help="Search for POIs")
    search_p.add_argument("--category", default=None)
    search_p.add_argument("--keyword", default=None)
    search_p.set_defaults(func=lambda args, env: _execute(env, args.session_id, "search_poi", category=args.category, keyword=args.keyword))

    start_p = sub.add_parser("start-nav", parents=[base_parser], help="Start navigation to a destination")
    start_p.add_argument("--poi-id", dest="poi_id", required=True)
    start_p.set_defaults(func=lambda args, env: _execute(env, args.session_id, "start_navigation", poi_id=args.poi_id))

    add_wp = sub.add_parser("add-waypoint", parents=[base_parser], help="Add a waypoint")
    add_wp.add_argument("--poi-id", dest="poi_id", required=True)
    add_wp.set_defaults(func=lambda args, env: _execute(env, args.session_id, "add_waypoint", poi_id=args.poi_id))

    rem_wp = sub.add_parser("remove-waypoint", parents=[base_parser], help="Remove a waypoint")
    rem_wp.add_argument("--waypoint-index", dest="waypoint_index", type=int, default=0)
    rem_wp.set_defaults(func=lambda args, env: _execute(env, args.session_id, "remove_waypoint", waypoint_index=args.waypoint_index))

    route_p = sub.add_parser("route-preference", parents=[base_parser], help="Set route preference")
    route_p.add_argument("--preference", default="fastest")
    route_p.set_defaults(func=lambda args, env: _execute(env, args.session_id, "route_preference", preference=args.preference))

    reroute_p = sub.add_parser("reroute", parents=[base_parser], help="Recalculate route")
    reroute_p.set_defaults(func=lambda args, env: _execute(env, args.session_id, "reroute"))

    traffic_p = sub.add_parser("traffic", parents=[base_parser], help="Query traffic information")
    traffic_p.add_argument("--query-type", dest="query_type", default=None)
    traffic_p.set_defaults(func=lambda args, env: _execute(env, args.session_id, "traffic_query", query_type=args.query_type))

    charge_p = sub.add_parser("charging-plan", parents=[base_parser], help="Plan EV charging")
    charge_p.add_argument("--target-charge", dest="target_charge", type=float, default=80)
    charge_p.add_argument("--max-stops", dest="max_stops", type=int, default=3)
    charge_p.set_defaults(func=lambda args, env: _execute(env, args.session_id, "charging_plan", target_charge=args.target_charge, max_stops=args.max_stops))

    arrive_wp = sub.add_parser("arrive-waypoint", parents=[base_parser], help="Confirm arrival at waypoint")
    arrive_wp.add_argument("--waypoint-index", dest="waypoint_index", type=int, default=0)
    arrive_wp.set_defaults(func=lambda args, env: _execute(env, args.session_id, "arrive_waypoint", waypoint_index=args.waypoint_index))

    arrive_dest = sub.add_parser("arrive-destination", parents=[base_parser], help="Confirm arrival at destination")
    arrive_dest.set_defaults(func=lambda args, env: _execute(env, args.session_id, "arrive_destination"))

    cancel_p = sub.add_parser("cancel-nav", parents=[base_parser], help="Cancel navigation")
    cancel_p.set_defaults(func=lambda args, env: _execute(env, args.session_id, "cancel_navigation"))

    summary_p = sub.add_parser("session-summary", parents=[base_parser], help="Get session summary")
    summary_p.set_defaults(func=lambda args, env: {"status": "success", "data": env.get_session_summary(args.session_id or _get_session_id())})

    eval_p = sub.add_parser("evaluate", parents=[base_parser], help=argparse.SUPPRESS)
    eval_p.set_defaults(func=lambda args, env: {"status": "success", "data": env.get_reward(args.session_id or _get_session_id())})

    args = main_parser.parse_args()

    data_root = _get_data_root()
    state_root = _get_state_root()
    env = NaviEnvironment(data_root, state_root)

    if not args.command:
        main_parser.print_help()
        return

    try:
        result = args.func(args, env)
    except Exception as e:
        result = {"status": "error", "message": str(e)}

    print(json.dumps(result, ensure_ascii=False))


def _execute(env: NaviEnvironment, session_id: str | None, action_type: str, **kwargs) -> dict:
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
