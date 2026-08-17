from __future__ import annotations

from copy import deepcopy
from typing import Any


def _record_id(action_index: int) -> str:
    return f"temp_{action_index:06d}"


def _find_document(session: dict[str, Any], document_id: str) -> dict[str, Any]:
    for report in session["reports"]:
        if report["report_id"] == document_id:
            return {
                "document_id": report["report_id"],
                "source_type": "report",
                "title": report["title"],
                "published_at": report["published_at"],
            }
    for presentation in session["presentations"]:
        if presentation["presentation_id"] == document_id:
            return {
                "document_id": presentation["presentation_id"],
                "source_type": "presentation",
                "title": presentation["title"],
                "published_at": presentation["updated_at"],
            }
    for sample in session["media_samples"]:
        if sample["sample_id"] == document_id:
            return {
                "document_id": sample["sample_id"],
                "source_type": "media_sample",
                "title": sample["title"],
                "published_at": sample["captured_at"],
            }
    raise KeyError(f"Document not found: {document_id}")


def save_clue_list(
    session: dict[str, Any],
    solution_id: str,
    solution_name: str,
    document_ids: list[str],
    clues: list[str],
    summary: str,
    confidence: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    if not document_ids:
        raise ValueError("At least one document_id is required.")
    if not clues:
        raise ValueError("At least one clue is required.")

    documents: list[dict[str, Any]] = []
    source_types: list[str] = []
    for document_id in document_ids:
        document = _find_document(session, document_id)
        documents.append(document)
        if document["source_type"] not in source_types:
            source_types.append(document["source_type"])

    record = {
        "record_id": _record_id(action_index),
        "record_type": "clue_list",
        "created_at": event_at,
        "action_index": action_index,
        "solution_id": solution_id,
        "solution_name": solution_name,
        "summary": summary,
        "confidence": confidence,
        "document_ids": document_ids,
        "source_types": source_types,
        "documents": documents,
        "clues": clues,
    }
    session["temp_records"].append(record)
    session["temp_record_index"][record["record_id"]] = len(session["temp_records"]) - 1
    if record["record_id"] not in session["observations"]["temp_record_ids"]:
        session["observations"]["temp_record_ids"].append(record["record_id"])
    return deepcopy(record)


def list_temp_records(
    session: dict[str, Any],
    *,
    record_type: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    record_type_lower = record_type.strip().lower() if record_type else None
    for record in reversed(session["temp_records"]):
        if record_type_lower and str(record["record_type"]).lower() != record_type_lower:
            continue
        results.append(
            {
                "record_id": record["record_id"],
                "record_type": record["record_type"],
                "created_at": record["created_at"],
                "solution_id": record["solution_id"],
                "solution_name": record["solution_name"],
                "document_count": len(record["document_ids"]),
                "source_types": record["source_types"],
                "confidence": record["confidence"],
            }
        )
    return results[:limit] if limit is not None else results


def get_temp_record(session: dict[str, Any], record_id: str) -> dict[str, Any]:
    index = session["temp_record_index"].get(record_id)
    if index is None:
        raise KeyError(f"Temporary record not found: {record_id}")
    return deepcopy(session["temp_records"][index])
