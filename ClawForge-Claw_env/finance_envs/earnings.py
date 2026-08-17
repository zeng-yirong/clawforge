from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_earnings_summary(earnings: dict[str, Any]) -> dict[str, Any]:
    return {
        "earnings_id": earnings["earnings_id"],
        "ticker": earnings["ticker"],
        "quarter": earnings["quarter"],
        "report_date": earnings["report_date"],
        "revenue_actual": earnings["revenue_actual"],
        "revenue_beat": earnings["revenue_beat"],
        "revenue_beat_pct": earnings["revenue_beat_pct"],
        "eps_actual": earnings["eps_actual"],
        "eps_beat": earnings["eps_beat"],
        "eps_beat_pct": earnings["eps_beat_pct"],
        "gross_margin_actual": earnings["gross_margin_actual"],
        "net_margin_actual": earnings["net_margin_actual"],
    }


def list_earnings(
    session: dict[str, Any],
    *,
    ticker: str | None = None,
    beat_only: bool = False,
    miss_only: bool = False,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    results = []

    for earnings in session["earnings"]:
        if ticker and earnings["ticker"] != ticker:
            continue
        if beat_only and not (earnings["revenue_beat"] or earnings["eps_beat"]):
            continue
        if miss_only and not (not earnings["revenue_beat"] and not earnings["eps_beat"]):
            continue
        results.append(build_earnings_summary(earnings))

    results.sort(key=lambda item: item["report_date"], reverse=True)
    return results[:limit] if limit is not None else results


def get_earnings(session: dict[str, Any], earnings_id: str) -> dict[str, Any]:
    for earnings in session["earnings"]:
        if earnings["earnings_id"] == earnings_id:
            return deepcopy(earnings)
    raise KeyError(f"Earnings record not found: {earnings_id}")


def create_earnings_summary(
    session: dict[str, Any],
    tickers: list[str],
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    summary = {
        "summary_id": f"earn_sum_{action_index}",
        "created_at": event_at,
        "action_index": action_index,
        "tickers_covered": tickers,
        "records": [],
    }

    for ticker in tickers:
        for earnings in session["earnings"]:
            if earnings["ticker"] == ticker:
                summary["records"].append({
                    "ticker": ticker,
                    "quarter": earnings["quarter"],
                    "revenue_beat": earnings["revenue_beat"],
                    "revenue_beat_pct": earnings["revenue_beat_pct"],
                    "eps_beat": earnings["eps_beat"],
                    "eps_beat_pct": earnings["eps_beat_pct"],
                    "key_highlights": earnings.get("key_highlights", []),
                })

    session.setdefault("earnings_summaries", []).append(summary)
    session["last_action_index"] = action_index
    return summary
