from __future__ import annotations

from copy import deepcopy
from typing import Any


USAGE_KEYS = (
    "vcpu",
    "memory_gb",
    "gpu",
    "block_storage_gb",
    "object_storage_gb",
)


def _normalize_query(value: str | None) -> str:
    return value.strip().lower() if value else ""


def _clean_number(value: float) -> int | float:
    rounded = round(float(value), 4)
    if rounded.is_integer():
        return int(rounded)
    return rounded


def build_cluster_summary(cluster: dict[str, Any]) -> dict[str, Any]:
    return {
        "cluster_id": cluster["cluster_id"],
        "cluster_name": cluster["cluster_name"],
        "business_service": cluster["business_service"],
        "domain": cluster["domain"],
        "environment": cluster["environment"],
        "owner_team": cluster["owner_team"],
        "cluster_role": cluster["cluster_role"],
        "service_tier": cluster["service_tier"],
        "region": cluster["region"],
    }


def list_clusters(
    session: dict[str, Any],
    *,
    query: str = "",
    domain: str | None = None,
    cluster_role: str | None = None,
    environment: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query_lower = _normalize_query(query)
    domain_lower = _normalize_query(domain)
    role_lower = _normalize_query(cluster_role)
    environment_lower = _normalize_query(environment)
    results: list[dict[str, Any]] = []

    for cluster in session["clusters"]:
        searchable = " ".join(
            [
                str(cluster["cluster_name"]),
                str(cluster["business_service"]),
                str(cluster["domain"]),
                str(cluster["owner_team"]),
                " ".join(str(item) for item in cluster.get("workload_tags", [])),
            ]
        ).lower()
        if query_lower and query_lower not in searchable:
            continue
        if domain_lower and str(cluster["domain"]).lower() != domain_lower:
            continue
        if role_lower and str(cluster["cluster_role"]).lower() != role_lower:
            continue
        if environment_lower and str(cluster["environment"]).lower() != environment_lower:
            continue
        results.append(build_cluster_summary(cluster))

    results.sort(key=lambda item: str(item["cluster_name"]))
    return results[:limit] if limit is not None else results


def get_cluster(session: dict[str, Any], cluster_id: str) -> dict[str, Any]:
    for cluster in session["clusters"]:
        if cluster["cluster_id"] == cluster_id:
            return deepcopy(cluster)
    raise KeyError(f"Cluster not found: {cluster_id}")


def build_ledger_entry_summary(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "entry_id": entry["entry_id"],
        "cluster_id": entry["cluster_id"],
        "cluster_name": entry["cluster_name"],
        "resource_name": entry["resource_name"],
        "resource_family": entry["resource_family"],
        "metric_code": entry["metric_code"],
        "quantity": entry["quantity"],
        "unit": entry["unit"],
        "billing_model": entry["billing_model"],
    }


def list_ledger_entries(
    session: dict[str, Any],
    *,
    cluster_id: str | None = None,
    resource_family: str | None = None,
    metric_code: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    family_lower = _normalize_query(resource_family)
    metric_lower = _normalize_query(metric_code)
    results: list[dict[str, Any]] = []

    for entry in session["ledger_entries"]:
        if cluster_id and entry["cluster_id"] != cluster_id:
            continue
        if family_lower and str(entry["resource_family"]).lower() != family_lower:
            continue
        if metric_lower and str(entry["metric_code"]).lower() != metric_lower:
            continue
        results.append(build_ledger_entry_summary(entry))

    results.sort(key=lambda item: (str(item["cluster_name"]), str(item["resource_family"]), str(item["resource_name"])))
    return results[:limit] if limit is not None else results


def get_ledger_entry(session: dict[str, Any], entry_id: str) -> dict[str, Any]:
    for entry in session["ledger_entries"]:
        if entry["entry_id"] == entry_id:
            return deepcopy(entry)
    raise KeyError(f"Ledger entry not found: {entry_id}")


def aggregate_usage_snapshot(session: dict[str, Any], cluster_id: str) -> dict[str, Any]:
    cluster = get_cluster(session, cluster_id)
    relevant_entries = [entry for entry in session["ledger_entries"] if entry["cluster_id"] == cluster_id]
    if not relevant_entries:
        raise ValueError(f"No ledger entries available for cluster: {cluster_id}")

    totals = {key: 0.0 for key in USAGE_KEYS}
    entry_ids: list[str] = []

    for entry in relevant_entries:
        metric_code = str(entry["metric_code"])
        if metric_code not in totals:
            continue
        totals[metric_code] += float(entry["quantity"])
        entry_ids.append(entry["entry_id"])

    return {
        "cluster_id": cluster["cluster_id"],
        "cluster_name": cluster["cluster_name"],
        "business_service": cluster["business_service"],
        "domain": cluster["domain"],
        "environment": cluster["environment"],
        "owner_team": cluster["owner_team"],
        "cluster_role": cluster["cluster_role"],
        "resource_entry_count": len(relevant_entries),
        "ledger_entry_ids": entry_ids,
        "usage": {key: _clean_number(totals[key]) for key in USAGE_KEYS},
    }
