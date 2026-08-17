from __future__ import annotations

from copy import deepcopy
from typing import Any


def _normalize(value: str | None) -> str:
    return value.strip().lower() if value else ""


def build_incident_summary(incident: dict[str, Any]) -> dict[str, Any]:
    return {
        "incident_id": incident["incident_id"],
        "title": incident["title"],
        "category": incident["category"],
        "severity": incident["severity"],
        "status": incident["status"],
        "assigned_team": incident["assigned_team"],
        "ticket_type": incident["ticket_type"],
        "opened_at": incident["opened_at"],
    }


def list_incidents(
    session: dict[str, Any],
    *,
    query: str = "",
    category: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query_lower = query.strip().lower()
    category_lower = _normalize(category)
    severity_lower = _normalize(severity)
    status_lower = _normalize(status)
    results: list[dict[str, Any]] = []

    for incident in session["incidents"]:
        if category_lower and str(incident["category"]).lower() != category_lower:
            continue
        if severity_lower and str(incident["severity"]).lower() != severity_lower:
            continue
        if status_lower and str(incident["status"]).lower() != status_lower:
            continue
        searchable = " ".join(
            [
                incident["title"],
                incident["description"],
                " ".join(incident.get("tags", [])),
                incident["assigned_team"],
                incident["ticket_type"],
            ]
        ).lower()
        if query_lower and query_lower not in searchable:
            continue
        results.append(build_incident_summary(incident))

    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    results.sort(
        key=lambda item: (
            severity_rank.get(str(item["severity"]).lower(), 9),
            str(item["opened_at"]),
            str(item["incident_id"]),
        )
    )
    return results[:limit] if limit is not None else results


def get_incident(session: dict[str, Any], incident_id: str) -> dict[str, Any]:
    for incident in session["incidents"]:
        if incident["incident_id"] == incident_id:
            return deepcopy(incident)
    raise KeyError(f"Incident not found: {incident_id}")


def screen_risk_incidents(
    session: dict[str, Any],
    *,
    categories: list[str] | None = None,
    statuses: list[str] | None = None,
    severities: list[str] | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    category_set = {item.lower() for item in categories} if categories else None
    status_set = {item.lower() for item in statuses} if statuses else None
    severity_set = {item.lower() for item in severities} if severities else None
    results: list[dict[str, Any]] = []

    for incident in session["incidents"]:
        if category_set and str(incident["category"]).lower() not in category_set:
            continue
        if status_set and str(incident["status"]).lower() not in status_set:
            continue
        if severity_set and str(incident["severity"]).lower() not in severity_set:
            continue
        results.append(
            {
                "incident_id": incident["incident_id"],
                "title": incident["title"],
                "category": incident["category"],
                "severity": incident["severity"],
                "status": incident["status"],
                "service": incident["service"],
                "ticket_type": incident["ticket_type"],
                "risk_flags": incident.get("risk_flags", []),
            }
        )

    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    results.sort(
        key=lambda item: (
            severity_rank.get(str(item["severity"]).lower(), 9),
            str(item["opened_at"]) if "opened_at" in item else "",
            str(item["incident_id"]),
        )
    )
    return results[:limit] if limit is not None else results
