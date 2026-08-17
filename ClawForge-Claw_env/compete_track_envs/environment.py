from __future__ import annotations

import os
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .competitors import (
    add_competitor_note as do_add_competitor_note,
    compare_competitors as do_compare_competitors,
    get_competitor,
    get_competitor_financials,
    get_competitor_products,
    list_competitor_news,
    list_competitors,
    screen_competitors,
    track_competitor_metric as do_track_competitor_metric,
)
from .evaluator import evaluate_session
from .policies import (
    analyze_policy_trend,
    check_policy_impact,
    filter_policies_by_competitor,
    get_policy,
    get_policy_full_text,
    get_regulatory_risks,
    list_policies,
    list_policy_changes,
    search_policies_by_keyword,
    track_policy_approval as do_track_policy_approval,
)
from .reports import (
    acknowledge_alert as do_acknowledge_alert,
    create_alert as do_create_alert,
    create_market_report as do_create_market_report,
    finalize_report as do_finalize_report,
    generate_competitive_landscape,
    generate_regulatory_summary,
    generate_user_acquisition_analysis,
    get_report,
    list_alerts,
    list_reports,
    update_report as do_update_report,
)
from .repository import DatasetRepository
from .store import SessionStore
from .users import (
    analyze_acquisition_sources,
    compare_user_cohorts,
    get_user,
    get_user_acquisition_details,
    get_user_acquisition_funnel,
    get_user_engagement,
    list_user_cohorts,
    list_users,
    screen_users,
    track_user_event as do_track_user_event,
    update_user_tier as do_update_user_tier,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_iso_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


class CompeteTrackEnvironment:
    def __init__(
        self,
        *,
        data_root: str | Path | None = None,
        state_root: str | Path | None = None,
    ):
        default_state_root = Path(os.getenv("COMPETE_TRACK_STATE_ROOT", Path.cwd() / ".compete_track_state"))
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
            "competitors_count": len(session.get("competitors", [])),
            "policies_count": len(session.get("policies", [])),
            "users_count": len(session.get("users", [])),
        }

    def list_competitors(
        self,
        session_id: str,
        *,
        query: str = "",
        sector: str | None = None,
        min_market_share: float | None = None,
        sort_by: str = "market_cap",
        sort_desc: bool = True,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_competitors(
                session,
                query=query,
                sector=sector,
                min_market_share=min_market_share,
                sort_by=sort_by,
                sort_desc=sort_desc,
            ),
        }

    def get_competitor(self, session_id: str, competitor_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_competitor(session, competitor_id)}

    def get_competitor_financials(self, session_id: str, competitor_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_competitor_financials(session, competitor_id)}

    def get_competitor_products(self, session_id: str, competitor_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_competitor_products(session, competitor_id)}

    def list_competitor_news(
        self,
        session_id: str,
        competitor_id: str,
        *,
        category: str | None = None,
        sentiment: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_competitor_news(session, competitor_id, category=category, sentiment=sentiment, limit=limit),
        }

    def compare_competitors(
        self,
        session_id: str,
        competitor_ids: list[str],
        metrics: list[str] | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": do_compare_competitors(session, competitor_ids, metrics)}

    def screen_competitors(
        self,
        session_id: str,
        *,
        min_market_cap: int | None = None,
        max_market_cap: int | None = None,
        min_market_share: float | None = None,
        max_market_share: float | None = None,
        min_revenue_growth: float | None = None,
        min_user_count: int | None = None,
        sectors: list[str] | None = None,
        sort_by: str = "market_cap",
        sort_desc: bool = True,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": screen_competitors(
                session,
                min_market_cap=min_market_cap,
                max_market_cap=max_market_cap,
                min_market_share=min_market_share,
                max_market_share=max_market_share,
                min_revenue_growth=min_revenue_growth,
                min_user_count=min_user_count,
                sectors=sectors,
                sort_by=sort_by,
                sort_desc=sort_desc,
            ),
        }

    def add_competitor_note(self, session_id: str, competitor_id: str, note: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = do_add_competitor_note(session, competitor_id, note, event_at, action_index)
            self._record_action(session, action_index, event_at, "add_competitor_note", {"competitor_id": competitor_id})
            self.store.save_session_unlocked(session_id, session)
            return {"session_id": session_id, "data": payload}

    def list_policies(
        self,
        session_id: str,
        *,
        query: str = "",
        policy_type: str | None = None,
        jurisdiction: str | None = None,
        status: str | None = None,
        impact_level: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_policies(
                session,
                query=query,
                policy_type=policy_type,
                jurisdiction=jurisdiction,
                status=status,
                impact_level=impact_level,
                limit=limit,
            ),
        }

    def get_policy(self, session_id: str, policy_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_policy(session, policy_id)}

    def get_policy_full_text(self, session_id: str, policy_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_policy_full_text(session, policy_id)}

    def get_policy_impact(self, session_id: str, policy_id: str, competitor_ids: list[str] | None = None) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": check_policy_impact(session, policy_id, competitor_ids)}

    def filter_policies_by_competitor(
        self,
        session_id: str,
        competitor_id: str,
        *,
        impact_level: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": filter_policies_by_competitor(session, competitor_id, impact_level=impact_level, status=status),
        }

    def get_regulatory_risks(
        self,
        session_id: str,
        competitor_id: str | None = None,
        min_impact_level: str = "medium",
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_regulatory_risks(session, competitor_id, min_impact_level)}

    def analyze_policy_trend(
        self,
        session_id: str,
        jurisdiction: str | None = None,
        policy_type: str | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": analyze_policy_trend(session, jurisdiction, policy_type)}

    def list_users(
        self,
        session_id: str,
        *,
        query: str = "",
        acquisition_source: str | None = None,
        user_tier: str | None = None,
        cohort: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_users(
                session,
                query=query,
                acquisition_source=acquisition_source,
                user_tier=user_tier,
                cohort=cohort,
                limit=limit,
            ),
        }

    def get_user(self, session_id: str, user_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_user(session, user_id)}

    def get_user_engagement(self, session_id: str, user_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_user_engagement(session, user_id)}

    def get_user_acquisition_details(self, session_id: str, user_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_user_acquisition_details(session, user_id)}

    def analyze_acquisition_sources(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": analyze_acquisition_sources(session)}

    def screen_users(
        self,
        session_id: str,
        *,
        min_lifetime_value: float | None = None,
        max_lifetime_value: float | None = None,
        min_engagement_score: float | None = None,
        user_tiers: list[str] | None = None,
        acquisition_sources: list[str] | None = None,
        has_churned: bool | None = None,
        sort_by: str = "lifetime_value",
        sort_desc: bool = True,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": screen_users(
                session,
                min_lifetime_value=min_lifetime_value,
                max_lifetime_value=max_lifetime_value,
                min_engagement_score=min_engagement_score,
                user_tiers=user_tiers,
                acquisition_sources=acquisition_sources,
                has_churned=has_churned,
                sort_by=sort_by,
                sort_desc=sort_desc,
            ),
        }

    def update_user_tier(self, session_id: str, user_id: str, new_tier: str, reason: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = do_update_user_tier(session, user_id, new_tier, reason, event_at, action_index)
            self._record_action(session, action_index, event_at, "update_user_tier", {"user_id": user_id, "new_tier": new_tier})
            self.store.save_session_unlocked(session_id, session)
            return {"session_id": session_id, "data": payload}

    def list_reports(
        self,
        session_id: str,
        *,
        report_type: str | None = None,
        status: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_reports(session, report_type=report_type, status=status, limit=limit),
        }

    def get_report(self, session_id: str, report_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_report(session, report_id)}

    def create_market_report(
        self,
        session_id: str,
        title: str,
        report_type: str,
        competitor_ids: list[str],
        include_sections: list[str],
        findings: list[str],
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = do_create_market_report(
                session, title, report_type, competitor_ids, include_sections, findings, event_at, action_index
            )
            self._record_action(
                session, action_index, event_at, "create_market_report",
                {"report_id": payload["report_id"], "competitor_ids": competitor_ids}
            )
            self.store.save_session_unlocked(session_id, session)
            return {"session_id": session_id, "data": payload}

    def update_report(self, session_id: str, report_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = do_update_report(session, report_id, updates, event_at, action_index)
            self._record_action(session, action_index, event_at, "update_report", {"report_id": report_id})
            self.store.save_session_unlocked(session_id, session)
            return {"session_id": session_id, "data": payload}

    def finalize_report(self, session_id: str, report_id: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = do_finalize_report(session, report_id, event_at, action_index)
            self._record_action(session, action_index, event_at, "finalize_report", {"report_id": report_id})
            self.store.save_session_unlocked(session_id, session)
            return {"session_id": session_id, "data": payload}

    def generate_competitive_landscape(self, session_id: str, competitor_ids: list[str]) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = generate_competitive_landscape(session, competitor_ids, event_at, action_index)
            self._record_action(
                session, action_index, event_at, "generate_competitive_landscape",
                {"competitor_ids": competitor_ids}
            )
            self.store.save_session_unlocked(session_id, session)
            return {"session_id": session_id, "data": payload}

    def generate_regulatory_summary(
        self,
        session_id: str,
        competitor_ids: list[str] | None = None,
        impact_filter: str | None = None,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = generate_regulatory_summary(session, event_at, action_index, competitor_ids, impact_filter)
            self._record_action(session, action_index, event_at, "generate_regulatory_summary", {})
            self.store.save_session_unlocked(session_id, session)
            return {"session_id": session_id, "data": payload}

    def generate_user_acquisition_analysis(
        self,
        session_id: str,
        cohort_filter: str | None = None,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = generate_user_acquisition_analysis(session, event_at, action_index, cohort_filter)
            self._record_action(session, action_index, event_at, "generate_user_acquisition_analysis", {})
            self.store.save_session_unlocked(session_id, session)
            return {"session_id": session_id, "data": payload}

    def list_alerts(
        self,
        session_id: str,
        *,
        alert_type: str | None = None,
        severity: str | None = None,
        acknowledged: bool | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_alerts(session, alert_type=alert_type, severity=severity, acknowledged=acknowledged, limit=limit),
        }

    def create_alert(
        self,
        session_id: str,
        alert_type: str,
        title: str,
        description: str,
        severity: str,
        related_competitor_id: str | None = None,
        related_policy_id: str | None = None,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = do_create_alert(
                session, alert_type, title, description, severity,
                related_competitor_id, related_policy_id, event_at, action_index
            )
            self._record_action(session, action_index, event_at, "create_alert", {"alert_type": alert_type, "severity": severity})
            self.store.save_session_unlocked(session_id, session)
            return {"session_id": session_id, "data": payload}

    def acknowledge_alert(
        self,
        session_id: str,
        alert_id: str,
        acknowledged_by: str,
        notes: str | None = None,
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = do_acknowledge_alert(session, alert_id, acknowledged_by, notes, event_at, action_index)
            self._record_action(session, action_index, event_at, "acknowledge_alert", {"alert_id": alert_id})
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
            "competitors_count": len(session.get("competitors", [])),
            "policies_count": len(session.get("policies", [])),
            "users_count": len(session.get("users", [])),
            "reports_count": len(session.get("reports", [])),
            "alerts_count": len(session.get("alerts", [])),
            "action_count": len(session.get("actions", [])),
        }

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
        all_competitors = self.repository.load_competitors()
        all_policies = self.repository.load_policies()
        all_users = self.repository.load_users()

        competitors = [
            self._hydrate_competitor(all_competitors[cid])
            for cid in scenario["competitor_ids"]
            if cid in all_competitors
        ]
        policies = [
            self._hydrate_policy(all_policies[pid])
            for pid in scenario["policy_ids"]
            if pid in all_policies
        ]
        users = [
            self._hydrate_user(all_users[uid])
            for uid in scenario["user_ids"]
            if uid in all_users
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
            "competitors": competitors,
            "policies": policies,
            "users": users,
            "actions": [],
            "reports": [],
            "alerts": [],
        }

    def _hydrate_competitor(self, competitor: dict[str, Any]) -> dict[str, Any]:
        hydrated = deepcopy(competitor)
        hydrated["metrics_history"] = []
        hydrated["notes"] = []
        return hydrated

    def _hydrate_policy(self, policy: dict[str, Any]) -> dict[str, Any]:
        hydrated = deepcopy(policy)
        hydrated["approval_history"] = []
        return hydrated

    def _hydrate_user(self, user: dict[str, Any]) -> dict[str, Any]:
        hydrated = deepcopy(user)
        hydrated["events"] = []
        hydrated["tier_history"] = []
        return hydrated

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
        session["actions"].append({
            "action_index": action_index,
            "timestamp": event_at,
            "action_type": action_type,
            "details": details,
        })
