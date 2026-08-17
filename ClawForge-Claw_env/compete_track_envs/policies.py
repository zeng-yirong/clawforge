from __future__ import annotations

import re
from typing import Any


def list_policies(
    session: dict[str, Any],
    *,
    query: str = "",
    policy_type: str | None = None,
    jurisdiction: str | None = None,
    status: str | None = None,
    impact_level: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    policies = session.get("policies", [])
    results = []

    for policy in policies:
        if query:
            q_lower = query.lower()
            title_match = q_lower in policy.get("title", "").lower()
            desc_match = q_lower in policy.get("description", "").lower()
            if not (title_match or desc_match):
                continue

        if policy_type and policy.get("policy_type") != policy_type:
            continue
        if jurisdiction and policy.get("jurisdiction") != jurisdiction:
            continue
        if status and policy.get("status") != status:
            continue
        if impact_level and policy.get("impact_level") != impact_level:
            continue

        results.append(policy)

    if limit is not None:
        results = results[:limit]

    return results


def get_policy(session: dict[str, Any], policy_id: str) -> dict[str, Any]:
    policies = session.get("policies", [])
    for policy in policies:
        if policy.get("policy_id") == policy_id:
            return policy
    raise KeyError(f"Policy not found: {policy_id}")


def get_policy_full_text(session: dict[str, Any], policy_id: str) -> dict[str, Any]:
    policy = get_policy(session, policy_id)
    return {
        "policy_id": policy_id,
        "title": policy.get("title"),
        "full_text": policy.get("full_text", ""),
        "summary": policy.get("summary", ""),
    }


def list_policy_changes(
    session: dict[str, Any],
    policy_id: str,
    *,
    change_type: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    policy = get_policy(session, policy_id)
    changes = policy.get("changes", [])

    results = changes
    if change_type:
        results = [c for c in changes if c.get("change_type") == change_type]

    if limit is not None:
        results = results[:limit]

    return results


def check_policy_impact(
    session: dict[str, Any],
    policy_id: str,
    competitor_ids: list[str] | None = None,
) -> dict[str, Any]:
    policy = get_policy(session, policy_id)
    impact = policy.get("impact", {})
    affected_competitors = impact.get("affected_competitors", [])

    if competitor_ids:
        affected_competitors = [c for c in affected_competitors if c in competitor_ids]

    return {
        "policy_id": policy_id,
        "title": policy.get("title"),
        "impact_level": policy.get("impact_level"),
        "affected_competitors": affected_competitors,
        "key_requirements": impact.get("key_requirements", []),
        "deadline": impact.get("deadline"),
        "compliance_cost_estimate": impact.get("compliance_cost_estimate"),
    }


def filter_policies_by_competitor(
    session: dict[str, Any],
    competitor_id: str,
    *,
    impact_level: str | None = None,
    status: str | None = None,
) -> list[dict[str, Any]]:
    policies = session.get("policies", [])
    results = []

    for policy in policies:
        impact = policy.get("impact", {})
        affected = impact.get("affected_competitors", [])

        if competitor_id not in affected:
            continue

        if impact_level and policy.get("impact_level") != impact_level:
            continue
        if status and policy.get("status") != status:
            continue

        results.append({
            "policy_id": policy.get("policy_id"),
            "title": policy.get("title"),
            "policy_type": policy.get("policy_type"),
            "impact_level": policy.get("impact_level"),
            "status": policy.get("status"),
            "deadline": impact.get("deadline"),
        })

    return results


def track_policy_approval(
    session: dict[str, Any],
    policy_id: str,
    approval_status: str,
    approved_by: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    policy = get_policy(session, policy_id)

    if "approval_history" not in policy:
        policy["approval_history"] = []

    entry = {
        "approval_status": approval_status,
        "approved_by": approved_by,
        "timestamp": event_at,
        "action_index": action_index,
    }
    policy["approval_history"].append(entry)
    policy["status"] = approval_status

    return {
        "policy_id": policy_id,
        "approval": entry,
    }


def search_policies_by_keyword(
    session: dict[str, Any],
    keyword: str,
    *,
    case_sensitive: bool = False,
) -> list[dict[str, Any]]:
    policies = session.get("policies", [])
    results = []

    for policy in policies:
        text_to_search = keyword if case_sensitive else keyword.lower()

        title = policy.get("title", "")
        description = policy.get("description", "")
        full_text = policy.get("full_text", "")

        if not case_sensitive:
            title = title.lower()
            description = description.lower()
            full_text = full_text.lower()

        if text_to_search in title or text_to_search in description or text_to_search in full_text:
            results.append(policy)

    return results


def get_regulatory_risks(
    session: dict[str, Any],
    competitor_id: str | None = None,
    min_impact_level: str = "medium",
) -> dict[str, Any]:
    policies = session.get("policies", [])
    impact_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}

    min_level_idx = impact_order.get(min_impact_level, 0)

    risks = []
    for policy in policies:
        policy_level = impact_order.get(policy.get("impact_level", "low"), 0)
        if policy_level < min_level_idx:
            continue

        impact = policy.get("impact", {})
        affected = impact.get("affected_competitors", [])

        if competitor_id and competitor_id not in affected:
            continue

        risks.append({
            "policy_id": policy.get("policy_id"),
            "title": policy.get("title"),
            "impact_level": policy.get("impact_level"),
            "status": policy.get("status"),
            "deadline": impact.get("deadline"),
            "compliance_cost_estimate": impact.get("compliance_cost_estimate"),
        })

    risks.sort(key=lambda x: impact_order.get(x.get("impact_level", "low"), 0), reverse=True)

    return {
        "competitor_id": competitor_id,
        "risks_count": len(risks),
        "risks": risks,
    }


def analyze_policy_trend(
    session: dict[str, Any],
    jurisdiction: str | None = None,
    policy_type: str | None = None,
) -> dict[str, Any]:
    policies = session.get("policies", [])

    status_counts = {"proposed": 0, "active": 0, "amended": 0, "repealed": 0}
    impact_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}

    filtered = []
    for policy in policies:
        if jurisdiction and policy.get("jurisdiction") != jurisdiction:
            continue
        if policy_type and policy.get("policy_type") != policy_type:
            continue
        filtered.append(policy)
        status_counts[policy.get("status", "unknown")] = status_counts.get(policy.get("status", "unknown"), 0) + 1
        impact_counts[policy.get("impact_level", "unknown")] = impact_counts.get(policy.get("impact_level", "unknown"), 0) + 1

    return {
        "jurisdiction": jurisdiction,
        "policy_type": policy_type,
        "total_policies": len(filtered),
        "status_breakdown": status_counts,
        "impact_breakdown": impact_counts,
    }
