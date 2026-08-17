from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any
import uuid


def build_hotel_booking_summary(booking: dict[str, Any]) -> dict[str, Any]:
    return {
        "booking_id": booking["booking_id"],
        "hotel_id": booking["hotel_id"],
        "hotel_name": booking["hotel_name"],
        "check_in": booking["check_in"],
        "check_out": booking["check_out"],
        "guest_name": booking["guest_name"],
        "status": booking["status"],
        "total_cost": booking["total_cost"],
        "room_type": booking.get("room_type"),
    }


def list_hotel_bookings(
    session: dict[str, Any],
    *,
    query: str = "",
    status: str | None = None,
    guest_name: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query_lower = query.strip().lower()
    results = []

    for booking in session.get("hotel_bookings", []):
        if status and booking["status"].lower() != status.lower():
            continue
        if guest_name and booking["guest_name"].lower() != guest_name.lower():
            continue

        searchable = f"{booking['hotel_name']} {booking['guest_name']} {booking.get('confirmation_number', '')}".lower()
        if query_lower and query_lower not in searchable:
            continue

        results.append(build_hotel_booking_summary(booking))

    results.sort(key=lambda x: x["check_in"], reverse=True)
    return results[:limit] if limit is not None else results


def get_hotel_booking(session: dict[str, Any], booking_id: str) -> dict[str, Any]:
    for booking in session.get("hotel_bookings", []):
        if booking["booking_id"] == booking_id:
            return deepcopy(booking)
    raise KeyError(f"Hotel booking not found: {booking_id}")


def create_hotel_booking(
    session: dict[str, Any],
    hotel_id: str,
    hotel_name: str,
    check_in: str,
    check_out: str,
    guest_name: str,
    guest_count: int,
    room_type: str,
    special_requests: str | None,
    linked_flight_id: str | None,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    check_in_dt = datetime.fromisoformat(check_in.replace("Z", "+00:00"))
    check_out_dt = datetime.fromisoformat(check_out.replace("Z", "+00:00"))
    nights = max(1, (check_out_dt - check_in_dt).days)

    base_price = 150.0
    if room_type == "deluxe":
        base_price = 220.0
    elif room_type == "suite":
        base_price = 350.0

    total_cost = base_price * nights

    booking_id = f"hotel_{uuid.uuid4().hex[:8]}"
    confirmation_number = f"H{uuid.uuid4().hex[:6].upper()}"

    new_booking = {
        "booking_id": booking_id,
        "confirmation_number": confirmation_number,
        "hotel_id": hotel_id,
        "hotel_name": hotel_name,
        "check_in": check_in,
        "check_out": check_out,
        "guest_name": guest_name,
        "guest_count": guest_count,
        "room_type": room_type,
        "special_requests": special_requests,
        "linked_flight_id": linked_flight_id,
        "status": "confirmed",
        "total_cost": total_cost,
        "created_at": event_at,
        "last_action_index": action_index,
    }

    session.setdefault("hotel_bookings", []).insert(0, new_booking)
    session["last_action_index"] = action_index

    return deepcopy(new_booking)


def adjust_hotel_booking(
    session: dict[str, Any],
    booking_id: str,
    new_check_in: str | None = None,
    new_check_out: str | None = None,
    event_at: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    for booking in session.get("hotel_bookings", []):
        if booking["booking_id"] == booking_id:
            old_check_in = booking["check_in"]
            old_check_out = booking["check_out"]

            if new_check_in:
                booking["check_in"] = new_check_in
            if new_check_out:
                booking["check_out"] = new_check_out

            check_in_dt = datetime.fromisoformat(booking["check_in"].replace("Z", "+00:00"))
            check_out_dt = datetime.fromisoformat(booking["check_out"].replace("Z", "+00:00"))
            nights = max(1, (check_out_dt - check_in_dt).days)

            base_price = 150.0
            if booking.get("room_type") == "deluxe":
                base_price = 220.0
            elif booking.get("room_type") == "suite":
                base_price = 350.0

            booking["total_cost"] = base_price * nights

            if event_at:
                booking["last_updated"] = event_at
            if action_index is not None:
                booking["last_action_index"] = action_index

            session.setdefault("hotel_adjustments", []).append({
                "booking_id": booking_id,
                "action_index": action_index,
                "timestamp": event_at,
                "old_check_in": old_check_in,
                "new_check_in": new_check_in,
                "old_check_out": old_check_out,
                "new_check_out": new_check_out,
            })

            return deepcopy(booking)

    raise KeyError(f"Hotel booking not found: {booking_id}")


def cancel_hotel_booking(
    session: dict[str, Any],
    booking_id: str,
    cancellation_reason: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    for booking in session.get("hotel_bookings", []):
        if booking["booking_id"] == booking_id:
            booking["status"] = "cancelled"
            booking["cancellation_reason"] = cancellation_reason
            booking["cancelled_at"] = event_at
            booking["last_action_index"] = action_index

            session.setdefault("hotel_cancellations", []).append({
                "booking_id": booking_id,
                "action_index": action_index,
                "timestamp": event_at,
                "reason": cancellation_reason,
            })

            return deepcopy(booking)

    raise KeyError(f"Hotel booking not found: {booking_id}")


def get_hotel_booking_for_flight(session: dict[str, Any], flight_id: str) -> list[dict[str, Any]]:
    return [
        deepcopy(b)
        for b in session.get("hotel_bookings", [])
        if b.get("linked_flight_id") == flight_id and b.get("status") == "confirmed"
    ]


def calculate_refund_amount(booking: dict[str, Any]) -> dict[str, Any]:
    if booking["status"] != "cancelled":
        return {
            "booking_id": booking["booking_id"],
            "total_cost": booking["total_cost"],
            "refund_amount": 0.0,
            "cancellation_fee": 0.0,
            "message": "Booking is not cancelled",
        }

    check_in = datetime.fromisoformat(booking["check_in"].replace("Z", "+00:00"))
    now = datetime.now(check_in.tzinfo)
    hours_until_checkin = (check_in - now).total_seconds() / 3600

    if hours_until_checkin >= 48:
        refund_pct = 1.0
        cancellation_fee = 0.0
        message = "Full refund - cancelled more than 48 hours before check-in"
    elif hours_until_checkin >= 24:
        refund_pct = 0.5
        cancellation_fee = booking["total_cost"] * 0.5
        message = "50% refund - cancelled between 24-48 hours before check-in"
    else:
        refund_pct = 0.0
        cancellation_fee = booking["total_cost"]
        message = "No refund - cancelled less than 24 hours before check-in"

    return {
        "booking_id": booking["booking_id"],
        "total_cost": booking["total_cost"],
        "refund_amount": booking["total_cost"] * refund_pct,
        "cancellation_fee": cancellation_fee,
        "message": message,
    }


def search_alternative_hotels(
    session: dict[str, Any],
    city: str,
    check_in: str,
    check_out: str,
    exclude_booking_ids: list[str],
) -> list[dict[str, Any]]:
    results = []
    check_in_dt = datetime.fromisoformat(check_in.replace("Z", "+00:00"))
    check_out_dt = datetime.fromisoformat(check_out.replace("Z", "+00:00"))
    nights = max(1, (check_out_dt - check_in_dt).days)

    for hotel in session.get("available_hotels", []):
        if hotel["city"].lower() != city.lower():
            continue
        if hotel.get("available_rooms", 0) <= 0:
            continue

        existing_booking_ids = [b["hotel_id"] for b in session.get("hotel_bookings", []) if b.get("status") == "confirmed"]
        if hotel["hotel_id"] in existing_booking_ids and hotel["hotel_id"] not in exclude_booking_ids:
            continue

        total_cost = hotel["price_per_night"] * nights

        results.append({
            "hotel_id": hotel["hotel_id"],
            "hotel_name": hotel["hotel_name"],
            "address": hotel["address"],
            "star_rating": hotel["star_rating"],
            "price_per_night": hotel["price_per_night"],
            "total_cost": total_cost,
            "available_rooms": hotel.get("available_rooms", 0),
        })

    return sorted(results, key=lambda x: x["total_cost"])
