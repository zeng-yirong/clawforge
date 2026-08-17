from __future__ import annotations


def evaluate_session(session: dict[str, object], scenario: dict[str, object]) -> dict[str, object]:
    action_types = [str(item.get("action_type")) for item in session.get("actions", [])]
    required_actions = scenario.get("required_actions", [])
    matched = len({item for item in required_actions if item in action_types}) if required_actions else 0
    required_action_score = ((matched / len(required_actions)) * 20.0) if required_actions else 0.0
    candidate_seen = scenario["target_candidate_id"] in set(session.get("observations", {}).get("candidate_ids_seen", []))
    job_seen = scenario["target_job_id"] in set(session.get("observations", {}).get("job_ids_seen", []))
    retrieval_score = 10.0 if candidate_seen else 0.0
    retrieval_score += 10.0 if job_seen else 0.0
    invite = session["schedule_entries"][-1] if session["schedule_entries"] else None
    reminder = session["reminders"][-1] if session["reminders"] else None
    artifact_score = 0.0
    artifact_score += 30.0 if invite is not None and invite.get("candidate_id") == scenario["target_candidate_id"] and invite.get("job_id") == scenario["target_job_id"] else 0.0
    artifact_score += 30.0 if reminder is not None and reminder.get("candidate_id") == scenario["target_candidate_id"] else 0.0
    overall_score = max(0.0, min(100.0, required_action_score + retrieval_score + artifact_score))
    return {
        "overall_score": round(overall_score, 4),
        "breakdown": {
            "required_action_score": round(required_action_score, 4),
            "retrieval_score": round(retrieval_score, 4),
            "artifact_score": round(artifact_score, 4),
        },
    }
