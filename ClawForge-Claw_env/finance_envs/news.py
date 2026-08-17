from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_news_summary(news_item: dict[str, Any]) -> dict[str, Any]:
    return {
        "news_id": news_item["news_id"],
        "headline": news_item["headline"],
        "summary": news_item["summary"],
        "category": news_item["category"],
        "source": news_item["source"],
        "published_at": news_item["published_at"],
        "sentiment": news_item.get("sentiment"),
        "impact": news_item.get("impact"),
        "related_tickers": news_item.get("related_tickers", []),
    }


def list_news(
    session: dict[str, Any],
    *,
    query: str = "",
    ticker: str | None = None,
    category: str | None = None,
    sentiment: str | None = None,
    impact: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query_lower = query.strip().lower()
    category_lower = category.strip().lower() if category else None
    sentiment_lower = sentiment.strip().lower() if sentiment else None
    impact_lower = impact.strip().lower() if impact else None
    results = []

    for news in session["news"]:
        if ticker:
            if ticker not in news.get("related_tickers", []):
                continue
        if category_lower and news["category"].lower() != category_lower:
            continue
        if sentiment_lower and news.get("sentiment", "").lower() != sentiment_lower:
            continue
        if impact_lower and news.get("impact", "").lower() != impact_lower:
            continue

        searchable = f"{news['headline']} {news['summary']}".lower()
        if query_lower and query_lower not in searchable:
            continue

        results.append(build_news_summary(news))

    results.sort(key=lambda x: x["published_at"], reverse=True)
    return results[:limit] if limit is not None else results


def get_news(session: dict[str, Any], news_id: str) -> dict[str, Any]:
    for news in session["news"]:
        if news["news_id"] == news_id:
            return deepcopy(news)
    raise KeyError(f"News not found: {news_id}")
