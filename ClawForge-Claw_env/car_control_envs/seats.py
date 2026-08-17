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


def adjust_seat_position(ctrl: VehicleController, zone: str, position: int) -> dict[str, Any]:
    valid_zones = ["fl", "fr", "rl", "rr", "rc"]
    if zone not in valid_zones:
        return {"status": "error", "message": f"区域必须是{valid_zones}之一"}
    if not 0 <= position <= 100:
        return {"status": "error", "message": "位置范围为0-100"}
    ctrl.vehicle_state["seats"][zone]["position"] = position
    ctrl._save()
    return {"status": "ok", "message": f"{zone}位置已调整为{position}", "zone": zone, "position": position}


def adjust_seat_recline(ctrl: VehicleController, zone: str, recline: int) -> dict[str, Any]:
    valid_zones = ["fl", "fr", "rl", "rr", "rc"]
    if zone not in valid_zones:
        return {"status": "error", "message": f"区域必须是{valid_zones}之一"}
    if not 0 <= recline <= 100:
        return {"status": "error", "message": "靠背角度范围为0-100"}
    ctrl.vehicle_state["seats"][zone]["recline"] = recline
    ctrl._save()
    return {"status": "ok", "message": f"{zone}靠背角度已调整为{recline}", "zone": zone, "recline": recline}


def adjust_seat_lumbar(ctrl: VehicleController, zone: str, lumbar: int) -> dict[str, Any]:
    valid_zones = ["fl", "fr", "rl", "rr", "rc"]
    if zone not in valid_zones:
        return {"status": "error", "message": f"区域必须是{valid_zones}之一"}
    if not 0 <= lumbar <= 100:
        return {"status": "error", "message": "腰托力度范围为0-100"}
    ctrl.vehicle_state["seats"][zone]["lumbar"] = lumbar
    ctrl._save()
    return {"status": "ok", "message": f"{zone}腰托力度已调整为{lumbar}", "zone": zone, "lumbar": lumbar}


def set_seat_heating(ctrl: VehicleController, zone: str, level: int) -> dict[str, Any]:
    valid_zones = ["fl", "fr", "rl", "rr", "rc"]
    if zone not in valid_zones:
        return {"status": "error", "message": f"区域必须是{valid_zones}之一"}
    if not 0 <= level <= 3:
        return {"status": "error", "message": "加热档位范围为0-3"}
    ctrl.vehicle_state["seats"][zone]["heating"] = level
    ctrl._save()
    return {"status": "ok", "message": f"{zone}座椅加热已设置为{level}档", "zone": zone, "heating": level}


def set_seat_ventilation(ctrl: VehicleController, zone: str, level: int) -> dict[str, Any]:
    valid_zones = ["fl", "fr", "rl", "rr", "rc"]
    if zone not in valid_zones:
        return {"status": "error", "message": f"区域必须是{valid_zones}之一"}
    if not 0 <= level <= 3:
        return {"status": "error", "message": "通风档位范围为0-3"}
    ctrl.vehicle_state["seats"][zone]["ventilation"] = level
    ctrl._save()
    return {"status": "ok", "message": f"{zone}座椅通风已设置为{level}档", "zone": zone, "ventilation": level}


def get_seat_status(ctrl: VehicleController, zone: str | None = None) -> dict[str, Any]:
    if zone:
        valid_zones = ["fl", "fr", "rl", "rr", "rc"]
        if zone not in valid_zones:
            return {"status": "error", "message": f"区域必须是{valid_zones}之一"}
        return {"status": "ok", "data": ctrl.vehicle_state["seats"][zone]}
    return {"status": "ok", "data": ctrl.vehicle_state["seats"]}
