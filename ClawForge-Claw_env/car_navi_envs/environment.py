from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .repository import NavigationRepository
from .store import SessionStore
from .navi import NaviController, start_navigation, search_poi, add_waypoint, remove_waypoint, set_route_preference, reroute, arrive_waypoint, arrive_destination, cancel_navigation
from .traffic import query_traffic, get_traffic_status
from .charging import plan_charging, check_range_sufficiency


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _action_timestamp(base_time: str, action_index: int) -> str:
    base = _coerce_iso_datetime(base_time)
    return (base + timedelta(seconds=action_index * 30)).isoformat()


class NaviEnvironment:
    def __init__(
        self,
        data_root: Path | str,
        state_root: Path | str,
    ):
        self.data_root = Path(data_root)
        self.state_root = Path(state_root)
        self.repo = NavigationRepository(data_root)
        self.store = SessionStore(state_root)

    def _get_binding(self, key: str) -> str | None:
        env_key = f"CAR_NAVI_{key}"
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
        session_id = f"navi-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:4]}"

        state_root = str(self.state_root)
        self.store.create_session(
            session_id=session_id,
            scenario_id=scenario_id,
            base_time=base_time,
            workspace_account=account,
        )

        bindings = {
            "CAR_NAVI_SESSION_ID": session_id,
            "CAR_NAVI_STATE_ROOT": state_root,
            "CAR_NAVI_SCENARIO_ID": scenario_id,
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

        ctrl = NaviController(session, self.store, session_id)
        result: dict[str, Any] = {"status": "ok"}

        if action_type == "search_poi":
            category = kwargs.get("category")
            keyword = kwargs.get("keyword")
            result = search_poi(self.repo, category=category, keyword=keyword)
        elif action_type == "start_navigation":
            poi_id = kwargs.get("poi_id")
            result = start_navigation(ctrl, poi_id, self.repo)
        elif action_type == "add_waypoint":
            poi_id = kwargs.get("poi_id")
            result = add_waypoint(ctrl, poi_id, self.repo)
        elif action_type == "remove_waypoint":
            waypoint_index = kwargs.get("waypoint_index", 0)
            result = remove_waypoint(ctrl, waypoint_index)
        elif action_type == "route_preference":
            preference = kwargs.get("preference", "fastest")
            result = set_route_preference(ctrl, preference, self.repo)
        elif action_type == "reroute":
            result = reroute(ctrl)
        elif action_type == "traffic_query":
            query_type = kwargs.get("query_type")
            result = query_traffic(query_type)
        elif action_type == "traffic_status":
            result = get_traffic_status()
        elif action_type == "charging_plan":
            target_charge = kwargs.get("target_charge", 80)
            max_stops = kwargs.get("max_stops", 3)
            result = plan_charging(
                session.get("workspace_account", {}).get("current_charge", 50),
                target_charge,
                max_stops,
                self.repo,
            )
        elif action_type == "arrive_waypoint":
            waypoint_index = kwargs.get("waypoint_index", 0)
            result = arrive_waypoint(ctrl, waypoint_index)
        elif action_type == "arrive_destination":
            result = arrive_destination(ctrl)
        elif action_type == "cancel_navigation":
            result = cancel_navigation(ctrl)
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
            "navigation_state": session["navigation_state"],
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
