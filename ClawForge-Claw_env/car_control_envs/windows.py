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


def set_window_open(ctrl: VehicleController, window: str, percentage: int) -> dict[str, Any]:
    valid_windows = ["fl", "fr", "rl", "rr", "sunroof", "moonroof", "sunshade"]
    if window not in valid_windows:
        return {"status": "error", "message": f"车窗必须是{valid_windows}之一"}
    if not 0 <= percentage <= 100:
        return {"status": "error", "message": "开合度范围为0-100"}
    ctrl.vehicle_state["windows"][window]["open"] = percentage
    ctrl._save()
    return {"status": "ok", "message": f"{window}已打开{percentage}%", "window": window, "open": percentage}


def close_window(ctrl: VehicleController, window: str) -> dict[str, Any]:
    valid_windows = ["fl", "fr", "rl", "rr", "sunroof", "moonroof", "sunshade"]
    if window not in valid_windows:
        return {"status": "error", "message": f"车窗必须是{valid_windows}之一"}
    ctrl.vehicle_state["windows"][window]["open"] = 0
    ctrl._save()
    return {"status": "ok", "message": f"{window}已关闭", "window": window, "open": 0}


def open_all_windows(ctrl: VehicleController) -> dict[str, Any]:
    for window in ["fl", "fr", "rl", "rr"]:
        ctrl.vehicle_state["windows"][window]["open"] = 100
    ctrl._save()
    return {"status": "ok", "message": "所有车窗已打开"}


def close_all_windows(ctrl: VehicleController) -> dict[str, Any]:
    for window in ["fl", "fr", "rl", "rr", "sunroof", "moonroof", "sunshade"]:
        ctrl.vehicle_state["windows"][window]["open"] = 0
    ctrl._save()
    return {"status": "ok", "message": "所有车窗和天窗已关闭"}


def get_window_status(ctrl: VehicleController) -> dict[str, Any]:
    return {"status": "ok", "data": ctrl.vehicle_state["windows"]}
