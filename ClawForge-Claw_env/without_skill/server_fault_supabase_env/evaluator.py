from __future__ import annotations

from typing import Any


def _action_types(session: dict[str, Any]) -> list[str]:
    return [str(item.get("action_type")) for item in session.get("actions", [])]


def evaluate_session(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    action_types = _action_types(session)
    required_actions = scenario.get("required_actions", [])
    if required_actions:
        matched = len({item for item in required_actions if item in action_types})
        required_action_score = (matched / len(required_actions)) * 25.0
    else:
        matched = 0
        required_action_score = 0.0

    required_attachment_paths = set(scenario.get("required_attachment_paths", []))
    expected_incident_ids = set(scenario.get("expected_incident_ids", []))
    forbidden_incident_ids = set(scenario.get("forbidden_incident_ids", []))
    expected_resolution_states = scenario.get("expected_resolution_states", {})
    required_audit_actions = set(scenario.get("required_audit_actions", []))

    attachments_read = set(session.get("observations", {}).get("attachments_read", []))
    screened_ids = set(session.get("observations", {}).get("screened_incident_ids", []))
    remediated_ids = set(session.get("observations", {}).get("remediated_incident_ids", []))
    supabase_rows = session.get("supabase_memory", {}).get("incident_resolutions", [])
    audit_logs = session.get("audit_logs", [])

    reading_score = 0.0
    if required_attachment_paths:
        reading_score += 10.0 * (len(attachments_read & required_attachment_paths) / len(required_attachment_paths))

    triage_score = 0.0
    triage_checks = {
        "screened_expected_incidents": expected_incident_ids.issubset(screened_ids),
        "remediated_expected_incidents": expected_incident_ids.issubset(remediated_ids),
    }
    triage_score += 12.5 if triage_checks["screened_expected_incidents"] else 0.0
    triage_score += 12.5 if triage_checks["remediated_expected_incidents"] else 0.0

    supabase_score = 0.0
    row_ids = {row["incident_id"] for row in supabase_rows}
    resolution_checks = {}
    for incident_id, resolution_state in expected_resolution_states.items():
        resolution_checks[incident_id] = any(
            row["incident_id"] == incident_id and row["resolution_state"] == resolution_state
            for row in supabase_rows
        )
    supabase_score += 10.0 if expected_incident_ids.issubset(row_ids) else 0.0
    if expected_resolution_states:
        supabase_score += 15.0 * (
            sum(1 for value in resolution_checks.values() if value) / len(expected_resolution_states)
        )

    audit_score = 0.0
    audit_action_types = {str(item["action_type"]) for item in audit_logs}
    audit_checks = {
        "audit_log_present": len(audit_logs) > 0,
        "required_audit_actions_present": required_audit_actions.issubset(audit_action_types),
    }
    audit_score += 5.0 if audit_checks["audit_log_present"] else 0.0
    audit_score += 10.0 if audit_checks["required_audit_actions_present"] else 0.0

    penalty = 0.0
    forbidden_written = {row["incident_id"] for row in supabase_rows if row["incident_id"] in forbidden_incident_ids}
    if forbidden_written:
        penalty -= 10.0 * len(forbidden_written)

    overall_score = max(
        0.0,
        min(100.0, required_action_score + reading_score + triage_score + supabase_score + audit_score + penalty),
    )

    return {
        "overall_score": round(overall_score, 4),
        "breakdown": {
            "required_action_score": round(required_action_score, 4),
            "reading_score": round(reading_score, 4),
            "triage_score": round(triage_score, 4),
            "supabase_score": round(supabase_score, 4),
            "audit_score": round(audit_score, 4),
            "penalty": round(penalty, 4),
        },
        "required_actions": {
            "expected": required_actions,
            "matched_count": matched,
            "observed_actions": action_types,
        },
        "checks": {
            "triage": triage_checks,
            "resolution_checks": resolution_checks,
            "audit": audit_checks,
            "attachments_read": sorted(attachments_read),
            "screened_incident_ids": sorted(screened_ids),
            "remediated_incident_ids": sorted(remediated_ids),
            "forbidden_written": sorted(forbidden_written),
        },
    }
