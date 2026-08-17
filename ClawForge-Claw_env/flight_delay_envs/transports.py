from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any
import uuid


def build_transport_booking_summary(booking: dict[str, Any]) -> dict[str, Any]:
    return {
        "booking_id": booking["booking_id"],
        "transport_type": booking["transport_type"],
        "service_provider": booking["service_provider"],
        "passenger_name": booking["passenger_name"],
        "pickup_location": booking["pickup_location"],
        "dropoff_location": booking["dropoff_location"],
        "pickup_time": booking["pickup_time"],
        "status": booking["status"],
        "linked_flight_id": booking.get("linked_flight_id"),
    }


def list_transport_bookings(
    session: dict[str, Any],
    *,
    query: str = "",
    status: str | None = None,
    transport_type: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query_lower = query.strip().lower()
    results = []

    for booking in session.get("transport_bookings", []):
        if status and booking["status"].lower() != status.lower():
            continue
        if transport_type and booking["transport_type"].lower() != transport_type.lower():
            continue

        searchable = f"{booking['service_provider']} {booking['passenger_name']} {booking['pickup_location']}".lower()
        if query_lower and query_lower not in searchable:
            continue

        results.append(build_transport_booking_summary(booking))

    results.sort(key=lambda x: x["pickup_time"], reverse=True)
    return results[:limit] if limit is not None else results


def get_transport_booking(session: dict[str, Any], booking_id: str) -> dict[str, Any]:
    for booking in session.get("transport_bookings", []):
        if booking["booking_id"] == booking_id:
            return deepcopy(booking)
    raise KeyError(f"Transport booking not found: {booking_id}")


def create_transport_booking(
    session: dict[str, Any],
    transport_type: str,
    service_provider: str,
    passenger_name: str,
    passenger_phone: str,
    pickup_location: str,
    dropoff_location: str,
    pickup_time: str,
    vehicle_type: str,
    passengers_count: int,
    special_requests: str | None,
    linked_flight_id: str | None,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    base_price = 45.0
    if transport_type.lower() == "limousine":
        base_price = 150.0
    elif transport_type.lower() == "suv":
        base_price = 75.0
    elif transport_type.lower() == "shuttle":
        base_price = 25.0

    if vehicle_type.lower() == "luxury":
        base_price *= 1.5
    elif vehicle_type.lower() == "premium":
        base_price *= 1.25

    booking_id = f"trans_{uuid.uuid4().hex[:8]}"
    confirmation_number = f"T{uuid.uuid4().hex[:6].upper()}"

    new_booking = {
        "booking_id": booking_id,
        "confirmation_number": confirmation_number,
        "transport_type": transport_type,
        "service_provider": service_provider,
        "passenger_name": passenger_name,
        "passenger_phone": passenger_phone,
        "pickup_location": pickup_location,
        "dropoff_location": dropoff_location,
        "pickup_time": pickup_time,
        "vehicle_type": vehicle_type,
        "passengers_count": passengers_count,
        "special_requests": special_requests,
        "linked_flight_id": linked_flight_id,
        "status": "confirmed",
        "total_cost": base_price,
        "created_at": event_at,
        "last_action_index": action_index,
    }

    session.setdefault("transport_bookings", []).insert(0, new_booking)
    session["last_action_index"] = action_index

    return deepcopy(new_booking)


def reschedule_transport_booking(
    session: dict[str, Any],
    booking_id: str,
    new_pickup_time: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    for booking in session.get("transport_bookings", []):
        if booking["booking_id"] == booking_id:
            old_pickup_time = booking["pickup_time"]
            booking["pickup_time"] = new_pickup_time
            booking["last_updated"] = event_at
            booking["last_action_index"] = action_index

            session.setdefault("transport_reschedules", []).append({
                "booking_id": booking_id,
                "action_index": action_index,
                "timestamp": event_at,
                "old_pickup_time": old_pickup_time,
                "new_pickup_time": new_pickup_time,
            })

            return deepcopy(booking)

    raise KeyError(f"Transport booking not found: {booking_id}")


def cancel_transport_booking(
    session: dict[str, Any],
    booking_id: str,
    cancellation_reason: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    for booking in session.get("transport_bookings", []):
        if booking["booking_id"] == booking_id:
            booking["status"] = "cancelled"
            booking["cancellation_reason"] = cancellation_reason
            booking["cancelled_at"] = event_at
            booking["last_action_index"] = action_index

            session.setdefault("transport_cancellations", []).append({
                "booking_id": booking_id,
                "action_index": action_index,
                "timestamp": event_at,
                "reason": cancellation_reason,
            })

            return deepcopy(booking)

    raise KeyError(f"Transport booking not found: {booking_id}")


def get_transport_booking_for_flight(session: dict[str, Any], flight_id: str) -> list[dict[str, Any]]:
    return [
        deepcopy(b)
        for b in session.get("transport_bookings", [])
        if b.get("linked_flight_id") == flight_id and b.get("status") == "confirmed"
    ]


def calculate_cancellation_fee(booking: dict[str, Any]) -> dict[str, Any]:
    if booking["status"] != "cancelled":
        return {
            "booking_id": booking["booking_id"],
            "total_cost": booking["total_cost"],
            "refund_amount": 0.0,
            "cancellation_fee": 0.0,
            "message": "Booking is not cancelled",
        }

    pickup_time = datetime.fromisoformat(booking["pickup_time"].replace("Z", "+00:00"))
    now = datetime.now(pickup_time.tzinfo)
    hours_until_pickup = (pickup_time - now).total_seconds() / 3600

    if hours_until_pickup >= 24:
        refund_pct = 1.0
        cancellation_fee = 0.0
        message = "Full refund - cancelled more than 24 hours before pickup"
    elif hours_until_pickup >= 12:
        refund_pct = 0.5
        cancellation_fee = booking["total_cost"] * 0.5
        message = "50% refund - cancelled between 12-24 hours before pickup"
    else:
        refund_pct = 0.0
        cancellation_fee = booking["total_cost"]
        message = "No refund - cancelled less than 12 hours before pickup"

    return {
        "booking_id": booking["booking_id"],
        "total_cost": booking["total_cost"],
        "refund_amount": booking["total_cost"] * refund_pct,
        "cancellation_fee": cancellation_fee,
        "message": message,
    }


def find_alternative_transports(
    session: dict[str, Any],
    pickup_location: str,
    dropoff_location: str,
    target_pickup_time: str,
    exclude_booking_ids: list[str],
) -> list[dict[str, Any]]:
    results = []
    target_dt = datetime.fromisoformat(target_pickup_time.replace("Z", "+00:00"))

    for transport in session.get("available_transports", []):
        if transport["service_area"].lower() != pickup_location.lower():
            continue

        pickup_dt = datetime.fromisoformat(transport["next_available"].replace("Z", "+00:00")) if isinstance(transport.get("next_available"), str) else None
        if pickup_dt and pickup_dt > target_dt:
            continue

        results.append({
            "transport_id": transport["transport_id"],
            "transport_type": transport["transport_type"],
            "service_provider": transport["service_provider"],
            "vehicle_type": transport["vehicle_type"],
            "base_price": transport["base_price"],
            "next_available": transport.get("next_available"),
        })

    return sorted(results, key=lambda x: x["base_price"])
