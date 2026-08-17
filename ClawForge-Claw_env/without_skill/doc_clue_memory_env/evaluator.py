from __future__ import annotations

from typing import Any


def _action_types(session: dict[str, Any]) -> list[str]:
    return [str(item.get("action_type")) for item in session.get("actions", [])]


def _latest_clue_list(session: dict[str, Any]) -> dict[str, Any] | None:
    for record in reversed(session.get("temp_records", [])):
        if record.get("record_type") == "clue_list":
            return record
    return None


def evaluate_session(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    action_types = _action_types(session)
    required_actions = scenario.get("required_actions", [])
    if required_actions:
        matched = len({item for item in required_actions if item in action_types})
        required_action_score = (matched / len(required_actions)) * 25.0
    else:
        matched = 0
        required_action_score = 0.0

    target_solution_id = scenario["target_solution_id"]
    target_solution_name = scenario["target_solution_name"]
    expected_document_ids = set(scenario.get("expected_document_ids", []))
    forbidden_document_ids = set(scenario.get("forbidden_document_ids", []))
    required_attachment_paths = set(scenario.get("required_attachment_paths", []))
    required_source_types = set(scenario.get("required_source_types", []))
    minimum_clue_count = int(scenario.get("minimum_clue_count", 0))

    attachments_read = set(session.get("observations", {}).get("attachments_read", []))
    document_ids_seen = set(session.get("observations", {}).get("document_ids_seen", []))
    queries_run = [str(item) for item in session.get("observations", {}).get("queries_run", [])]
    source_types_seen = set(session.get("observations", {}).get("source_types_seen", []))

    reading_score = 0.0
    if required_attachment_paths:
        reading_score += 10.0 * (len(attachments_read & required_attachment_paths) / len(required_attachment_paths))
    if queries_run:
        reading_score += 5.0

    retrieval_score = 0.0
    retrieval_checks = {
        "expected_documents_read": expected_document_ids.issubset(document_ids_seen),
        "required_source_types_seen": required_source_types.issubset(source_types_seen),
        "query_mentions_target": any(
            alias.lower() in query.lower()
            for alias in [target_solution_name, *scenario.get("target_solution_aliases", [])]
            for query in queries_run
        ),
    }
    retrieval_score += 10.0 if retrieval_checks["expected_documents_read"] else 0.0
    retrieval_score += 7.5 if retrieval_checks["required_source_types_seen"] else 0.0
    retrieval_score += 7.5 if retrieval_checks["query_mentions_target"] else 0.0

    record = _latest_clue_list(session)
    record_score = 0.0
    record_checks = {
        "exists": False,
        "correct_solution_id": False,
        "correct_solution_name": False,
        "expected_documents_saved": False,
        "required_source_types_saved": False,
        "minimum_clue_count_met": False,
    }
    if record:
        record_checks["exists"] = True
        record_checks["correct_solution_id"] = record.get("solution_id") == target_solution_id
        record_checks["correct_solution_name"] = record.get("solution_name") == target_solution_name
        record_document_ids = set(record.get("document_ids", []))
        record_source_types = set(record.get("source_types", []))
        record_checks["expected_documents_saved"] = expected_document_ids.issubset(record_document_ids)
        record_checks["required_source_types_saved"] = required_source_types.issubset(record_source_types)
        record_checks["minimum_clue_count_met"] = len(record.get("clues", [])) >= minimum_clue_count
        record_score += 10.0 if record_checks["correct_solution_id"] else 0.0
        record_score += 7.5 if record_checks["correct_solution_name"] else 0.0
        record_score += 12.5 if record_checks["expected_documents_saved"] else 0.0
        record_score += 5.0 if record_checks["required_source_types_saved"] else 0.0
        record_score += 5.0 if record_checks["minimum_clue_count_met"] else 0.0

    penalty = 0.0
    if record:
        forbidden_hits = forbidden_document_ids & set(record.get("document_ids", []))
        penalty -= 10.0 * len(forbidden_hits)
    else:
        forbidden_hits = set()

    overall_score = max(
        0.0,
        min(100.0, required_action_score + reading_score + retrieval_score + record_score + penalty),
    )

    return {
        "overall_score": round(overall_score, 4),
        "breakdown": {
            "required_action_score": round(required_action_score, 4),
            "reading_score": round(reading_score, 4),
            "retrieval_score": round(retrieval_score, 4),
            "record_score": round(record_score, 4),
            "penalty": round(penalty, 4),
        },
        "required_actions": {
            "expected": required_actions,
            "matched_count": matched,
            "observed_actions": action_types,
        },
        "checks": {
            "retrieval": retrieval_checks,
            "record": record_checks,
            "attachments_read": sorted(attachments_read),
            "document_ids_seen": sorted(document_ids_seen),
            "source_types_seen": sorted(source_types_seen),
            "forbidden_document_hits": sorted(forbidden_hits),
        },
    }
