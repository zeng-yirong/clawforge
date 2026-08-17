from __future__ import annotations

from typing import Any


def list_competitors(
    session: dict[str, Any],
    *,
    query: str = "",
    sector: str | None = None,
    min_market_share: float | None = None,
    sort_by: str = "market_cap",
    sort_desc: bool = True,
) -> list[dict[str, Any]]:
    competitors = session.get("competitors", [])
    results = []

    for comp in competitors:
        if query:
            q_lower = query.lower()
            name_match = q_lower in comp.get("name", "").lower()
            desc_match = q_lower in comp.get("description", "").lower()
            if not (name_match or desc_match):
                continue

        if sector and comp.get("sector") != sector:
            continue

        if min_market_share is not None:
            if comp.get("market_share", 0) < min_market_share:
                continue

        results.append(comp)

    sort_key_map = {
        "market_cap": lambda x: x.get("market_cap", 0),
        "market_share": lambda x: x.get("market_share", 0),
        "revenue": lambda x: x.get("revenue", 0),
        "user_count": lambda x: x.get("user_count", 0),
        "name": lambda x: x.get("name", ""),
    }

    sort_key = sort_key_map.get(sort_by, lambda x: x.get("name", ""))
    results.sort(key=sort_key, reverse=sort_desc)

    return results


def get_competitor(session: dict[str, Any], competitor_id: str) -> dict[str, Any]:
    competitors = session.get("competitors", [])
    for comp in competitors:
        if comp.get("competitor_id") == competitor_id:
            return comp
    raise KeyError(f"Competitor not found: {competitor_id}")


def get_competitor_financials(session: dict[str, Any], competitor_id: str) -> dict[str, Any]:
    comp = get_competitor(session, competitor_id)
    return {
        "competitor_id": competitor_id,
        "name": comp.get("name"),
        "financials": comp.get("financials", {}),
    }


def get_competitor_products(session: dict[str, Any], competitor_id: str) -> dict[str, Any]:
    comp = get_competitor(session, competitor_id)
    return {
        "competitor_id": competitor_id,
        "name": comp.get("name"),
        "products": comp.get("products", []),
    }


def list_competitor_news(
    session: dict[str, Any],
    competitor_id: str,
    *,
    category: str | None = None,
    sentiment: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    comp = get_competitor(session, competitor_id)
    news_items = comp.get("news", [])

    results = []
    for news in news_items:
        if category and news.get("category") != category:
            continue
        if sentiment and news.get("sentiment") != sentiment:
            continue
        results.append(news)

    if limit is not None:
        results = results[:limit]

    return results


def track_competitor_metric(
    session: dict[str, Any],
    competitor_id: str,
    metric_name: str,
    new_value: float,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    comp = get_competitor(session, competitor_id)

    if "metrics_history" not in comp:
        comp["metrics_history"] = []

    entry = {
        "metric_name": metric_name,
        "value": new_value,
        "timestamp": event_at,
        "action_index": action_index,
    }
    comp["metrics_history"].append(entry)

    if metric_name == "market_share":
        comp["market_share"] = new_value
    elif metric_name == "user_count":
        comp["user_count"] = int(new_value)
    elif metric_name == "revenue":
        comp["revenue"] = new_value

    return {
        "competitor_id": competitor_id,
        "metric_name": metric_name,
        "new_value": new_value,
        "recorded_at": event_at,
    }


def compare_competitors(
    session: dict[str, Any],
    competitor_ids: list[str],
    metrics: list[str] | None = None,
) -> dict[str, Any]:
    if metrics is None:
        metrics = ["market_cap", "market_share", "revenue", "user_count", "growth_rate"]

    comparison = {"metrics": metrics, "competitors": {}}

    for cid in competitor_ids:
        comp = get_competitor(session, cid)
        comparison["competitors"][cid] = {
            "name": comp.get("name"),
            "sector": comp.get("sector"),
        }
        for metric in metrics:
            comparison["competitors"][cid][metric] = comp.get(metric)

    return comparison


def screen_competitors(
    session: dict[str, Any],
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
) -> list[dict[str, Any]]:
    competitors = session.get("competitors", [])
    results = []

    for comp in competitors:
        if min_market_cap is not None:
            if comp.get("market_cap", 0) < min_market_cap:
                continue
        if max_market_cap is not None:
            if comp.get("market_cap", 0) > max_market_cap:
                continue
        if min_market_share is not None:
            if comp.get("market_share", 0) < min_market_share:
                continue
        if max_market_share is not None:
            if comp.get("market_share", 0) > max_market_share:
                continue
        if min_revenue_growth is not None:
            if comp.get("growth_rate", 0) < min_revenue_growth:
                continue
        if min_user_count is not None:
            if comp.get("user_count", 0) < min_user_count:
                continue
        if sectors and comp.get("sector") not in sectors:
            continue

        results.append(comp)

    sort_key_map = {
        "market_cap": lambda x: x.get("market_cap", 0),
        "market_share": lambda x: x.get("market_share", 0),
        "revenue": lambda x: x.get("revenue", 0),
        "user_count": lambda x: x.get("user_count", 0),
        "growth_rate": lambda x: x.get("growth_rate", 0),
        "name": lambda x: x.get("name", ""),
    }

    sort_key = sort_key_map.get(sort_by, lambda x: x.get("name", ""))
    results.sort(key=sort_key, reverse=sort_desc)

    return results


def add_competitor_note(
    session: dict[str, Any],
    competitor_id: str,
    note: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    comp = get_competitor(session, competitor_id)

    if "notes" not in comp:
        comp["notes"] = []

    note_entry = {
        "note_id": f"note_{action_index}",
        "content": note,
        "timestamp": event_at,
        "action_index": action_index,
    }
    comp["notes"].append(note_entry)

    return {
        "competitor_id": competitor_id,
        "note": note_entry,
    }
