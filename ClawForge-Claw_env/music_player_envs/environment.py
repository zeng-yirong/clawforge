from __future__ import annotations

import os
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .player import (
    PlayerController,
    play_song,
    pause_playback,
    resume_playback,
    next_track,
    previous_track,
    seek_to,
    set_play_mode,
    set_volume,
    switch_player as switch_player_cmd,
    get_status,
    add_to_favorites,
    remove_from_favorites,
)
from .search import SearchEngine, search_songs as search_songs_fn
from .repository import MusicRepository
from .store import SessionStore


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _action_timestamp(base_time: str, action_index: int) -> str:
    base = _coerce_iso_datetime(base_time)
    return (base + timedelta(seconds=action_index * 30)).isoformat()


class MusicEnvironment:
    def __init__(
        self,
        data_root: Path | str,
        state_root: Path | str,
    ):
        self.data_root = Path(data_root)
        self.state_root = Path(state_root)
        self.repo = MusicRepository(data_root)
        self.store = SessionStore(state_root)

    def _get_binding(self, key: str) -> str | None:
        env_key = f"MUSIC_{key}"
        return os.environ.get(env_key)

    def _require_binding(self, key: str) -> str:
        value = self._get_binding(key)
        if value is None:
            raise RuntimeError(
                f"Missing required binding: {key}. "
                "Trainer must call prepare-rollout first."
            )
        return value

    def prepare_rollout(
        self,
        scenario_id: str,
        session_id: str | None = None,
        show_bindings: bool = False,
    ) -> dict[str, Any]:
        scenario = self.repo.get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        base_time = scenario.get("base_time", _utc_now_iso())
        workspace_account_id = scenario.get("workspace_account_id", "acc_001")
        account = self.repo.get_account(workspace_account_id)
        if not account:
            raise ValueError(f"Account {workspace_account_id} not found")

        if not session_id:
            import uuid

            session_id = f"music-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:4]}"

        state_root = str(self.state_root)
        self.store.create_session(
            session_id=session_id,
            scenario_id=scenario_id,
            base_time=base_time,
            workspace_account=account,
        )

        bindings = {
            "MUSIC_SESSION_ID": session_id,
            "MUSIC_STATE_ROOT": state_root,
            "MUSIC_SCENARIO_ID": scenario_id,
        }

        result = {
            "session_id": session_id,
            "scenario_id": scenario_id,
            "state_root": state_root,
            "bindings": bindings,
        }
        return result

    def reset_rollout(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        scenario = self.repo.get_scenario(session["scenario_id"])
        if not scenario:
            raise ValueError(f"Scenario {session['scenario_id']} not found")

        base_time = scenario.get("base_time", _utc_now_iso())
        workspace_account_id = scenario.get("workspace_account_id", "acc_001")
        account = self.repo.get_account(workspace_account_id)

        self.store.delete_session(session_id)
        self.store.create_session(
            session_id=session_id,
            scenario_id=session["scenario_id"],
            base_time=base_time,
            workspace_account=account,
        )

        return {"session_id": session_id, "status": "reset"}

    def execute_action(
        self,
        session_id: str,
        action_type: str,
        action_index: int,
        **kwargs: Any,
    ) -> dict[str, Any]:
        search_only_actions = ("list_songs", "list_playlists", "list_players", "search", "get_song", "get_playlist")
        session = self.store.load_session(session_id) if session_id else None

        if action_type not in search_only_actions and not session:
            raise ValueError(f"Session {session_id} not found")

        search_eng = SearchEngine(self.repo)
        result: dict[str, Any] = {"status": "ok"}

        if action_type == "list_songs":
            songs = self.repo.list_songs()
            result = {"status": "ok", "data": songs}
        elif action_type == "list_playlists":
            playlists = self.repo.list_playlists()
            result = {"status": "ok", "data": playlists}
        elif action_type == "list_players":
            result = {
                "status": "ok",
                "data": [
                    {"player_id": "local", "name": "本地音乐", "description": "本机存储的音乐"},
                    {"player_id": "bluetooth", "name": "蓝牙", "description": "蓝牙连接的手机或其他设备"},
                    {"player_id": "usb", "name": "USB", "description": "USB设备"},
                    {"player_id": "aux", "name": "AUX", "description": "AUX输入"},
                ],
            }
        elif action_type == "search":
            result = search_songs_fn(search_eng, **kwargs)
        elif action_type == "get_song":
            song_id = kwargs.get("song_id")
            song = self.repo.get_song(song_id) if song_id else None
            result = {"status": "ok", "data": song}
        elif action_type == "get_playlist":
            playlist_id = kwargs.get("playlist_id")
            playlist = self.repo.get_playlist(playlist_id) if playlist_id else None
            result = {"status": "ok", "data": playlist}
        else:
            base_time = session["meta"]["base_time"]
            timestamp = _action_timestamp(base_time, action_index)
            player_ctrl = PlayerController(session, self.store, session_id)

            if action_type == "play":
                song_id = kwargs.get("song_id")
                result = play_song(player_ctrl, song_id)
            elif action_type == "pause":
                result = pause_playback(player_ctrl)
            elif action_type == "resume":
                result = resume_playback(player_ctrl)
            elif action_type == "next":
                result = next_track(player_ctrl)
            elif action_type == "previous":
                result = previous_track(player_ctrl)
            elif action_type == "seek":
                position = kwargs.get("position", 0)
                result = seek_to(player_ctrl, position)
            elif action_type == "set_mode":
                mode = kwargs.get("mode", "repeat_all")
                result = set_play_mode(player_ctrl, mode)
            elif action_type == "set_volume":
                volume = kwargs.get("volume", 15)
                result = set_volume(player_ctrl, volume)
            elif action_type == "switch_player":
                player_name = kwargs.get("player", "local")
                result = switch_player_cmd(player_ctrl, player_name)
            elif action_type == "status":
                result = get_status(player_ctrl)
            elif action_type == "play_playlist":
                playlist_id = kwargs.get("playlist_id")
                playlist = self.repo.get_playlist(playlist_id)
                if not playlist:
                    result = {"status": "error", "message": f"Playlist {playlist_id} not found"}
                else:
                    song_ids = playlist.get("song_ids", [])
                    if song_ids:
                        result = play_song(player_ctrl, song_ids[0])
                    else:
                        result = {"status": "error", "message": "Playlist is empty"}
            elif action_type == "favorite_add":
                song_id = kwargs.get("song_id")
                result = add_to_favorites(player_ctrl, song_id)
            elif action_type == "favorite_remove":
                song_id = kwargs.get("song_id")
                result = remove_from_favorites(player_ctrl, song_id)
            else:
                result = {"status": "error", "message": f"Unknown action: {action_type}"}

            session["meta"]["action_index"] = action_index + 1
            session["actions"].append({
                "action_index": action_index,
                "timestamp": timestamp,
                "action_type": action_type,
                "details": kwargs,
                "result": result,
            })
            self.store.save_session(session_id, session)

        return result

    def get_session_summary(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        current_song_id = session["player"].get("current_song_id")
        current_song = self.repo.get_song(current_song_id) if current_song_id else None

        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "player": session["player"],
            "current_song": current_song,
            "play_history_count": len(session.get("play_history", [])),
            "favorites_count": len(session.get("favorites", [])),
            "action_count": len(session.get("actions", [])),
        }

    def get_reward(self, session_id: str) -> dict[str, Any]:
        from .evaluator import evaluate_session
        session = self.store.load_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        scenario = self.repo.get_scenario(session["scenario_id"])
        if not scenario:
            raise ValueError(f"Scenario {session['scenario_id']} not found")
        return evaluate_session(session, scenario)