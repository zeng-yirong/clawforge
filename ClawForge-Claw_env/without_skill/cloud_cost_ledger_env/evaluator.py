from __future__ import annotations

from typing import Any


def _action_types(session: dict[str, Any]) -> list[str]:
    return [str(item.get("action_type")) for item in session.get("actions", [])]


def _latest_entry_of_type(session: dict[str, Any], entry_type: str) -> dict[str, Any] | None:
    for entry in reversed(session.get("cache", {}).get("entries", [])):
        if entry.get("entry_type") == entry_type:
            return entry
    return None


def _latest_cluster_aggregate(session: dict[str, Any], cluster_id: str) -> dict[str, Any] | None:
    for entry in reversed(session.get("cache", {}).get("entries", [])):
        if entry.get("entry_type") != "cluster_usage_aggregate":
            continue
        payload = entry.get("payload", {})
        if payload.get("cluster_id") == cluster_id:
            return entry
    return None


def _approx_equal(actual: Any, expected: Any, tolerance: float = 0.01) -> bool:
    try:
        return abs(float(actual) - float(expected)) <= tolerance
    except (TypeError, ValueError):
        return False


def evaluate_session(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    action_types = _action_types(session)
    required_actions = scenario.get("required_actions", [])
    if required_actions:
        matched = len({item for item in required_actions if item in action_types})
        required_action_score = (matched / len(required_actions)) * 20.0
    else:
        matched = 0
        required_action_score = 0.0

    target_cluster_ids = list(scenario.get("target_cluster_ids", []))
    expected_aggregate_totals = scenario.get("expected_aggregate_totals", {})
    required_attachment_paths = set(scenario.get("required_attachment_paths", []))
    active_catalog_id = scenario["active_pricing_catalog_id"]
    stale_catalog_ids = set(scenario.get("stale_pricing_catalog_ids", []))
    excluded_cluster_ids = set(scenario.get("excluded_cluster_ids", []))
    expected_report_cluster_costs = scenario.get("expected_report_cluster_costs", {})
    expected_report_total_cost = scenario.get("expected_report_total_cost")
    expected_totals = scenario.get("expected_totals", {})
    expected_highest_cost_cluster_id = scenario.get("expected_highest_cost_cluster_id")

    attachments_read = set(session.get("observations", {}).get("attachments_read", []))
    pricing_catalog_ids_seen = set(session.get("observations", {}).get("pricing_catalog_ids_seen", []))

    reading_score = 0.0
    if required_attachment_paths:
        reading_score += 10.0 * (len(attachments_read & required_attachment_paths) / len(required_attachment_paths))
    if active_catalog_id in pricing_catalog_ids_seen:
        reading_score += 5.0

    aggregate_score = 0.0
    aggregate_checks: dict[str, dict[str, Any]] = {}
    for cluster_id in target_cluster_ids:
        entry = _latest_cluster_aggregate(session, cluster_id)
        expected_usage = expected_aggregate_totals.get(cluster_id, {})
        exists = entry is not None
        metrics_match = False
        if entry:
            payload_usage = entry.get("payload", {}).get("usage", {})
            metrics_match = all(_approx_equal(payload_usage.get(key), value) for key, value in expected_usage.items())
        aggregate_checks[cluster_id] = {
            "exists": exists,
            "metrics_match": metrics_match,
        }
        if exists:
            aggregate_score += 3.0
        if metrics_match:
            aggregate_score += 7.0

    report_entry = _latest_entry_of_type(session, "monthly_cost_detail_report")
    report_score = 0.0
    report_checks = {
        "exists": False,
        "correct_catalog": False,
        "covers_target_clusters": False,
        "excludes_non_target_clusters": False,
        "totals_match": False,
        "cluster_costs_match": False,
        "grand_total_match": False,
        "highest_cost_cluster_match": False,
    }
    forbidden_cluster_hits: list[str] = []
    if report_entry:
        payload = report_entry.get("payload", {})
        report_checks["exists"] = True
        report_checks["correct_catalog"] = payload.get("catalog_id") == active_catalog_id
        reported_cluster_ids = set(payload.get("cluster_ids", []))
        report_checks["covers_target_clusters"] = set(target_cluster_ids).issubset(reported_cluster_ids)
        forbidden_cluster_hits = sorted(reported_cluster_ids & excluded_cluster_ids)
        report_checks["excludes_non_target_clusters"] = not forbidden_cluster_hits

        report_totals = payload.get("totals", {})
        report_checks["totals_match"] = all(
            _approx_equal(report_totals.get(key), value) for key, value in expected_totals.items()
        )

        actual_cluster_costs = {
            item.get("cluster_id"): item.get("monthly_cost_total")
            for item in payload.get("clusters", [])
        }
        report_checks["cluster_costs_match"] = all(
            _approx_equal(actual_cluster_costs.get(cluster_id), value)
            for cluster_id, value in expected_report_cluster_costs.items()
        )
        report_checks["grand_total_match"] = _approx_equal(
            payload.get("cost_totals", {}).get("monthly_cost_total"),
            expected_report_total_cost,
        )
        report_checks["highest_cost_cluster_match"] = (
            payload.get("summary", {}).get("highest_cost_cluster_id") == expected_highest_cost_cluster_id
        )

        report_score += 5.0
        report_score += 5.0 if report_checks["correct_catalog"] else 0.0
        report_score += 8.0 if report_checks["covers_target_clusters"] else 0.0
        report_score += 2.0 if report_checks["excludes_non_target_clusters"] else 0.0
        report_score += 5.0 if report_checks["totals_match"] else 0.0
        report_score += 5.0 if report_checks["cluster_costs_match"] else 0.0
        report_score += 3.0 if report_checks["grand_total_match"] else 0.0
        report_score += 2.0 if report_checks["highest_cost_cluster_match"] else 0.0

    penalty = 0.0
    stale_catalog_hits: list[str] = []
    for entry in session.get("cache", {}).get("entries", []):
        payload = entry.get("payload", {})
        catalog_id = payload.get("catalog_id")
        if catalog_id in stale_catalog_ids:
            stale_catalog_hits.append(str(catalog_id))
            penalty -= 15.0
        entry_cluster_ids = payload.get("cluster_ids", [])
        if isinstance(entry_cluster_ids, list):
            penalty -= 10.0 * len(set(entry_cluster_ids) & excluded_cluster_ids)

    overall_score = max(
        0.0,
        min(100.0, required_action_score + reading_score + aggregate_score + report_score + penalty),
    )

    return {
        "overall_score": round(overall_score, 4),
        "breakdown": {
            "required_action_score": round(required_action_score, 4),
            "reading_score": round(reading_score, 4),
            "aggregate_score": round(aggregate_score, 4),
            "report_score": round(report_score, 4),
            "penalty": round(penalty, 4),
        },
        "required_actions": {
            "expected": required_actions,
            "matched_count": matched,
            "observed_actions": action_types,
        },
        "checks": {
            "aggregate": aggregate_checks,
            "report": report_checks,
            "attachments_read": sorted(attachments_read),
            "pricing_catalog_ids_seen": sorted(pricing_catalog_ids_seen),
            "stale_catalog_hits": stale_catalog_hits,
            "forbidden_cluster_hits": forbidden_cluster_hits,
        },
    }
