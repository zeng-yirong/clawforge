from __future__ import annotations


def evaluate_session(session: dict[str, object], scenario: dict[str, object]) -> dict[str, object]:
    action_types = [str(item.get("action_type")) for item in session.get("actions", [])]
    required_actions = scenario.get("required_actions", [])
    matched = len({item for item in required_actions if item in action_types}) if required_actions else 0
    required_action_score = ((matched / len(required_actions)) * 20.0) if required_actions else 0.0

    attachments_read = set(session.get("observations", {}).get("attachments_read", []))
    updated_customer_ids = set(session.get("observations", {}).get("updated_customer_ids", []))
    reading_score = 10.0 if scenario["required_attachment_path"] in attachments_read else 0.0
    update_score = 20.0 if scenario["target_customer_id"] in updated_customer_ids else 0.0

    target_customer = None
    for customer in session["customers"]:
        if customer["customer_id"] == scenario["target_customer_id"]:
            target_customer = customer
            break
    labels_match = target_customer is not None and set(target_customer.get("labels", [])) == set(scenario["expected_labels"])
    profile_score = 50.0 if labels_match else 0.0

    overall_score = max(0.0, min(100.0, required_action_score + reading_score + update_score + profile_score))
    return {
        "overall_score": round(overall_score, 4),
        "breakdown": {
            "required_action_score": round(required_action_score, 4),
            "reading_score": round(reading_score, 4),
            "update_score": round(update_score, 4),
            "profile_score": round(profile_score, 4),
        },
        "checks": {
            "attachments_read": sorted(attachments_read),
            "updated_customer_ids": sorted(updated_customer_ids),
            "labels_match": labels_match,
        },
    }
