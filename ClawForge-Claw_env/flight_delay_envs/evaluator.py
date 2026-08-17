from __future__ import annotations

from typing import Any


def evaluate_session(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    required_actions = scenario.get("required_actions", [])
    completed_actions = {a["action_type"] for a in session.get("actions", [])}

    score = 0.0
    if required_actions:
        for req in required_actions:
            if req in completed_actions:
                score += 100.0 / len(required_actions)

    bonus_actions = {
        "adjust_hotel_booking",
        "reschedule_transport_booking",
        "send_notification",
        "compose_delay_notification",
        "create_bulk_notification",
        "update_attendee_rsvp",
    }
    bonus_count = len(completed_actions & bonus_actions)
    score += bonus_count * 5

    delay_detected = any(
        a["action_type"] == "check_flight_status" and a["details"].get("is_delayed", False)
        for a in session.get("actions", [])
    )

    hotel_adjusted = any(
        a["action_type"] == "adjust_hotel_booking"
        for a in session.get("actions", [])
    )

    transport_rescheduled = any(
        a["action_type"] == "reschedule_transport_booking"
        for a in session.get("actions", [])
    )

    notification_sent = any(
        a["action_type"] == "send_notification"
        for a in session.get("actions", [])
    )

    cascade_completed = 0
    if delay_detected:
        cascade_completed += 1
    if hotel_adjusted:
        cascade_completed += 1
    if transport_rescheduled:
        cascade_completed += 1
    if notification_sent:
        cascade_completed += 1

    cascade_score = (cascade_completed / 4) * 20

    return {
        "score": min(score + cascade_score, 100.0),
        "required_actions": len(required_actions),
        "completed_actions": len(completed_actions & set(required_actions)),
        "bonus_points": bonus_count * 5,
        "cascade_completed": cascade_completed,
        "cascade_score": cascade_score,
        "delay_detection": delay_detected,
        "hotel_adjusted": hotel_adjusted,
        "transport_rescheduled": transport_rescheduled,
        "notification_sent": notification_sent,
    }
