from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_stock_summary(stock: dict[str, Any]) -> dict[str, Any]:
    return {
        "ticker": stock["ticker"],
        "company_name": stock["company_name"],
        "sector": stock["sector"],
        "current_price": stock["current_price"],
        "change_pct": stock["change_pct"],
        "volume": stock["volume"],
        "market_cap": stock["market_cap"],
        "pe_ratio": stock["pe_ratio"],
        "analyst_rating": stock["analyst_rating"],
        "fifty_two_week_high": stock["fifty_two_week_high"],
        "fifty_two_week_low": stock["fifty_two_week_low"],
    }


def list_stocks(
    session: dict[str, Any],
    *,
    query: str = "",
    sector: str | None = None,
    min_market_cap: int | None = None,
    min_revenue_growth: float | None = None,
    min_analyst_rating: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query_lower = query.strip().lower()
    sector_lower = sector.strip().lower() if sector else None
    results = []

    for stock in session["stocks"]:
        if sector_lower and stock["sector"].lower() != sector_lower:
            continue
        if min_market_cap is not None and stock["market_cap"] < min_market_cap:
            continue
        if min_revenue_growth is not None:
            if stock.get("revenue_growth_yoy", 0) < min_revenue_growth:
                continue
        if min_analyst_rating:
            rating_order = {"Buy": 3, "Hold": 2, "Sell": 1}
            stock_rating = rating_order.get(stock.get("analyst_rating", "Hold"), 2)
            min_rating = rating_order.get(min_analyst_rating, 2)
            if stock_rating < min_rating:
                continue

        searchable = f"{stock['ticker']} {stock['company_name']} {stock['sector']}".lower()
        if query_lower and query_lower not in searchable:
            continue

        results.append(build_stock_summary(stock))

    results.sort(key=lambda x: x["market_cap"], reverse=True)
    return results[:limit] if limit is not None else results


def get_stock(session: dict[str, Any], ticker: str) -> dict[str, Any]:
    for stock in session["stocks"]:
        if stock["ticker"] == ticker:
            return deepcopy(stock)
    raise KeyError(f"Stock not found: {ticker}")


def screen_stocks(
    session: dict[str, Any],
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
) -> list[dict[str, Any]]:
    sector_lower = sector.strip().lower() if sector else None
    results = []

    for stock in session["stocks"]:
        if sector_lower and stock["sector"].lower() != sector_lower:
            continue
        if min_market_cap is not None and stock["market_cap"] < min_market_cap:
            continue
        if max_pe_ratio is not None and stock.get("pe_ratio", 999) > max_pe_ratio:
            continue
        if min_revenue_growth is not None and stock.get("revenue_growth_yoy", 0) < min_revenue_growth:
            continue
        if min_eps_growth is not None and stock.get("eps_growth_yoy", 0) < min_eps_growth:
            continue
        if min_dividend_yield is not None and stock.get("dividend_yield", 0) < min_dividend_yield:
            continue
        if max_debt_to_equity is not None and stock.get("debt_to_equity", 999) > max_debt_to_equity:
            continue
        if min_analyst_rating:
            rating_order = {"Buy": 3, "Hold": 2, "Sell": 1}
            stock_rating = rating_order.get(stock.get("analyst_rating", "Hold"), 2)
            min_rating = rating_order.get(min_analyst_rating, 2)
            if stock_rating < min_rating:
                continue

        results.append(build_stock_summary(stock))

    sort_keys = {
        "market_cap": lambda x: x["market_cap"],
        "pe_ratio": lambda x: x["pe_ratio"],
        "current_price": lambda x: x["current_price"],
        "change_pct": lambda x: x["change_pct"],
        "volume": lambda x: x["volume"],
    }
    sort_key = sort_keys.get(sort_by, sort_keys["market_cap"])
    results.sort(key=sort_key, reverse=sort_desc)

    return results
