from __future__ import annotations

from typing import Any


def create_market_report(
    session: dict[str, Any],
    title: str,
    report_type: str,
    competitor_ids: list[str],
    include_sections: list[str],
    findings: list[str],
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    if "reports" not in session:
        session["reports"] = []

    report_id = f"rpt_{action_index}"

    report = {
        "report_id": report_id,
        "title": title,
        "report_type": report_type,
        "competitor_ids": competitor_ids,
        "include_sections": include_sections,
        "findings": findings,
        "created_at": event_at,
        "action_index": action_index,
        "status": "draft",
    }

    session["reports"].append(report)

    return {
        "report_id": report_id,
        "title": title,
        "report_type": report_type,
        "status": "draft",
    }


def update_report(
    session: dict[str, Any],
    report_id: str,
    updates: dict[str, Any],
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    reports = session.get("reports", [])
    for report in reports:
        if report.get("report_id") == report_id:
            if "title" in updates:
                report["title"] = updates["title"]
            if "findings" in updates:
                report["findings"] = updates["findings"]
            if "include_sections" in updates:
                report["include_sections"] = updates["include_sections"]
            report["updated_at"] = event_at
            report["last_action_index"] = action_index
            return {"report_id": report_id, "updated": True}
    raise KeyError(f"Report not found: {report_id}")


def finalize_report(
    session: dict[str, Any],
    report_id: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    reports = session.get("reports", [])
    for report in reports:
        if report.get("report_id") == report_id:
            report["status"] = "finalized"
            report["finalized_at"] = event_at
            report["finalized_action_index"] = action_index
            return {"report_id": report_id, "status": "finalized"}
    raise KeyError(f"Report not found: {report_id}")


def list_reports(
    session: dict[str, Any],
    *,
    report_type: str | None = None,
    status: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    reports = session.get("reports", [])
    results = []

    for report in reports:
        if report_type and report.get("report_type") != report_type:
            continue
        if status and report.get("status") != status:
            continue
        results.append(report)

    if limit is not None:
        results = results[:limit]

    return results


def get_report(session: dict[str, Any], report_id: str) -> dict[str, Any]:
    reports = session.get("reports", [])
    for report in reports:
        if report.get("report_id") == report_id:
            return report
    raise KeyError(f"Report not found: {report_id}")


def generate_competitive_landscape(
    session: dict[str, Any],
    competitor_ids: list[str],
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    from .competitors import get_competitor, compare_competitors

    competitors_data = []
    for cid in competitor_ids:
        comp = get_competitor(session, cid)
        competitors_data.append({
            "competitor_id": cid,
            "name": comp.get("name"),
            "market_cap": comp.get("market_cap"),
            "market_share": comp.get("market_share"),
            "user_count": comp.get("user_count"),
            "revenue": comp.get("revenue"),
            "growth_rate": comp.get("growth_rate"),
        })

    comparison = compare_competitors(session, competitor_ids)

    landscape = {
        "competitors": competitors_data,
        "comparison": comparison,
        "generated_at": event_at,
        "action_index": action_index,
    }

    return landscape


def generate_regulatory_summary(
    session: dict[str, Any],
    event_at: str,
    action_index: int,
    competitor_ids: list[str] | None = None,
    impact_filter: str | None = None,
) -> dict[str, Any]:
    from .policies import filter_policies_by_competitor, list_policies

    all_policies = list_policies(session, impact_level=impact_filter)

    policy_map = {}
    for policy in all_policies:
        impact = policy.get("impact", {})
        affected = impact.get("affected_competitors", [])

        if competitor_ids:
            affected = [c for c in affected if c in competitor_ids]

        for cid in affected:
            if cid not in policy_map:
                policy_map[cid] = []
            policy_map[cid].append({
                "policy_id": policy.get("policy_id"),
                "title": policy.get("title"),
                "impact_level": policy.get("impact_level"),
                "deadline": impact.get("deadline"),
            })

    return {
        "competitor_policies": policy_map,
        "total_policies": len(all_policies),
        "generated_at": event_at,
        "action_index": action_index,
    }


def generate_user_acquisition_analysis(
    session: dict[str, Any],
    event_at: str,
    action_index: int,
    cohort_filter: str | None = None,
) -> dict[str, Any]:
    from .users import list_users, analyze_acquisition_sources, list_user_cohorts

    users = list_users(session, cohort=cohort_filter)
    source_analysis = analyze_acquisition_sources(session)
    cohorts = list_user_cohorts(session, cohort=cohort_filter)

    total_users = len(users)
    churned = sum(1 for u in users if u.get("churned", False))
    total_ltv = sum(u.get("lifetime_value", 0) for u in users)

    return {
        "total_users": total_users,
        "churned_users": churned,
        "churn_rate": (churned / total_users * 100) if total_users > 0 else 0,
        "total_lifetime_value": total_ltv,
        "avg_lifetime_value": (total_ltv / total_users) if total_users > 0 else 0,
        "source_analysis": source_analysis,
        "cohorts": cohorts,
        "generated_at": event_at,
        "action_index": action_index,
    }


def create_alert(
    session: dict[str, Any],
    alert_type: str,
    title: str,
    description: str,
    severity: str,
    related_competitor_id: str | None = None,
    related_policy_id: str | None = None,
    event_at: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    if "alerts" not in session:
        session["alerts"] = []

    alert_id = f"alert_{action_index or 0}"

    alert = {
        "alert_id": alert_id,
        "alert_type": alert_type,
        "title": title,
        "description": description,
        "severity": severity,
        "related_competitor_id": related_competitor_id,
        "related_policy_id": related_policy_id,
        "created_at": event_at,
        "acknowledged": False,
    }

    session["alerts"].append(alert)

    return {
        "alert_id": alert_id,
        "title": title,
        "severity": severity,
    }


def acknowledge_alert(
    session: dict[str, Any],
    alert_id: str,
    acknowledged_by: str,
    notes: str | None = None,
    event_at: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    alerts = session.get("alerts", [])
    for alert in alerts:
        if alert.get("alert_id") == alert_id:
            alert["acknowledged"] = True
            alert["acknowledged_by"] = acknowledged_by
            alert["acknowledged_at"] = event_at
            if notes:
                alert["acknowledgment_notes"] = notes
            return {"alert_id": alert_id, "acknowledged": True}
    raise KeyError(f"Alert not found: {alert_id}")


def list_alerts(
    session: dict[str, Any],
    *,
    alert_type: str | None = None,
    severity: str | None = None,
    acknowledged: bool | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    alerts = session.get("alerts", [])
    results = []

    for alert in alerts:
        if alert_type and alert.get("alert_type") != alert_type:
            continue
        if severity and alert.get("severity") != severity:
            continue
        if acknowledged is not None:
            if alert.get("acknowledged", False) != acknowledged:
                continue
        results.append(alert)

    if limit is not None:
        results = results[:limit]

    return results
