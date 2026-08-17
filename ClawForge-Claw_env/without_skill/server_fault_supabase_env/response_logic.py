from __future__ import annotations

from copy import deepcopy
from typing import Any


def _normalize_list(values: list[str] | None) -> list[str]:
    return [item.strip() for item in values or [] if item and item.strip()]


def get_service_key(service: str) -> str:
    return service.strip().lower().replace(" ", "_")


def execute_fault_remediation(
    session: dict[str, Any],
    incident_id: str,
    *,
    remediation_mode: str,
    operator_note: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    for incident in session["incidents"]:
        if incident["incident_id"] != incident_id:
            continue
        if incident["status"] not in {"open", "triaged"}:
            raise ValueError(f"Incident {incident_id} is not actionable in status {incident['status']}")

        category = incident["category"]
        if category == "ups_outage":
            incident["status"] = "resolved"
            incident["resolution_state"] = "power_restored"
            incident["remediation_steps"] = [
                "Confirm UPS battery and upstream power",
                "Escalate to facilities if battery health is degraded",
                "Recheck dependent services after power recovery",
            ]
        elif category == "service_down":
            incident["status"] = "resolved"
            incident["resolution_state"] = "service_restarted"
            incident["remediation_steps"] = [
                "Verify host health and process liveness",
                "Restart application service",
                "Validate health checks and incident closure criteria",
            ]
        elif category == "network_degradation":
            incident["status"] = "mitigated"
            incident["resolution_state"] = "degraded_link_contained"
            incident["remediation_steps"] = [
                "Reroute traffic away from degraded link",
                "Notify network operations",
                "Monitor packet loss until stable",
            ]
        else:
            raise ValueError(f"Unsupported category for remediation: {category}")

        incident["remediation_mode"] = remediation_mode
        incident["operator_note"] = operator_note
        incident["last_action_index"] = action_index
        incident["updated_at"] = event_at
        incident["resolved_at"] = event_at if incident["status"] == "resolved" else None

        payload = {
            "incident_id": incident_id,
            "category": category,
            "status": incident["status"],
            "resolution_state": incident.get("resolution_state"),
            "remediation_steps": deepcopy(incident["remediation_steps"]),
            "remediation_mode": remediation_mode,
            "operator_note": operator_note,
        }
        session["last_action_index"] = action_index
        return payload

    raise KeyError(f"Incident not found: {incident_id}")


def batch_remediate(
    session: dict[str, Any],
    incident_ids: list[str],
    *,
    remediation_mode: str,
    operator_note: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    results = []
    for incident_id in incident_ids:
        results.append(
            execute_fault_remediation(
                session,
                incident_id,
                remediation_mode=remediation_mode,
                operator_note=operator_note,
                event_at=event_at,
                action_index=action_index,
            )
        )

    return {
        "batch_id": f"batch_{action_index:06d}",
        "incident_ids": incident_ids,
        "results": results,
        "remediation_mode": remediation_mode,
        "operator_note": operator_note,
        "completed_count": len(results),
    }
