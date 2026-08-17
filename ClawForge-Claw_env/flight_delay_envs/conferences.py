from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any
import uuid


def build_conference_summary(conference: dict[str, Any]) -> dict[str, Any]:
    return {
        "conference_id": conference["conference_id"],
        "conference_name": conference["conference_name"],
        "organizer": conference["organizer"],
        "start_date": conference["start_date"],
        "end_date": conference["end_date"],
        "location": conference["location"],
        "status": conference["status"],
        "attendee_count": len(conference.get("attendees", [])),
    }


def list_conferences(
    session: dict[str, Any],
    *,
    query: str = "",
    status: str | None = None,
    location: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query_lower = query.strip().lower()
    results = []

    for conference in session.get("conferences", []):
        if status and conference["status"].lower() != status.lower():
            continue
        if location and conference["location"].lower() != location.lower():
            continue

        searchable = f"{conference['conference_name']} {conference['organizer']} {conference['location']}".lower()
        if query_lower and query_lower not in searchable:
            continue

        results.append(build_conference_summary(conference))

    results.sort(key=lambda x: x["start_date"], reverse=True)
    return results[:limit] if limit is not None else results


def get_conference(session: dict[str, Any], conference_id: str) -> dict[str, Any]:
    for conference in session.get("conferences", []):
        if conference["conference_id"] == conference_id:
            return deepcopy(conference)
    raise KeyError(f"Conference not found: {conference_id}")


def list_attendees(
    session: dict[str, Any],
    conference_id: str,
    *,
    attending: bool | None = None,
    query: str = "",
) -> list[dict[str, Any]]:
    conference = get_conference(session, conference_id)
    results = []

    for attendee in conference.get("attendees", []):
        if attending is not None:
            if attendee.get("attending") != attending:
                continue

        searchable = f"{attendee['name']} {attendee['email']} {attendee.get('company', '')}".lower()
        if query and query.lower() not in searchable:
            continue

        results.append({
            "attendee_id": attendee["attendee_id"],
            "name": attendee["name"],
            "email": attendee["email"],
            "company": attendee.get("company"),
            "attending": attendee.get("attending", True),
            "rsvp_status": attendee.get("rsvp_status", "confirmed"),
        })

    return results


def get_attendee(session: dict[str, Any], conference_id: str, attendee_id: str) -> dict[str, Any]:
    conference = get_conference(session, conference_id)
    for attendee in conference.get("attendees", []):
        if attendee["attendee_id"] == attendee_id:
            return deepcopy(attendee)
    raise KeyError(f"Attendee not found: {attendee_id}")


def update_attendee_rsvp(
    session: dict[str, Any],
    conference_id: str,
    attendee_id: str,
    rsvp_status: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    for conference in session.get("conferences", []):
        if conference["conference_id"] == conference_id:
            for attendee in conference.get("attendees", []):
                if attendee["attendee_id"] == attendee_id:
                    old_status = attendee.get("rsvp_status", "confirmed")
                    attendee["rsvp_status"] = rsvp_status
                    attendee["rsvp_updated_at"] = event_at
                    attendee["last_action_index"] = action_index

                    session.setdefault("rsvp_changes", []).append({
                        "conference_id": conference_id,
                        "attendee_id": attendee_id,
                        "old_rsvp_status": old_status,
                        "new_rsvp_status": rsvp_status,
                        "timestamp": event_at,
                        "action_index": action_index,
                    })

                    return deepcopy(attendee)
            raise KeyError(f"Attendee not found: {attendee_id}")
    raise KeyError(f"Conference not found: {conference_id}")


def notify_attendees_of_schedule_change(
    session: dict[str, Any],
    conference_id: str,
    notification_ids: list[str],
    change_type: str,
    change_details: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    conference = get_conference(session, conference_id)
    attending_count = sum(1 for a in conference.get("attendees", []) if a.get("attending", True))

    change_record = {
        "change_id": f"change_{uuid.uuid4().hex[:8]}",
        "conference_id": conference_id,
        "change_type": change_type,
        "change_details": change_details,
        "notification_ids": notification_ids,
        "attendees_notified": len(notification_ids),
        "total_attendees": attending_count,
        "timestamp": event_at,
        "action_index": action_index,
    }

    session.setdefault("schedule_changes", []).append(change_record)
    session["last_action_index"] = action_index

    return change_record


def check_attendee_schedule_conflicts(
    session: dict[str, Any],
    conference_id: str,
    new_start_time: str,
    new_end_time: str,
) -> list[dict[str, Any]]:
    conference = get_conference(session, conference_id)
    conflicts = []

    new_start = datetime.fromisoformat(new_start_time.replace("Z", "+00:00"))
    new_end = datetime.fromisoformat(new_end_time.replace("Z", "+00:00"))

    for attendee in conference.get("attendees", []):
        if not attendee.get("attending", True):
            continue

        attendee_conflicts = []

        for other_conference in session.get("conferences", []):
            if other_conference["conference_id"] == conference_id:
                continue

            other_start = datetime.fromisoformat(other_conference["start_date"].replace("Z", "+00:00"))
            other_end = datetime.fromisoformat(other_conference["end_date"].replace("Z", "+00:00"))

            if new_start < other_end and new_end > other_start:
                attendee_conflicts.append({
                    "other_conference_id": other_conference["conference_id"],
                    "other_conference_name": other_conference["conference_name"],
                    "other_start": other_conference["start_date"],
                    "other_end": other_conference["end_date"],
                })

        if attendee_conflicts:
            conflicts.append({
                "attendee_id": attendee["attendee_id"],
                "attendee_name": attendee["name"],
                "attendee_email": attendee["email"],
                "conflicts": attendee_conflicts,
            })

    return conflicts


def get_conference_schedule(session: dict[str, Any], conference_id: str) -> dict[str, Any]:
    conference = get_conference(session, conference_id)

    sessions = []
    for session_item in conference.get("sessions", []):
        sessions.append({
            "session_id": session_item["session_id"],
            "title": session_item["title"],
            "start_time": session_item["start_time"],
            "end_time": session_item["end_time"],
            "location": session_item.get("location"),
            "speaker": session_item.get("speaker"),
        })

    return {
        "conference_id": conference_id,
        "conference_name": conference["conference_name"],
        "start_date": conference["start_date"],
        "end_date": conference["end_date"],
        "location": conference["location"],
        "sessions": sorted(sessions, key=lambda x: x["start_time"]),
    }


def update_conference_session(
    session: dict[str, Any],
    conference_id: str,
    session_id: str,
    new_start_time: str | None = None,
    new_end_time: str | None = None,
    new_location: str | None = None,
    event_at: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    for conference in session.get("conferences", []):
        if conference["conference_id"] == conference_id:
            for conf_session in conference.get("sessions", []):
                if conf_session["session_id"] == session_id:
                    old_start = conf_session["start_time"]
                    old_end = conf_session["end_time"]
                    old_location = conf_session.get("location")

                    if new_start_time:
                        conf_session["start_time"] = new_start_time
                    if new_end_time:
                        conf_session["end_time"] = new_end_time
                    if new_location:
                        conf_session["location"] = new_location

                    if event_at:
                        conf_session["last_updated"] = event_at
                    if action_index is not None:
                        conf_session["last_action_index"] = action_index

                    session.setdefault("session_updates", []).append({
                        "conference_id": conference_id,
                        "session_id": session_id,
                        "old_start_time": old_start,
                        "new_start_time": new_start_time,
                        "old_end_time": old_end,
                        "new_end_time": new_end_time,
                        "old_location": old_location,
                        "new_location": new_location,
                        "timestamp": event_at,
                        "action_index": action_index,
                    })

                    return deepcopy(conf_session)
            raise KeyError(f"Session not found: {session_id}")
    raise KeyError(f"Conference not found: {conference_id}")


def get_conference_travel_info(session: dict[str, Any], conference_id: str) -> dict[str, Any]:
    conference = get_conference(session, conference_id)

    attendee_travel = []
    for attendee in conference.get("attendees", []):
        if not attendee.get("attending", True):
            continue

        linked_hotel = None
        for booking in session.get("hotel_bookings", []):
            if booking.get("linked_flight_id") and booking.get("guest_name") == attendee["name"]:
                linked_hotel = {
                    "booking_id": booking["booking_id"],
                    "hotel_name": booking["hotel_name"],
                    "check_in": booking["check_in"],
                    "check_out": booking["check_out"],
                }

        linked_transport = None
        for transport in session.get("transport_bookings", []):
            if transport.get("linked_flight_id") and transport.get("passenger_name") == attendee["name"]:
                linked_transport = {
                    "booking_id": transport["booking_id"],
                    "transport_type": transport["transport_type"],
                    "pickup_time": transport["pickup_time"],
                }

        attendee_travel.append({
            "attendee_id": attendee["attendee_id"],
            "attendee_name": attendee["name"],
            "hotel_booking": linked_hotel,
            "transport_booking": linked_transport,
        })

    return {
        "conference_id": conference_id,
        "conference_name": conference["conference_name"],
        "conference_start": conference["start_date"],
        "conference_end": conference["end_date"],
        "attendee_travel": attendee_travel,
    }
