from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .repository import ItineraryRepository
from .store import SessionStore
from .planner import ItineraryController, search_routes, compare_transport, plan_transfer, generate_itinerary


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _action_timestamp(base_time: str, action_index: int) -> str:
    base = _coerce_iso_datetime(base_time)
    return (base + timedelta(seconds=action_index * 30)).isoformat()


class ItineraryEnvironment:
    def __init__(
        self,
        data_root: Path | str,
        state_root: Path | str,
    ):
        self.data_root = Path(data_root)
        self.state_root = Path(state_root)
        self.repo = ItineraryRepository(data_root)
        self.store = SessionStore(state_root)

    def _get_binding(self, key: str) -> str | None:
        env_key = f"ITINERARY_{key}"
        return os.environ.get(env_key)

    def prepare_rollout(self, scenario_id: str, show_bindings: bool = False) -> dict[str, Any]:
        scenario = self.repo.get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        base_time = scenario.get("base_time", _utc_now_iso())
        workspace_account_id = scenario.get("workspace_account_id", "acc_001")
        account = self.repo.get_account(workspace_account_id)
        if not account:
            raise ValueError(f"Account {workspace_account_id} not found")

        import uuid
        session_id = f"itin-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:4]}"

        state_root = str(self.state_root)
        self.store.create_session(
            session_id=session_id,
            scenario_id=scenario_id,
            base_time=base_time,
            workspace_account=account,
        )

        bindings = {
            "ITINERARY_SESSION_ID": session_id,
            "ITINERARY_STATE_ROOT": state_root,
            "ITINERARY_SCENARIO_ID": scenario_id,
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
        session = self.store.load_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        base_time = session["meta"]["base_time"]
        timestamp = _action_timestamp(base_time, action_index)

        ctrl = ItineraryController(session, self.store, session_id)
        result: dict[str, Any] = {"status": "ok"}

        if action_type == "load_cities":
            city_id = kwargs.get("city_id")
            if city_id:
                city = self.repo.get_city(city_id)
                if not city:
                    return {"status": "error", "message": f"City {city_id} not found"}
                result = {"status": "success", "data": city}
            else:
                cities = self.repo.list_cities()
                result = {"status": "success", "data": {"cities": cities}}
        elif action_type == "search_routes":
            origin = kwargs.get("origin")
            destination = kwargs.get("destination")
            if not origin or not destination:
                return {"status": "error", "message": "origin and destination are required"}
            result = search_routes(self.repo, origin, destination)
            if result.get("status") == "success":
                ctrl._update_itinerary_state({"origin": origin, "destination": destination})
        elif action_type == "compare_transport":
            route_result = kwargs.get("route_result")
            if not route_result:
                return {"status": "error", "message": "route_result is required"}
            result = compare_transport(route_result)
        elif action_type == "plan_transfer":
            origin = kwargs.get("origin")
            destination = kwargs.get("destination")
            waypoints = kwargs.get("waypoints", [])
            if not origin or not destination:
                return {"status": "error", "message": "origin and destination are required"}
            result = plan_transfer(self.repo, origin, destination, waypoints)
        elif action_type == "generate_itinerary":
            routes = kwargs.get("routes")
            preferences = kwargs.get("preferences", {})
            if not routes:
                return {"status": "error", "message": "routes is required"}
            result = generate_itinerary(ctrl, routes, preferences)
        elif action_type == "optimize_route":
            criteria = kwargs.get("criteria", "balanced")
            ctrl._update_itinerary_state({"route_preference": criteria})
            itinerary_state = ctrl._get_itinerary_state()
            itinerary = itinerary_state.get("generated_itinerary")
            if not itinerary:
                return {"status": "error", "message": "No itinerary generated yet"}
            result = {
                "status": "success",
                "data": {
                    "criteria": criteria,
                    "optimization_applied": True,
                    "itinerary": itinerary.get("data") if itinerary.get("data") else itinerary,
                },
            }
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

        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "itinerary_state": session["itinerary_state"],
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
