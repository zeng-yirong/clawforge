from __future__ import annotations


def evaluate_session(session: dict[str, object], scenario: dict[str, object]) -> dict[str, object]:
    action_types = [str(item.get("action_type")) for item in session.get("actions", [])]
    required_actions = scenario.get("required_actions", [])
    matched = len({item for item in required_actions if item in action_types}) if required_actions else 0
    required_action_score = ((matched / len(required_actions)) * 20.0) if required_actions else 0.0
    observed_ids = set(session.get("observations", {}).get("employee_ids_seen", []))
    retrieval_score = 20.0 if scenario["target_employee_id"] in observed_ids else 0.0
    profile = session["performance_profiles"][-1] if session["performance_profiles"] else None
    artifact_checks = {
        "exists": profile is not None,
        "employee_match": profile is not None and profile.get("employee_id") == scenario["target_employee_id"],
        "score_match": profile is not None and abs(float(profile.get("score", 0)) - float(scenario["expected_score"])) <= 0.01,
        "band_match": profile is not None and profile.get("performance_band") == scenario["expected_band"],
    }
    artifact_score = 0.0
    artifact_score += 20.0 if artifact_checks["employee_match"] else 0.0
    artifact_score += 20.0 if artifact_checks["score_match"] else 0.0
    artifact_score += 20.0 if artifact_checks["band_match"] else 0.0
    overall_score = max(0.0, min(100.0, required_action_score + retrieval_score + artifact_score))
    return {
        "overall_score": round(overall_score, 4),
        "breakdown": {
            "required_action_score": round(required_action_score, 4),
            "retrieval_score": round(retrieval_score, 4),
            "artifact_score": round(artifact_score, 4),
        },
        "checks": {
            "artifact": artifact_checks,
            "employee_ids_seen": sorted(observed_ids),
        },
    }
