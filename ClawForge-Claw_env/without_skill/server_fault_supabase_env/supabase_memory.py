from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_row_summary(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "row_id": row["row_id"],
        "table_name": row["table_name"],
        "incident_id": row["incident_id"],
        "service": row["service"],
        "resolution_state": row["resolution_state"],
        "written_at": row["written_at"],
    }


def insert_incident_resolution(
    session: dict[str, Any],
    *,
    incident_id: str,
    table_name: str,
    service: str,
    category: str,
    severity: str,
    resolution_state: str,
    remediation_mode: str,
    operator_note: str,
    written_at: str,
    action_index: int,
) -> dict[str, Any]:
    row_id = f"row_{action_index:06d}"
    row = {
        "row_id": row_id,
        "table_name": table_name,
        "incident_id": incident_id,
        "service": service,
        "category": category,
        "severity": severity,
        "resolution_state": resolution_state,
        "remediation_mode": remediation_mode,
        "operator_note": operator_note,
        "written_at": written_at,
        "action_index": action_index,
    }
    session["supabase_memory"]["incident_resolutions"].append(row)
    session["supabase_memory"]["row_index"][row_id] = len(session["supabase_memory"]["incident_resolutions"]) - 1
    if row_id not in session["observations"]["supabase_row_ids"]:
        session["observations"]["supabase_row_ids"].append(row_id)
    return deepcopy(row)


def list_supabase_rows(
    session: dict[str, Any],
    *,
    table_name: str | None = None,
    incident_id: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    table_name_lower = table_name.strip().lower() if table_name else None
    for row in reversed(session["supabase_memory"]["incident_resolutions"]):
        if table_name_lower and str(row["table_name"]).lower() != table_name_lower:
            continue
        if incident_id and row["incident_id"] != incident_id:
            continue
        results.append(build_row_summary(row))
    return results[:limit] if limit is not None else results


def get_supabase_row(session: dict[str, Any], row_id: str) -> dict[str, Any]:
    index = session["supabase_memory"]["row_index"].get(row_id)
    if index is None:
        raise KeyError(f"Supabase row not found: {row_id}")
    return deepcopy(session["supabase_memory"]["incident_resolutions"][index])
