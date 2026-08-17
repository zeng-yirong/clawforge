from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any
import uuid


def build_notification_summary(notification: dict[str, Any]) -> dict[str, Any]:
    return {
        "notification_id": notification["notification_id"],
        "notification_type": notification["notification_type"],
        "recipient_name": notification["recipient_name"],
        "recipient_email": notification["recipient_email"],
        "subject": notification["subject"],
        "status": notification["status"],
        "sent_at": notification.get("sent_at"),
    }


def list_notifications(
    session: dict[str, Any],
    *,
    query: str = "",
    notification_type: str | None = None,
    status: str | None = None,
    recipient_email: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query_lower = query.strip().lower()
    results = []

    for notification in session.get("notifications", []):
        if notification_type and notification["notification_type"].lower() != notification_type.lower():
            continue
        if status and notification["status"].lower() != status.lower():
            continue
        if recipient_email and notification["recipient_email"].lower() != recipient_email.lower():
            continue

        searchable = f"{notification['subject']} {notification['recipient_name']} {notification.get('body', '')}".lower()
        if query_lower and query_lower not in searchable:
            continue

        results.append(build_notification_summary(notification))

    results.sort(key=lambda x: x.get("sent_at", ""), reverse=True)
    return results[:limit] if limit is not None else results


def get_notification(session: dict[str, Any], notification_id: str) -> dict[str, Any]:
    for notification in session.get("notifications", []):
        if notification["notification_id"] == notification_id:
            return deepcopy(notification)
    raise KeyError(f"Notification not found: {notification_id}")


def create_email_notification(
    session: dict[str, Any],
    recipient_name: str,
    recipient_email: str,
    subject: str,
    body: str,
    priority: str,
    linked_flight_id: str | None,
    linked_hotel_booking_ids: list[str],
    linked_transport_booking_ids: list[str],
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    notification_id = f"notif_{uuid.uuid4().hex[:8]}"

    new_notification = {
        "notification_id": notification_id,
        "notification_type": "email",
        "recipient_name": recipient_name,
        "recipient_email": recipient_email,
        "subject": subject,
        "body": body,
        "priority": priority,
        "linked_flight_id": linked_flight_id,
        "linked_hotel_booking_ids": linked_hotel_booking_ids,
        "linked_transport_booking_ids": linked_transport_booking_ids,
        "status": "draft",
        "created_at": event_at,
        "last_action_index": action_index,
    }

    session.setdefault("notifications", []).insert(0, new_notification)
    session["last_action_index"] = action_index

    return deepcopy(new_notification)


def send_notification(
    session: dict[str, Any],
    notification_id: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    for notification in session.get("notifications", []):
        if notification["notification_id"] == notification_id:
            if notification["status"] == "sent":
                raise ValueError(f"Notification {notification_id} has already been sent")

            notification["status"] = "sent"
            notification["sent_at"] = event_at
            notification["last_action_index"] = action_index

            session.setdefault("sent_notifications", []).append({
                "notification_id": notification_id,
                "sent_at": event_at,
                "action_index": action_index,
            })

            return deepcopy(notification)

    raise KeyError(f"Notification not found: {notification_id}")


def cancel_notification(
    session: dict[str, Any],
    notification_id: str,
    cancellation_reason: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    for notification in session.get("notifications", []):
        if notification["notification_id"] == notification_id:
            if notification["status"] == "sent":
                raise ValueError(f"Cannot cancel notification {notification_id} - already sent")

            notification["status"] = "cancelled"
            notification["cancellation_reason"] = cancellation_reason
            notification["cancelled_at"] = event_at
            notification["last_action_index"] = action_index

            return deepcopy(notification)

    raise KeyError(f"Notification not found: {notification_id}")


def compose_delay_notification(
    session: dict[str, Any],
    flight_id: str,
    recipient_name: str,
    recipient_email: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    from .flights import get_flight, _calculate_adjusted_time

    flight = get_flight(session, flight_id)
    delay_minutes = flight.get("delay_minutes", 0)
    adjusted_arrival = _calculate_adjusted_time(flight["arrival_time"], delay_minutes)

    affected_hotel_bookings = [
        b["booking_id"] for b in session.get("hotel_bookings", [])
        if b.get("linked_flight_id") == flight_id and b.get("status") == "confirmed"
    ]
    affected_transport_bookings = [
        b["booking_id"] for b in session.get("transport_bookings", [])
        if b.get("linked_flight_id") == flight_id and b.get("status") == "confirmed"
    ]

    original_arrival_dt = datetime.fromisoformat(flight["arrival_time"].replace("Z", "+00:00"))
    adjusted_arrival_dt = datetime.fromisoformat(adjusted_arrival.replace("Z", "+00:00"))

    body = f"""Dear {recipient_name},

We are writing to inform you about a flight delay that may affect your travel plans.

FLIGHT INFORMATION:
- Flight Number: {flight['flight_number']}
- Route: {flight['origin']} to {flight['destination']}
- Original Arrival: {original_arrival_dt.strftime('%Y-%m-%d %H:%M')}
- New Arrival Time: {adjusted_arrival_dt.strftime('%Y-%m-%d %H:%M')}
- Delay Duration: {delay_minutes} minutes

"""

    if affected_hotel_bookings:
        body += """HOTEL BOOKINGS:
Your hotel check-in times have been automatically adjusted to accommodate the new arrival time.
Please contact the hotel directly if you need further assistance.

"""

    if affected_transport_bookings:
        body += """TRANSPORT ARRANGEMENTS:
Your airport pickup service has been notified of the delay and will adjust pickup times accordingly.

"""

    body += """We apologize for any inconvenience this may cause. Please reach out if you have any questions.

Best regards,
Travel Services Team
"""

    subject = f"Important: Flight {flight['flight_number']} Delay Notification - Action Required"

    return create_email_notification(
        session=session,
        recipient_name=recipient_name,
        recipient_email=recipient_email,
        subject=subject,
        body=body,
        priority="high",
        linked_flight_id=flight_id,
        linked_hotel_booking_ids=affected_hotel_bookings,
        linked_transport_booking_ids=affected_transport_bookings,
        event_at=event_at,
        action_index=action_index,
    )


def create_bulk_notification(
    session: dict[str, Any],
    recipients: list[dict[str, Any]],
    subject: str,
    body_template: str,
    priority: str,
    linked_flight_id: str | None,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    notifications = []
    for recipient in recipients:
        personalized_body = body_template.replace("{recipient_name}", recipient["name"])

        notification = create_email_notification(
            session=session,
            recipient_name=recipient["name"],
            recipient_email=recipient["email"],
            subject=subject,
            body=personalized_body,
            priority=priority,
            linked_flight_id=linked_flight_id,
            linked_hotel_booking_ids=[],
            linked_transport_booking_ids=[],
            event_at=event_at,
            action_index=action_index,
        )
        notifications.append(notification)

    return {
        "bulk_notification_id": f"bulk_{uuid.uuid4().hex[:8]}",
        "total_recipients": len(recipients),
        "notifications_created": len(notifications),
        "notification_ids": [n["notification_id"] for n in notifications],
        "created_at": event_at,
        "action_index": action_index,
    }


def get_notification_stats(session: dict[str, Any]) -> dict[str, Any]:
    notifications = session.get("notifications", [])
    sent = [n for n in notifications if n["status"] == "sent"]
    draft = [n for n in notifications if n["status"] == "draft"]
    cancelled = [n for n in notifications if n["status"] == "cancelled"]

    return {
        "total_notifications": len(notifications),
        "sent_count": len(sent),
        "draft_count": len(draft),
        "cancelled_count": len(cancelled),
        "by_priority": {
            "high": len([n for n in notifications if n.get("priority") == "high"]),
            "medium": len([n for n in notifications if n.get("priority") == "medium"]),
            "low": len([n for n in notifications if n.get("priority") == "low"]),
        },
    }
