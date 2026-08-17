from __future__ import annotations

from copy import deepcopy
from typing import Any


def dial_emergency(
    session: dict[str, Any],
    call_type: str,
    description: str,
    location: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    emergency_calls = session.setdefault("emergency_calls", [])

    call_id = f"call_{len(emergency_calls) + 1:04d}"
    timestamp = session.get("meta", {}).get("current_time")

    call = {
        "call_id": call_id,
        "call_type": call_type,
        "description": description,
        "location": location,
        "status": "dialed",
        "dialed_at": timestamp,
        "action_index": action_index,
    }

    emergency_calls.append(call)
    session.setdefault("active_calls", {})[call_id] = call

    action = {
        "action": "dial_emergency",
        "call_id": call_id,
        "call_type": call_type,
        "action_index": action_index,
        "timestamp": timestamp,
    }
    session.setdefault("actions", []).append(action)

    return deepcopy(call)


def get_emergency_call(session: dict[str, Any], call_id: str) -> dict[str, Any]:
    emergency_calls = session.get("emergency_calls", [])
    for call in emergency_calls:
        if call.get("call_id") == call_id:
            return deepcopy(call)
    return {"error": f"Emergency call {call_id} not found"}


def list_emergency_calls(
    session: dict[str, Any],
    query: str = "",
    call_type: str | None = None,
    status: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    emergency_calls = session.get("emergency_calls", [])
    results = []

    for call in emergency_calls:
        if query:
            if query.lower() not in call.get("description", "").lower():
                continue

        if call_type and call.get("call_type") != call_type:
            continue

        if status and call.get("status") != status:
            continue

        results.append(deepcopy(call))

    results.sort(key=lambda x: x.get("dialed_at", ""), reverse=True)

    if limit:
        results = results[:limit]

    return results


def update_call_status(
    session: dict[str, Any],
    call_id: str,
    new_status: str,
    notes: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    emergency_calls = session.get("emergency_calls", [])
    for call in emergency_calls:
        if call.get("call_id") == call_id:
            call["status"] = new_status
            call["last_updated"] = session.get("meta", {}).get("current_time")
            if notes:
                call["notes"] = notes

            action = {
                "action": "update_call_status",
                "call_id": call_id,
                "new_status": new_status,
                "action_index": action_index,
                "timestamp": session.get("meta", {}).get("current_time"),
            }
            session.setdefault("actions", []).append(action)

            return deepcopy(call)

    return {"error": f"Emergency call {call_id} not found"}


def get_emergency_contacts(session: dict[str, Any]) -> list[dict[str, Any]]:
    contacts = session.get("contacts", {})
    emergency_contacts = []

    for contact_id, contact in contacts.items():
        if contact.get("is_emergency_contact"):
            emergency_contacts.append({"contact_id": contact_id, **deepcopy(contact)})

    return emergency_contacts


def get_contact(session: dict[str, Any], contact_id: str) -> dict[str, Any]:
    contacts = session.get("contacts", {})
    if contact_id in contacts:
        return deepcopy(contacts[contact_id])
    return {"error": f"Contact {contact_id} not found"}


def list_contacts(
    session: dict[str, Any],
    query: str = "",
    role: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    contacts = session.get("contacts", {})
    results = []

    for contact_id, contact in contacts.items():
        if query:
            if query.lower() not in contact.get("name", "").lower() and query.lower() not in contact.get("title", "").lower():
                continue

        if role and contact.get("role") != role:
            continue

        results.append({"contact_id": contact_id, **deepcopy(contact)})

    if limit:
        results = results[:limit]

    return results
