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


def set_driving_mode(ctrl: VehicleController, mode: str) -> dict[str, Any]:
    valid_modes = ["eco", "comfort", "sport", "individual"]
    if mode not in valid_modes:
        return {"status": "error", "message": f"驾驶模式必须是{valid_modes}之一"}
    ctrl.vehicle_state["driving_mode"] = mode
    ctrl._save()
    mode_names = {"eco": "节能", "comfort": "舒适", "sport": "运动", "individual": "个性化"}
    return {"status": "ok", "message": f"驾驶模式已切换为{mode_names.get(mode, mode)}", "driving_mode": mode}


def get_driving_mode(ctrl: VehicleController) -> dict[str, Any]:
    return {"status": "ok", "data": {"driving_mode": ctrl.vehicle_state["driving_mode"]}}
