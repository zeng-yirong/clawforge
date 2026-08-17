from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from without_skill._shared.base_env import LoggedEnvironmentBase, utc_now_iso
from without_skill._shared.json_repository import load_json
from without_skill._shared.records import append_indexed_record, list_indexed_records, make_action_record_id


class FaultRepository:
    def __init__(self, data_root: str | Path | None = None):
        base_root = Path(data_root) if data_root is not None else Path(__file__).parent
        self.data_root = base_root.resolve()
        self.accounts_file = self.data_root / "data" / "accounts.json"
        self.contacts_file = self.data_root / "data" / "contacts.json"
        self.attachments_file = self.data_root / "data" / "attachments.json"
        self.faults_file = self.data_root / "data" / "faults" / "fault_cases.json"
        self.attachments_dir = self.data_root / "data" / "attachments"
        self.scenario_dir = self.data_root / "data" / "scenarios"

    def load_accounts(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.accounts_file)
        return {item["account_id"]: item for item in payload["accounts"]}

    def load_contacts(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.contacts_file)
        return {item["contact_id"]: item for item in payload["contacts"]}

    def load_attachment_manifest(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.attachments_file)
        return {item["path"]: item for item in payload["attachments"]}

    def load_fault_cases(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.faults_file)
        return {item["fault_id"]: item for item in payload["fault_cases"]}

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        return load_json(self.scenario_dir / f"{scenario_id}.json")

    def list_scenarios(self) -> list[dict[str, Any]]:
        return [load_json(path) for path in sorted(self.scenario_dir.glob("*.json"))]

    def read_attachment(self, relative_path: str) -> str:
        attachment_path = self.attachments_dir / relative_path
        if not attachment_path.exists():
            raise FileNotFoundError(f"Attachment not found: {relative_path}")
        return attachment_path.read_text(encoding="utf-8")


class FaultPostmortemKbEnvironment(LoggedEnvironmentBase):
    state_root_env_var = "FAULT_POSTMORTEM_KB_STATE_ROOT"
    default_state_dir_name = ".fault_postmortem_kb_state"

    def __init__(self, *, data_root: str | Path | None = None, state_root: str | Path | None = None):
        self.repository = FaultRepository(data_root)
        super().__init__(state_root=state_root)
        self.accounts = self.repository.load_accounts()
        self.contacts = self.repository.load_contacts()
        self.attachment_manifest = self.repository.load_attachment_manifest()

    def list_fault_cases(self, session_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> list[dict[str, Any]]:
            return [
                {
                    "fault_id": item["fault_id"],
                    "service_name": item["service_name"],
                    "severity": item["severity"],
                }
                for item in session["fault_cases"]
            ]
        return self._run_logged_action(session_id, "list_fault_cases", {}, handler)

    def get_fault_case(self, session_id: str, fault_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            for item in session["fault_cases"]:
                if item["fault_id"] == fault_id:
                    self._append_unique(session["observations"]["fault_ids_seen"], fault_id)
                    return deepcopy(item)
            raise KeyError(f"Fault case not found: {fault_id}")
        return self._run_logged_action(session_id, "get_fault_case", {"fault_id": fault_id}, handler)

    def read_attachment(self, session_id: str, attachment_path: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            metadata = deepcopy(self.attachment_manifest[attachment_path])
            metadata["content"] = self.repository.read_attachment(attachment_path)
            self._append_unique(session["observations"]["attachments_read"], attachment_path)
            return metadata
        return self._run_logged_action(session_id, "read_attachment", {"attachment_path": attachment_path}, handler)

    def generate_postmortem(self, session_id: str, fault_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], event_at: str, action_index: int) -> dict[str, Any]:
            case = next(item for item in session["fault_cases"] if item["fault_id"] == fault_id)
            record = {
                "entry_id": make_action_record_id("kb", action_index),
                "record_type": "fault_postmortem",
                "created_at": event_at,
                "fault_id": fault_id,
                "service_name": case["service_name"],
                "root_cause": case["root_cause_hint"],
                "repair_plan": case["repair_plan_hint"],
                "markdown": f"# Postmortem {fault_id}\n\n## Root Cause\n{case['root_cause_hint']}\n\n## Repair Plan\n{case['repair_plan_hint']}",
            }
            append_indexed_record(session, collection_name="knowledge_entries", index_name="knowledge_entry_index", id_field="entry_id", record=record)
            return deepcopy(record)
        return self._run_logged_action(session_id, "generate_postmortem", {"fault_id": fault_id}, handler)

    def list_knowledge_entries(self, session_id: str) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "list_knowledge_entries",
            {},
            lambda session, _event_at, _action_index: list_indexed_records(
                session,
                collection_name="knowledge_entries",
                summary_builder=lambda record: {
                    "entry_id": record["entry_id"],
                    "fault_id": record["fault_id"],
                    "service_name": record["service_name"],
                },
            ),
        )

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        from .evaluator import evaluate_session
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
        all_faults = self.repository.load_fault_cases()
        attachments = [deepcopy(self.attachment_manifest[path]) for path in scenario.get("attachment_paths", []) if path in self.attachment_manifest]
        return {
            "session_id": session_id,
            "scenario_id": scenario["scenario_id"],
            "created_at": utc_now_iso(),
            "meta": {"base_time": scenario["current_time"], "action_index": 0},
            "workspace_account": deepcopy(self.accounts[scenario["workspace_account_id"]]),
            "fault_cases": [deepcopy(all_faults[fid]) for fid in scenario["fault_ids"]],
            "attachments": attachments,
            "contacts": [deepcopy(item) for item in self.contacts.values()],
            "knowledge_entries": [],
            "knowledge_entry_index": {},
            "observations": {
                "fault_ids_seen": [],
                "attachments_read": [],
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
            "fault_case_count": len(session["fault_cases"]),
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
            "fault_case_count": len(session["fault_cases"]),
            "knowledge_entry_count": len(session["knowledge_entries"]),
            "action_count": len(session["actions"]),
        }
