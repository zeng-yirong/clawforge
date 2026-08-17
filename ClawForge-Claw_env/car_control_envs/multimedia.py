from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .store import SessionStore


class VehicleController:
    def __init__(self, session: dict[str, Any], store: SessionStore, session_id: str):
        self._session = session
        self._store = store
        self._session_id = session_id

    @property
    def vehicle_state(self) -> dict[str, Any]:
        return self._session["vehicle_state"]

    def _save(self) -> None:
        self._store.save_session(self._session_id, self._session)


def play_media(ctrl: VehicleController, source: str | None = None) -> dict[str, Any]:
    if source:
        valid_sources = ["bluetooth", "usb", "radio", "aux", "wifi"]
        if source not in valid_sources:
            return {"status": "error", "message": f"音源必须是{valid_sources}之一"}
        ctrl.vehicle_state["multimedia"]["source"] = source
    ctrl.vehicle_state["multimedia"]["playing"] = True
    ctrl._save()
    return {"status": "ok", "message": "开始播放", "multimedia": ctrl.vehicle_state["multimedia"]}


def pause_media(ctrl: VehicleController) -> dict[str, Any]:
    ctrl.vehicle_state["multimedia"]["playing"] = False
    ctrl._save()
    return {"status": "ok", "message": "已暂停", "multimedia": ctrl.vehicle_state["multimedia"]}


def set_volume(ctrl: VehicleController, volume: int) -> dict[str, Any]:
    if not 0 <= volume <= 50:
        return {"status": "error", "message": "音量范围为0-50"}
    ctrl.vehicle_state["multimedia"]["volume"] = volume
    ctrl._save()
    return {"status": "ok", "message": f"音量已设置为{volume}", "volume": volume}


def adjust_volume(ctrl: VehicleController, delta: int) -> dict[str, Any]:
    current = ctrl.vehicle_state["multimedia"]["volume"]
    new_volume = max(0, min(50, current + delta))
    ctrl.vehicle_state["multimedia"]["volume"] = new_volume
    ctrl._save()
    return {"status": "ok", "message": f"音量已调整到{new_volume}", "volume": new_volume}


def get_multimedia_status(ctrl: VehicleController) -> dict[str, Any]:
    return {"status": "ok", "data": ctrl.vehicle_state["multimedia"]}
