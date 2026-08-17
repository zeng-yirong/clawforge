from __future__ import annotations

import os
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .evaluator import evaluate_session
from .mail import list_emails, read_attachment, read_email
from .repository import DatasetRepository
from .social import list_posts, publish_post, reply_to_post, view_post
from .store import SessionStore


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_iso_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


class PostMailsEnvironment:
    def __init__(
        self,
        *,
        data_root: str | Path | None = None,
        state_root: str | Path | None = None,
    ):
        default_state_root = Path(os.getenv("POST_MAILS_STATE_ROOT", Path.cwd() / ".post_mails_state"))
        self.repository = DatasetRepository(data_root)
        self.store = SessionStore(state_root or default_state_root)
        self.accounts = self.repository.load_accounts()
        self.contacts = self.repository.load_contacts()

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
            "unread_email_count": sum(1 for email in session["mail"]["emails"] if not email["read"]),
        }

    def list_emails(
        self,
        session_id: str,
        *,
        query: str = "",
        unread_only: bool = False,
        folder: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_emails(
                session,
                query=query,
                unread_only=unread_only,
                folder=folder,
                limit=limit,
            ),
        }

    def read_email(self, session_id: str, email_id: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = read_email(session, email_id, event_at, action_index)
            self._record_action(session, action_index, event_at, "read_email", {"email_id": email_id})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def read_attachment(self, session_id: str, attachment_id: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            attachment_meta = self._find_attachment_metadata(session, attachment_id)
            content = self.repository.read_attachment(attachment_meta["relative_path"])
            payload = read_attachment(session, attachment_id, content, event_at, action_index)
            self._record_action(
                session,
                action_index,
                event_at,
                "read_attachment",
                {"attachment_id": attachment_id, "source_email_id": payload["source_email_id"]},
            )
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def list_posts(
        self,
        session_id: str,
        *,
        query: str = "",
        platform: str | None = None,
        needs_response_only: bool = False,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_posts(
                session,
                query=query,
                platform=platform,
                needs_response_only=needs_response_only,
                limit=limit,
            ),
        }

    def view_post(self, session_id: str, post_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": view_post(session, post_id)}

    def publish_post(
        self,
        session_id: str,
        *,
        platform: str,
        content: str,
        title: str | None = None,
        community: str | None = None,
        author: str | None = None,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            author_name = author or session["workspace_account"]["display_name"]
            payload = publish_post(
                session,
                platform=platform,
                content=content,
                title=title,
                community=community,
                event_at=event_at,
                author=author_name,
                action_index=action_index,
            )
            self._record_action(
                session,
                action_index,
                event_at,
                "publish_post",
                {"platform": platform, "post_id": payload["post_id"]},
            )
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def reply_to_post(
        self,
        session_id: str,
        *,
        post_id: str,
        content: str,
        author: str | None = None,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            author_name = author or session["workspace_account"]["display_name"]
            payload = reply_to_post(
                session,
                post_id=post_id,
                content=content,
                event_at=event_at,
                author=author_name,
                action_index=action_index,
            )
            self._record_action(
                session,
                action_index,
                event_at,
                "reply_to_post",
                {"post_id": post_id, "reply_id": payload["reply_id"]},
            )
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def session_summary(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "workspace_account": session["workspace_account"],
            "state_root": str(self.store.state_root),
            "unread_email_count": sum(1 for email in session["mail"]["emails"] if not email["read"]),
            "attachments_read": sorted(
                attachment["attachment_id"]
                for email in session["mail"]["emails"]
                for attachment in email.get("attachments", [])
                if attachment.get("read")
            ),
            "agent_post_count": len(session["social"]["agent_posts"]),
            "agent_reply_count": len(session["social"]["agent_replies"]),
            "action_count": len(session.get("actions", [])),
        }

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
        emails = [self._hydrate_email(self.repository.load_email(email_id)) for email_id in scenario["email_ids"]]
        posts = [self._hydrate_post(self.repository.load_social_post(post_id)) for post_id in scenario["social_post_ids"]]
        return {
            "session_id": session_id,
            "scenario_id": scenario["scenario_id"],
            "created_at": _utc_now_iso(),
            "meta": {
                "base_time": scenario["current_time"],
                "action_index": 0,
            },
            "workspace_account": deepcopy(self.accounts[scenario["workspace_account_id"]]),
            "mail": {"emails": emails},
            "social": {
                "seed_posts": posts,
                "agent_posts": [],
                "agent_replies": [],
            },
            "actions": [],
        }

    def _hydrate_email(self, email: dict[str, Any]) -> dict[str, Any]:
        hydrated = deepcopy(email)
        sender = deepcopy(self.contacts[hydrated["sender_id"]])
        hydrated["sender"] = {
            "contact_id": sender["contact_id"],
            "name": sender["name"],
            "email": sender["email"],
            "role": sender["role"],
            "team": sender["team"],
        }
        hydrated["read"] = False
        hydrated["opened_at"] = None
        for attachment in hydrated.get("attachments", []):
            attachment["read"] = False
            attachment["read_at"] = None
        return hydrated

    def _hydrate_post(self, post: dict[str, Any]) -> dict[str, Any]:
        hydrated = deepcopy(post)
        author = deepcopy(self.contacts[hydrated["author_id"]])
        hydrated["author"] = author["name"]
        hydrated["author_handle"] = author.get("social_handle")
        hydrated["created_by_agent"] = False
        return hydrated

    def _find_attachment_metadata(self, session: dict[str, Any], attachment_id: str) -> dict[str, Any]:
        for email in session["mail"]["emails"]:
            for attachment in email.get("attachments", []):
                if attachment["attachment_id"] == attachment_id:
                    return attachment
        raise KeyError(f"Attachment not found: {attachment_id}")

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
