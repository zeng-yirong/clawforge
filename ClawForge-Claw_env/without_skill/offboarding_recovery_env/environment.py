from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from without_skill._shared.base_env import LoggedEnvironmentBase, utc_now_iso
from without_skill._shared.json_repository import load_json
from without_skill._shared.records import append_indexed_record, list_indexed_records, make_action_record_id


class OffboardingRepository:
    def __init__(self, data_root: str | Path | None = None):
        base_root = Path(data_root) if data_root is not None else Path(__file__).parent
        self.data_root = base_root.resolve()
        self.accounts_file = self.data_root / "data" / "accounts.json"
        self.contacts_file = self.data_root / "data" / "contacts.json"
        self.requests_file = self.data_root / "data" / "offboarding" / "exit_requests.json"
        self.access_file = self.data_root / "data" / "offboarding" / "system_access.json"
        self.equipment_file = self.data_root / "data" / "offboarding" / "equipment_assignments.json"
        self.scenario_dir = self.data_root / "data" / "scenarios"

    def load_accounts(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.accounts_file)
        return {item["account_id"]: item for item in payload["accounts"]}

    def load_contacts(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.contacts_file)
        return {item["contact_id"]: item for item in payload["contacts"]}

    def load_exit_requests(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.requests_file)
        return {item["employee_id"]: item for item in payload["exit_requests"]}

    def load_system_access(self) -> dict[str, list[dict[str, Any]]]:
        payload = load_json(self.access_file)
        mapping: dict[str, list[dict[str, Any]]] = {}
        for row in payload["system_access"]:
            mapping.setdefault(row["employee_id"], []).append(row)
        return mapping

    def load_equipment_assignments(self) -> dict[str, list[dict[str, Any]]]:
        payload = load_json(self.equipment_file)
        mapping: dict[str, list[dict[str, Any]]] = {}
        for row in payload["equipment_assignments"]:
            mapping.setdefault(row["employee_id"], []).append(row)
        return mapping

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        return load_json(self.scenario_dir / f"{scenario_id}.json")

    def list_scenarios(self) -> list[dict[str, Any]]:
        return [load_json(path) for path in sorted(self.scenario_dir.glob("*.json"))]


class OffboardingRecoveryEnvironment(LoggedEnvironmentBase):
    state_root_env_var = "OFFBOARDING_RECOVERY_STATE_ROOT"
    default_state_dir_name = ".offboarding_recovery_state"

    def __init__(self, *, data_root: str | Path | None = None, state_root: str | Path | None = None):
        self.repository = OffboardingRepository(data_root)
        super().__init__(state_root=state_root)
        self.accounts = self.repository.load_accounts()
        self.contacts = self.repository.load_contacts()

    def list_exit_requests(self, session_id: str, *, status: str | None = None) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> list[dict[str, Any]]:
            results = []
            for request in session["exit_requests"]:
                if status and str(request["approval_status"]).lower() != str(status).lower():
                    continue
                results.append(
                    {
                        "employee_id": request["employee_id"],
                        "employee_name": request["employee_name"],
                        "approval_status": request["approval_status"],
                    }
                )
                self._append_unique(session["observations"]["employee_ids_seen"], request["employee_id"])
            return results
        return self._run_logged_action(session_id, "list_exit_requests", {"status": status}, handler)

    def get_exit_request(self, session_id: str, employee_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            for request in session["exit_requests"]:
                if request["employee_id"] == employee_id:
                    self._append_unique(session["observations"]["employee_ids_seen"], employee_id)
                    return deepcopy(request)
            raise KeyError(f"Exit request not found: {employee_id}")
        return self._run_logged_action(session_id, "get_exit_request", {"employee_id": employee_id}, handler)

    def revoke_system_access(self, session_id: str, employee_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            rows = session["system_access"].get(employee_id, [])
            for row in rows:
                row["status"] = "revoked"
            self._append_unique(session["observations"]["revoked_employee_ids"], employee_id)
            return {"employee_id": employee_id, "revoked_count": len(rows)}
        return self._run_logged_action(session_id, "revoke_system_access", {"employee_id": employee_id}, handler)

    def reclaim_equipment(self, session_id: str, employee_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            rows = session["equipment_assignments"].get(employee_id, [])
            for row in rows:
                row["status"] = "returned"
            self._append_unique(session["observations"]["reclaimed_employee_ids"], employee_id)
            return {"employee_id": employee_id, "returned_count": len(rows)}
        return self._run_logged_action(session_id, "reclaim_equipment", {"employee_id": employee_id}, handler)

    def generate_handover_checklist(self, session_id: str, employee_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], event_at: str, action_index: int) -> dict[str, Any]:
            request = next((item for item in session["exit_requests"] if item["employee_id"] == employee_id), None)
            if request is None:
                raise KeyError(f"Exit request not found: {employee_id}")
            record = {
                "checklist_id": make_action_record_id("handover", action_index),
                "record_type": "offboarding_handover",
                "created_at": event_at,
                "employee_id": employee_id,
                "content": f"Offboarding checklist for {request['employee_name']}: revoke system access, reclaim assigned laptop and badge, confirm final knowledge transfer.",
            }
            append_indexed_record(
                session,
                collection_name="handover_records",
                index_name="handover_record_index",
                id_field="checklist_id",
                record=record,
            )
            return deepcopy(record)
        return self._run_logged_action(session_id, "generate_handover_checklist", {"employee_id": employee_id}, handler)

    def list_handover_records(self, session_id: str) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "list_handover_records",
            {},
            lambda session, _event_at, _action_index: list_indexed_records(
                session,
                collection_name="handover_records",
                summary_builder=lambda record: {
                    "checklist_id": record["checklist_id"],
                    "employee_id": record["employee_id"],
                    "created_at": record["created_at"],
                },
            ),
        )

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        from .evaluator import evaluate_session
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
        requests = self.repository.load_exit_requests()
        access = self.repository.load_system_access()
        equipment = self.repository.load_equipment_assignments()
        return {
            "session_id": session_id,
            "scenario_id": scenario["scenario_id"],
            "created_at": utc_now_iso(),
            "meta": {"base_time": scenario["current_time"], "action_index": 0},
            "workspace_account": deepcopy(self.accounts[scenario["workspace_account_id"]]),
            "exit_requests": [deepcopy(requests[eid]) for eid in scenario["employee_ids"]],
            "system_access": {eid: deepcopy(access[eid]) for eid in scenario["employee_ids"]},
            "equipment_assignments": {eid: deepcopy(equipment[eid]) for eid in scenario["employee_ids"]},
            "contacts": [deepcopy(item) for item in self.contacts.values()],
            "handover_records": [],
            "handover_record_index": {},
            "observations": {
                "employee_ids_seen": [],
                "revoked_employee_ids": [],
                "reclaimed_employee_ids": [],
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
            "exit_request_count": len(session["exit_requests"]),
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
            "exit_request_count": len(session["exit_requests"]),
            "handover_record_count": len(session["handover_records"]),
            "action_count": len(session["actions"]),
        }
