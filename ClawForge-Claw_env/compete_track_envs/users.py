from __future__ import annotations

from typing import Any


def list_users(
    session: dict[str, Any],
    *,
    query: str = "",
    acquisition_source: str | None = None,
    user_tier: str | None = None,
    cohort: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    users = session.get("users", [])
    results = []

    for user in users:
        if query:
            q_lower = query.lower()
            name_match = q_lower in user.get("name", "").lower()
            email_match = q_lower in user.get("email", "").lower()
            if not (name_match or email_match):
                continue

        if acquisition_source and user.get("acquisition_source") != acquisition_source:
            continue
        if user_tier and user.get("tier") != user_tier:
            continue
        if cohort and user.get("cohort") != cohort:
            continue

        results.append(user)

    if limit is not None:
        results = results[:limit]

    return results


def get_user(session: dict[str, Any], user_id: str) -> dict[str, Any]:
    users = session.get("users", [])
    for user in users:
        if user.get("user_id") == user_id:
            return user
    raise KeyError(f"User not found: {user_id}")


def get_user_engagement(session: dict[str, Any], user_id: str) -> dict[str, Any]:
    user = get_user(session, user_id)
    return {
        "user_id": user_id,
        "name": user.get("name"),
        "engagement_metrics": user.get("engagement", {}),
        "activity_history": user.get("activity_history", []),
    }


def get_user_acquisition_details(
    session: dict[str, Any],
    user_id: str,
) -> dict[str, Any]:
    user = get_user(session, user_id)
    return {
        "user_id": user_id,
        "name": user.get("name"),
        "acquisition_source": user.get("acquisition_source"),
        "acquisition_campaign": user.get("acquisition_campaign"),
        "acquisition_date": user.get("acquisition_date"),
        "acquisition_cost": user.get("acquisition_cost"),
        "initial_channel": user.get("initial_channel"),
    }


def list_user_cohorts(
    session: dict[str, Any],
    cohort: str | None = None,
) -> list[dict[str, Any]]:
    users = session.get("users", [])
    cohort_map = {}

    for user in users:
        c = user.get("cohort")
        if cohort and c != cohort:
            continue

        if c not in cohort_map:
            cohort_map[c] = {
                "cohort": c,
                "count": 0,
                "total_revenue": 0,
                "avg_engagement": 0,
                "tier_breakdown": {"basic": 0, "premium": 0, "enterprise": 0},
            }

        cohort_map[c]["count"] += 1
        cohort_map[c]["total_revenue"] += user.get("lifetime_value", 0)
        tier = user.get("tier", "basic")
        if tier in cohort_map[c]["tier_breakdown"]:
            cohort_map[c]["tier_breakdown"][tier] += 1

    for c in cohort_map:
        if cohort_map[c]["count"] > 0:
            cohort_map[c]["avg_engagement"] = sum(
                u.get("engagement", {}).get("score", 0) for u in users if u.get("cohort") == c
            ) / cohort_map[c]["count"]
            cohort_map[c]["avg_lifetime_value"] = cohort_map[c]["total_revenue"] / cohort_map[c]["count"]

    return list(cohort_map.values())


def analyze_acquisition_sources(
    session: dict[str, Any],
) -> dict[str, Any]:
    users = session.get("users", [])
    source_map = {}

    for user in users:
        source = user.get("acquisition_source", "unknown")
        if source not in source_map:
            source_map[source] = {
                "source": source,
                "user_count": 0,
                "total_acquisition_cost": 0,
                "total_lifetime_value": 0,
                "avg_engagement": 0,
                "conversion_rate": 0,
            }

        source_map[source]["user_count"] += 1
        source_map[source]["total_acquisition_cost"] += user.get("acquisition_cost", 0)
        source_map[source]["total_lifetime_value"] += user.get("lifetime_value", 0)

    for source in source_map:
        count = source_map[source]["user_count"]
        if count > 0:
            source_map[source]["avg_acquisition_cost"] = source_map[source]["total_acquisition_cost"] / count
            source_map[source]["avg_lifetime_value"] = source_map[source]["total_lifetime_value"] / count
            if source_map[source]["total_acquisition_cost"] > 0:
                source_map[source]["roi"] = (
                    source_map[source]["total_lifetime_value"] / source_map[source]["total_acquisition_cost"]
                )

    return {
        "sources": list(source_map.values()),
        "total_users": len(users),
    }


def screen_users(
    session: dict[str, Any],
    *,
    min_lifetime_value: float | None = None,
    max_lifetime_value: float | None = None,
    min_engagement_score: float | None = None,
    user_tiers: list[str] | None = None,
    acquisition_sources: list[str] | None = None,
    has_churned: bool | None = None,
    sort_by: str = "lifetime_value",
    sort_desc: bool = True,
) -> list[dict[str, Any]]:
    users = session.get("users", [])
    results = []

    for user in users:
        if min_lifetime_value is not None:
            if user.get("lifetime_value", 0) < min_lifetime_value:
                continue
        if max_lifetime_value is not None:
            if user.get("lifetime_value", 0) > max_lifetime_value:
                continue
        if min_engagement_score is not None:
            if user.get("engagement", {}).get("score", 0) < min_engagement_score:
                continue
        if user_tiers and user.get("tier") not in user_tiers:
            continue
        if acquisition_sources and user.get("acquisition_source") not in acquisition_sources:
            continue
        if has_churned is not None:
            if user.get("churned", False) != has_churned:
                continue

        results.append(user)

    sort_key_map = {
        "lifetime_value": lambda x: x.get("lifetime_value", 0),
        "engagement_score": lambda x: x.get("engagement", {}).get("score", 0),
        "acquisition_cost": lambda x: x.get("acquisition_cost", 0),
        "name": lambda x: x.get("name", ""),
    }

    sort_key = sort_key_map.get(sort_by, lambda x: x.get("name", ""))
    results.sort(key=sort_key, reverse=sort_desc)

    return results


def track_user_event(
    session: dict[str, Any],
    user_id: str,
    event_type: str,
    event_details: dict[str, Any],
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    user = get_user(session, user_id)

    if "events" not in user:
        user["events"] = []

    event_entry = {
        "event_id": f"evt_{action_index}",
        "event_type": event_type,
        "details": event_details,
        "timestamp": event_at,
        "action_index": action_index,
    }
    user["events"].append(event_entry)

    if event_type == "upgrade":
        user["tier"] = event_details.get("new_tier", user.get("tier"))
    elif event_type == "churn":
        user["churned"] = True
        user["churn_date"] = event_at

    return {
        "user_id": user_id,
        "event": event_entry,
    }


def compare_user_cohorts(
    session: dict[str, Any],
    cohort_ids: list[str],
) -> dict[str, Any]:
    users = session.get("users", [])
    comparison = {"cohorts": {}}

    for cohort_id in cohort_ids:
        cohort_users = [u for u in users if u.get("cohort") == cohort_id]
        if not cohort_users:
            continue

        comparison["cohorts"][cohort_id] = {
            "user_count": len(cohort_users),
            "avg_lifetime_value": sum(u.get("lifetime_value", 0) for u in cohort_users) / len(cohort_users),
            "avg_engagement": sum(u.get("engagement", {}).get("score", 0) for u in cohort_users) / len(cohort_users),
            "churn_rate": sum(1 for u in cohort_users if u.get("churned")) / len(cohort_users),
            "tier_breakdown": {},
        }

        for u in cohort_users:
            tier = u.get("tier", "basic")
            comparison["cohorts"][cohort_id]["tier_breakdown"][tier] = (
                comparison["cohorts"][cohort_id]["tier_breakdown"].get(tier, 0) + 1
            )

    return comparison


def get_user_acquisition_funnel(
    session: dict[str, Any],
    competitor_id: str | None = None,
) -> dict[str, Any]:
    users = session.get("users", [])

    if competitor_id:
        users = [u for u in users if u.get("competitor_id") == competitor_id]

    total = len(users)
    if total == 0:
        return {"funnel": [], "total": 0}

    converted = sum(1 for u in users if u.get("converted", False))
    active = sum(1 for u in users if not u.get("churned", False))
    premium = sum(1 for u in users if u.get("tier") in ["premium", "enterprise"])

    return {
        "funnel": [
            {"stage": "acquired", "count": total, "percentage": 100.0},
            {"stage": "converted", "count": converted, "percentage": (converted / total * 100) if total > 0 else 0},
            {"stage": "active", "count": active, "percentage": (active / total * 100) if total > 0 else 0},
            {"stage": "premium", "count": premium, "percentage": (premium / total * 100) if total > 0 else 0},
        ],
        "total": total,
    }


def update_user_tier(
    session: dict[str, Any],
    user_id: str,
    new_tier: str,
    reason: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    user = get_user(session, user_id)
    old_tier = user.get("tier", "basic")

    if "tier_history" not in user:
        user["tier_history"] = []

    user["tier_history"].append({
        "from_tier": old_tier,
        "to_tier": new_tier,
        "reason": reason,
        "timestamp": event_at,
        "action_index": action_index,
    })

    user["tier"] = new_tier

    return {
        "user_id": user_id,
        "old_tier": old_tier,
        "new_tier": new_tier,
        "reason": reason,
    }
