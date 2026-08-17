from __future__ import annotations

from typing import Any
from datetime import datetime
import random


def create_booking(
    store,
    session_id: str,
    platform_id: str,
    platform_name: str,
    flight_details: dict[str, Any],
    total_cost: float,
    approval_id: str | None = None,
    booking_ref: str | None = None,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    if booking_ref is None:
        booking_ref = f"BK{random.randint(100000, 999999)}"
    booking = {
        "booking_id": f"booking_{action_index}",
        "booking_ref": booking_ref,
        "platform_id": platform_id,
        "platform_name": platform_name,
        "flight_details": flight_details,
        "total_cost": total_cost,
        "approval_id": approval_id,
        "status": "confirmed",
        "booked_at": event_at,
        "action_index": action_index,
    }
    session = store.get_session(session_id)
    if session:
        session["bookings"].append(booking)
        store._save_session(session_id, session)
    return {
        "success": True,
        "booking_id": booking["booking_id"],
        "booking_ref": booking_ref,
        "status": "confirmed",
        "total_cost": total_cost,
        "message": f"Booking {booking_ref} confirmed on {platform_name}",
    }


def cancel_booking(
    store,
    session_id: str,
    booking_ref: str,
    cancellation_reason: str,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    session = store.get_session(session_id)
    if not session:
        return {"success": False, "error": "Session not found"}
    for b in session.get("bookings", []):
        if b["booking_ref"] == booking_ref:
            b["status"] = "cancelled"
            b["cancelled_at"] = event_at
            b["cancellation_reason"] = cancellation_reason
            store._save_session(session_id, session)
            refund_amount = _calculate_refund(b["total_cost"])
            return {
                "success": True,
                "booking_ref": booking_ref,
                "status": "cancelled",
                "refund_amount": refund_amount,
                "message": f"Booking {booking_ref} cancelled. Refund: {refund_amount}",
            }
    return {"success": False, "error": f"Booking {booking_ref} not found"}


def get_booking_details(
    store,
    session_id: str,
    booking_ref: str,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    session = store.get_session(session_id)
    if not session:
        return {"success": False, "error": "Session not found"}
    for b in session.get("bookings", []):
        if b["booking_ref"] == booking_ref:
            return {"success": True, "booking": b}
    return {"success": False, "error": f"Booking {booking_ref} not found"}


def list_bookings(
    store,
    session_id: str,
    status_filter: str | None = None,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    session = store.get_session(session_id)
    if not session:
        return {"success": False, "error": "Session not found"}
    bookings = session.get("bookings", [])
    if status_filter:
        bookings = [b for b in bookings if b.get("status") == status_filter]
    return {
        "success": True,
        "total_bookings": len(bookings),
        "bookings": bookings,
    }


def update_booking(
    store,
    session_id: str,
    booking_ref: str,
    update_fields: dict[str, Any],
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    session = store.get_session(session_id)
    if not session:
        return {"success": False, "error": "Session not found"}
    for b in session.get("bookings", []):
        if b["booking_ref"] == booking_ref:
            if b["status"] != "confirmed":
                return {"success": False, "error": "Can only update confirmed bookings"}
            allowed_fields = ["seat_selection", "meal_preference", "baggage_addon", "contact_email", "contact_phone"]
            for key in update_fields:
                if key in allowed_fields:
                    b[key] = update_fields[key]
            b["updated_at"] = event_at
            store._save_session(session_id, session)
            return {
                "success": True,
                "booking_ref": booking_ref,
                "message": f"Booking {booking_ref} updated",
                "updates": update_fields,
            }
    return {"success": False, "error": f"Booking {booking_ref} not found"}


def get_booking_itinerary(
    store,
    session_id: str,
    booking_ref: str,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    session = store.get_session(session_id)
    if not session:
        return {"success": False, "error": "Session not found"}
    for b in session.get("bookings", []):
        if b["booking_ref"] == booking_ref:
            flight = b.get("flight_details", {})
            return {
                "success": True,
                "booking_ref": booking_ref,
                "status": b["status"],
                "itinerary": {
                    "passenger_name": b.get("passenger_name", "N/A"),
                    "flight_number": flight.get("flight_number"),
                    "origin": flight.get("origin"),
                    "destination": flight.get("destination"),
                    "departure": flight.get("departure_time"),
                    "arrival": flight.get("arrival_time"),
                    "cabin_class": flight.get("cabin_class"),
                },
                "total_cost": b["total_cost"],
                "booking_date": b["booked_at"],
            }
    return {"success": False, "error": f"Booking {booking_ref} not found"}


def confirm_booking_received(
    store,
    session_id: str,
    booking_ref: str,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    session = store.get_session(session_id)
    if not session:
        return {"success": False, "error": "Session not found"}
    for b in session.get("bookings", []):
        if b["booking_ref"] == booking_ref:
            b["confirmation_received"] = True
            b["confirmed_at"] = event_at
            store._save_session(session_id, session)
            return {
                "success": True,
                "booking_ref": booking_ref,
                "message": f"Booking {booking_ref} receipt confirmed",
            }
    return {"success": False, "error": f"Booking {booking_ref} not found"}


def _calculate_refund(total_cost: float) -> float:
    return total_cost * 0.8


def get_booking_statistics(
    store,
    session_id: str,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    session = store.get_session(session_id)
    if not session:
        return {"success": False, "error": "Session not found"}
    bookings = session.get("bookings", [])
    total_cost = sum(b["total_cost"] for b in bookings)
    confirmed = len([b for b in bookings if b["status"] == "confirmed"])
    cancelled = len([b for b in bookings if b["status"] == "cancelled"])
    return {
        "success": True,
        "total_bookings": len(bookings),
        "confirmed": confirmed,
        "cancelled": cancelled,
        "total_cost": total_cost,
        "average_cost": total_cost / len(bookings) if bookings else 0,
    }
