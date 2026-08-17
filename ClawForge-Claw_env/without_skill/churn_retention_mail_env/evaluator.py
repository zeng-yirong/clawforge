from __future__ import annotations


def evaluate_session(session: dict[str, object], scenario: dict[str, object]) -> dict[str, object]:
    action_types = [str(item.get("action_type")) for item in session.get("actions", [])]
    required_actions = scenario.get("required_actions", [])
    matched = len({item for item in required_actions if item in action_types}) if required_actions else 0
    required_action_score = ((matched / len(required_actions)) * 20.0) if required_actions else 0.0

    expected_customer_id = scenario["target_customer_id"]
    expected_news_ids = set(scenario.get("expected_news_ids", []))
    customer_ids_seen = set(session.get("observations", {}).get("customer_ids_seen", []))
    news_ids_seen = set(session.get("observations", {}).get("news_ids_seen", []))
    retrieval_score = 20.0 if expected_customer_id in customer_ids_seen else 0.0
    retrieval_score += 10.0 if expected_news_ids.issubset(news_ids_seen) else 0.0

    email_entry = None
    for entry in reversed(session.get("cache", {}).get("entries", [])):
        if entry.get("entry_type") == "retention_email":
            email_entry = entry
            break

    artifact_checks = {
        "exists": False,
        "customer_match": False,
        "news_ids_match": False,
        "subject_present": False,
        "body_present": False,
    }
    artifact_score = 0.0
    if email_entry:
        payload = email_entry["payload"]
        artifact_checks["exists"] = True
        artifact_checks["customer_match"] = payload.get("customer_id") == expected_customer_id
        artifact_checks["news_ids_match"] = expected_news_ids.issubset(set(payload.get("news_ids", [])))
        artifact_checks["subject_present"] = bool(str(payload.get("subject", "")).strip())
        artifact_checks["body_present"] = bool(str(payload.get("body", "")).strip())
        artifact_score += 15.0 if artifact_checks["customer_match"] else 0.0
        artifact_score += 15.0 if artifact_checks["news_ids_match"] else 0.0
        artifact_score += 10.0 if artifact_checks["subject_present"] else 0.0
        artifact_score += 10.0 if artifact_checks["body_present"] else 0.0

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
            "customer_ids_seen": sorted(customer_ids_seen),
            "news_ids_seen": sorted(news_ids_seen),
        },
    }
