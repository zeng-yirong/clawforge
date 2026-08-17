from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .store import SessionStore


class PlayerController:
    def __init__(self, session: dict[str, Any], store: SessionStore, session_id: str):
        self._session = session
        self._store = store
        self._session_id = session_id

    @property
    def player(self) -> dict[str, Any]:
        return self._session["player"]

    def _save(self) -> None:
        self._store.save_session(self._session_id, self._session)


def play_song(ctrl: PlayerController, song_id: str | None = None) -> dict[str, Any]:
    if not song_id:
        return {"status": "error", "message": "song_id is required"}
    ctrl.player["current_song_id"] = song_id
    ctrl.player["status"] = "playing"
    ctrl.player["position"] = 0
    ctrl._save()
    if song_id not in ctrl._session.get("play_history", []):
        ctrl._session.setdefault("play_history", []).append(song_id)
        ctrl._save()
    return {
        "status": "ok",
        "message": f"Playing {song_id}",
        "current_song_id": song_id,
        "status_playback": "playing",
        "position": 0,
    }


def pause_playback(ctrl: PlayerController) -> dict[str, Any]:
    if ctrl.player.get("status") != "playing":
        return {"status": "error", "message": "Nothing is playing"}
    ctrl.player["status"] = "paused"
    ctrl._save()
    return {"status": "ok", "message": "Paused", "status_playback": "paused"}


def resume_playback(ctrl: PlayerController) -> dict[str, Any]:
    if ctrl.player.get("status") != "paused":
        return {"status": "error", "message": "Nothing is paused"}
    ctrl.player["status"] = "playing"
    ctrl._save()
    return {"status": "ok", "message": "Resumed", "status_playback": "playing"}


def next_track(ctrl: PlayerController) -> dict[str, Any]:
    history = ctrl._session.get("play_history", [])
    if not history:
        return {"status": "error", "message": "No play history"}
    current = ctrl.player.get("current_song_id")
    try:
        idx = history.index(current)
        next_idx = (idx + 1) % len(history)
    except ValueError:
        next_idx = 0
    next_song_id = history[next_idx]
    ctrl.player["current_song_id"] = next_song_id
    ctrl.player["status"] = "playing"
    ctrl.player["position"] = 0
    ctrl._save()
    return {
        "status": "ok",
        "message": f"Playing next: {next_song_id}",
        "current_song_id": next_song_id,
    }


def previous_track(ctrl: PlayerController) -> dict[str, Any]:
    history = ctrl._session.get("play_history", [])
    if not history:
        return {"status": "error", "message": "No play history"}
    current = ctrl.player.get("current_song_id")
    try:
        idx = history.index(current)
        prev_idx = (idx - 1) % len(history)
    except ValueError:
        prev_idx = -1
    prev_song_id = history[prev_idx]
    ctrl.player["current_song_id"] = prev_song_id
    ctrl.player["status"] = "playing"
    ctrl.player["position"] = 0
    ctrl._save()
    return {
        "status": "ok",
        "message": f"Playing previous: {prev_song_id}",
        "current_song_id": prev_song_id,
    }


def seek_to(ctrl: PlayerController, position: int) -> dict[str, Any]:
    if position < 0:
        return {"status": "error", "message": "Position must be non-negative"}
    ctrl.player["position"] = position
    ctrl._save()
    return {"status": "ok", "message": f"Seeked to {position}s", "position": position}


def set_play_mode(ctrl: PlayerController, mode: str) -> dict[str, Any]:
    valid_modes = ["repeat_all", "repeat_one", "shuffle", "sequential"]
    if mode not in valid_modes:
        return {"status": "error", "message": f"Invalid mode. Must be one of {valid_modes}"}
    ctrl.player["play_mode"] = mode
    ctrl._save()
    return {"status": "ok", "message": f"Play mode set to {mode}", "play_mode": mode}


def set_volume(ctrl: PlayerController, volume: int) -> dict[str, Any]:
    if not 0 <= volume <= 100:
        return {"status": "error", "message": "Volume must be between 0 and 100"}
    ctrl.player["volume"] = volume
    ctrl._save()
    return {"status": "ok", "message": f"Volume set to {volume}", "volume": volume}


def switch_player(ctrl: PlayerController, player_name: str) -> dict[str, Any]:
    valid_players = ["local", "bluetooth", "usb", "aux"]
    if player_name not in valid_players:
        return {"status": "error", "message": f"Invalid player. Must be one of {valid_players}"}
    ctrl.player["player_name"] = player_name
    ctrl._save()
    return {"status": "ok", "message": f"Switched to {player_name}", "player_name": player_name}


def get_status(ctrl: PlayerController) -> dict[str, Any]:
    return {
        "status": "ok",
        "data": {
            "current_song_id": ctrl.player.get("current_song_id"),
            "playback_status": ctrl.player.get("status"),
            "position": ctrl.player.get("position"),
            "volume": ctrl.player.get("volume"),
            "play_mode": ctrl.player.get("play_mode"),
            "player_name": ctrl.player.get("player_name"),
        },
    }


def add_to_favorites(ctrl: PlayerController, song_id: str) -> dict[str, Any]:
    favorites = ctrl._session.setdefault("favorites", [])
    if song_id not in favorites:
        favorites.append(song_id)
        ctrl._save()
    return {"status": "ok", "message": f"Added {song_id} to favorites"}


def remove_from_favorites(ctrl: PlayerController, song_id: str) -> dict[str, Any]:
    favorites = ctrl._session.get("favorites", [])
    if song_id in favorites:
        favorites.remove(song_id)
        ctrl._save()
    return {"status": "ok", "message": f"Removed {song_id} from favorites"}
