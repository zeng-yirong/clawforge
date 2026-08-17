from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from without_skill._shared.base_env import LoggedEnvironmentBase, utc_now_iso
from without_skill._shared.json_repository import load_json
from without_skill._shared.records import append_indexed_record, list_indexed_records, make_action_record_id


class ReproductionRepository:
    def __init__(self, data_root: str | Path | None = None):
        base_root = Path(data_root) if data_root is not None else Path(__file__).parent
        self.data_root = base_root.resolve()
        self.accounts_file = self.data_root / "data" / "accounts.json"
        self.contacts_file = self.data_root / "data" / "contacts.json"
        self.docs_file = self.data_root / "data" / "projects" / "project_docs.json"
        self.docs_dir = self.data_root / "data" / "project_docs"
        self.scenario_dir = self.data_root / "data" / "scenarios"

    def load_accounts(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.accounts_file)
        return {item["account_id"]: item for item in payload["accounts"]}

    def load_contacts(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.contacts_file)
        return {item["contact_id"]: item for item in payload["contacts"]}

    def load_project_docs(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.docs_file)
        return {item["doc_id"]: item for item in payload["project_docs"]}

    def read_doc(self, path: str) -> str:
        doc_path = self.docs_dir / path
        if not doc_path.exists():
            raise FileNotFoundError(f"Project doc not found: {path}")
        return doc_path.read_text(encoding="utf-8")

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        return load_json(self.scenario_dir / f"{scenario_id}.json")

    def list_scenarios(self) -> list[dict[str, Any]]:
        return [load_json(path) for path in sorted(self.scenario_dir.glob("*.json"))]


class ReproductionLedgerEnvironment(LoggedEnvironmentBase):
    state_root_env_var = "REPRODUCTION_LEDGER_STATE_ROOT"
    default_state_dir_name = ".reproduction_ledger_state"

    def __init__(self, *, data_root: str | Path | None = None, state_root: str | Path | None = None):
        self.repository = ReproductionRepository(data_root)
        super().__init__(state_root=state_root)
        self.accounts = self.repository.load_accounts()
        self.contacts = self.repository.load_contacts()

    def list_project_docs(self, session_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> list[dict[str, Any]]:
            return [{"doc_id": doc["doc_id"], "project_id": doc["project_id"], "title": doc["title"]} for doc in session["project_docs"]]
        return self._run_logged_action(session_id, "list_project_docs", {}, handler)

    def get_project_doc(self, session_id: str, doc_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            for doc in session["project_docs"]:
                if doc["doc_id"] == doc_id:
                    payload = deepcopy(doc)
                    payload["content"] = self.repository.read_doc(doc["path"])
                    self._append_unique(session["observations"]["doc_ids_seen"], doc_id)
                    return payload
            raise KeyError(f"Project doc not found: {doc_id}")
        return self._run_logged_action(session_id, "get_project_doc", {"doc_id": doc_id}, handler)

    def archive_reproduction_ledger(self, session_id: str, *, project_id: str, steps: str, result: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], event_at: str, action_index: int) -> dict[str, Any]:
            record = {
                "entry_id": make_action_record_id("repro", action_index),
                "record_type": "reproduction_ledger",
                "created_at": event_at,
                "project_id": project_id,
                "steps": steps,
                "result": result,
            }
            append_indexed_record(session, collection_name="knowledge_entries", index_name="knowledge_entry_index", id_field="entry_id", record=record)
            return deepcopy(record)
        return self._run_logged_action(session_id, "archive_reproduction_ledger", {"project_id": project_id}, handler)

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
                    "project_id": record["project_id"],
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
        all_docs = self.repository.load_project_docs()
        return {
            "session_id": session_id,
            "scenario_id": scenario["scenario_id"],
            "created_at": utc_now_iso(),
            "meta": {"base_time": scenario["current_time"], "action_index": 0},
            "workspace_account": deepcopy(self.accounts[scenario["workspace_account_id"]]),
            "project_docs": [deepcopy(all_docs[doc_id]) for doc_id in scenario["doc_ids"]],
            "contacts": [deepcopy(item) for item in self.contacts.values()],
            "knowledge_entries": [],
            "knowledge_entry_index": {},
            "observations": {
                "doc_ids_seen": [],
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
            "doc_count": len(session["project_docs"]),
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
            "doc_count": len(session["project_docs"]),
            "knowledge_entry_count": len(session["knowledge_entries"]),
            "action_count": len(session["actions"]),
        }
