from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from without_skill._shared.base_env import LoggedEnvironmentBase, utc_now_iso
from without_skill._shared.json_repository import load_json
from without_skill._shared.records import append_indexed_record, get_indexed_record, list_indexed_records, make_action_record_id


class PerformanceRepository:
    def __init__(self, data_root: str | Path | None = None):
        base_root = Path(data_root) if data_root is not None else Path(__file__).parent
        self.data_root = base_root.resolve()
        self.accounts_file = self.data_root / "data" / "accounts.json"
        self.contacts_file = self.data_root / "data" / "contacts.json"
        self.employees_file = self.data_root / "data" / "employees" / "employees.json"
        self.outputs_file = self.data_root / "data" / "ledgers" / "monthly_outputs.json"
        self.rules_file = self.data_root / "data" / "rules" / "scoring_rules.json"
        self.scenario_dir = self.data_root / "data" / "scenarios"

    def load_accounts(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.accounts_file)
        return {item["account_id"]: item for item in payload["accounts"]}

    def load_contacts(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.contacts_file)
        return {item["contact_id"]: item for item in payload["contacts"]}

    def load_employees(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.employees_file)
        return {item["employee_id"]: item for item in payload["employees"]}

    def load_outputs(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.outputs_file)
        return {item["employee_id"]: item for item in payload["monthly_outputs"]}

    def load_rules(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.rules_file)
        return {item["role_code"]: item for item in payload["scoring_rules"]}

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        return load_json(self.scenario_dir / f"{scenario_id}.json")

    def list_scenarios(self) -> list[dict[str, Any]]:
        return [load_json(path) for path in sorted(self.scenario_dir.glob("*.json"))]


class PerformanceReviewEnvironment(LoggedEnvironmentBase):
    state_root_env_var = "PERFORMANCE_REVIEW_STATE_ROOT"
    default_state_dir_name = ".performance_review_state"

    def __init__(self, *, data_root: str | Path | None = None, state_root: str | Path | None = None):
        self.repository = PerformanceRepository(data_root)
        super().__init__(state_root=state_root)
        self.accounts = self.repository.load_accounts()
        self.contacts = self.repository.load_contacts()

    def list_employees(self, session_id: str, *, department: str | None = None, limit: int | None = None) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> list[dict[str, Any]]:
            results: list[dict[str, Any]] = []
            for employee in session["employees"]:
                if department and str(employee["department"]).lower() != str(department).lower():
                    continue
                results.append(
                    {
                        "employee_id": employee["employee_id"],
                        "employee_name": employee["employee_name"],
                        "department": employee["department"],
                        "role_code": employee["role_code"],
                    }
                )
                self._append_unique(session["observations"]["employee_ids_seen"], employee["employee_id"])
            return results[:limit] if limit is not None else results
        return self._run_logged_action(session_id, "list_employees", {"department": department}, handler)

    def get_employee(self, session_id: str, employee_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            for employee in session["employees"]:
                if employee["employee_id"] == employee_id:
                    self._append_unique(session["observations"]["employee_ids_seen"], employee_id)
                    return deepcopy(employee)
            raise KeyError(f"Employee not found: {employee_id}")
        return self._run_logged_action(session_id, "get_employee", {"employee_id": employee_id}, handler)

    def get_output_ledger(self, session_id: str, employee_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            if employee_id not in session["monthly_outputs"]:
                raise KeyError(f"Monthly output ledger not found: {employee_id}")
            self._append_unique(session["observations"]["employee_ids_seen"], employee_id)
            return deepcopy(session["monthly_outputs"][employee_id])
        return self._run_logged_action(session_id, "get_output_ledger", {"employee_id": employee_id}, handler)

    def get_scoring_rule(self, session_id: str, role_code: str) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "get_scoring_rule",
            {"role_code": role_code},
            lambda session, _event_at, _action_index: deepcopy(session["scoring_rules"][role_code]),
        )

    def generate_performance_profile(self, session_id: str, employee_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], event_at: str, action_index: int) -> dict[str, Any]:
            employee = next((item for item in session["employees"] if item["employee_id"] == employee_id), None)
            if employee is None:
                raise KeyError(f"Employee not found: {employee_id}")
            output = session["monthly_outputs"][employee_id]
            rule = session["scoring_rules"][employee["role_code"]]
            score = (
                float(output["feature_delivery"]) * float(rule["feature_delivery_weight"])
                + float(output["quality_score"]) * float(rule["quality_weight"])
                + float(output["collaboration_score"]) * float(rule["collaboration_weight"])
            )
            profile = {
                "profile_id": make_action_record_id("perf", action_index),
                "record_type": "performance_profile",
                "created_at": event_at,
                "employee_id": employee_id,
                "employee_name": employee["employee_name"],
                "role_code": employee["role_code"],
                "score": round(score, 2),
                "performance_band": "exceeds" if score >= 85 else "meets" if score >= 70 else "needs_support",
            }
            append_indexed_record(
                session,
                collection_name="performance_profiles",
                index_name="performance_profile_index",
                id_field="profile_id",
                record=profile,
            )
            self._append_unique(session["observations"]["profile_employee_ids"], employee_id)
            return deepcopy(profile)
        return self._run_logged_action(session_id, "generate_performance_profile", {"employee_id": employee_id}, handler)

    def list_performance_profiles(self, session_id: str) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "list_performance_profiles",
            {},
            lambda session, _event_at, _action_index: list_indexed_records(
                session,
                collection_name="performance_profiles",
                summary_builder=lambda record: {
                    "profile_id": record["profile_id"],
                    "employee_id": record["employee_id"],
                    "score": record["score"],
                    "performance_band": record["performance_band"],
                },
            ),
        )

    def get_performance_profile(self, session_id: str, profile_id: str) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "get_performance_profile",
            {"profile_id": profile_id},
            lambda session, _event_at, _action_index: get_indexed_record(
                session,
                collection_name="performance_profiles",
                index_name="performance_profile_index",
                record_id=profile_id,
                error_label="Performance profile",
            ),
        )

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        from .evaluator import evaluate_session
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
        all_employees = self.repository.load_employees()
        all_outputs = self.repository.load_outputs()
        rules = self.repository.load_rules()
        return {
            "session_id": session_id,
            "scenario_id": scenario["scenario_id"],
            "created_at": utc_now_iso(),
            "meta": {"base_time": scenario["current_time"], "action_index": 0},
            "workspace_account": deepcopy(self.accounts[scenario["workspace_account_id"]]),
            "employees": [deepcopy(all_employees[eid]) for eid in scenario["employee_ids"]],
            "monthly_outputs": {eid: deepcopy(all_outputs[eid]) for eid in scenario["employee_ids"]},
            "scoring_rules": deepcopy(rules),
            "contacts": [deepcopy(item) for item in self.contacts.values()],
            "performance_profiles": [],
            "performance_profile_index": {},
            "observations": {
                "employee_ids_seen": [],
                "profile_employee_ids": [],
            },
            "actions": [],
        }

    def _build_task_payload(self, session_id: str, session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "task_prompt": scenario["task_prompt"],
            "workspace_account": session["workspace_account"],
            "employee_count": len(session["employees"]),
        }

    def session_summary(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "workspace_account": session["workspace_account"],
            "state_root": str(self.store.state_root),
            "employee_count": len(session["employees"]),
            "profile_count": len(session["performance_profiles"]),
            "action_count": len(session["actions"]),
        }
