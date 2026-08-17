from __future__ import annotations


def evaluate_session(session: dict[str, object], scenario: dict[str, object]) -> dict[str, object]:
    action_types = [str(item.get("action_type")) for item in session.get("actions", [])]
    required_actions = scenario.get("required_actions", [])
    matched = len({item for item in required_actions if item in action_types}) if required_actions else 0
    required_action_score = ((matched / len(required_actions)) * 20.0) if required_actions else 0.0
    ledgers_seen = set(session.get("observations", {}).get("ledger_names_seen", []))
    retrieval_score = 20.0 if set(scenario["expected_ledgers"]).issubset(ledgers_seen) else 0.0
    report = session["cache"]["entries"][-1]["payload"] if session["cache"]["entries"] else None
    metrics_match = report is not None and report.get("metrics") == scenario["expected_metrics"]
    markdown_ok = report is not None and str(report.get("markdown", "")).startswith("# Weekly Business Report:")
    artifact_score = 30.0 if metrics_match else 0.0
    artifact_score += 30.0 if markdown_ok else 0.0
    overall_score = max(0.0, min(100.0, required_action_score + retrieval_score + artifact_score))
    return {
        "overall_score": round(overall_score, 4),
        "breakdown": {
            "required_action_score": round(required_action_score, 4),
            "retrieval_score": round(retrieval_score, 4),
            "artifact_score": round(artifact_score, 4),
        },
        "checks": {
            "metrics_match": metrics_match,
            "markdown_ok": markdown_ok,
        },
    }
