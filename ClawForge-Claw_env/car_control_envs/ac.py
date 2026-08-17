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


def set_ac_power(ctrl: VehicleController, on: bool) -> dict[str, Any]:
    ctrl.vehicle_state["ac"]["power"] = on
    ctrl._save()
    return {"status": "ok", "message": f"空调已{'开启' if on else '关闭'}", "ac_power": on}


def set_ac_temperature(ctrl: VehicleController, temperature: int) -> dict[str, Any]:
    if not 16 <= temperature <= 30:
        return {"status": "error", "message": "温度范围为16-30度"}
    ctrl.vehicle_state["ac"]["temperature"] = temperature
    ctrl._save()
    return {"status": "ok", "message": f"温度已设置为{temperature}度", "temperature": temperature}


def set_ac_fan_speed(ctrl: VehicleController, speed: int) -> dict[str, Any]:
    if not 0 <= speed <= 5:
        return {"status": "error", "message": "风速范围为0-5"}
    ctrl.vehicle_state["ac"]["fan_speed"] = speed
    ctrl._save()
    return {"status": "ok", "message": f"风速已设置为{speed}档", "fan_speed": speed}


def set_ac_mode(ctrl: VehicleController, mode: str) -> dict[str, Any]:
    valid_modes = ["auto", "cool", "warm", "defog", "defrost"]
    if mode not in valid_modes:
        return {"status": "error", "message": f"模式必须是{valid_modes}之一"}
    ctrl.vehicle_state["ac"]["mode"] = mode
    ctrl._save()
    return {"status": "ok", "message": f"空调模式已设置为{mode}", "mode": mode}


def set_ac_direction(ctrl: VehicleController, direction: str) -> dict[str, Any]:
    valid_directions = ["face", "body", "foot", "face_body", "body_foot", "all"]
    if direction not in valid_directions:
        return {"status": "error", "message": f"风向必须是{valid_directions}之一"}
    ctrl.vehicle_state["ac"]["air_direction"] = direction
    ctrl._save()
    return {"status": "ok", "message": f"风向已设置为{direction}", "air_direction": direction}


def set_ac_circulation(ctrl: VehicleController, circulation: str) -> dict[str, Any]:
    valid_circulations = ["internal", "external", "auto"]
    if circulation not in valid_circulations:
        return {"status": "error", "message": f"循环模式必须是{valid_circulations}之一"}
    ctrl.vehicle_state["ac"]["circulation"] = circulation
    ctrl._save()
    return {"status": "ok", "message": f"循环模式已设置为{'内循环' if circulation == 'internal' else '外循环'}", "circulation": circulation}


def set_ac_defog(ctrl: VehicleController, on: bool) -> dict[str, Any]:
    ctrl.vehicle_state["ac"]["defog"] = on
    ctrl._save()
    return {"status": "ok", "message": f"除雾功能已{'开启' if on else '关闭'}", "defog": on}


def set_ac_defrost(ctrl: VehicleController, on: bool) -> dict[str, Any]:
    ctrl.vehicle_state["ac"]["defrost"] = on
    ctrl._save()
    return {"status": "ok", "message": f"除霜功能已{'开启' if on else '关闭'}", "defrost": on}


def get_ac_status(ctrl: VehicleController) -> dict[str, Any]:
    return {"status": "ok", "data": ctrl.vehicle_state["ac"]}
