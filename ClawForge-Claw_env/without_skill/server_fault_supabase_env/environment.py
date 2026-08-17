from __future__ import annotations

import os
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from .audit import append_audit_log, get_audit_log, list_audit_logs
from .evaluator import evaluate_session
from .incident_pool import get_incident, list_incidents, screen_risk_incidents
from .repository import DatasetRepository
from .response_logic import batch_remediate as do_batch_remediate
from .response_logic import execute_fault_remediation as do_execute_fault_remediation
from .store import SessionStore
from .supabase_memory import get_supabase_row, insert_incident_resolution, list_supabase_rows


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_iso_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


class ServerFaultSupabaseEnvironment:
    def __init__(
        self,
        *,
        data_root: str | Path | None = None,
        state_root: str | Path | None = None,
    ):
        default_state_root = Path(
            os.getenv("SERVER_FAULT_SUPABASE_STATE_ROOT", Path.cwd() / ".server_fault_supabase_state")
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

    def list_incidents(
        self,
        session_id: str,
        *,
        query: str = "",
        category: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "list_incidents",
            {"query": query, "category": category, "severity": severity, "status": status},
            lambda session, _event_at, _action_index: list_incidents(
                session,
                query=query,
                category=category,
                severity=severity,
                status=status,
                limit=limit,
            ),
        )

    def get_incident(self, session_id: str, incident_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            payload = get_incident(session, incident_id)
            self._append_unique(session["observations"]["incident_ids_seen"], incident_id)
            return payload

        return self._run_logged_action(session_id, "get_incident", {"incident_id": incident_id}, handler)

    def screen_risk_incidents(
        self,
        session_id: str,
        *,
        categories: list[str] | None = None,
        statuses: list[str] | None = None,
        severities: list[str] | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> list[dict[str, Any]]:
            data = screen_risk_incidents(
                session,
                categories=categories,
                statuses=statuses,
                severities=severities,
                limit=limit,
            )
            for item in data:
                self._append_unique(session["observations"]["screened_incident_ids"], item["incident_id"])
            return data

        return self._run_logged_action(
            session_id,
            "screen_risk_incidents",
            {"categories": categories, "statuses": statuses, "severities": severities},
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

    def remediate_incident(
        self,
        session_id: str,
        incident_id: str,
        *,
        remediation_mode: str,
        operator_note: str,
    ) -> dict[str, Any]:
        def handler(session: dict[str, Any], event_at: str, action_index: int) -> dict[str, Any]:
            payload = do_execute_fault_remediation(
                session,
                incident_id,
                remediation_mode=remediation_mode,
                operator_note=operator_note,
                event_at=event_at,
                action_index=action_index,
            )
            self._append_unique(session["observations"]["remediated_incident_ids"], incident_id)
            return payload

        return self._run_logged_action(
            session_id,
            "remediate_incident",
            {"incident_id": incident_id, "remediation_mode": remediation_mode},
            handler,
        )

    def batch_remediate(
        self,
        session_id: str,
        incident_ids: list[str],
        *,
        remediation_mode: str,
        operator_note: str,
    ) -> dict[str, Any]:
        def handler(session: dict[str, Any], event_at: str, action_index: int) -> dict[str, Any]:
            payload = do_batch_remediate(
                session,
                incident_ids,
                remediation_mode=remediation_mode,
                operator_note=operator_note,
                event_at=event_at,
                action_index=action_index,
            )
            for incident_id in incident_ids:
                self._append_unique(session["observations"]["remediated_incident_ids"], incident_id)
            return payload

        return self._run_logged_action(
            session_id,
            "batch_remediate",
            {"incident_ids": incident_ids, "remediation_mode": remediation_mode},
            handler,
        )

    def write_supabase_resolution(
        self,
        session_id: str,
        incident_id: str,
        *,
        table_name: str = "incident_resolutions",
    ) -> dict[str, Any]:
        def handler(session: dict[str, Any], event_at: str, action_index: int) -> dict[str, Any]:
            incident = get_incident(session, incident_id)
            if incident["status"] not in {"resolved", "mitigated"}:
                raise ValueError(f"Incident {incident_id} must be remediated before writing to Supabase memory.")
            return insert_incident_resolution(
                session,
                incident_id=incident_id,
                table_name=table_name,
                service=incident["service"],
                category=incident["category"],
                severity=incident["severity"],
                resolution_state=incident["resolution_state"],
                remediation_mode=incident["remediation_mode"],
                operator_note=incident["operator_note"],
                written_at=event_at,
                action_index=action_index,
            )

        return self._run_logged_action(
            session_id,
            "write_supabase_resolution",
            {"incident_id": incident_id, "table_name": table_name},
            handler,
        )

    def list_supabase_rows(
        self,
        session_id: str,
        *,
        table_name: str | None = None,
        incident_id: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "list_supabase_rows",
            {"table_name": table_name, "incident_id": incident_id},
            lambda session, _event_at, _action_index: list_supabase_rows(
                session,
                table_name=table_name,
                incident_id=incident_id,
                limit=limit,
            ),
        )

    def get_supabase_row(self, session_id: str, row_id: str) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "get_supabase_row",
            {"row_id": row_id},
            lambda session, _event_at, _action_index: get_supabase_row(session, row_id),
        )

    def list_audit_logs(
        self,
        session_id: str,
        *,
        action_type: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "list_audit_logs",
            {"action_type": action_type},
            lambda session, _event_at, _action_index: list_audit_logs(
                session,
                action_type=action_type,
                limit=limit,
            ),
        )

    def get_audit_log(self, session_id: str, audit_id: str) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "get_audit_log",
            {"audit_id": audit_id},
            lambda session, _event_at, _action_index: get_audit_log(session, audit_id),
        )

    def session_summary(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "workspace_account": session["workspace_account"],
            "state_root": str(self.store.state_root),
            "incidents_count": len(session["incidents"]),
            "supabase_rows_count": len(session["supabase_memory"]["incident_resolutions"]),
            "audit_logs_count": len(session["audit_logs"]),
            "action_count": len(session.get("actions", [])),
        }

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
        all_incidents = self.repository.load_incidents()
        incidents = [
            deepcopy(all_incidents[incident_id])
            for incident_id in scenario["incident_ids"]
            if incident_id in all_incidents
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
            "incidents": incidents,
            "attachments": attachments,
            "contacts": [deepcopy(item) for item in self.contacts.values()],
            "supabase_memory": {
                "incident_resolutions": [],
                "row_index": {},
            },
            "audit_logs": [],
            "audit_index": {},
            "observations": {
                "incident_ids_seen": [],
                "screened_incident_ids": [],
                "remediated_incident_ids": [],
                "attachments_read": [],
                "supabase_row_ids": [],
                "audit_ids": [],
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
            "target_categories": scenario.get("target_categories", []),
            "target_statuses": scenario.get("target_statuses", []),
            "incident_count": len(session["incidents"]),
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
            append_audit_log(
                session,
                action_index=action_index,
                event_at=event_at,
                action_type=action_type,
                details=details,
            )
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
