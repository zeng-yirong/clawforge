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


def get_vehicle_status(ctrl: VehicleController, query_type: str | None = None) -> dict[str, Any]:
    if query_type == "tire_pressure":
        return {"status": "ok", "data": ctrl.vehicle_state["status"]["tire_pressure"]}
    elif query_type == "range":
        return {"status": "ok", "data": {"range": ctrl.vehicle_state["status"]["range"]}}
    elif query_type == "energy_consumption":
        return {"status": "ok", "data": {"energy_consumption": ctrl.vehicle_state["status"]["energy_consumption"]}}
    elif query_type == "oil_level":
        return {"status": "ok", "data": {"oil_level": ctrl.vehicle_state["status"]["oil_level"]}}
    elif query_type == "ac":
        return {"status": "ok", "data": ctrl.vehicle_state["ac"]}
    elif query_type == "seats":
        return {"status": "ok", "data": ctrl.vehicle_state["seats"]}
    elif query_type == "windows":
        return {"status": "ok", "data": ctrl.vehicle_state["windows"]}
    elif query_type == "lights":
        return {"status": "ok", "data": ctrl.vehicle_state["lights"]}
    elif query_type == "multimedia":
        return {"status": "ok", "data": ctrl.vehicle_state["multimedia"]}
    else:
        return {"status": "ok", "data": ctrl.vehicle_state["status"]}
