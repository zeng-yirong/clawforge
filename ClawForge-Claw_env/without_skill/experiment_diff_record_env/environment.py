from __future__ import annotations

import csv
from copy import deepcopy
from pathlib import Path
from typing import Any

from without_skill._shared.base_env import LoggedEnvironmentBase, utc_now_iso
from without_skill._shared.json_repository import load_json
from without_skill._shared.records import append_indexed_record, get_indexed_record, list_indexed_records, make_action_record_id


class ExperimentRepository:
    def __init__(self, data_root: str | Path | None = None):
        base_root = Path(data_root) if data_root is not None else Path(__file__).parent
        self.data_root = base_root.resolve()
        self.accounts_file = self.data_root / "data" / "accounts.json"
        self.contacts_file = self.data_root / "data" / "contacts.json"
        self.results_file = self.data_root / "data" / "experiments" / "experiment_results.csv"
        self.scenario_dir = self.data_root / "data" / "scenarios"

    def load_accounts(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.accounts_file)
        return {item["account_id"]: item for item in payload["accounts"]}

    def load_contacts(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.contacts_file)
        return {item["contact_id"]: item for item in payload["contacts"]}

    def load_results(self) -> list[dict[str, str]]:
        with self.results_file.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        return load_json(self.scenario_dir / f"{scenario_id}.json")

    def list_scenarios(self) -> list[dict[str, Any]]:
        return [load_json(path) for path in sorted(self.scenario_dir.glob("*.json"))]


class ExperimentDiffRecordEnvironment(LoggedEnvironmentBase):
    state_root_env_var = "EXPERIMENT_DIFF_RECORD_STATE_ROOT"
    default_state_dir_name = ".experiment_diff_record_state"

    def __init__(self, *, data_root: str | Path | None = None, state_root: str | Path | None = None):
        self.repository = ExperimentRepository(data_root)
        super().__init__(state_root=state_root)
        self.accounts = self.repository.load_accounts()
        self.contacts = self.repository.load_contacts()

    def list_experiment_batches(self, session_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> list[dict[str, Any]]:
            batches = sorted({row["batch_id"] for row in session["results"]})
            return [{"batch_id": batch_id} for batch_id in batches]
        return self._run_logged_action(session_id, "list_experiment_batches", {}, handler)

    def get_batch(self, session_id: str, batch_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            rows = [deepcopy(row) for row in session["results"] if row["batch_id"] == batch_id]
            if not rows:
                raise KeyError(f"Batch not found: {batch_id}")
            self._append_unique(session["observations"]["batch_ids_seen"], batch_id)
            return {"batch_id": batch_id, "rows": rows}
        return self._run_logged_action(session_id, "get_batch", {"batch_id": batch_id}, handler)

    def generate_diff_record(self, session_id: str, *, batch_ids: list[str]) -> dict[str, Any]:
        def handler(session: dict[str, Any], event_at: str, action_index: int) -> dict[str, Any]:
            selected = [row for row in session["results"] if row["batch_id"] in batch_ids]
            if not selected:
                raise ValueError("No experiment rows selected.")
            grouped: dict[str, dict[str, float]] = {}
            for row in selected:
                batch = row["batch_id"]
                grouped[batch] = {
                    "accuracy": float(row["accuracy"]),
                    "latency_ms": float(row["latency_ms"]),
                    "cost_usd": float(row["cost_usd"]),
                }
                self._append_unique(session["observations"]["batch_ids_seen"], batch)
            baseline, contender = batch_ids[0], batch_ids[1]
            diff = {
                "accuracy_delta": round(grouped[contender]["accuracy"] - grouped[baseline]["accuracy"], 3),
                "latency_delta": round(grouped[contender]["latency_ms"] - grouped[baseline]["latency_ms"], 1),
                "cost_delta": round(grouped[contender]["cost_usd"] - grouped[baseline]["cost_usd"], 2),
            }
            record = {
                "record_id": make_action_record_id("expdiff", action_index),
                "record_type": "experiment_diff_record",
                "created_at": event_at,
                "batch_ids": batch_ids,
                "diff": diff,
            }
            append_indexed_record(
                session,
                collection_name="records",
                index_name="record_index",
                id_field="record_id",
                record=record,
            )
            return deepcopy(record)
        return self._run_logged_action(session_id, "generate_diff_record", {"batch_ids": batch_ids}, handler)

    def list_records(self, session_id: str) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "list_records",
            {},
            lambda session, _event_at, _action_index: list_indexed_records(
                session,
                collection_name="records",
                summary_builder=lambda record: {
                    "record_id": record["record_id"],
                    "batch_ids": record["batch_ids"],
                    "diff": record["diff"],
                },
            ),
        )

    def get_record(self, session_id: str, record_id: str) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "get_record",
            {"record_id": record_id},
            lambda session, _event_at, _action_index: get_indexed_record(
                session,
                collection_name="records",
                index_name="record_index",
                record_id=record_id,
                error_label="Record",
            ),
        )

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        from .evaluator import evaluate_session
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
        return {
            "session_id": session_id,
            "scenario_id": scenario["scenario_id"],
            "created_at": utc_now_iso(),
            "meta": {"base_time": scenario["current_time"], "action_index": 0},
            "workspace_account": deepcopy(self.accounts[scenario["workspace_account_id"]]),
            "results": self.repository.load_results(),
            "contacts": [deepcopy(item) for item in self.contacts.values()],
            "records": [],
            "record_index": {},
            "observations": {
                "batch_ids_seen": [],
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
            "result_row_count": len(session["results"]),
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
            "result_row_count": len(session["results"]),
            "record_count": len(session["records"]),
            "action_count": len(session["actions"]),
        }
