from __future__ import annotations

import os
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from .evaluator import evaluate_session
from .ledger import get_cluster, get_ledger_entry, list_clusters, list_ledger_entries
from .pricing import get_pricing_catalog, list_pricing_catalogs
from .reports import (
    aggregate_cluster_usage as do_aggregate_cluster_usage,
    generate_cost_report as do_generate_cost_report,
    get_cache_entry,
    list_cache_entries,
)
from .repository import DatasetRepository
from .store import SessionStore


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_iso_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


class CloudCostLedgerEnvironment:
    def __init__(
        self,
        *,
        data_root: str | Path | None = None,
        state_root: str | Path | None = None,
    ):
        default_state_root = Path(
            os.getenv("CLOUD_COST_LEDGER_STATE_ROOT", Path.cwd() / ".cloud_cost_ledger_state")
        )
        self.repository = DatasetRepository(data_root)
        self.store = SessionStore(state_root or default_state_root)
        self.accounts = self.repository.load_accounts()
        self.contacts = self.repository.load_contacts()
        self.attachment_manifest = self.repository.load_attachment_manifest()

    def list_scenarios(self) -> dict[str, Any]:
        return {
            "scenarios": [
                {
                    "scenario_id": item["scenario_id"],
                    "title": item["title"],
                    "task_prompt": item["task_prompt"],
                }
                for item in self.repository.list_scenarios()
            ]
        }

    def create_session(self, session_id: str, scenario_id: str, overwrite: bool = False) -> dict[str, Any]:
        scenario = self.repository.load_scenario(scenario_id)
        session_payload = self._build_session_payload(session_id=session_id, scenario=scenario)
        self.store.create_session(session_id, session_payload, overwrite=overwrite)
        return self.session_summary(session_id)

    def reset_session(self, session_id: str) -> dict[str, Any]:
        existing = self.store.load_session(session_id)
        return self.create_session(session_id, existing["scenario_id"], overwrite=True)

    def get_task(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return self._build_task_payload(session_id, session, scenario)

    def view_task(self, session_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            scenario = self.repository.load_scenario(session["scenario_id"])
            return self._build_task_payload(session_id, session, scenario)

        return self._run_logged_action(session_id, "task", {}, handler)

    def list_clusters(
        self,
        session_id: str,
        *,
        query: str = "",
        domain: str | None = None,
        cluster_role: str | None = None,
        environment: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> list[dict[str, Any]]:
            data = list_clusters(
                session,
                query=query,
                domain=domain,
                cluster_role=cluster_role,
                environment=environment,
                limit=limit,
            )
            for item in data:
                self._append_unique(session["observations"]["cluster_ids_seen"], str(item["cluster_id"]))
            return data

        return self._run_logged_action(
            session_id,
            "list_clusters",
            {
                "query": query,
                "domain": domain,
                "cluster_role": cluster_role,
                "environment": environment,
            },
            handler,
        )

    def get_cluster(self, session_id: str, cluster_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            payload = get_cluster(session, cluster_id)
            self._append_unique(session["observations"]["cluster_ids_seen"], cluster_id)
            return payload

        return self._run_logged_action(session_id, "get_cluster", {"cluster_id": cluster_id}, handler)

    def list_ledger_entries(
        self,
        session_id: str,
        *,
        cluster_id: str | None = None,
        resource_family: str | None = None,
        metric_code: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> list[dict[str, Any]]:
            data = list_ledger_entries(
                session,
                cluster_id=cluster_id,
                resource_family=resource_family,
                metric_code=metric_code,
                limit=limit,
            )
            for item in data:
                self._append_unique(session["observations"]["ledger_entry_ids_seen"], str(item["entry_id"]))
                self._append_unique(session["observations"]["cluster_ids_seen"], str(item["cluster_id"]))
            return data

        return self._run_logged_action(
            session_id,
            "list_ledger_entries",
            {
                "cluster_id": cluster_id,
                "resource_family": resource_family,
                "metric_code": metric_code,
            },
            handler,
        )

    def get_ledger_entry(self, session_id: str, entry_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            payload = get_ledger_entry(session, entry_id)
            self._append_unique(session["observations"]["ledger_entry_ids_seen"], entry_id)
            self._append_unique(session["observations"]["cluster_ids_seen"], str(payload["cluster_id"]))
            return payload

        return self._run_logged_action(session_id, "get_ledger_entry", {"entry_id": entry_id}, handler)

    def list_pricing_catalogs(
        self,
        session_id: str,
        *,
        status: str | None = None,
        current_only: bool = False,
    ) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "list_pricing_catalogs",
            {"status": status, "current_only": current_only},
            lambda session, _event_at, _action_index: list_pricing_catalogs(
                session,
                status=status,
                current_only=current_only,
            ),
        )

    def get_pricing_catalog(self, session_id: str, catalog_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            payload = get_pricing_catalog(session, catalog_id)
            self._append_unique(session["observations"]["pricing_catalog_ids_seen"], catalog_id)
            return payload

        return self._run_logged_action(
            session_id,
            "get_pricing_catalog",
            {"catalog_id": catalog_id},
            handler,
        )

    def list_attachments(self, session_id: str) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "list_attachments",
            {},
            lambda session, _event_at, _action_index: deepcopy(session["attachments"]),
        )

    def read_attachment(self, session_id: str, attachment_path: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            if attachment_path not in self.attachment_manifest:
                raise FileNotFoundError(f"Attachment not found: {attachment_path}")
            metadata = deepcopy(self.attachment_manifest[attachment_path])
            metadata["content"] = self.repository.read_attachment(attachment_path)
            self._append_unique(session["observations"]["attachments_read"], attachment_path)
            return metadata

        return self._run_logged_action(
            session_id,
            "read_attachment",
            {"attachment_path": attachment_path},
            handler,
        )

    def aggregate_cluster_usage(self, session_id: str, cluster_id: str) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "aggregate_cluster_usage",
            {"cluster_id": cluster_id},
            lambda session, event_at, action_index: do_aggregate_cluster_usage(
                session,
                cluster_id,
                event_at,
                action_index,
            ),
        )

    def generate_cost_report(
        self,
        session_id: str,
        catalog_id: str,
        *,
        cluster_ids: list[str] | None = None,
        billing_month: str | None = None,
    ) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "generate_cost_report",
            {"catalog_id": catalog_id, "cluster_ids": cluster_ids, "billing_month": billing_month},
            lambda session, event_at, action_index: do_generate_cost_report(
                session,
                catalog_id,
                event_at,
                action_index,
                cluster_ids=cluster_ids,
                billing_month=billing_month,
            ),
        )

    def list_cache(
        self,
        session_id: str,
        *,
        entry_type: str | None = None,
        cache_key: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "list_cache",
            {"entry_type": entry_type, "cache_key": cache_key},
            lambda session, _event_at, _action_index: list_cache_entries(
                session,
                entry_type=entry_type,
                cache_key=cache_key,
                limit=limit,
            ),
        )

    def get_cache_entry(self, session_id: str, entry_id: str) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "get_cache_entry",
            {"entry_id": entry_id},
            lambda session, _event_at, _action_index: get_cache_entry(session, entry_id),
        )

    def session_summary(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        aggregate_count = len(
            [item for item in session["cache"]["entries"] if item["entry_type"] == "cluster_usage_aggregate"]
        )
        report_count = len(
            [item for item in session["cache"]["entries"] if item["entry_type"] == "monthly_cost_detail_report"]
        )
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "workspace_account": session["workspace_account"],
            "state_root": str(self.store.state_root),
            "clusters_count": len(session["clusters"]),
            "ledger_entries_count": len(session["ledger_entries"]),
            "pricing_catalogs_count": len(session["pricing_catalogs"]),
            "cache_entries_count": len(session["cache"]["entries"]),
            "aggregate_count": aggregate_count,
            "report_count": report_count,
            "action_count": len(session.get("actions", [])),
        }

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
        all_clusters = self.repository.load_clusters()
        all_ledger_entries = self.repository.load_resource_ledger()
        all_pricing_catalogs = self.repository.load_pricing_catalogs()

        clusters = [
            deepcopy(all_clusters[cluster_id])
            for cluster_id in scenario["cluster_ids"]
            if cluster_id in all_clusters
        ]
        cluster_id_set = {item["cluster_id"] for item in clusters}
        ledger_entries = [
            deepcopy(all_ledger_entries[entry_id])
            for entry_id in scenario.get("ledger_entry_ids", [])
            if entry_id in all_ledger_entries
        ]
        if not ledger_entries:
            ledger_entries = [
                deepcopy(entry)
                for entry in all_ledger_entries.values()
                if entry["cluster_id"] in cluster_id_set
            ]
        pricing_catalogs = [
            deepcopy(all_pricing_catalogs[catalog_id])
            for catalog_id in scenario["pricing_catalog_ids"]
            if catalog_id in all_pricing_catalogs
        ]
        attachments = [
            deepcopy(self.attachment_manifest[path])
            for path in scenario.get("attachment_paths", [])
            if path in self.attachment_manifest
        ]

        return {
            "session_id": session_id,
            "scenario_id": scenario["scenario_id"],
            "created_at": _utc_now_iso(),
            "meta": {
                "base_time": scenario["current_time"],
                "action_index": 0,
            },
            "workspace_account": deepcopy(self.accounts[scenario["workspace_account_id"]]),
            "clusters": clusters,
            "ledger_entries": ledger_entries,
            "pricing_catalogs": pricing_catalogs,
            "attachments": attachments,
            "contacts": [deepcopy(item) for item in self.contacts.values()],
            "cache": {
                "entries": [],
                "latest": {},
            },
            "observations": {
                "cluster_ids_seen": [],
                "ledger_entry_ids_seen": [],
                "pricing_catalog_ids_seen": [],
                "attachments_read": [],
                "cache_entry_ids": [],
                "aggregated_cluster_ids": [],
            },
            "actions": [],
        }

    def _build_task_payload(
        self,
        session_id: str,
        session: dict[str, Any],
        scenario: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "task_prompt": scenario["task_prompt"],
            "workspace_account": session["workspace_account"],
            "billing_month": scenario["billing_month"],
            "target_cluster_ids": scenario["target_cluster_ids"],
            "excluded_cluster_ids": scenario.get("excluded_cluster_ids", []),
            "active_pricing_catalog_id": scenario["active_pricing_catalog_id"],
            "cluster_count": len(session["clusters"]),
            "ledger_entries_count": len(session["ledger_entries"]),
        }

    def _run_logged_action(
        self,
        session_id: str,
        action_type: str,
        details: dict[str, Any],
        handler: Callable[[dict[str, Any], str, int], Any],
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            data = handler(session, event_at, action_index)
            self._record_action(session, action_index, event_at, action_type, details)
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": data}

    def _next_event(self, session: dict[str, Any]) -> tuple[str, int]:
        action_index = int(session["meta"]["action_index"]) + 1
        session["meta"]["action_index"] = action_index
        event_at = (_coerce_iso_datetime(session["meta"]["base_time"]) + timedelta(minutes=action_index)).isoformat()
        return event_at, action_index

    def _record_action(
        self,
        session: dict[str, Any],
        action_index: int,
        event_at: str,
        action_type: str,
        details: dict[str, Any],
    ) -> None:
        session["actions"].append(
            {
                "action_index": action_index,
                "timestamp": event_at,
                "action_type": action_type,
                "details": details,
            }
        )

    def _append_unique(self, items: list[str], value: str) -> None:
        if value not in items:
            items.append(value)
