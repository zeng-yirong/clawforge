from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .environment import MusicEnvironment

_HIDDEN_HELP_MARKERS = ("prepare-rollout", "reset-rollout", "evaluate", "==SUPPRESS==")


def _get_data_root() -> Path:
    return Path(__file__).parent / "data"


def _get_state_root() -> Path:
    default = Path.home() / ".music_player_state"
    return Path(os.environ.get("MUSIC_STATE_ROOT", default))


def _get_session_id() -> str | None:
    return os.environ.get("MUSIC_SESSION_ID")


class MusicArgumentParser(argparse.ArgumentParser):
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


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--session-id", dest="session_id", default=None, help=argparse.SUPPRESS)


def _nested_parser() -> tuple[argparse.ArgumentParser, list[argparse.ArgumentParser]]:
    base = MusicArgumentParser(add_help=False)
    _add_common_args(base)
    return base, []


def cmd_list_scenarios(args: argparse.Namespace, env: MusicEnvironment) -> dict:
    scenarios = env.repo.list_scenarios()
    return {"status": "success", "data": {"scenarios": scenarios}}


def cmd_prepare_rollout(args: argparse.Namespace, env: MusicEnvironment) -> dict:
    scenario_id = getattr(args, "scenario_id", None)
    session_id = args.session_id or _get_session_id()
    show_bindings = getattr(args, "show_bindings", False)
    if not scenario_id:
        return {"status": "error", "message": "--scenario-id is required"}
    result = env.prepare_rollout(scenario_id, session_id=session_id, show_bindings=show_bindings)
    return {"status": "success", "data": result}


def cmd_reset_rollout(args: argparse.Namespace, env: MusicEnvironment) -> dict:
    session_id = args.session_id or _get_session_id()
    if not session_id:
        return {"status": "error", "message": "No session bound. Trainer must prepare rollout first."}
    result = env.reset_rollout(session_id)
    return {"status": "success", "data": result}


def cmd_status(args: argparse.Namespace, env: MusicEnvironment) -> dict:
    session_id = args.session_id or _get_session_id()
    if not session_id:
        return {"status": "error", "message": "No session bound. Trainer must prepare rollout first."}
    result = env.execute_action(session_id, "status", env.store.load_session(session_id)["meta"]["action_index"])
    return {"status": "success", "data": result}


def cmd_play(args: argparse.Namespace, env: MusicEnvironment) -> dict:
    session_id = args.session_id or _get_session_id()
    if not session_id:
        return {"status": "error", "message": "No session bound. Trainer must prepare rollout first."}
    song_id = getattr(args, "song_id", None)
    if not song_id:
        return {"status": "error", "message": "--song-id is required"}
    action_idx = env.store.load_session(session_id)["meta"]["action_index"]
    result = env.execute_action(session_id, "play", action_idx, song_id=song_id)
    return {"status": "success", "data": result}


def cmd_pause(args: argparse.Namespace, env: MusicEnvironment) -> dict:
    session_id = args.session_id or _get_session_id()
    if not session_id:
        return {"status": "error", "message": "No session bound. Trainer must prepare rollout first."}
    action_idx = env.store.load_session(session_id)["meta"]["action_index"]
    result = env.execute_action(session_id, "pause", action_idx)
    return {"status": "success", "data": result}


def cmd_resume(args: argparse.Namespace, env: MusicEnvironment) -> dict:
    session_id = args.session_id or _get_session_id()
    if not session_id:
        return {"status": "error", "message": "No session bound. Trainer must prepare rollout first."}
    action_idx = env.store.load_session(session_id)["meta"]["action_index"]
    result = env.execute_action(session_id, "resume", action_idx)
    return {"status": "success", "data": result}


def cmd_next(args: argparse.Namespace, env: MusicEnvironment) -> dict:
    session_id = args.session_id or _get_session_id()
    if not session_id:
        return {"status": "error", "message": "No session bound. Trainer must prepare rollout first."}
    action_idx = env.store.load_session(session_id)["meta"]["action_index"]
    result = env.execute_action(session_id, "next", action_idx)
    return {"status": "success", "data": result}


def cmd_previous(args: argparse.Namespace, env: MusicEnvironment) -> dict:
    session_id = args.session_id or _get_session_id()
    if not session_id:
        return {"status": "error", "message": "No session bound. Trainer must prepare rollout first."}
    action_idx = env.store.load_session(session_id)["meta"]["action_index"]
    result = env.execute_action(session_id, "previous", action_idx)
    return {"status": "success", "data": result}


def cmd_seek(args: argparse.Namespace, env: MusicEnvironment) -> dict:
    session_id = args.session_id or _get_session_id()
    if not session_id:
        return {"status": "error", "message": "No session bound. Trainer must prepare rollout first."}
    position = getattr(args, "position", 0)
    action_idx = env.store.load_session(session_id)["meta"]["action_index"]
    result = env.execute_action(session_id, "seek", action_idx, position=position)
    return {"status": "success", "data": result}


def cmd_set_mode(args: argparse.Namespace, env: MusicEnvironment) -> dict:
    session_id = args.session_id or _get_session_id()
    if not session_id:
        return {"status": "error", "message": "No session bound. Trainer must prepare rollout first."}
    mode = getattr(args, "mode", "repeat_all")
    action_idx = env.store.load_session(session_id)["meta"]["action_index"]
    result = env.execute_action(session_id, "set_mode", action_idx, mode=mode)
    return {"status": "success", "data": result}


def cmd_switch_player(args: argparse.Namespace, env: MusicEnvironment) -> dict:
    session_id = args.session_id or _get_session_id()
    if not session_id:
        return {"status": "error", "message": "No session bound. Trainer must prepare rollout first."}
    player = getattr(args, "player", "local")
    action_idx = env.store.load_session(session_id)["meta"]["action_index"]
    result = env.execute_action(session_id, "switch_player", action_idx, player=player)
    return {"status": "success", "data": result}


def cmd_list_songs(args: argparse.Namespace, env: MusicEnvironment) -> dict:
    result = env.execute_action("", "list_songs", 0)
    return {"status": "success", "data": result}


def cmd_list_playlists(args: argparse.Namespace, env: MusicEnvironment) -> dict:
    result = env.execute_action("", "list_playlists", 0)
    return {"status": "success", "data": result}


def cmd_list_players(args: argparse.Namespace, env: MusicEnvironment) -> dict:
    result = env.execute_action("", "list_players", 0)
    return {"status": "success", "data": result}


def cmd_search(args: argparse.Namespace, env: MusicEnvironment) -> dict:
    session_id = args.session_id or _get_session_id()
    if not session_id:
        return {"status": "error", "message": "No session bound. Trainer must prepare rollout first."}
    kwargs = {}
    if getattr(args, "title", None):
        kwargs["title"] = args.title
    if getattr(args, "artist", None):
        kwargs["artist"] = args.artist
    if getattr(args, "album", None):
        kwargs["album"] = args.album
    if getattr(args, "brand", None):
        kwargs["brand"] = args.brand
    if getattr(args, "tag", None):
        kwargs["tag"] = args.tag
    if getattr(args, "scene", None):
        kwargs["scene"] = args.scene
    if getattr(args, "style", None):
        kwargs["style"] = args.style
    if getattr(args, "language", None):
        kwargs["language"] = args.language
    if getattr(args, "era", None):
        kwargs["era"] = args.era
    if getattr(args, "crowd", None):
        kwargs["crowd"] = args.crowd
    if getattr(args, "similar_to", None):
        kwargs["similar_to"] = args.similar_to
    action_idx = env.store.load_session(session_id)["meta"]["action_index"]
    result = env.execute_action(session_id, "search", action_idx, **kwargs)
    return {"status": "success", "data": result}


def cmd_session_summary(args: argparse.Namespace, env: MusicEnvironment) -> dict:
    session_id = args.session_id or _get_session_id()
    if not session_id:
        return {"status": "error", "message": "No session bound. Trainer must prepare rollout first."}
    result = env.get_session_summary(session_id)
    return {"status": "success", "data": result}


def cmd_evaluate(args: argparse.Namespace, env: MusicEnvironment) -> dict:
    session_id = args.session_id or _get_session_id()
    if not session_id:
        return {"status": "error", "message": "No session bound. Trainer must prepare rollout first."}
    result = env.get_reward(session_id)
    return {"status": "success", "data": result}


def main():
    base_parser, shared_parses = _nested_parser()
    main_parser = MusicArgumentParser(description="Music Player CLI")
    sub = main_parser.add_subparsers(dest="command", metavar="")

    hidden = MusicArgumentParser(add_help=False)
    hidden.add_argument("--show-bindings", action="store_true")
    hidden.add_argument("--scenario-id", dest="scenario_id")

    list_sc = sub.add_parser("list-scenarios", parents=[base_parser], help="List available scenarios")
    list_sc.set_defaults(func=cmd_list_scenarios)

    hidden.add_argument("--session-id", dest="session_id", default=None, help=argparse.SUPPRESS)

    prep = sub.add_parser("prepare-rollout", parents=[hidden], help=argparse.SUPPRESS)
    prep.set_defaults(func=cmd_prepare_rollout)

    reset = sub.add_parser("reset-rollout", parents=[hidden], help=argparse.SUPPRESS)
    reset.set_defaults(func=cmd_reset_rollout)

    status_p = sub.add_parser("status", parents=[base_parser], help="Get current playback status")
    status_p.set_defaults(func=cmd_status)

    play_p = sub.add_parser("play", parents=[base_parser], help="Play a song by ID")
    play_p.add_argument("--song-id", dest="song_id", required=True)
    play_p.set_defaults(func=cmd_play)

    pause_p = sub.add_parser("pause", parents=[base_parser], help="Pause playback")
    pause_p.set_defaults(func=cmd_pause)

    resume_p = sub.add_parser("resume", parents=[base_parser], help="Resume playback")
    resume_p.set_defaults(func=cmd_resume)

    next_p = sub.add_parser("next", parents=[base_parser], help="Next track")
    next_p.set_defaults(func=cmd_next)

    prev_p = sub.add_parser("previous", parents=[base_parser], help="Previous track")
    prev_p.set_defaults(func=cmd_previous)

    seek_p = sub.add_parser("seek", parents=[base_parser], help="Seek to position")
    seek_p.add_argument("--position", type=int, default=0)
    seek_p.set_defaults(func=cmd_seek)

    mode_p = sub.add_parser("set-mode", parents=[base_parser], help="Set play mode")
    mode_p.add_argument("--mode", default="repeat_all")
    mode_p.set_defaults(func=cmd_set_mode)

    sw_p = sub.add_parser("switch-player", parents=[base_parser], help="Switch audio player")
    sw_p.add_argument("--player", default="local")
    sw_p.set_defaults(func=cmd_switch_player)

    list_songs_p = sub.add_parser("list-songs", parents=[base_parser], help="List all songs")
    list_songs_p.set_defaults(func=cmd_list_songs)

    list_pl_p = sub.add_parser("list-playlists", parents=[base_parser], help="List all playlists")
    list_pl_p.set_defaults(func=cmd_list_playlists)

    list_players_p = sub.add_parser("list-players", parents=[base_parser], help="List available players")
    list_players_p.set_defaults(func=cmd_list_players)

    search_p = sub.add_parser("search", parents=[base_parser], help="Search songs")
    search_p.add_argument("--title")
    search_p.add_argument("--artist")
    search_p.add_argument("--album")
    search_p.add_argument("--brand")
    search_p.add_argument("--tag")
    search_p.add_argument("--scene")
    search_p.add_argument("--style")
    search_p.add_argument("--language")
    search_p.add_argument("--era")
    search_p.add_argument("--crowd")
    search_p.add_argument("--similar-to", dest="similar_to")
    search_p.set_defaults(func=cmd_search)

    summary_p = sub.add_parser("session-summary", parents=[base_parser], help="Get session summary")
    summary_p.set_defaults(func=cmd_session_summary)

    eval_p = sub.add_parser("evaluate", parents=[base_parser], help=argparse.SUPPRESS)
    eval_p.set_defaults(func=cmd_evaluate)

    args = main_parser.parse_args()

    data_root = _get_data_root()
    state_root = _get_state_root()
    env = MusicEnvironment(data_root, state_root)

    if not args.command:
        main_parser.print_help()
        return

    if args.command == "list-scenarios":
        result = cmd_list_scenarios(args, env)
    elif args.command == "prepare-rollout":
        result = cmd_prepare_rollout(args, env)
    elif args.command == "reset-rollout":
        result = cmd_reset_rollout(args, env)
    elif args.command == "status":
        result = cmd_status(args, env)
    elif args.command == "play":
        result = cmd_play(args, env)
    elif args.command == "pause":
        result = cmd_pause(args, env)
    elif args.command == "resume":
        result = cmd_resume(args, env)
    elif args.command == "next":
        result = cmd_next(args, env)
    elif args.command == "previous":
        result = cmd_previous(args, env)
    elif args.command == "seek":
        result = cmd_seek(args, env)
    elif args.command == "set-mode":
        result = cmd_set_mode(args, env)
    elif args.command == "switch-player":
        result = cmd_switch_player(args, env)
    elif args.command == "list-songs":
        result = cmd_list_songs(args, env)
    elif args.command == "list-playlists":
        result = cmd_list_playlists(args, env)
    elif args.command == "list-players":
        result = cmd_list_players(args, env)
    elif args.command == "search":
        result = cmd_search(args, env)
    elif args.command == "session-summary":
        result = cmd_session_summary(args, env)
    elif args.command == "evaluate":
        result = cmd_evaluate(args, env)
    else:
        result = {"status": "error", "message": f"Unknown command: {args.command}"}

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()