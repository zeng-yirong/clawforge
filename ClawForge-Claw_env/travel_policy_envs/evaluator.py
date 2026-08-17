from __future__ import annotations

from typing import Any


def evaluate_session(store, session_id: str) -> dict[str, Any]:
    session = store.get_session(session_id)
    if not session:
        return {"success": False, "error": "Session not found"}

    required_actions = []
    scenario_id = session.get("scenario_id")
    if scenario_id == "q2_business_travel_2026":
        required_actions = [
            "compare_platform_prices",
            "validate_booking_against_policy",
            "initiate_approval_request",
            "create_booking",
        ]
    elif scenario_id == "emergency_travel_approval":
        required_actions = [
            "search_flights",
            "validate_booking_against_policy",
            "initiate_approval_request",
            "escalate_approval",
        ]

    completed_actions = [a["action"] for a in session.get("actions", [])]
    base_score = 0
    for ra in required_actions:
        if ra in completed_actions:
            base_score += 100 / len(required_actions) if required_actions else 0

    bonus_actions = ["create_booking", "confirm_booking_received", "get_booking_itinerary", "get_booking_statistics"]
    bonus_score = 0
    for ba in bonus_actions:
        if ba in completed_actions:
            bonus_score += 5

    total_score = min(100, base_score + bonus_score)
    completed = sum(1 for ra in required_actions if ra in completed_actions)

    return {
        "success": True,
        "session_id": session_id,
        "scenario_id": scenario_id,
        "base_score": round(base_score, 2),
        "bonus_score": bonus_score,
        "total_score": round(total_score, 2),
        "required_actions": required_actions,
        "completed_actions": completed,
        "total_required": len(required_actions),
        "completion_rate": round(completed / len(required_actions) * 100, 2) if required_actions else 100,
    }
