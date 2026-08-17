from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any
import uuid


def build_flight_summary(flight: dict[str, Any]) -> dict[str, Any]:
    return {
        "flight_id": flight["flight_id"],
        "flight_number": flight["flight_number"],
        "airline": flight["airline"],
        "origin": flight["origin"],
        "destination": flight["destination"],
        "departure_time": flight["departure_time"],
        "arrival_time": flight["arrival_time"],
        "status": flight["status"],
        "delay_minutes": flight.get("delay_minutes", 0),
        "gate": flight.get("gate"),
    }


def list_flights(
    session: dict[str, Any],
    *,
    query: str = "",
    status: str | None = None,
    airline: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query_lower = query.strip().lower()
    results = []

    for flight in session["flights"]:
        if status and flight["status"].lower() != status.lower():
            continue
        if airline and flight["airline"].lower() != airline.lower():
            continue

        searchable = f"{flight['flight_number']} {flight['airline']} {flight['origin']} {flight['destination']}".lower()
        if query_lower and query_lower not in searchable:
            continue

        results.append(build_flight_summary(flight))

    results.sort(key=lambda x: x["departure_time"])
    return results[:limit] if limit is not None else results


def get_flight(session: dict[str, Any], flight_id: str) -> dict[str, Any]:
    for flight in session["flights"]:
        if flight["flight_id"] == flight_id:
            return deepcopy(flight)
    raise KeyError(f"Flight not found: {flight_id}")


def check_flight_status(session: dict[str, Any], flight_id: str) -> dict[str, Any]:
    flight = get_flight(session, flight_id)
    is_delayed = flight["status"] == "delayed" or flight.get("delay_minutes", 0) > 0
    return {
        "flight_id": flight_id,
        "flight_number": flight["flight_number"],
        "status": flight["status"],
        "delay_minutes": flight.get("delay_minutes", 0),
        "is_delayed": is_delayed,
        "original_departure": flight["departure_time"],
        "original_arrival": flight["arrival_time"],
        "adjusted_departure": _calculate_adjusted_time(flight["departure_time"], flight.get("delay_minutes", 0)),
        "adjusted_arrival": _calculate_adjusted_time(flight["arrival_time"], flight.get("delay_minutes", 0)),
    }


def _calculate_adjusted_time(base_time: str, delay_minutes: int) -> str:
    dt = datetime.fromisoformat(base_time.replace("Z", "+00:00"))
    dt += timedelta(minutes=delay_minutes)
    return dt.isoformat()


def detect_delayed_flights(session: dict[str, Any]) -> list[dict[str, Any]]:
    delayed = []
    for flight in session["flights"]:
        if flight["status"] == "delayed" or flight.get("delay_minutes", 0) > 0:
            delayed.append({
                "flight_id": flight["flight_id"],
                "flight_number": flight["flight_number"],
                "delay_minutes": flight.get("delay_minutes", 0),
                "adjusted_arrival": _calculate_adjusted_time(
                    flight["arrival_time"], flight.get("delay_minutes", 0)
                ),
            })
    return delayed


def update_flight_status(
    session: dict[str, Any],
    flight_id: str,
    new_status: str,
    event_at: str,
    action_index: int,
    delay_minutes: int | None = None,
) -> dict[str, Any]:
    for flight in session["flights"]:
        if flight["flight_id"] == flight_id:
            old_status = flight["status"]
            old_delay = flight.get("delay_minutes", 0)

            flight["status"] = new_status
            if delay_minutes is not None:
                flight["delay_minutes"] = delay_minutes

            flight["last_action_index"] = action_index
            flight["last_updated"] = event_at

            session.setdefault("flight_status_changes", []).append({
                "flight_id": flight_id,
                "action_index": action_index,
                "timestamp": event_at,
                "old_status": old_status,
                "new_status": new_status,
                "old_delay_minutes": old_delay,
                "new_delay_minutes": delay_minutes or old_delay,
            })
            session["last_action_index"] = action_index

            return deepcopy(flight)

    raise KeyError(f"Flight not found: {flight_id}")


def get_affected_connections(session: dict[str, Any], flight_id: str) -> dict[str, Any]:
    delayed_flight = get_flight(session, flight_id)
    if delayed_flight["status"] != "delayed" and delayed_flight.get("delay_minutes", 0) == 0:
        return {
            "flight_id": flight_id,
            "has_delay": False,
            "affected_hotels": [],
            "affected_transports": [],
        }

    delay_minutes = delayed_flight.get("delay_minutes", 0)
    adjusted_arrival = _calculate_adjusted_time(delayed_flight["arrival_time"], delay_minutes)

    affected_hotels = []
    for booking in session.get("hotel_bookings", []):
        if booking.get("linked_flight_id") == flight_id and booking.get("status") == "confirmed":
            check_in = datetime.fromisoformat(booking["check_in"].replace("Z", "+00:00"))
            new_check_in = datetime.fromisoformat(adjusted_arrival.replace("Z", "+00:00")) + timedelta(hours=2)

            affected_hotels.append({
                "booking_id": booking["booking_id"],
                "hotel_name": booking["hotel_name"],
                "original_check_in": booking["check_in"],
                "suggested_check_in": new_check_in.isoformat(),
                "needs_adjustment": new_check_in > check_in,
            })

    affected_transports = []
    for transport in session.get("transport_bookings", []):
        if transport.get("linked_flight_id") == flight_id and transport.get("status") == "confirmed":
            pickup_time = datetime.fromisoformat(transport["pickup_time"].replace("Z", "+00:00"))
            new_pickup = datetime.fromisoformat(adjusted_arrival.replace("Z", "+00:00")) + timedelta(minutes=delay_minutes + 30)

            affected_transports.append({
                "booking_id": transport["booking_id"],
                "transport_type": transport["transport_type"],
                "original_pickup_time": transport["pickup_time"],
                "suggested_pickup_time": new_pickup.isoformat(),
                "needs_reschedule": new_pickup != pickup_time,
            })

    return {
        "flight_id": flight_id,
        "has_delay": True,
        "delay_minutes": delay_minutes,
        "adjusted_arrival": adjusted_arrival,
        "affected_hotels": affected_hotels,
        "affected_transports": affected_transports,
    }


def search_available_hotels(
    session: dict[str, Any],
    city: str,
    check_in: str,
    check_out: str,
    guest_count: int,
) -> list[dict[str, Any]]:
    results = []
    for hotel in session.get("available_hotels", []):
        if hotel["city"].lower() != city.lower():
            continue
        if guest_count > hotel.get("max_occupancy", 2):
            continue
        results.append({
            "hotel_id": hotel["hotel_id"],
            "hotel_name": hotel["hotel_name"],
            "city": hotel["city"],
            "address": hotel["address"],
            "star_rating": hotel["star_rating"],
            "price_per_night": hotel["price_per_night"],
            "available_rooms": hotel.get("available_rooms", 5),
        })
    return results
