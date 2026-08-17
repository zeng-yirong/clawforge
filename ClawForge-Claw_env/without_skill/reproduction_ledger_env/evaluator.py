from __future__ import annotations


def evaluate_session(session: dict[str, object], scenario: dict[str, object]) -> dict[str, object]:
    action_types = [str(item.get("action_type")) for item in session.get("actions", [])]
    required_actions = scenario.get("required_actions", [])
    matched = len({item for item in required_actions if item in action_types}) if required_actions else 0
    required_action_score = ((matched / len(required_actions)) * 20.0) if required_actions else 0.0
    doc_seen = scenario["required_doc_id"] in set(session.get("observations", {}).get("doc_ids_seen", []))
    retrieval_score = 20.0 if doc_seen else 0.0
    entry = session["knowledge_entries"][-1] if session["knowledge_entries"] else None
    artifact_score = 0.0
    artifact_score += 20.0 if entry is not None and entry.get("project_id") == scenario["target_project_id"] else 0.0
    artifact_score += 20.0 if entry is not None and bool(str(entry.get("steps", "")).strip()) else 0.0
    artifact_score += 20.0 if entry is not None and bool(str(entry.get("result", "")).strip()) else 0.0
    overall_score = max(0.0, min(100.0, required_action_score + retrieval_score + artifact_score))
    return {
        "overall_score": round(overall_score, 4),
        "breakdown": {
            "required_action_score": round(required_action_score, 4),
            "retrieval_score": round(retrieval_score, 4),
            "artifact_score": round(artifact_score, 4),
        },
    }
