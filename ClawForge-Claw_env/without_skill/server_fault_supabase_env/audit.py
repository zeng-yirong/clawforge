from __future__ import annotations

from copy import deepcopy
from typing import Any


def append_audit_log(
    session: dict[str, Any],
    *,
    action_index: int,
    event_at: str,
    action_type: str,
    details: dict[str, Any],
) -> dict[str, Any]:
    entry = {
        "audit_id": f"audit_{action_index:06d}",
        "timestamp": event_at,
        "action_index": action_index,
        "action_type": action_type,
        "details": details,
    }
    session["audit_logs"].append(entry)
    session["audit_index"][entry["audit_id"]] = len(session["audit_logs"]) - 1
    if entry["audit_id"] not in session["observations"]["audit_ids"]:
        session["observations"]["audit_ids"].append(entry["audit_id"])
    return deepcopy(entry)


def list_audit_logs(
    session: dict[str, Any],
    *,
    action_type: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    action_type_lower = action_type.strip().lower() if action_type else None
    results: list[dict[str, Any]] = []
    for entry in reversed(session["audit_logs"]):
        if action_type_lower and str(entry["action_type"]).lower() != action_type_lower:
            continue
        results.append(
            {
                "audit_id": entry["audit_id"],
                "timestamp": entry["timestamp"],
                "action_index": entry["action_index"],
                "action_type": entry["action_type"],
                "details": entry["details"],
            }
        )
    return results[:limit] if limit is not None else results


def get_audit_log(session: dict[str, Any], audit_id: str) -> dict[str, Any]:
    index = session["audit_index"].get(audit_id)
    if index is None:
        raise KeyError(f"Audit log not found: {audit_id}")
    return deepcopy(session["audit_logs"][index])
