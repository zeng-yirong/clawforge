from __future__ import annotations


def evaluate_session(session: dict[str, object], scenario: dict[str, object]) -> dict[str, object]:
    action_types = [str(item.get("action_type")) for item in session.get("actions", [])]
    required_actions = scenario.get("required_actions", [])
    matched = len({item for item in required_actions if item in action_types}) if required_actions else 0
    required_action_score = ((matched / len(required_actions)) * 20.0) if required_actions else 0.0
    target_employee_id = scenario["target_employee_id"]
    retrieval_score = 20.0 if target_employee_id in set(session.get("observations", {}).get("employee_ids_seen", [])) else 0.0
    revoke_ok = target_employee_id in set(session.get("observations", {}).get("revoked_employee_ids", []))
    reclaim_ok = target_employee_id in set(session.get("observations", {}).get("reclaimed_employee_ids", []))
    checklist = session["handover_records"][-1] if session["handover_records"] else None
    checklist_ok = checklist is not None and checklist.get("employee_id") == target_employee_id
    artifact_score = 20.0 if revoke_ok else 0.0
    artifact_score += 20.0 if reclaim_ok else 0.0
    artifact_score += 20.0 if checklist_ok else 0.0
    overall_score = max(0.0, min(100.0, required_action_score + retrieval_score + artifact_score))
    return {
        "overall_score": round(overall_score, 4),
        "breakdown": {
            "required_action_score": round(required_action_score, 4),
            "retrieval_score": round(retrieval_score, 4),
            "artifact_score": round(artifact_score, 4),
        },
        "checks": {
            "employee_seen": retrieval_score > 0.0,
            "revoke_ok": revoke_ok,
            "reclaim_ok": reclaim_ok,
            "checklist_ok": checklist_ok,
        },
    }
