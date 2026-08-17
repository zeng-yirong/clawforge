from __future__ import annotations

from copy import deepcopy
from typing import Any
import uuid


def build_brief_summary(brief: dict[str, Any]) -> dict[str, Any]:
    return {
        "brief_id": brief["brief_id"],
        "title": brief["title"],
        "ticker": brief["ticker"],
        "brief_type": brief["brief_type"],
        "status": brief["status"],
        "created_by": brief["created_by"],
        "created_at": brief["created_at"],
    }


def list_briefs(
    session: dict[str, Any],
    *,
    query: str = "",
    ticker: str | None = None,
    brief_type: str | None = None,
    status: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query_lower = query.strip().lower()
    brief_type_lower = brief_type.strip().lower() if brief_type else None
    status_lower = status.strip().lower() if status else None
    results = []

    for brief in session["briefs"]:
        if ticker and brief["ticker"] != ticker:
            continue
        if brief_type_lower and brief["brief_type"].lower() != brief_type_lower:
            continue
        if status_lower and brief["status"].lower() != status_lower:
            continue

        searchable_text = " ".join(
            [
                brief["title"],
                brief.get("summary", ""),
                brief["ticker"],
            ]
        ).lower()
        if query_lower and query_lower not in searchable_text:
            continue
        results.append(build_brief_summary(brief))

    results.sort(key=lambda item: item["created_at"], reverse=True)
    return results[:limit] if limit is not None else results


def get_brief(session: dict[str, Any], brief_id: str) -> dict[str, Any]:
    for brief in session["briefs"]:
        if brief["brief_id"] == brief_id:
            return deepcopy(brief)
    raise KeyError(f"Brief not found: {brief_id}")


def create_brief(
    session: dict[str, Any],
    ticker: str,
    title: str,
    brief_type: str,
    summary: str,
    investment_rationale: list[str],
    risks: list[str],
    valuation_methodology: str,
    key_metrics: dict[str, Any],
    event_at: str,
    action_index: int,
    created_by: str = "Analyst",
) -> dict[str, Any]:
    brief_id = f"brief_{uuid.uuid4().hex[:8]}"
    new_brief = {
        "brief_id": brief_id,
        "title": title,
        "ticker": ticker,
        "created_by": created_by,
        "created_at": event_at,
        "updated_at": event_at,
        "brief_type": brief_type,
        "status": "draft",
        "summary": summary,
        "investment_rationale": investment_rationale,
        "risks": risks,
        "valuation_methodology": valuation_methodology,
        "key_metrics": key_metrics,
        "last_action_index": action_index,
    }
    session["briefs"].insert(0, new_brief)
    session["last_action_index"] = action_index
    return deepcopy(new_brief)


def update_brief(
    session: dict[str, Any],
    brief_id: str,
    updates: dict[str, Any],
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    for brief in session["briefs"]:
        if brief["brief_id"] == brief_id:
            allowed_fields = {"title", "summary", "status", "investment_rationale", "risks", "valuation_methodology", "key_metrics"}
            for key, value in updates.items():
                if key in allowed_fields:
                    brief[key] = value
            brief["updated_at"] = event_at
            brief["last_action_index"] = action_index
            return deepcopy(brief)
    raise KeyError(f"Brief not found: {brief_id}")


def submit_brief(
    session: dict[str, Any],
    brief_id: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    for brief in session["briefs"]:
        if brief["brief_id"] == brief_id:
            if brief["status"] != "draft":
                raise ValueError(f"Brief {brief_id} is not in draft status")
            brief["status"] = "submitted"
            brief["submitted_at"] = event_at
            brief["last_action_index"] = action_index
            return deepcopy(brief)
    raise KeyError(f"Brief not found: {brief_id}")


def review_brief(
    session: dict[str, Any],
    brief_id: str,
    decision: str,
    comments: str | None,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    for brief in session["briefs"]:
        if brief["brief_id"] == brief_id:
            if brief["status"] != "submitted":
                raise ValueError(f"Brief {brief_id} is not in submitted status")
            brief["status"] = decision
            brief["reviewed_at"] = event_at
            if comments:
                brief["review_comments"] = comments
            brief["last_action_index"] = action_index
            return deepcopy(brief)
    raise KeyError(f"Brief not found: {brief_id}")


def generate_sector_overview(
    session: dict[str, Any],
    sector: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    sector_stocks = [s for s in session["stocks"] if s["sector"].lower() == sector.lower()]

    overview = {
        "overview_id": f"overview_{action_index}",
        "sector": sector,
        "generated_at": event_at,
        "action_index": action_index,
        "total_companies": len(sector_stocks),
        "aggregate_market_cap": sum(s["market_cap"] for s in sector_stocks),
        "avg_pe_ratio": sum(s["pe_ratio"] for s in sector_stocks) / len(sector_stocks) if sector_stocks else 0,
        "avg_revenue_growth": sum(s.get("revenue_growth_yoy", 0) for s in sector_stocks) / len(sector_stocks) if sector_stocks else 0,
        "top_performers": sorted(sector_stocks, key=lambda x: x["current_price"] / x.get("open_price", x["current_price"]) - 1, reverse=True)[:3],
        "analyst_sentiment": _calculate_sector_sentiment(sector_stocks),
    }

    session.setdefault("sector_overviews", []).append(overview)
    session["last_action_index"] = action_index
    return overview


def _calculate_sector_sentiment(stocks: list[dict[str, Any]]) -> dict[str, Any]:
    ratings = {"Buy": 0, "Hold": 0, "Sell": 0}
    for stock in stocks:
        rating = stock.get("analyst_rating", "Hold")
        ratings[rating] = ratings.get(rating, 0) + 1
    total = sum(ratings.values())
    return {
        "buy_count": ratings["Buy"],
        "hold_count": ratings["Hold"],
        "sell_count": ratings["Sell"],
        "buy_pct": ratings["Buy"] / total if total else 0,
    }


def provide_recommendations(
    session: dict[str, Any],
    tickers: list[str],
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    recommendations = {
        "recommendations_id": f"rec_{action_index}",
        "created_at": event_at,
        "action_index": action_index,
        "recommendations": [],
    }

    for ticker in tickers:
        for stock in session["stocks"]:
            if stock["ticker"] == ticker:
                recommendations["recommendations"].append({
                    "ticker": ticker,
                    "company_name": stock["company_name"],
                    "current_price": stock["current_price"],
                    "target_price": stock.get("target_price_mean", stock["current_price"] * 1.1),
                    "upside_pct": ((stock.get("target_price_mean", stock["current_price"] * 1.1) - stock["current_price"]) / stock["current_price"]) * 100,
                    "rating": stock["analyst_rating"],
                    "key_thesis": _generate_key_thesis(stock),
                })

    session.setdefault("recommendations", []).append(recommendations)
    session["last_action_index"] = action_index
    return recommendations


def _generate_key_thesis(stock: dict[str, Any]) -> str:
    growth_str = f"{stock.get('revenue_growth_yoy', 0):.0%}"
    target = stock.get("target_price_mean", stock["current_price"] * 1.1)
    upside = ((target - stock["current_price"]) / stock["current_price"]) * 100
    return f"Trading at {stock['pe_ratio']}x PE with {growth_str} revenue growth. Target {target:.0f} implies {upside:.0f}% upside."
