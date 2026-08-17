from __future__ import annotations

from typing import Any


def list_policies(repo) -> list[dict[str, Any]]:
    policy_ids = repo.list_policy_ids()
    policies = []
    for pid in policy_ids:
        p = repo.get_policy(pid)
        p["policy_id"] = pid
        policies.append(p)
    return policies


def get_policy(repo, policy_id: str) -> dict[str, Any]:
    policy = repo.get_policy(policy_id)
    policy["policy_id"] = policy_id
    return policy


def validate_booking_against_policy(
    repo,
    policy_id: str,
    estimated_cost: float,
    cabin_class: str,
    advance_booking_days: int,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    policy = repo.get_policy(policy_id)
    violations = []
    warnings = []

    max_cost = policy.get("max_cost_per_booking", float("inf"))
    if estimated_cost > max_cost:
        violations.append(f"Estimated cost {estimated_cost} exceeds policy limit {max_cost}")

    allowed_classes = policy.get("allowed_cabin_classes", ["economy"])
    if cabin_class not in allowed_classes:
        violations.append(f"Cabin class {cabin_class} not in allowed classes: {allowed_classes}")

    min_advance = policy.get("min_advance_booking_days", 0)
    if advance_booking_days < min_advance:
        violations.append(f"Advance booking {advance_booking_days} days is less than required {min_advance}")

    max_single = policy.get("max_single_booking_cost", float("inf"))
    if estimated_cost > max_single:
        warnings.append(f"Cost exceeds typical single booking threshold of {max_single}")

    requires_approval = policy.get("requires_approval_above", 0)
    approval_needed = estimated_cost >= requires_approval

    return {
        "success": True,
        "policy_id": policy_id,
        "policy_name": policy.get("name", ""),
        "estimated_cost": estimated_cost,
        "cabin_class": cabin_class,
        "violations": violations,
        "warnings": warnings,
        "approval_needed": approval_needed,
        "approval_threshold": requires_approval,
        "validated_at": event_at,
    }


def get_policy_approval_chain(
    repo,
    policy_id: str,
    estimated_cost: float,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    policy = repo.get_policy(policy_id)
    approval_threshold = policy.get("requires_approval_above", 0)
    if estimated_cost < approval_threshold:
        return {"success": True, "approval_needed": False, "approvers": []}

    approvers = []
    for level_name, level_config in policy.get("approval_levels", {}).items():
        threshold = level_config.get("threshold", 0)
        if estimated_cost >= threshold:
            approvers.append({
                "level": level_name,
                "role": level_config.get("role", ""),
                "approver_name": level_config.get("approver", ""),
                "email": level_config.get("email", ""),
            })

    return {
        "success": True,
        "policy_id": policy_id,
        "estimated_cost": estimated_cost,
        "approval_needed": True,
        "approvers": approvers,
        "approval_chain": [a["level"] for a in approvers],
    }


def check_policy_compliance(
    repo,
    policy_id: str,
    booking_details: dict[str, Any],
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    policy = repo.get_policy(policy_id)
    issues = []
    recommendations = []

    preferred_vendors = policy.get("preferred_vendors", [])
    if preferred_vendors:
        vendor = booking_details.get("platform_id", "")
        if vendor not in preferred_vendors:
            issues.append(f"Vendor {vendor} is not in preferred vendor list")
            recommendations.append(f"Consider using one of: {', '.join(preferred_vendors)}")

    restricted_routes = policy.get("restricted_routes", [])
    route = f"{booking_details.get('origin', '')}-{booking_details.get('destination', '')}"
    if route in restricted_routes:
        issues.append(f"Route {route} is restricted by policy")
        recommendations.append("Submit exception request to HR/Legal")

    no_refund_classes = policy.get("no_refund_cabin_classes", [])
    if booking_details.get("cabin_class") in no_refund_classes:
        issues.append(f"Cabin class {booking_details.get('cabin_class')} is non-refundable")
        recommendations.append("Consider economy class for flexibility")

    return {
        "success": True,
        "policy_id": policy_id,
        "compliant": len(issues) == 0,
        "issues": issues,
        "recommendations": recommendations,
        "checked_at": event_at,
    }


def get_policy_restrictions(
    repo,
    policy_id: str,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    policy = repo.get_policy(policy_id)
    return {
        "success": True,
        "policy_id": policy_id,
        "policy_name": policy.get("name", ""),
        "max_cost_per_booking": policy.get("max_cost_per_booking"),
        "max_single_booking_cost": policy.get("max_single_booking_cost"),
        "allowed_cabin_classes": policy.get("allowed_cabin_classes", []),
        "min_advance_booking_days": policy.get("min_advance_booking_days", 0),
        "preferred_vendors": policy.get("preferred_vendors", []),
        "restricted_routes": policy.get("restricted_routes", []),
        "required_documents": policy.get("required_documents", []),
        "no_refund_cabin_classes": policy.get("no_refund_cabin_classes", []),
    }


def get_policy_travel_limits(
    repo,
    policy_id: str,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    policy = repo.get_policy(policy_id)
    return {
        "success": True,
        "policy_id": policy_id,
        "max_daily_limit": policy.get("max_daily_limit"),
        "max_monthly_limit": policy.get("max_monthly_limit"),
        "max_trips_per_month": policy.get("max_trips_per_month"),
        "requires_receipt_above": policy.get("requires_receipt_above", 0),
        "allow_upgrade_at_company_cost": policy.get("allow_upgrade_at_company_cost", False),
    }


def get_domestic_vs_international_policy(
    repo,
    policy_id: str,
    is_international: bool,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    policy = repo.get_policy(policy_id)
    if is_international:
        return {
            "success": True,
            "policy_id": policy_id,
            "is_international": True,
            "max_cost_per_booking": policy.get("international_max_cost", policy.get("max_cost_per_booking")),
            "allowed_cabin_classes": policy.get("international_cabin_classes", policy.get("allowed_cabin_classes", ["economy"])),
            "requires_approval_above": policy.get("international_approval_threshold", policy.get("requires_approval_above", 0)),
            "additional_requirements": policy.get("international_requirements", []),
        }
    else:
        return {
            "success": True,
            "policy_id": policy_id,
            "is_international": False,
            "max_cost_per_booking": policy.get("domestic_max_cost", policy.get("max_cost_per_booking")),
            "allowed_cabin_classes": policy.get("domestic_cabin_classes", policy.get("allowed_cabin_classes", ["economy"])),
            "requires_approval_above": policy.get("domestic_approval_threshold", policy.get("requires_approval_above", 0)),
            "additional_requirements": policy.get("domestic_requirements", []),
        }
