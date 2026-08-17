from __future__ import annotations

import os
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from .catalog import get_brand, get_sku, list_brands, list_skus
from .evaluator import evaluate_session
from .pricing import get_price_book, list_price_books
from .reports import (
    extract_brand_catalog as do_extract_brand_catalog,
    generate_category_report as do_generate_category_report,
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


class ProductCompetitionEnvironment:
    def __init__(
        self,
        *,
        data_root: str | Path | None = None,
        state_root: str | Path | None = None,
    ):
        default_state_root = Path(os.getenv("WITHOUT_SKILL_STATE_ROOT", Path.cwd() / ".without_skill_state"))
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

        return self._run_logged_action(
            session_id,
            "task",
            {},
            handler,
        )

    def list_brands(
        self,
        session_id: str,
        *,
        query: str = "",
        category_id: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "list_brands",
            {"query": query, "category_id": category_id},
            lambda session, _event_at, _action_index: list_brands(
                session,
                query=query,
                category_id=category_id,
                limit=limit,
            ),
        )

    def get_brand(self, session_id: str, brand_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            payload = get_brand(session, brand_id)
            self._append_unique(session["observations"]["brand_ids_seen"], brand_id)
            return payload

        return self._run_logged_action(session_id, "get_brand", {"brand_id": brand_id}, handler)

    def list_skus(
        self,
        session_id: str,
        *,
        brand_id: str | None = None,
        category_id: str | None = None,
        query: str = "",
        status: str | None = "active",
        limit: int | None = None,
    ) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> list[dict[str, Any]]:
            data = list_skus(
                session,
                brand_id=brand_id,
                category_id=category_id,
                query=query,
                status=status,
                limit=limit,
            )
            for item in data:
                self._append_unique(session["observations"]["sku_ids_seen"], item["sku_id"])
            if brand_id:
                self._append_unique(session["observations"]["brand_ids_seen"], brand_id)
            return data

        return self._run_logged_action(
            session_id,
            "list_skus",
            {"brand_id": brand_id, "category_id": category_id, "query": query, "status": status},
            handler,
        )

    def get_sku(self, session_id: str, sku_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            payload = get_sku(session, sku_id)
            self._append_unique(session["observations"]["sku_ids_seen"], sku_id)
            self._append_unique(session["observations"]["brand_ids_seen"], payload["brand_id"])
            return payload

        return self._run_logged_action(session_id, "get_sku", {"sku_id": sku_id}, handler)

    def list_price_books(
        self,
        session_id: str,
        *,
        status: str | None = None,
        current_only: bool = False,
    ) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "list_price_books",
            {"status": status, "current_only": current_only},
            lambda session, _event_at, _action_index: list_price_books(
                session,
                status=status,
                current_only=current_only,
            ),
        )

    def get_price_book(self, session_id: str, price_book_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            payload = get_price_book(session, price_book_id)
            self._append_unique(session["observations"]["price_book_ids_seen"], price_book_id)
            return payload

        return self._run_logged_action(
            session_id,
            "get_price_book",
            {"price_book_id": price_book_id},
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

    def extract_brand_catalog(self, session_id: str, brand_id: str, price_book_id: str) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "extract_brand_catalog",
            {"brand_id": brand_id, "price_book_id": price_book_id},
            lambda session, event_at, action_index: do_extract_brand_catalog(
                session,
                brand_id,
                price_book_id,
                event_at,
                action_index,
            ),
        )

    def generate_category_report(
        self,
        session_id: str,
        brand_id: str,
        price_book_id: str,
        *,
        category_id: str | None = None,
    ) -> dict[str, Any]:
        return self._run_logged_action(
            session_id,
            "generate_category_report",
            {"brand_id": brand_id, "price_book_id": price_book_id, "category_id": category_id},
            lambda session, event_at, action_index: do_generate_category_report(
                session,
                brand_id,
                price_book_id,
                event_at,
                action_index,
                category_id=category_id,
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
        report_count = len(
            [item for item in session["cache"]["entries"] if item["entry_type"] == "category_competition_report"]
        )
        extract_count = len(
            [item for item in session["cache"]["entries"] if item["entry_type"] == "brand_catalog_extract"]
        )
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "workspace_account": session["workspace_account"],
            "state_root": str(self.store.state_root),
            "brands_count": len(session["brands"]),
            "skus_count": len(session["skus"]),
            "price_books_count": len(session["price_books"]),
            "cache_entries_count": len(session["cache"]["entries"]),
            "extract_count": extract_count,
            "report_count": report_count,
            "action_count": len(session.get("actions", [])),
        }

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
        all_brands = self.repository.load_brands()
        all_skus = self.repository.load_skus()
        all_price_books = self.repository.load_price_books()

        brands = [deepcopy(all_brands[brand_id]) for brand_id in scenario["brand_ids"] if brand_id in all_brands]
        skus = [deepcopy(all_skus[sku_id]) for sku_id in scenario["sku_ids"] if sku_id in all_skus]
        price_books = [
            deepcopy(all_price_books[price_book_id])
            for price_book_id in scenario["price_book_ids"]
            if price_book_id in all_price_books
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
            "brands": brands,
            "skus": skus,
            "price_books": price_books,
            "attachments": attachments,
            "contacts": [deepcopy(item) for item in self.contacts.values()],
            "cache": {
                "entries": [],
                "latest": {},
            },
            "observations": {
                "brand_ids_seen": [],
                "sku_ids_seen": [],
                "price_book_ids_seen": [],
                "attachments_read": [],
                "cache_entry_ids": [],
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
            "target_brand_id": scenario["target_brand_id"],
            "target_category_id": scenario["target_category_id"],
            "attachment_count": len(session["attachments"]),
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
