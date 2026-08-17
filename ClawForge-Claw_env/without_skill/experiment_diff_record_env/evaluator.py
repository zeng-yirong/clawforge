from __future__ import annotations


def evaluate_session(session: dict[str, object], scenario: dict[str, object]) -> dict[str, object]:
    action_types = [str(item.get("action_type")) for item in session.get("actions", [])]
    required_actions = scenario.get("required_actions", [])
    matched = len({item for item in required_actions if item in action_types}) if required_actions else 0
    required_action_score = ((matched / len(required_actions)) * 20.0) if required_actions else 0.0
    seen = set(session.get("observations", {}).get("batch_ids_seen", []))
    retrieval_score = 20.0 if set(scenario["target_batch_ids"]).issubset(seen) else 0.0
    record = session["records"][-1] if session["records"] else None
    diff_match = record is not None and record.get("diff") == scenario["expected_diff"]
    artifact_score = 60.0 if diff_match else 0.0
    return {
        "overall_score": round(max(0.0, min(100.0, required_action_score + retrieval_score + artifact_score)), 4),
        "breakdown": {
            "required_action_score": round(required_action_score, 4),
            "retrieval_score": round(retrieval_score, 4),
            "artifact_score": round(artifact_score, 4),
        },
        "checks": {
            "diff_match": diff_match,
        },
    }
