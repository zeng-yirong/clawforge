from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .environment import CarControlEnvironment

_HIDDEN_HELP_MARKERS = ("prepare-rollout", "reset-rollout", "evaluate", "==SUPPRESS==")


def _get_data_root() -> Path:
    return Path(__file__).parent / "data"


def _get_state_root() -> Path:
    default = Path.home() / ".car_control_state"
    return Path(os.environ.get("CAR_STATE_ROOT", default))


def _get_session_id() -> str | None:
    return os.environ.get("CAR_SESSION_ID")


class CarArgumentParser(argparse.ArgumentParser):
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
    base_parser = CarArgumentParser(add_help=False)
    base_parser.add_argument("--session-id", dest="session_id", default=None, help=argparse.SUPPRESS)

    main_parser = CarArgumentParser(description="Car Control CLI")
    sub = main_parser.add_subparsers(dest="command", metavar="")

    hidden = CarArgumentParser(add_help=False)
    hidden.add_argument("--show-bindings", action="store_true")
    hidden.add_argument("--scenario-id", dest="scenario_id")
    hidden.add_argument("--session-id", dest="session_id", default=None, help=argparse.SUPPRESS)

    list_sc = sub.add_parser("list-scenarios", parents=[base_parser], help="List available scenarios")
    list_sc.set_defaults(func=lambda args, env: {"status": "success", "data": {"scenarios": env.repo.list_scenarios()}})

    prep = sub.add_parser("prepare-rollout", parents=[hidden], help=argparse.SUPPRESS)
    prep.set_defaults(func=lambda args, env: env.prepare_rollout(args.scenario_id, show_bindings=args.show_bindings))

    reset = sub.add_parser("reset-rollout", parents=[hidden], help=argparse.SUPPRESS)
    reset.set_defaults(func=lambda args, env: env.reset_rollout(args.session_id or _get_session_id()))

    ac_p = sub.add_parser("ac-power", parents=[base_parser], help="Set AC power")
    ac_p.add_argument("--on", type=bool, default=True)
    ac_p.set_defaults(func=lambda args, env: _execute(env, args.session_id, "ac_power", on=args.on))

    tmp_p = sub.add_parser("ac-temp", parents=[base_parser], help="Set AC temperature")
    tmp_p.add_argument("--temperature", type=int, default=24)
    tmp_p.set_defaults(func=lambda args, env: _execute(env, args.session_id, "ac_temperature", temperature=args.temperature))

    mode_p = sub.add_parser("ac-mode", parents=[base_parser], help="Set AC mode")
    mode_p.add_argument("--mode", default="auto")
    mode_p.set_defaults(func=lambda args, env: _execute(env, args.session_id, "ac_mode", mode=args.mode))

    fan_p = sub.add_parser("ac-fan", parents=[base_parser], help="Set AC fan speed")
    fan_p.add_argument("--speed", type=int, default=2)
    fan_p.set_defaults(func=lambda args, env: _execute(env, args.session_id, "ac_fan_speed", speed=args.speed))

    seat_p = sub.add_parser("seat", parents=[base_parser], help="Adjust seat")
    seat_p.add_argument("--zone", default="fl")
    seat_p.add_argument("--position", type=int, required=True)
    seat_p.set_defaults(func=lambda args, env: _execute(env, args.session_id, "seat_position", zone=args.zone, position=args.position))

    seat_h = sub.add_parser("seat-heat", parents=[base_parser], help="Set seat heating")
    seat_h.add_argument("--zone", default="fl")
    seat_h.add_argument("--level", type=int, default=1)
    seat_h.set_defaults(func=lambda args, env: _execute(env, args.session_id, "seat_heating", zone=args.zone, level=args.level))

    win_p = sub.add_parser("window", parents=[base_parser], help="Control window")
    win_p.add_argument("--window", default="fl")
    win_p.add_argument("--percentage", type=int, default=100)
    win_p.set_defaults(func=lambda args, env: _execute(env, args.session_id, "window_open", window=args.window, percentage=args.percentage))

    light_p = sub.add_parser("ambient-light", parents=[base_parser], help="Set ambient light")
    light_p.add_argument("--on", type=bool, default=True)
    light_p.add_argument("--color", default="blue")
    light_p.add_argument("--brightness", type=int, default=50)
    light_p.set_defaults(func=lambda args, env: _execute(env, args.session_id, "ambient_light", on=args.on, color=args.color, brightness=args.brightness))

    drive_p = sub.add_parser("driving-mode", parents=[base_parser], help="Set driving mode")
    drive_p.add_argument("--mode", default="comfort")
    drive_p.set_defaults(func=lambda args, env: _execute(env, args.session_id, "driving_mode", mode=args.mode))

    vol_p = sub.add_parser("volume", parents=[base_parser], help="Set volume")
    vol_p.add_argument("--volume", type=int, default=15)
    vol_p.set_defaults(func=lambda args, env: _execute(env, args.session_id, "volume_set", volume=args.volume))

    media_p = sub.add_parser("media-play", parents=[base_parser], help="Play media")
    media_p.add_argument("--source", default="bluetooth")
    media_p.set_defaults(func=lambda args, env: _execute(env, args.session_id, "media_play", source=args.source))

    status_p = sub.add_parser("status", parents=[base_parser], help="Get vehicle status")
    status_p.add_argument("--query-type", dest="query_type", default=None)
    status_p.set_defaults(func=lambda args, env: _execute(env, args.session_id, "status_query", query_type=args.query_type))

    summary_p = sub.add_parser("session-summary", parents=[base_parser], help="Get session summary")
    summary_p.set_defaults(func=lambda args, env: {"status": "success", "data": env.get_session_summary(args.session_id or _get_session_id())})

    eval_p = sub.add_parser("evaluate", parents=[base_parser], help=argparse.SUPPRESS)
    eval_p.set_defaults(func=lambda args, env: {"status": "success", "data": env.get_reward(args.session_id or _get_session_id())})

    args = main_parser.parse_args()

    data_root = _get_data_root()
    state_root = _get_state_root()
    env = CarControlEnvironment(data_root, state_root)

    if not args.command:
        main_parser.print_help()
        return

    try:
        result = args.func(args, env)
    except Exception as e:
        result = {"status": "error", "message": str(e)}

    print(json.dumps(result, ensure_ascii=False))


def _execute(env: CarControlEnvironment, session_id: str | None, action_type: str, **kwargs) -> dict:
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
