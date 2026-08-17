from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .repository import ExpenseRepository
from .store import SessionStore
from .budget import ExpenseController, calculate_budget, apply_policy_rules
from .analysis import generate_analysis, categorize_expenses, identify_overruns


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _action_timestamp(base_time: str, action_index: int) -> str:
    base = _coerce_iso_datetime(base_time)
    return (base + timedelta(seconds=action_index * 30)).isoformat()


class ExpenseEnvironment:
    def __init__(
        self,
        data_root: Path | str,
        state_root: Path | str,
    ):
        self.data_root = Path(data_root)
        self.state_root = Path(state_root)
        self.repo = ExpenseRepository(data_root)
        self.store = SessionStore(state_root)

    def _get_binding(self, key: str) -> str | None:
        env_key = f"EXPENSE_{key}"
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
        session_id = f"exp-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:4]}"

        state_root = str(self.state_root)
        self.store.create_session(
            session_id=session_id,
            scenario_id=scenario_id,
            base_time=base_time,
            workspace_account=account,
        )

        bindings = {
            "EXPENSE_SESSION_ID": session_id,
            "EXPENSE_STATE_ROOT": state_root,
            "EXPENSE_SCENARIO_ID": scenario_id,
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

        ctrl = ExpenseController(session, self.store, session_id)
        result: dict[str, Any] = {"status": "ok"}

        if action_type == "load_policy":
            tier = kwargs.get("tier")
            if not tier:
                tier = session.get("expense_state", {}).get("policy_tier")
            if not tier:
                return {"status": "error", "message": "No policy tier specified"}
            policy = self.repo.get_travel_policy(tier)
            if not policy:
                return {"status": "error", "message": f"Policy tier {tier} not found"}
            ctrl._update_expense_state({"policy_tier": tier})
            result = {"status": "success", "data": {"policy_tier": tier, "policy": policy}}
        elif action_type == "calculate_budget":
            expense_state = ctrl._get_expense_state()
            tier = expense_state.get("policy_tier") or kwargs.get("tier")
            destination = kwargs.get("destination") or expense_state.get("destination")
            duration_days = kwargs.get("duration_days") or expense_state.get("duration_days")
            if not tier:
                return {"status": "error", "message": "No policy tier specified"}
            if not destination:
                return {"status": "error", "message": "No destination specified"}
            if not duration_days:
                return {"status": "error", "message": "No duration_days specified"}
            budget_result = calculate_budget(self.repo, tier, destination, duration_days)
            ctrl._update_expense_state({
                "policy_tier": tier,
                "destination": destination,
                "duration_days": duration_days,
                "calculated_budget": budget_result,
            })
            result = budget_result
        elif action_type == "load_consumption":
            trip_id = kwargs.get("trip_id")
            if not trip_id:
                return {"status": "error", "message": "No trip_id specified"}
            records = self.repo.get_consumption_records(trip_id)
            if not records:
                return {"status": "error", "message": f"Consumption records for trip {trip_id} not found"}
            ctrl._update_expense_state({"loaded_consumption": records})
            categorized = categorize_expenses(records.get("records", []))
            result = {"status": "success", "data": {"trip_id": trip_id, "record_count": len(records.get("records", [])), "categorized": {k: len(v) for k, v in categorized.items()}}}
        elif action_type == "generate_analysis":
            result = generate_analysis(ctrl, self.repo)
        elif action_type == "export_report":
            expense_state = ctrl._get_expense_state()
            analysis = expense_state.get("analysis_result")
            budget = expense_state.get("calculated_budget")
            consumption = expense_state.get("loaded_consumption")
            if not analysis:
                return {"status": "error", "message": "No analysis available. Run generate_analysis first."}
            report = {
                "status": "success",
                "data": {
                    "budget": budget.get("data") if budget else None,
                    "consumption": consumption,
                    "analysis": analysis.get("data") if analysis else None,
                    "export_timestamp": _utc_now_iso(),
                },
            }
            ctrl._update_expense_state({"report_generated": True})
            result = report
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
            "expense_state": session["expense_state"],
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
