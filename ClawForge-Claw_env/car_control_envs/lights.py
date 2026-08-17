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


def set_ambient_light(ctrl: VehicleController, on: bool, color: str | None = None, brightness: int | None = None) -> dict[str, Any]:
    ctrl.vehicle_state["lights"]["ambient"]["on"] = on
    if color:
        valid_colors = ["blue", "green", "red", "orange", "purple", "white"]
        if color not in valid_colors:
            return {"status": "error", "message": f"颜色必须是{valid_colors}之一"}
        ctrl.vehicle_state["lights"]["ambient"]["color"] = color
    if brightness is not None:
        if not 0 <= brightness <= 100:
            return {"status": "error", "message": "亮度范围为0-100"}
        ctrl.vehicle_state["lights"]["ambient"]["brightness"] = brightness
    ctrl._save()
    return {
        "status": "ok",
        "message": f"氛围灯已{'开启' if on else '关闭'}",
        "ambient": ctrl.vehicle_state["lights"]["ambient"]
    }


def set_reading_light(ctrl: VehicleController, zone: str, on: bool) -> dict[str, Any]:
    valid_zones = ["fl", "fr", "rl", "rr"]
    if zone not in valid_zones:
        return {"status": "error", "message": f"区域必须是{valid_zones}之一"}
    ctrl.vehicle_state["lights"]["reading"][zone] = on
    ctrl._save()
    return {"status": "ok", "message": f"阅读灯{zone}已{'开启' if on else '关闭'}", "reading": ctrl.vehicle_state["lights"]["reading"]}


def set_fog_lights(ctrl: VehicleController, fog_type: str, on: bool) -> dict[str, Any]:
    valid_types = ["front", "rear"]
    if fog_type not in valid_types:
        return {"status": "error", "message": f"雾灯类型必须是{valid_types}之一"}
    ctrl.vehicle_state["lights"]["fog"][fog_type] = on
    ctrl._save()
    return {"status": "ok", "message": f"{'前' if fog_type == 'front' else '后'}雾灯已{'开启' if on else '关闭'}", "fog": ctrl.vehicle_state["lights"]["fog"]}


def get_light_status(ctrl: VehicleController) -> dict[str, Any]:
    return {"status": "ok", "data": ctrl.vehicle_state["lights"]}
