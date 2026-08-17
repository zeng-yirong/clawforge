from __future__ import annotations

import os
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .contacts import add_tags_to_contact, archive_contact, classify_contact, get_contact, list_contacts, remove_tags_from_contact, search_contacts
from .reminders import create_birthday_reminder, disable_reminder, enable_reminder, list_reminders
from .repository import DatasetRepository
from .store import SessionStore
from .tags import get_or_create_tag, list_tag_definitions


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_iso_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


class CRMEnvironment:
    def __init__(
        self,
        *,
        data_root: str | Path | None = None,
        state_root: str | Path | None = None,
    ):
        default_state_root = Path(os.getenv("CRM_STATE_ROOT", Path.cwd() / ".crm_state"))
        self.repository = DatasetRepository(data_root)
        self.store = SessionStore(state_root or default_state_root)
        self.accounts = self.repository.load_accounts()

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
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "task_prompt": scenario["task_prompt"],
            "workspace_account": session["workspace_account"],
        }

    def list_contacts(
        self,
        session_id: str,
        *,
        query: str = "",
        folder: str | None = None,
        contact_type: str | None = None,
        tag: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_contacts(
                session,
                query=query,
                folder=folder,
                contact_type=contact_type,
                tag=tag,
                limit=limit,
            ),
        }

    def get_contact(self, session_id: str, contact_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_contact(session, contact_id)}

    def classify_contact(
        self,
        session_id: str,
        contact_id: str,
        target_folder: str,
        target_tags: list[str],
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = classify_contact(session, contact_id, target_folder, target_tags, event_at, action_index)
            self._record_action(
                session,
                action_index,
                event_at,
                "classify_contact",
                {"contact_id": contact_id, "target_folder": target_folder, "target_tags": target_tags},
            )
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def add_tags(
        self,
        session_id: str,
        contact_id: str,
        tags_to_add: list[str],
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = add_tags_to_contact(session, contact_id, tags_to_add, event_at, action_index)
            self._record_action(
                session,
                action_index,
                event_at,
                "add_tags",
                {"contact_id": contact_id, "tags_added": tags_to_add},
            )
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def remove_tags(
        self,
        session_id: str,
        contact_id: str,
        tags_to_remove: list[str],
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = remove_tags_from_contact(session, contact_id, tags_to_remove, event_at, action_index)
            self._record_action(
                session,
                action_index,
                event_at,
                "remove_tags",
                {"contact_id": contact_id, "tags_removed": tags_to_remove},
            )
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def archive_contact(self, session_id: str, contact_id: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = archive_contact(session, contact_id, event_at, action_index)
            self._record_action(
                session,
                action_index,
                event_at,
                "archive_contact",
                {"contact_id": contact_id},
            )
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def search_contacts(
        self,
        session_id: str,
        *,
        name_query: str = "",
        email_query: str = "",
        company_id: str | None = None,
        tag: str | None = None,
        folder: str | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": search_contacts(
                session,
                name_query=name_query,
                email_query=email_query,
                company_id=company_id,
                tag=tag,
                folder=folder,
            ),
        }

    def list_reminders(
        self,
        session_id: str,
        *,
        contact_id: str | None = None,
        reminder_type: str | None = None,
        upcoming_only: bool = False,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_reminders(
                session,
                contact_id=contact_id,
                reminder_type=reminder_type,
                upcoming_only=upcoming_only,
                limit=limit,
            ),
        }

    def create_birthday_reminder(
        self,
        session_id: str,
        contact_id: str,
        days_before: int = 7,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            contact = get_contact(session, contact_id)
            payload = create_birthday_reminder(
                session,
                contact_id=contact_id,
                contact_name=contact["full_name"],
                birthday=contact["birthday"],
                days_before=days_before,
                event_at=event_at,
                action_index=action_index,
            )
            self._record_action(
                session,
                action_index,
                event_at,
                "create_birthday_reminder",
                {"contact_id": contact_id, "reminder_id": payload["reminder_id"]},
            )
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def enable_reminder(self, session_id: str, reminder_id: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = enable_reminder(session, reminder_id, event_at, action_index)
            self._record_action(
                session,
                action_index,
                event_at,
                "enable_reminder",
                {"reminder_id": reminder_id},
            )
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def disable_reminder(self, session_id: str, reminder_id: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = disable_reminder(session, reminder_id, event_at, action_index)
            self._record_action(
                session,
                action_index,
                event_at,
                "disable_reminder",
                {"reminder_id": reminder_id},
            )
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def list_tags(self, session_id: str, *, category: str | None = None) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_tag_definitions(session, category=category),
        }

    def get_or_create_tag(self, session_id: str, tag_name: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = get_or_create_tag(session, tag_name, event_at, action_index)
            self._record_action(
                session,
                action_index,
                event_at,
                "get_or_create_tag",
                {"tag_name": tag_name, "tag_id": payload.get("tag_id")},
            )
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def session_summary(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        contacts = session["crm"]["contacts"]
        reminders = session["crm"]["reminders"]
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "workspace_account": session["workspace_account"],
            "state_root": str(self.store.state_root),
            "total_contacts": len(contacts),
            "business_contacts": sum(1 for c in contacts if c["folder"] == "business"),
            "personal_contacts": sum(1 for c in contacts if c["folder"] == "personal"),
            "archived_contacts": sum(1 for c in contacts if c["folder"] == "archive"),
            "inactive_contacts": sum(1 for c in contacts if c["folder"] == "inactive"),
            "active_reminders": sum(1 for r in reminders if r["enabled"]),
            "action_count": len(session.get("actions", [])),
        }

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return self._evaluate(session, scenario)

    def _evaluate(self, session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
        from .evaluator import evaluate_session
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
        all_contacts = self.repository.load_contacts()
        all_tag_defs = self.repository.load_tag_definitions()
        all_reminders = self.repository.load_reminders()

        contacts = [deepcopy(all_contacts[cid]) for cid in scenario["contact_ids"]]
        for contact in contacts:
            contact["last_action_index"] = 0
            contact["archived_at"] = None

        return {
            "session_id": session_id,
            "scenario_id": scenario["scenario_id"],
            "created_at": _utc_now_iso(),
            "meta": {
                "base_time": scenario["current_time"],
                "action_index": 0,
            },
            "workspace_account": deepcopy(self.accounts[scenario["workspace_account_id"]]),
            "crm": {
                "contacts": contacts,
                "reminders": [deepcopy(all_reminders.get(f"rem_{cid}_birthday")) for cid in scenario["contact_ids"] if all_reminders.get(f"rem_{cid}_birthday") is not None],
            },
            "tag_definitions": deepcopy(all_tag_defs),
            "actions": [],
        }

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
