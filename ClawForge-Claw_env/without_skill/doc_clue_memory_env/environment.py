from __future__ import annotations

import os
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from .evaluator import evaluate_session
from .library import (
    get_media_sample,
    get_presentation,
    get_report,
    list_media_samples,
    list_presentations,
    list_reports,
    search_library,
)
from .records import get_temp_record, list_temp_records, save_clue_list as do_save_clue_list
from .repository import DatasetRepository
from .store import SessionStore


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_iso_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


class DocumentClueMemoryEnvironment:
    def __init__(
        self,
        *,
        data_root: str | Path | None = None,
        state_root: str | Path | None = None,
    ):
        default_state_root = Path(os.getenv("DOC_CLUE_MEMORY_STATE_ROOT", Path.cwd() / ".doc_clue_memory_state"))
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

    def list_reports(
        self,
        session_id: str,
        *,
        query: str = "",
        sector: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "list_reports",
            {"query": query, "sector": sector},
            lambda session, _event_at, _action_index: list_reports(
                session,
                query=query,
                sector=sector,
                limit=limit,
            ),
        )

    def get_report(self, session_id: str, report_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            payload = get_report(session, report_id)
            self._observe_document(session, payload["document_id"], payload["source_type"])
            return payload

        return self._run_logged_action(session_id, "get_report", {"report_id": report_id}, handler)

    def list_presentations(
        self,
        session_id: str,
        *,
        query: str = "",
        owner: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "list_presentations",
            {"query": query, "owner": owner},
            lambda session, _event_at, _action_index: list_presentations(
                session,
                query=query,
                owner=owner,
                limit=limit,
            ),
        )

    def get_presentation(self, session_id: str, presentation_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            payload = get_presentation(session, presentation_id)
            self._observe_document(session, payload["document_id"], payload["source_type"])
            return payload

        return self._run_logged_action(
            session_id,
            "get_presentation",
            {"presentation_id": presentation_id},
            handler,
        )

    def list_media_samples(
        self,
        session_id: str,
        *,
        query: str = "",
        channel: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "list_media_samples",
            {"query": query, "channel": channel},
            lambda session, _event_at, _action_index: list_media_samples(
                session,
                query=query,
                channel=channel,
                limit=limit,
            ),
        )

    def get_media_sample(self, session_id: str, sample_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            payload = get_media_sample(session, sample_id)
            self._observe_document(session, payload["document_id"], payload["source_type"])
            return payload

        return self._run_logged_action(session_id, "get_media_sample", {"sample_id": sample_id}, handler)

    def search_library(
        self,
        session_id: str,
        *,
        query: str,
        source_type: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> list[dict[str, Any]]:
            if query not in session["observations"]["queries_run"]:
                session["observations"]["queries_run"].append(query)
            return search_library(session, query=query, source_type=source_type, limit=limit)

        return self._run_logged_action(
            session_id,
            "search_library",
            {"query": query, "source_type": source_type},
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

    def save_clue_list(
        self,
        session_id: str,
        *,
        solution_id: str,
        solution_name: str,
        document_ids: list[str],
        clues: list[str],
        summary: str,
        confidence: str = "medium",
    ) -> dict[str, Any]:
        def handler(session: dict[str, Any], event_at: str, action_index: int) -> dict[str, Any]:
            return do_save_clue_list(
                session,
                solution_id=solution_id,
                solution_name=solution_name,
                document_ids=document_ids,
                clues=clues,
                summary=summary,
                confidence=confidence,
                event_at=event_at,
                action_index=action_index,
            )

        return self._run_logged_action(
            session_id,
            "save_clue_list",
            {"solution_id": solution_id, "document_ids": document_ids, "confidence": confidence},
            handler,
        )

    def list_temp_records(
        self,
        session_id: str,
        *,
        record_type: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "list_temp_records",
            {"record_type": record_type},
            lambda session, _event_at, _action_index: list_temp_records(
                session,
                record_type=record_type,
                limit=limit,
            ),
        )

    def get_temp_record(self, session_id: str, record_id: str) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "get_temp_record",
            {"record_id": record_id},
            lambda session, _event_at, _action_index: get_temp_record(session, record_id),
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
            "reports_count": len(session["reports"]),
            "presentations_count": len(session["presentations"]),
            "media_samples_count": len(session["media_samples"]),
            "temp_records_count": len(session["temp_records"]),
            "action_count": len(session.get("actions", [])),
        }

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
        all_reports = self.repository.load_reports()
        all_presentations = self.repository.load_presentations()
        all_media_samples = self.repository.load_media_samples()

        reports = [
            deepcopy(all_reports[report_id])
            for report_id in scenario["report_ids"]
            if report_id in all_reports
        ]
        presentations = [
            deepcopy(all_presentations[presentation_id])
            for presentation_id in scenario["presentation_ids"]
            if presentation_id in all_presentations
        ]
        media_samples = [
            deepcopy(all_media_samples[sample_id])
            for sample_id in scenario["media_sample_ids"]
            if sample_id in all_media_samples
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
            "reports": reports,
            "presentations": presentations,
            "media_samples": media_samples,
            "attachments": attachments,
            "contacts": [deepcopy(item) for item in self.contacts.values()],
            "temp_records": [],
            "temp_record_index": {},
            "observations": {
                "document_ids_seen": [],
                "source_types_seen": [],
                "attachments_read": [],
                "queries_run": [],
                "temp_record_ids": [],
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
            "target_solution_id": scenario["target_solution_id"],
            "target_solution_name": scenario["target_solution_name"],
            "target_solution_aliases": scenario.get("target_solution_aliases", []),
            "report_count": len(session["reports"]),
            "presentation_count": len(session["presentations"]),
            "media_sample_count": len(session["media_samples"]),
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

    def _observe_document(self, session: dict[str, Any], document_id: str, source_type: str) -> None:
        self._append_unique(session["observations"]["document_ids_seen"], document_id)
        self._append_unique(session["observations"]["source_types_seen"], source_type)
