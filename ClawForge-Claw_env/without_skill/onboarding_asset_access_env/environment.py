from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from without_skill._shared.base_env import LoggedEnvironmentBase, utc_now_iso
from without_skill._shared.json_repository import load_json
from without_skill._shared.records import append_indexed_record, list_indexed_records, make_action_record_id


class OnboardingRepository:
    def __init__(self, data_root: str | Path | None = None):
        base_root = Path(data_root) if data_root is not None else Path(__file__).parent
        self.data_root = base_root.resolve()
        self.accounts_file = self.data_root / "data" / "accounts.json"
        self.contacts_file = self.data_root / "data" / "contacts.json"
        self.contracts_file = self.data_root / "data" / "onboarding" / "contracts.json"
        self.access_file = self.data_root / "data" / "onboarding" / "permission_packs.json"
        self.equipment_file = self.data_root / "data" / "onboarding" / "equipment_inventory.json"
        self.scenario_dir = self.data_root / "data" / "scenarios"

    def load_accounts(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.accounts_file)
        return {item["account_id"]: item for item in payload["accounts"]}

    def load_contacts(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.contacts_file)
        return {item["contact_id"]: item for item in payload["contacts"]}

    def load_contracts(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.contracts_file)
        return {item["employee_id"]: item for item in payload["contracts"]}

    def load_permission_packs(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.access_file)
        return {item["pack_id"]: item for item in payload["permission_packs"]}

    def load_equipment_inventory(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.equipment_file)
        return {item["asset_tag"]: item for item in payload["equipment_inventory"]}

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        return load_json(self.scenario_dir / f"{scenario_id}.json")

    def list_scenarios(self) -> list[dict[str, Any]]:
        return [load_json(path) for path in sorted(self.scenario_dir.glob("*.json"))]


class OnboardingAssetAccessEnvironment(LoggedEnvironmentBase):
    state_root_env_var = "ONBOARDING_ASSET_ACCESS_STATE_ROOT"
    default_state_dir_name = ".onboarding_asset_access_state"

    def __init__(self, *, data_root: str | Path | None = None, state_root: str | Path | None = None):
        self.repository = OnboardingRepository(data_root)
        super().__init__(state_root=state_root)
        self.accounts = self.repository.load_accounts()
        self.contacts = self.repository.load_contacts()

    def list_contracts(self, session_id: str, *, status: str | None = None) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> list[dict[str, Any]]:
            results = []
            for contract in session["contracts"]:
                if status and str(contract["status"]).lower() != str(status).lower():
                    continue
                results.append({"employee_id": contract["employee_id"], "employee_name": contract["employee_name"], "status": contract["status"]})
                self._append_unique(session["observations"]["employee_ids_seen"], contract["employee_id"])
            return results
        return self._run_logged_action(session_id, "list_contracts", {"status": status}, handler)

    def get_contract(self, session_id: str, employee_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            for contract in session["contracts"]:
                if contract["employee_id"] == employee_id:
                    self._append_unique(session["observations"]["employee_ids_seen"], employee_id)
                    return deepcopy(contract)
            raise KeyError(f"Contract not found: {employee_id}")
        return self._run_logged_action(session_id, "get_contract", {"employee_id": employee_id}, handler)

    def create_email_profile(self, session_id: str, employee_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], event_at: str, action_index: int) -> dict[str, Any]:
            contract = next(item for item in session["contracts"] if item["employee_id"] == employee_id)
            record = {
                "email_profile_id": make_action_record_id("mail", action_index),
                "employee_id": employee_id,
                "email": contract["email"],
                "created_at": event_at,
            }
            append_indexed_record(session, collection_name="email_profiles", index_name="email_profile_index", id_field="email_profile_id", record=record)
            return deepcopy(record)
        return self._run_logged_action(session_id, "create_email_profile", {"employee_id": employee_id}, handler)

    def assign_system_access(self, session_id: str, employee_id: str, pack_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], event_at: str, action_index: int) -> dict[str, Any]:
            pack = deepcopy(session["permission_packs"][pack_id])
            record = {
                "access_assignment_id": make_action_record_id("access", action_index),
                "employee_id": employee_id,
                "pack_id": pack_id,
                "systems": pack["systems"],
                "created_at": event_at,
            }
            append_indexed_record(session, collection_name="access_assignments", index_name="access_assignment_index", id_field="access_assignment_id", record=record)
            return deepcopy(record)
        return self._run_logged_action(session_id, "assign_system_access", {"employee_id": employee_id, "pack_id": pack_id}, handler)

    def allocate_equipment(self, session_id: str, employee_id: str, asset_tag: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], event_at: str, action_index: int) -> dict[str, Any]:
            asset = session["equipment_inventory"][asset_tag]
            asset["status"] = "allocated"
            record = {
                "allocation_id": make_action_record_id("equip", action_index),
                "employee_id": employee_id,
                "asset_tag": asset_tag,
                "created_at": event_at,
            }
            append_indexed_record(session, collection_name="equipment_allocations", index_name="equipment_allocation_index", id_field="allocation_id", record=record)
            return deepcopy(record)
        return self._run_logged_action(session_id, "allocate_equipment", {"employee_id": employee_id, "asset_tag": asset_tag}, handler)

    def post_welcome_message(self, session_id: str, employee_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], event_at: str, action_index: int) -> dict[str, Any]:
            contract = next(item for item in session["contracts"] if item["employee_id"] == employee_id)
            record = {
                "message_id": make_action_record_id("slack", action_index),
                "employee_id": employee_id,
                "created_at": event_at,
                "content": f"Welcome {contract['employee_name']} to the team. Your mailbox, system access, and starter device are ready.",
            }
            append_indexed_record(session, collection_name="slack_cache", index_name="slack_cache_index", id_field="message_id", record=record)
            return deepcopy(record)
        return self._run_logged_action(session_id, "post_welcome_message", {"employee_id": employee_id}, handler)

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        from .evaluator import evaluate_session
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
        contracts = self.repository.load_contracts()
        permission_packs = self.repository.load_permission_packs()
        equipment = self.repository.load_equipment_inventory()
        return {
            "session_id": session_id,
            "scenario_id": scenario["scenario_id"],
            "created_at": utc_now_iso(),
            "meta": {"base_time": scenario["current_time"], "action_index": 0},
            "workspace_account": deepcopy(self.accounts[scenario["workspace_account_id"]]),
            "contracts": [deepcopy(contracts[eid]) for eid in scenario["employee_ids"]],
            "permission_packs": deepcopy(permission_packs),
            "equipment_inventory": deepcopy(equipment),
            "contacts": [deepcopy(item) for item in self.contacts.values()],
            "email_profiles": [],
            "email_profile_index": {},
            "access_assignments": [],
            "access_assignment_index": {},
            "equipment_allocations": [],
            "equipment_allocation_index": {},
            "slack_cache": [],
            "slack_cache_index": {},
            "observations": {
                "employee_ids_seen": [],
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
            "contract_count": len(session["contracts"]),
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
            "email_profile_count": len(session["email_profiles"]),
            "access_assignment_count": len(session["access_assignments"]),
            "equipment_allocation_count": len(session["equipment_allocations"]),
            "slack_message_count": len(session["slack_cache"]),
            "action_count": len(session["actions"]),
        }
