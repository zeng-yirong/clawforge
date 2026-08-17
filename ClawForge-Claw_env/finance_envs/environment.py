from __future__ import annotations

import os
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .earnings import create_earnings_summary as do_create_earnings_summary, get_earnings, list_earnings
from .evaluator import evaluate_session
from .news import get_news, list_news
from .reports import (
    create_brief as do_create_brief,
    generate_sector_overview as do_generate_sector_overview,
    get_brief,
    list_briefs,
    provide_recommendations as do_provide_recommendations,
    review_brief as do_review_brief,
    submit_brief as do_submit_brief,
    update_brief as do_update_brief,
)
from .repository import DatasetRepository
from .stocks import get_stock, list_stocks, screen_stocks
from .store import SessionStore


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_iso_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


class FinanceEnvironment:
    def __init__(
        self,
        *,
        data_root: str | Path | None = None,
        state_root: str | Path | None = None,
    ):
        default_state_root = Path(os.getenv("FINANCE_STATE_ROOT", Path.cwd() / ".finance_state"))
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
            "news_count": len(session["news"]),
        }

    def list_stocks(
        self,
        session_id: str,
        *,
        query: str = "",
        sector: str | None = None,
        min_market_cap: int | None = None,
        min_revenue_growth: float | None = None,
        min_analyst_rating: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_stocks(
                session,
                query=query,
                sector=sector,
                min_market_cap=min_market_cap,
                min_revenue_growth=min_revenue_growth,
                min_analyst_rating=min_analyst_rating,
                limit=limit,
            ),
        }

    def get_stock(self, session_id: str, ticker: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_stock(session, ticker)}

    def screen_stocks(
        self,
        session_id: str,
        *,
        min_market_cap: int | None = None,
        max_pe_ratio: float | None = None,
        min_revenue_growth: float | None = None,
        min_eps_growth: float | None = None,
        min_dividend_yield: float | None = None,
        max_debt_to_equity: float | None = None,
        sector: str | None = None,
        min_analyst_rating: str | None = None,
        sort_by: str = "market_cap",
        sort_desc: bool = True,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": screen_stocks(
                session,
                min_market_cap=min_market_cap,
                max_pe_ratio=max_pe_ratio,
                min_revenue_growth=min_revenue_growth,
                min_eps_growth=min_eps_growth,
                min_dividend_yield=min_dividend_yield,
                max_debt_to_equity=max_debt_to_equity,
                sector=sector,
                min_analyst_rating=min_analyst_rating,
                sort_by=sort_by,
                sort_desc=sort_desc,
            ),
        }

    def list_news(
        self,
        session_id: str,
        *,
        query: str = "",
        ticker: str | None = None,
        category: str | None = None,
        sentiment: str | None = None,
        impact: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_news(
                session,
                query=query,
                ticker=ticker,
                category=category,
                sentiment=sentiment,
                impact=impact,
                limit=limit,
            ),
        }

    def get_news(self, session_id: str, news_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_news(session, news_id)}

    def list_earnings(
        self,
        session_id: str,
        *,
        ticker: str | None = None,
        beat_only: bool = False,
        miss_only: bool = False,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_earnings(
                session,
                ticker=ticker,
                beat_only=beat_only,
                miss_only=miss_only,
                limit=limit,
            ),
        }

    def get_earnings(self, session_id: str, earnings_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_earnings(session, earnings_id)}

    def create_earnings_summary(self, session_id: str, tickers: list[str]) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = do_create_earnings_summary(session, tickers, event_at, action_index)
            self._record_action(session, action_index, event_at, "create_earnings_summary", {"tickers": tickers})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def list_briefs(
        self,
        session_id: str,
        *,
        query: str = "",
        ticker: str | None = None,
        brief_type: str | None = None,
        status: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {
            "session_id": session_id,
            "data": list_briefs(
                session,
                query=query,
                ticker=ticker,
                brief_type=brief_type,
                status=status,
                limit=limit,
            ),
        }

    def get_brief(self, session_id: str, brief_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        return {"session_id": session_id, "data": get_brief(session, brief_id)}

    def create_brief(
        self,
        session_id: str,
        ticker: str,
        title: str,
        brief_type: str,
        summary: str,
        investment_rationale: list[str],
        risks: list[str],
        valuation_methodology: str,
        key_metrics: dict[str, Any],
    ) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = do_create_brief(
                session, ticker, title, brief_type, summary,
                investment_rationale, risks, valuation_methodology, key_metrics,
                event_at, action_index
            )
            self._record_action(session, action_index, event_at, "create_brief", {"ticker": ticker, "brief_id": payload["brief_id"]})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def update_brief(self, session_id: str, brief_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = do_update_brief(session, brief_id, updates, event_at, action_index)
            self._record_action(session, action_index, event_at, "update_brief", {"brief_id": brief_id})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def submit_brief(self, session_id: str, brief_id: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = do_submit_brief(session, brief_id, event_at, action_index)
            self._record_action(session, action_index, event_at, "submit_brief", {"brief_id": brief_id})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def review_brief(self, session_id: str, brief_id: str, decision: str, comments: str | None = None) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = do_review_brief(session, brief_id, decision, comments, event_at, action_index)
            self._record_action(session, action_index, event_at, "review_brief", {"brief_id": brief_id, "decision": decision})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def generate_sector_overview(self, session_id: str, sector: str) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = do_generate_sector_overview(session, sector, event_at, action_index)
            self._record_action(session, action_index, event_at, "generate_sector_overview", {"sector": sector})
            self.store.save_session(session_id, session)
            return {"session_id": session_id, "data": payload}

    def provide_recommendations(self, session_id: str, tickers: list[str]) -> dict[str, Any]:
        with self.store.session_lock(session_id):
            session = self.store.load_session(session_id)
            event_at, action_index = self._next_event(session)
            payload = do_provide_recommendations(session, tickers, event_at, action_index)
            self._record_action(session, action_index, event_at, "provide_recommendations", {"tickers": tickers})
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
            "stocks_count": len(session["stocks"]),
            "news_count": len(session["news"]),
            "briefs_count": len(session["briefs"]),
            "action_count": len(session.get("actions", [])),
        }

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
        all_stocks = self.repository.load_stocks()
        all_news = self.repository.load_news()
        all_earnings = self.repository.load_earnings()
        all_briefs = self.repository.load_briefs()

        stocks = [self._hydrate_stock(all_stocks[ticker]) for ticker in scenario["ticker_ids"] if ticker in all_stocks]
        news = [self._hydrate_news(all_news[nid]) for nid in scenario["news_ids"] if nid in all_news]
        earnings = [self._hydrate_earnings(all_earnings[eid]) for eid in scenario["earnings_ids"] if eid in all_earnings]
        briefs = [self._hydrate_brief(all_briefs[bid]) for bid in all_briefs]

        return {
            "session_id": session_id,
            "scenario_id": scenario["scenario_id"],
            "created_at": _utc_now_iso(),
            "meta": {
                "base_time": scenario["current_time"],
                "action_index": 0,
            },
            "workspace_account": deepcopy(self.accounts[scenario["workspace_account_id"]]),
            "stocks": stocks,
            "news": news,
            "earnings": earnings,
            "briefs": briefs,
            "actions": [],
            "earnings_summaries": [],
            "sector_overviews": [],
            "recommendations": [],
        }

    def _hydrate_stock(self, stock: dict[str, Any]) -> dict[str, Any]:
        return deepcopy(stock)

    def _hydrate_news(self, news_item: dict[str, Any]) -> dict[str, Any]:
        return deepcopy(news_item)

    def _hydrate_earnings(self, earnings: dict[str, Any]) -> dict[str, Any]:
        return deepcopy(earnings)

    def _hydrate_brief(self, brief: dict[str, Any]) -> dict[str, Any]:
        return deepcopy(brief)

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
