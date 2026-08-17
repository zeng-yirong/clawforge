from __future__ import annotations

from typing import Any


def evaluate_session(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    required_actions = scenario.get("required_actions", [])
    completed_actions = {a["action_type"] for a in session.get("actions", [])}

    score = 0.0
    if required_actions:
        for req in required_actions:
            if isinstance(req, dict):
                action_type = req.get("action_type")
                target = req.get("target_competitor_id") or req.get("target_policy_id") or req.get("target_user_id")
                details_match = True
                if target:
                    for action in session.get("actions", []):
                        if action.get("action_type") == action_type:
                            details = action.get("details", {})
                            if target in str(details):
                                break
                    else:
                        details_match = False
                if details_match and action_type in completed_actions:
                    score += 100.0 / len(required_actions)
            elif req in completed_actions:
                score += 100.0 / len(required_actions)

    bonus_actions = {
        "create_market_report", "finalize_report", "create_alert",
        "acknowledge_alert", "track_competitor_metric", "track_user_event",
        "add_competitor_note", "update_report",
    }
    bonus_count = len(completed_actions & bonus_actions)
    score += bonus_count * 5

    reports_created = len(session.get("reports", []))
    alerts_created = len(session.get("alerts", []))

    return {
        "score": min(score, 100.0),
        "required_actions": len(required_actions),
        "completed_actions": len(completed_actions & set(
            a if isinstance(a, str) else a.get("action_type") for a in required_actions
        )),
        "bonus_points": bonus_count * 5,
        "reports_created": reports_created,
        "alerts_created": alerts_created,
    }
