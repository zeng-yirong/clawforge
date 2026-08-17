from __future__ import annotations

from typing import Any


def evaluate_session(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    action_types = [str(item.get("action_type")) for item in session.get("actions", [])]
    required_actions = scenario.get("required_actions", [])
    matched = len({item for item in required_actions if item in action_types}) if required_actions else 0
    required_action_score = ((matched / len(required_actions)) * 20.0) if required_actions else 0.0

    attachments_read = set(session.get("observations", {}).get("attachments_read", []))
    paper_ids_seen = set(session.get("observations", {}).get("paper_ids_seen", []))
    expected_paper_ids = set(scenario.get("expected_paper_ids", []))
    required_attachment_paths = set(scenario.get("required_attachment_paths", []))

    reading_score = 10.0 * (len(attachments_read & required_attachment_paths) / len(required_attachment_paths))
    retrieval_score = 25.0 if expected_paper_ids.issubset(paper_ids_seen) else 0.0

    review_entry = None
    for entry in reversed(session.get("cache", {}).get("entries", [])):
        if entry.get("entry_type") == "arxiv_direction_review":
            review_entry = entry
            break

    artifact_checks = {
        "exists": False,
        "direction_match": False,
        "paper_ids_match": False,
        "markdown_present": False,
        "mermaid_present": False,
    }
    artifact_score = 0.0
    if review_entry:
        payload = review_entry["payload"]
        artifact_checks["exists"] = True
        artifact_checks["direction_match"] = payload.get("direction") == scenario["target_direction"]
        artifact_checks["paper_ids_match"] = expected_paper_ids.issubset(set(payload.get("paper_ids", [])))
        artifact_checks["markdown_present"] = str(payload.get("review_markdown", "")).startswith("# Review:")
        artifact_checks["mermaid_present"] = str(payload.get("roadmap_mermaid", "")).startswith("graph TD")
        artifact_score += 10.0 if artifact_checks["direction_match"] else 0.0
        artifact_score += 15.0 if artifact_checks["paper_ids_match"] else 0.0
        artifact_score += 10.0 if artifact_checks["markdown_present"] else 0.0
        artifact_score += 20.0 if artifact_checks["mermaid_present"] else 0.0

    overall_score = max(0.0, min(100.0, required_action_score + reading_score + retrieval_score + artifact_score))
    return {
        "overall_score": round(overall_score, 4),
        "breakdown": {
            "required_action_score": round(required_action_score, 4),
            "reading_score": round(reading_score, 4),
            "retrieval_score": round(retrieval_score, 4),
            "artifact_score": round(artifact_score, 4),
        },
        "checks": {
            "artifact": artifact_checks,
            "attachments_read": sorted(attachments_read),
            "paper_ids_seen": sorted(paper_ids_seen),
        },
    }
