from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .environment import ItineraryEnvironment

_HIDDEN_HELP_MARKERS = ("prepare-rollout", "reset-rollout", "evaluate", "==SUPPRESS==")


def _get_data_root() -> Path:
    return Path(__file__).parent / "data"


def _get_state_root() -> Path:
    default = Path.home() / ".itinerary_state"
    return Path(os.environ.get("ITINERARY_STATE_ROOT", default))


def _get_session_id() -> str | None:
    return os.environ.get("ITINERARY_SESSION_ID")


class ItineraryArgumentParser(argparse.ArgumentParser):
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
    base_parser = ItineraryArgumentParser(add_help=False)
    base_parser.add_argument("--session-id", dest="session_id", default=None, help=argparse.SUPPRESS)

    main_parser = ItineraryArgumentParser(description="Itinerary Planning CLI")
    sub = main_parser.add_subparsers(dest="command", metavar="")

    hidden = ItineraryArgumentParser(add_help=False)
    hidden.add_argument("--show-bindings", action="store_true")
    hidden.add_argument("--scenario-id", dest="scenario_id")
    hidden.add_argument("--session-id", dest="session_id", default=None, help=argparse.SUPPRESS)

    list_sc = sub.add_parser("list-scenarios", parents=[base_parser], help="List available scenarios")
    list_sc.set_defaults(func=lambda args, env: {"status": "success", "data": {"scenarios": env.repo.list_scenarios()}})

    prep = sub.add_parser("prepare-rollout", parents=[hidden], help=argparse.SUPPRESS)
    prep.set_defaults(func=lambda args, env: env.prepare_rollout(args.scenario_id, show_bindings=args.show_bindings))

    reset = sub.add_parser("reset-rollout", parents=[hidden], help=argparse.SUPPRESS)
    reset.set_defaults(func=lambda args, env: env.reset_rollout(args.session_id or _get_session_id()))

    list_cities = sub.add_parser("list-cities", parents=[base_parser], help="List all cities")
    list_cities.set_defaults(func=lambda args, env: _execute(env, args.session_id, "load_cities"))

    load_city = sub.add_parser("load-city", parents=[base_parser], help="Load a specific city")
    load_city.add_argument("--city-id", dest="city_id", required=True)
    load_city.set_defaults(func=lambda args, env: _execute(env, args.session_id, "load_cities", city_id=args.city_id))

    search_routes = sub.add_parser("search-routes", parents=[base_parser], help="Search routes between cities")
    search_routes.add_argument("--origin", required=True)
    search_routes.add_argument("--destination", required=True)
    search_routes.set_defaults(func=lambda args, env: _execute(env, args.session_id, "search_routes", origin=args.origin, destination=args.destination))

    compare_t = sub.add_parser("compare-transport", parents=[base_parser], help="Compare transport options")
    compare_t.add_argument("--route-result", dest="route_result", required=True, type=json.loads)
    compare_t.set_defaults(func=lambda args, env: _execute(env, args.session_id, "compare_transport", route_result=args.route_result))

    plan_transfer = sub.add_parser("plan-transfer", parents=[base_parser], help="Plan multi-stop transfer")
    plan_transfer.add_argument("--origin", required=True)
    plan_transfer.add_argument("--destination", required=True)
    plan_transfer.add_argument("--waypoints", default="", dest="waypoints")
    plan_transfer.set_defaults(func=lambda args, env: _execute(env, args.session_id, "plan_transfer", origin=args.origin, destination=args.destination, waypoints=args.waypoints.split(",") if args.waypoints else []))

    gen_itin = sub.add_parser("generate-itinerary", parents=[base_parser], help="Generate detailed itinerary")
    gen_itin.add_argument("--routes", required=True, type=json.loads, dest="routes")
    gen_itin.add_argument("--preference", default="balanced")
    gen_itin.set_defaults(func=lambda args, env: _execute(env, args.session_id, "generate_itinerary", routes=args.routes, preferences={"route_preference": args.preference}))

    opt_route = sub.add_parser("optimize-route", parents=[base_parser], help="Optimize route based on criteria")
    opt_route.add_argument("--criteria", default="balanced")
    opt_route.set_defaults(func=lambda args, env: _execute(env, args.session_id, "optimize_route", criteria=args.criteria))

    summary_p = sub.add_parser("session-summary", parents=[base_parser], help="Get session summary")
    summary_p.set_defaults(func=lambda args, env: {"status": "success", "data": env.get_session_summary(args.session_id or _get_session_id())})

    eval_p = sub.add_parser("evaluate", parents=[base_parser], help=argparse.SUPPRESS)
    eval_p.set_defaults(func=lambda args, env: {"status": "success", "data": env.get_reward(args.session_id or _get_session_id())})

    args = main_parser.parse_args()

    data_root = _get_data_root()
    state_root = _get_state_root()
    env = ItineraryEnvironment(data_root, state_root)

    if not args.command:
        main_parser.print_help()
        return

    try:
        result = args.func(args, env)
    except Exception as e:
        result = {"status": "error", "message": str(e)}

    print(json.dumps(result, ensure_ascii=False))


def _execute(env: ItineraryEnvironment, session_id: str | None, action_type: str, **kwargs) -> dict:
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
