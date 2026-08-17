from __future__ import annotations

from copy import deepcopy
from typing import Any


def _normalize_query(value: str | None) -> str:
    return value.strip().lower() if value else ""


def build_pricing_catalog_summary(catalog: dict[str, Any]) -> dict[str, Any]:
    return {
        "catalog_id": catalog["catalog_id"],
        "version": catalog["version"],
        "status": catalog["status"],
        "region": catalog["region"],
        "currency": catalog["currency"],
        "billing_hours": catalog["billing_hours"],
        "approved_for_reporting": catalog["approved_for_reporting"],
        "effective_from": catalog["effective_from"],
        "effective_to": catalog["effective_to"],
    }


def list_pricing_catalogs(
    session: dict[str, Any],
    *,
    status: str | None = None,
    current_only: bool = False,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    status_lower = _normalize_query(status)
    results: list[dict[str, Any]] = []

    for catalog in session["pricing_catalogs"]:
        if status_lower and str(catalog["status"]).lower() != status_lower:
            continue
        if current_only and not bool(catalog.get("approved_for_reporting")):
            continue
        results.append(build_pricing_catalog_summary(catalog))

    results.sort(key=lambda item: (str(item["status"]), str(item["catalog_id"])))
    return results[:limit] if limit is not None else results


def get_pricing_catalog(session: dict[str, Any], catalog_id: str) -> dict[str, Any]:
    for catalog in session["pricing_catalogs"]:
        if catalog["catalog_id"] == catalog_id:
            return deepcopy(catalog)
    raise KeyError(f"Pricing catalog not found: {catalog_id}")


def get_pricing_rate_map(session: dict[str, Any], catalog_id: str) -> dict[str, dict[str, Any]]:
    catalog = get_pricing_catalog(session, catalog_id)
    return {item["metric_code"]: item for item in catalog.get("rates", [])}
