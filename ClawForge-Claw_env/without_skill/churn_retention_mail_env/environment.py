from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from without_skill._shared.base_env import utc_now_iso
from without_skill._shared.cache import append_cache_entry
from without_skill._shared.cache_env import CacheArtifactEnvironmentBase
from without_skill._shared.customer_memory import CustomerMemoryRepository, get_customer, list_customers
from without_skill._shared.json_repository import load_json


class ChurnRepository(CustomerMemoryRepository):
    def __init__(self, data_root: str | Path | None = None):
        super().__init__(data_root)
        self.news_file = self.data_root / "data" / "news" / "news_samples.json"

    def load_news_samples(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.news_file)
        return {item["news_id"]: item for item in payload["news_samples"]}


class ChurnRetentionMailEnvironment(CacheArtifactEnvironmentBase):
    state_root_env_var = "CHURN_RETENTION_MAIL_STATE_ROOT"
    default_state_dir_name = ".churn_retention_mail_state"

    def __init__(self, *, data_root: str | Path | None = None, state_root: str | Path | None = None):
        resolved_data_root = Path(data_root) if data_root is not None else Path(__file__).parent
        self.repository = ChurnRepository(resolved_data_root)
        super().__init__(state_root=state_root)
        self.accounts = self.repository.load_accounts()
        self.contacts = self.repository.load_contacts()
        self.attachment_manifest = self.repository.load_attachment_manifest()

    def list_customers(
        self,
        session_id: str,
        *,
        query: str = "",
        industry: str | None = None,
        risk_level: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> list[dict[str, Any]]:
            data = list_customers(session, query=query, industry=industry, risk_level=risk_level, limit=limit)
            for item in data:
                self._append_unique(session["observations"]["customer_ids_seen"], str(item["customer_id"]))
            return data

        return self._run_logged_action(
            session_id,
            "list_customers",
            {"query": query, "industry": industry, "risk_level": risk_level},
            handler,
        )

    def get_customer(self, session_id: str, customer_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            payload = get_customer(session, customer_id)
            self._append_unique(session["observations"]["customer_ids_seen"], customer_id)
            return payload

        return self._run_logged_action(session_id, "get_customer", {"customer_id": customer_id}, handler)

    def list_news_samples(
        self,
        session_id: str,
        *,
        industry: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> list[dict[str, Any]]:
            results: list[dict[str, Any]] = []
            for news in session["news_samples"]:
                if industry and str(news["industry"]).lower() != str(industry).lower():
                    continue
                results.append(
                    {
                        "news_id": news["news_id"],
                        "industry": news["industry"],
                        "headline": news["headline"],
                        "tone": news["tone"],
                    }
                )
                self._append_unique(session["observations"]["news_ids_seen"], news["news_id"])
            return results[:limit] if limit is not None else results

        return self._run_logged_action(session_id, "list_news_samples", {"industry": industry}, handler)

    def get_news_sample(self, session_id: str, news_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            for news in session["news_samples"]:
                if news["news_id"] == news_id:
                    self._append_unique(session["observations"]["news_ids_seen"], news_id)
                    return deepcopy(news)
            raise KeyError(f"News sample not found: {news_id}")

        return self._run_logged_action(session_id, "get_news_sample", {"news_id": news_id}, handler)

    def generate_retention_email(self, session_id: str, customer_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], event_at: str, action_index: int) -> dict[str, Any]:
            customer = get_customer(session, customer_id)
            activity = customer["activity_log"]
            related_news = [news for news in session["news_samples"] if news["industry"] == customer["industry"]]
            if not related_news:
                raise ValueError(f"No related news samples for industry: {customer['industry']}")
            top_news = related_news[:2]
            for news in top_news:
                self._append_unique(session["observations"]["news_ids_seen"], news["news_id"])

            body_lines = [
                f"Hi {customer['owner_name']},",
                "",
                f"We noticed {customer['customer_name']} has shown churn risk indicators ({activity['risk_level']}, {activity['last_active_days']} inactive days).",
                "Relevant market context:",
            ]
            for news in top_news:
                body_lines.append(f"- {news['headline']}: {news['summary']}")
            body_lines.extend(
                [
                    "",
                    "We recommend a tailored retention review and a short executive sync this week.",
                ]
            )
            payload = {
                "customer_id": customer_id,
                "customer_name": customer["customer_name"],
                "risk_level": activity["risk_level"],
                "news_ids": [news["news_id"] for news in top_news],
                "subject": f"Retention support plan for {customer['customer_name']}",
                "body": "\n".join(body_lines),
            }
            entry = append_cache_entry(
                session,
                cache_key=f"retention_mail::{customer_id}",
                entry_type="retention_email",
                payload=payload,
                event_at=event_at,
                action_index=action_index,
            )
            self._append_unique(session["observations"]["cache_entry_ids"], entry["entry_id"])
            return entry

        return self._run_logged_action(
            session_id,
            "generate_retention_email",
            {"customer_id": customer_id},
            handler,
        )

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        from .evaluator import evaluate_session

        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
        all_customers = self.repository.load_customers()
        all_activity = self.repository.load_activity_logs()
        all_news = self.repository.load_news_samples()
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
            "customers": [deepcopy(all_customers[cid]) for cid in scenario["customer_ids"]],
            "activity_logs": {cid: deepcopy(all_activity[cid]) for cid in scenario["customer_ids"]},
            "news_samples": [deepcopy(all_news[nid]) for nid in scenario["news_ids"]],
            "attachments": attachments,
            "contacts": [deepcopy(item) for item in self.contacts.values()],
            "cache": {"entries": [], "latest": {}},
            "observations": {
                "customer_ids_seen": [],
                "news_ids_seen": [],
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
            "customer_count": len(session["customers"]),
            "news_sample_count": len(session["news_samples"]),
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
            "customer_count": len(session["customers"]),
            "cache_entries_count": len(session["cache"]["entries"]),
            "action_count": len(session["actions"]),
        }
