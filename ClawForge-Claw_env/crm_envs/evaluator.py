from __future__ import annotations

from typing import Any


def _lower_text(value: str | None) -> str:
    return (value or "").strip().lower()


def _contains_all(text: str, snippets: list[str]) -> tuple[bool, list[str]]:
    missing = [snippet for snippet in snippets if snippet.lower() not in text]
    return len(missing) == 0, missing


def _count_forbidden_hits(text: str, forbidden_phrases: list[str]) -> list[str]:
    return [phrase for phrase in forbidden_phrases if phrase.lower() in text]


def _score_classification(session: dict[str, Any], requirement: dict[str, Any]) -> dict[str, Any]:
    contact_id = requirement["contact_id"]
    expected_folder = requirement["expected_folder"]
    expected_tags = set(req_tag.lower() for req_tag in requirement["expected_tags"])

    contact = None
    for c in session["crm"]["contacts"]:
        if c["contact_id"] == contact_id:
            contact = c
            break

    if contact is None:
        return {
            "requirement_id": requirement["requirement_id"],
            "matched": False,
            "contact_id": contact_id,
            "reason": "contact_not_found",
            "score": 0.0,
        }

    folder_match = contact["folder"].lower() == expected_folder.lower()
    tags_match = expected_tags == set(t.lower() for t in contact.get("tags", []))
    score = 1.0 if (folder_match and tags_match) else 0.5 if folder_match else 0.0

    return {
        "requirement_id": requirement["requirement_id"],
        "matched": folder_match and tags_match,
        "contact_id": contact_id,
        "actual_folder": contact["folder"],
        "expected_folder": expected_folder,
        "actual_tags": contact.get("tags", []),
        "expected_tags": list(expected_tags),
        "score": score,
    }


def _score_reminder(session: dict[str, Any], requirement: dict[str, Any], tag_defs: dict[str, Any]) -> dict[str, Any]:
    contact_id = requirement["contact_id"]
    must_include = requirement.get("must_include", [])

    reminder_id = f"rem_{contact_id}_birthday"
    reminder = None
    for r in session["crm"]["reminders"]:
        if r["reminder_id"] == reminder_id:
            reminder = r
            break

    if reminder is None:
        return {
            "requirement_id": requirement["requirement_id"],
            "matched": False,
            "contact_id": contact_id,
            "reason": "reminder_not_found",
            "score": 0.0,
        }

    reminder_text = _lower_text(reminder.get("title")) + " " + _lower_text(reminder.get("description"))
    include_ok, missing_terms = _contains_all(reminder_text, must_include)
    enabled_ok = reminder.get("enabled", False)

    score = 1.0 if (include_ok and enabled_ok) else 0.5 if include_ok else 0.0

    return {
        "requirement_id": requirement["requirement_id"],
        "matched": include_ok and enabled_ok,
        "contact_id": contact_id,
        "reminder_id": reminder_id,
        "enabled": reminder.get("enabled", False),
        "title": reminder.get("title"),
        "missing_terms": missing_terms,
        "score": score,
    }


def _score_archive(session: dict[str, Any], contact_id: str) -> dict[str, Any]:
    for contact in session["crm"]["contacts"]:
        if contact["contact_id"] == contact_id:
            return {
                "contact_id": contact_id,
                "archived": contact["folder"] == "archive",
                "score": 1.0 if contact["folder"] == "archive" else 0.0,
            }
    return {"contact_id": contact_id, "archived": False, "score": 0.0}


def evaluate_session(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    tag_defs = session.get("tag_definitions", {})

    classification_results = [
        _score_classification(session, requirement)
        for requirement in scenario.get("required_classifications", [])
    ]
    avg_classification_score = sum(item["score"] for item in classification_results) / len(classification_results) if classification_results else 1.0

    reminder_results = [
        _score_reminder(session, requirement, tag_defs)
        for requirement in scenario.get("required_reminders", [])
    ]
    avg_reminder_score = sum(item["score"] for item in reminder_results) / len(reminder_results) if reminder_results else 1.0

    archived_contact_ids = scenario.get("required_archive", [])
    archive_results = [_score_archive(session, contact_id) for contact_id in archived_contact_ids]
    avg_archive_score = sum(item["score"] for item in archive_results) / len(archive_results) if archive_results else 1.0

    forbidden_phrases = scenario.get("forbidden_phrases", [])

    actions = session.get("actions", [])

    forbidden_hits_total = []
    for action in actions:
        action_type = action.get("action_type", "")
        details_str = str(action.get("details", "")).lower()
        for phrase in forbidden_phrases:
            if phrase.lower() in details_str:
                forbidden_hits_total.append(phrase)

    weighted_score = (
        (0.40 * avg_classification_score)
        + (0.35 * avg_reminder_score)
        + (0.25 * avg_archive_score)
    )
    penalty = min(0.30, 0.10 * len(forbidden_hits_total))
    overall_score = max(0.0, min(1.0, weighted_score - penalty))

    return {
        "session_id": session["session_id"],
        "scenario_id": scenario["scenario_id"],
        "classification_score": round(avg_classification_score, 4),
        "reminder_score": round(avg_reminder_score, 4),
        "archive_score": round(avg_archive_score, 4),
        "forbidden_hits_total": forbidden_hits_total,
        "overall_score": round(overall_score, 4),
        "classification_results": classification_results,
        "reminder_results": reminder_results,
        "archive_results": archive_results,
    }
