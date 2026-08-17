from __future__ import annotations


def evaluate_session(session: dict[str, object], scenario: dict[str, object]) -> dict[str, object]:
    action_types = [str(item.get("action_type")) for item in session.get("actions", [])]
    required_actions = scenario.get("required_actions", [])
    matched = len({item for item in required_actions if item in action_types}) if required_actions else 0
    required_action_score = ((matched / len(required_actions)) * 20.0) if required_actions else 0.0
    employee_id = scenario["target_employee_id"]
    artifact_score = 0.0
    artifact_score += 20.0 if any(item["employee_id"] == employee_id for item in session["email_profiles"]) else 0.0
    artifact_score += 20.0 if any(item["employee_id"] == employee_id for item in session["access_assignments"]) else 0.0
    artifact_score += 20.0 if any(item["employee_id"] == employee_id for item in session["equipment_allocations"]) else 0.0
    artifact_score += 20.0 if any(item["employee_id"] == employee_id for item in session["slack_cache"]) else 0.0
    overall_score = max(0.0, min(100.0, required_action_score + artifact_score))
    return {
        "overall_score": round(overall_score, 4),
        "breakdown": {
            "required_action_score": round(required_action_score, 4),
            "artifact_score": round(artifact_score, 4),
        },
    }
