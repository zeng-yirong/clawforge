from __future__ import annotations

from copy import deepcopy
from typing import Any

from .ledger import USAGE_KEYS, aggregate_usage_snapshot
from .pricing import get_pricing_catalog, get_pricing_rate_map


def _append_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def _clean_money(value: float) -> float:
    return round(float(value), 2)


def _cache_entry_id(action_index: int) -> str:
    return f"cache_{action_index:06d}"


def _append_cache_entry(
    session: dict[str, Any],
    *,
    cache_key: str,
    entry_type: str,
    payload: dict[str, Any],
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    entry = {
        "entry_id": _cache_entry_id(action_index),
        "cache_key": cache_key,
        "entry_type": entry_type,
        "created_at": event_at,
        "action_index": action_index,
        "payload": payload,
    }
    session["cache"]["entries"].append(entry)
    session["cache"]["latest"][cache_key] = entry["entry_id"]
    _append_unique(session["observations"]["cache_entry_ids"], entry["entry_id"])
    return deepcopy(entry)


def _latest_cache_entry(session: dict[str, Any], cache_key: str) -> dict[str, Any] | None:
    entry_id = session["cache"]["latest"].get(cache_key)
    if not entry_id:
        return None
    for entry in reversed(session["cache"]["entries"]):
        if entry["entry_id"] == entry_id:
            return deepcopy(entry)
    return None


def list_cache_entries(
    session: dict[str, Any],
    *,
    entry_type: str | None = None,
    cache_key: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    entry_type_lower = entry_type.strip().lower() if entry_type else None

    for entry in reversed(session["cache"]["entries"]):
        if entry_type_lower and str(entry["entry_type"]).lower() != entry_type_lower:
            continue
        if cache_key and entry["cache_key"] != cache_key:
            continue
        payload = entry["payload"]
        cost_totals = payload.get("cost_totals", {})
        results.append(
            {
                "entry_id": entry["entry_id"],
                "cache_key": entry["cache_key"],
                "entry_type": entry["entry_type"],
                "created_at": entry["created_at"],
                "action_index": entry["action_index"],
                "cluster_id": payload.get("cluster_id"),
                "catalog_id": payload.get("catalog_id"),
                "billing_month": payload.get("billing_month"),
                "cluster_count": payload.get("cluster_count"),
                "monthly_cost_total": cost_totals.get("monthly_cost_total"),
            }
        )

    return results[:limit] if limit is not None else results


def get_cache_entry(session: dict[str, Any], entry_id: str) -> dict[str, Any]:
    for entry in session["cache"]["entries"]:
        if entry["entry_id"] == entry_id:
            return deepcopy(entry)
    raise KeyError(f"Cache entry not found: {entry_id}")


def _latest_aggregate_entry_id(session: dict[str, Any], cluster_id: str) -> str | None:
    cache_key = f"cluster_usage::{cluster_id}"
    latest = _latest_cache_entry(session, cache_key)
    if latest is None:
        return None
    return str(latest["entry_id"])


def aggregate_cluster_usage(
    session: dict[str, Any],
    cluster_id: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    payload = aggregate_usage_snapshot(session, cluster_id)
    cache_key = f"cluster_usage::{cluster_id}"
    _append_unique(session["observations"]["cluster_ids_seen"], cluster_id)
    _append_unique(session["observations"]["aggregated_cluster_ids"], cluster_id)
    return _append_cache_entry(
        session,
        cache_key=cache_key,
        entry_type="cluster_usage_aggregate",
        payload=payload,
        event_at=event_at,
        action_index=action_index,
    )


def _default_business_cluster_ids(session: dict[str, Any]) -> list[str]:
    return [
        str(cluster["cluster_id"])
        for cluster in session["clusters"]
        if str(cluster.get("cluster_role")) == "business"
    ]


def _cost_breakdown_for_usage(
    usage: dict[str, Any],
    rate_map: dict[str, dict[str, Any]],
    billing_hours: int,
) -> dict[str, float]:
    costs: dict[str, float] = {}
    for usage_key in USAGE_KEYS:
        rate = rate_map.get(usage_key)
        if rate is None:
            raise KeyError(f"Pricing catalog does not define metric: {usage_key}")
        quantity = float(usage.get(usage_key, 0))
        unit_price = float(rate["unit_price"])
        billing_basis = str(rate["billing_basis"])
        metric_cost = quantity * unit_price * billing_hours if billing_basis == "hourly" else quantity * unit_price
        costs[f"{usage_key}_cost"] = _clean_money(metric_cost)
    return costs


def generate_cost_report(
    session: dict[str, Any],
    catalog_id: str,
    event_at: str,
    action_index: int,
    *,
    cluster_ids: list[str] | None = None,
    billing_month: str | None = None,
) -> dict[str, Any]:
    resolved_cluster_ids = cluster_ids or _default_business_cluster_ids(session)
    if not resolved_cluster_ids:
        raise ValueError("No business clusters are available for report generation.")

    catalog = get_pricing_catalog(session, catalog_id)
    rate_map = get_pricing_rate_map(session, catalog_id)
    resolved_billing_month = billing_month or str(catalog.get("billing_month", ""))
    billing_hours = int(catalog["billing_hours"])

    clusters_payload: list[dict[str, Any]] = []
    source_aggregate_entry_ids: list[str] = []
    totals = {key: 0.0 for key in USAGE_KEYS}
    compute_cost_total = 0.0
    storage_cost_total = 0.0

    for cluster_id in resolved_cluster_ids:
        snapshot = aggregate_usage_snapshot(session, cluster_id)
        latest_aggregate_entry_id = _latest_aggregate_entry_id(session, cluster_id)
        if latest_aggregate_entry_id:
            source_aggregate_entry_ids.append(latest_aggregate_entry_id)
        usage = snapshot["usage"]
        for usage_key in USAGE_KEYS:
            totals[usage_key] += float(usage.get(usage_key, 0))
        cost_breakdown = _cost_breakdown_for_usage(usage, rate_map, billing_hours)
        cluster_compute_cost = (
            cost_breakdown["vcpu_cost"] + cost_breakdown["memory_gb_cost"] + cost_breakdown["gpu_cost"]
        )
        cluster_storage_cost = (
            cost_breakdown["block_storage_gb_cost"] + cost_breakdown["object_storage_gb_cost"]
        )
        cluster_total_cost = _clean_money(cluster_compute_cost + cluster_storage_cost)
        compute_cost_total += cluster_compute_cost
        storage_cost_total += cluster_storage_cost
        clusters_payload.append(
            {
                "cluster_id": snapshot["cluster_id"],
                "cluster_name": snapshot["cluster_name"],
                "business_service": snapshot["business_service"],
                "usage": usage,
                "monthly_cost_breakdown": cost_breakdown,
                "monthly_compute_cost": _clean_money(cluster_compute_cost),
                "monthly_storage_cost": _clean_money(cluster_storage_cost),
                "monthly_cost_total": cluster_total_cost,
            }
        )
        _append_unique(session["observations"]["cluster_ids_seen"], cluster_id)

    monthly_cost_total = _clean_money(compute_cost_total + storage_cost_total)
    compute_cost_total = _clean_money(compute_cost_total)
    storage_cost_total = _clean_money(storage_cost_total)
    highest_cost_cluster = max(clusters_payload, key=lambda item: float(item["monthly_cost_total"]))

    payload = {
        "catalog_id": catalog_id,
        "catalog_version": catalog["version"],
        "billing_month": resolved_billing_month,
        "currency": catalog["currency"],
        "cluster_ids": resolved_cluster_ids,
        "cluster_count": len(clusters_payload),
        "clusters": clusters_payload,
        "totals": {key: int(value) if float(value).is_integer() else round(value, 4) for key, value in totals.items()},
        "cost_totals": {
            "compute_cost": compute_cost_total,
            "storage_cost": storage_cost_total,
            "monthly_cost_total": monthly_cost_total,
        },
        "summary": {
            "highest_cost_cluster_id": highest_cost_cluster["cluster_id"],
            "highest_cost_cluster_name": highest_cost_cluster["cluster_name"],
            "compute_share_pct": _clean_money((compute_cost_total / monthly_cost_total) * 100.0) if monthly_cost_total else 0.0,
            "storage_share_pct": _clean_money((storage_cost_total / monthly_cost_total) * 100.0) if monthly_cost_total else 0.0,
        },
        "source_aggregate_entry_ids": source_aggregate_entry_ids,
    }
    cache_key = f"monthly_cost_report::{resolved_billing_month}::{catalog_id}"
    _append_unique(session["observations"]["pricing_catalog_ids_seen"], catalog_id)
    return _append_cache_entry(
        session,
        cache_key=cache_key,
        entry_type="monthly_cost_detail_report",
        payload=payload,
        event_at=event_at,
        action_index=action_index,
    )
