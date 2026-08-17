from __future__ import annotations


def evaluate_session(session: dict[str, object], scenario: dict[str, object]) -> dict[str, object]:
    action_types = [str(item.get("action_type")) for item in session.get("actions", [])]
    required_actions = scenario.get("required_actions", [])
    matched = len({item for item in required_actions if item in action_types}) if required_actions else 0
    required_action_score = ((matched / len(required_actions)) * 20.0) if required_actions else 0.0

    paper_ids_seen = set(session.get("observations", {}).get("paper_ids_seen", []))
    expected_paper_ids = set(scenario.get("expected_paper_ids", []))
    retrieval_score = 20.0 if expected_paper_ids.issubset(paper_ids_seen) else 0.0

    graph_entry = None
    for entry in reversed(session.get("cache", {}).get("entries", [])):
        if entry.get("entry_type") == "paper_citation_graph":
            graph_entry = entry
            break

    artifact_checks = {
        "exists": False,
        "paper_ids_match": False,
        "node_count_match": False,
        "edge_count_match": False,
        "mermaid_present": False,
    }
    artifact_score = 0.0
    if graph_entry:
        payload = graph_entry["payload"]
        artifact_checks["exists"] = True
        artifact_checks["paper_ids_match"] = expected_paper_ids.issubset(set(payload.get("paper_ids", [])))
        artifact_checks["node_count_match"] = int(payload.get("node_count", 0)) == int(scenario["expected_node_count"])
        artifact_checks["edge_count_match"] = int(payload.get("edge_count", 0)) == int(scenario["expected_edge_count"])
        artifact_checks["mermaid_present"] = str(payload.get("graph_mermaid", "")).startswith("graph LR")
        artifact_score += 15.0 if artifact_checks["paper_ids_match"] else 0.0
        artifact_score += 15.0 if artifact_checks["node_count_match"] else 0.0
        artifact_score += 20.0 if artifact_checks["edge_count_match"] else 0.0
        artifact_score += 10.0 if artifact_checks["mermaid_present"] else 0.0

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
            "paper_ids_seen": sorted(paper_ids_seen),
        },
    }
