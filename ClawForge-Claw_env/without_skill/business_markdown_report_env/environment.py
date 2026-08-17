from __future__ import annotations

import csv
from copy import deepcopy
from pathlib import Path
from typing import Any

from without_skill._shared.base_env import utc_now_iso
from without_skill._shared.cache import append_cache_entry
from without_skill._shared.cache_env import CacheArtifactEnvironmentBase
from without_skill._shared.json_repository import load_json


class BusinessReportRepository:
    def __init__(self, data_root: str | Path | None = None):
        base_root = Path(data_root) if data_root is not None else Path(__file__).parent
        self.data_root = base_root.resolve()
        self.accounts_file = self.data_root / "data" / "accounts.json"
        self.contacts_file = self.data_root / "data" / "contacts.json"
        self.attachments_file = self.data_root / "data" / "attachments.json"
        self.ledgers_dir = self.data_root / "data" / "ledgers"
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

    def load_ledgers(self) -> dict[str, list[dict[str, str]]]:
        ledgers: dict[str, list[dict[str, str]]] = {}
        for path in sorted(self.ledgers_dir.glob("*.csv")):
            with path.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            ledgers[path.stem] = rows
        return ledgers

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        return load_json(self.scenario_dir / f"{scenario_id}.json")

    def list_scenarios(self) -> list[dict[str, Any]]:
        return [load_json(path) for path in sorted(self.scenario_dir.glob("*.json"))]

    def read_attachment(self, relative_path: str) -> str:
        attachment_path = self.attachments_dir / relative_path
        if not attachment_path.exists():
            raise FileNotFoundError(f"Attachment not found: {relative_path}")
        return attachment_path.read_text(encoding="utf-8")


class BusinessMarkdownReportEnvironment(CacheArtifactEnvironmentBase):
    state_root_env_var = "BUSINESS_MARKDOWN_REPORT_STATE_ROOT"
    default_state_dir_name = ".business_markdown_report_state"

    def __init__(self, *, data_root: str | Path | None = None, state_root: str | Path | None = None):
        self.repository = BusinessReportRepository(data_root)
        super().__init__(state_root=state_root)
        self.accounts = self.repository.load_accounts()
        self.contacts = self.repository.load_contacts()
        self.attachment_manifest = self.repository.load_attachment_manifest()

    def list_ledgers(self, session_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> list[dict[str, Any]]:
            return [
                {"ledger_name": name, "row_count": len(rows)}
                for name, rows in sorted(session["ledgers"].items())
            ]
        return self._run_logged_action(session_id, "list_ledgers", {}, handler)

    def preview_ledger(self, session_id: str, ledger_name: str, *, limit: int | None = 5) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            if ledger_name not in session["ledgers"]:
                raise KeyError(f"Ledger not found: {ledger_name}")
            self._append_unique(session["observations"]["ledger_names_seen"], ledger_name)
            return {"ledger_name": ledger_name, "rows": deepcopy(session["ledgers"][ledger_name][:limit])}
        return self._run_logged_action(session_id, "preview_ledger", {"ledger_name": ledger_name}, handler)

    def aggregate_period_metrics(self, session_id: str, period: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            totals: dict[str, float] = {}
            for ledger_name, rows in session["ledgers"].items():
                self._append_unique(session["observations"]["ledger_names_seen"], ledger_name)
                for row in rows:
                    if row["period"] != period:
                        continue
                    metric = row["metric_code"]
                    totals[metric] = totals.get(metric, 0.0) + float(row["metric_value"])
            return {"period": period, "totals": {k: round(v, 2) for k, v in totals.items()}}
        return self._run_logged_action(session_id, "aggregate_period_metrics", {"period": period}, handler)

    def generate_markdown_report(self, session_id: str, period: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], event_at: str, action_index: int) -> dict[str, Any]:
            totals: dict[str, float] = {}
            for ledger_name, rows in session["ledgers"].items():
                self._append_unique(session["observations"]["ledger_names_seen"], ledger_name)
                for row in rows:
                    if row["period"] != period:
                        continue
                    metric = row["metric_code"]
                    totals[metric] = totals.get(metric, 0.0) + float(row["metric_value"])
            lines = [f"# Weekly Business Report: {period}", "", "| Metric | Value |", "| --- | ---: |"]
            rounded_totals = {k: round(v, 2) for k, v in totals.items()}
            for metric, value in sorted(rounded_totals.items()):
                lines.append(f"| {metric} | {value} |")
            payload = {
                "period": period,
                "metrics": rounded_totals,
                "markdown": "\n".join(lines),
            }
            entry = append_cache_entry(
                session,
                cache_key=f"business_report::{period}",
                entry_type="business_markdown_report",
                payload=payload,
                event_at=event_at,
                action_index=action_index,
            )
            self._append_unique(session["observations"]["cache_entry_ids"], entry["entry_id"])
            return entry
        return self._run_logged_action(session_id, "generate_markdown_report", {"period": period}, handler)

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        from .evaluator import evaluate_session
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
        attachments = [
            deepcopy(self.attachment_manifest[path])
            for path in scenario.get("attachment_paths", [])
            if path in self.attachment_manifest
        ]
        return {
            "session_id": session_id,
            "scenario_id": scenario["scenario_id"],
            "created_at": utc_now_iso(),
            "meta": {"base_time": scenario["current_time"], "action_index": 0},
            "workspace_account": deepcopy(self.accounts[scenario["workspace_account_id"]]),
            "ledgers": self.repository.load_ledgers(),
            "attachments": attachments,
            "contacts": [deepcopy(item) for item in self.contacts.values()],
            "cache": {"entries": [], "latest": {}},
            "observations": {
                "ledger_names_seen": [],
                "attachments_read": [],
                "cache_entry_ids": [],
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
            "ledger_count": len(session["ledgers"]),
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
            "ledger_count": len(session["ledgers"]),
            "cache_entries_count": len(session["cache"]["entries"]),
            "action_count": len(session["actions"]),
        }
