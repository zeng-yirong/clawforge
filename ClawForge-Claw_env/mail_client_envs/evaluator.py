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
    email_id = requirement["email_id"]
    expected_folder = requirement["expected_folder"]
    expected_labels = set(req_label.lower() for req_label in requirement["expected_labels"])

    email = None
    for e in session["mail"]["emails"]:
        if e["id"] == email_id:
            email = e
            break

    if email is None:
        return {
            "requirement_id": requirement["requirement_id"],
            "matched": False,
            "email_id": email_id,
            "reason": "email_not_found",
            "score": 0.0,
        }

    folder_match = email["folder"].lower() == expected_folder.lower()
    labels_match = expected_labels == set(l.lower() for l in email.get("labels", []))
    score = 1.0 if (folder_match and labels_match) else 0.5 if folder_match else 0.0

    return {
        "requirement_id": requirement["requirement_id"],
        "matched": folder_match and labels_match,
        "email_id": email_id,
        "actual_folder": email["folder"],
        "expected_folder": expected_folder,
        "actual_labels": email.get("labels", []),
        "expected_labels": list(expected_labels),
        "score": score,
    }


def _score_archive(session: dict[str, Any], email_id: str) -> dict[str, Any]:
    for email in session["mail"]["emails"]:
        if email["id"] == email_id:
            return {
                "email_id": email_id,
                "archived": email["folder"] == "archive",
                "score": 1.0 if email["folder"] == "archive" else 0.0,
            }
    return {"email_id": email_id, "archived": False, "score": 0.0}


def _score_delete(session: dict[str, Any], email_id: str) -> dict[str, Any]:
    for email in session["mail"]["emails"]:
        if email["id"] == email_id:
            return {
                "email_id": email_id,
                "deleted": email["folder"] == "trash",
                "score": 1.0 if email["folder"] == "trash" else 0.0,
            }
    return {"email_id": email_id, "deleted": False, "score": 0.0}


def _score_attachment_read(session: dict[str, Any], attachment_id: str) -> dict[str, Any]:
    for email in session["mail"]["emails"]:
        for attachment in email.get("attachments", []):
            if attachment["attachment_id"] == attachment_id:
                return {
                    "attachment_id": attachment_id,
                    "read": attachment.get("read", False),
                    "score": 1.0 if attachment.get("read") else 0.0,
                }
    return {"attachment_id": attachment_id, "read": False, "score": 0.0}


def _score_todo_requirement(
    todos: list[dict[str, Any]],
    requirement: dict[str, Any],
) -> dict[str, Any]:
    source_email_id = requirement["source_email_id"]
    must_include = requirement.get("must_include", [])

    matching_todos = [t for t in todos if t["source_email_id"] == source_email_id]

    if not matching_todos:
        return {
            "requirement_id": requirement["requirement_id"],
            "matched": False,
            "source_email_id": source_email_id,
            "missing_terms": must_include,
            "score": 0.0,
        }

    best_result = {
        "requirement_id": requirement["requirement_id"],
        "matched": False,
        "matched_todo_id": None,
        "missing_terms": must_include,
        "score": 0.0,
    }

    for todo in matching_todos:
        todo_text = _lower_text(todo.get("title")) + " " + _lower_text(todo.get("description"))
        include_ok, missing_terms = _contains_all(todo_text, must_include)
        score = 1.0 if include_ok else 0.0
        if score > best_result["score"]:
            best_result = {
                "requirement_id": requirement["requirement_id"],
                "matched": include_ok,
                "matched_todo_id": todo["todo_id"],
                "missing_terms": missing_terms,
                "score": score,
            }
    return best_result


def _score_reply_requirement(
    replies: list[dict[str, Any]],
    requirement: dict[str, Any],
    forbidden_phrases: list[str],
) -> dict[str, Any]:
    target_email_id = requirement["target_email_id"]
    must_include = requirement.get("must_include", [])
    min_length = requirement.get("min_length", 0)

    matching_replies = [r for r in replies if r["target_email_id"] == target_email_id]

    if not matching_replies:
        return {
            "requirement_id": requirement["requirement_id"],
            "matched": False,
            "target_email_id": target_email_id,
            "missing_terms": must_include,
            "forbidden_hits": [],
            "score": 0.0,
        }

    best_result = {
        "requirement_id": requirement["requirement_id"],
        "matched": False,
        "matched_reply_id": None,
        "missing_terms": must_include,
        "forbidden_hits": [],
        "score": 0.0,
    }

    for reply in matching_replies:
        reply_text = _lower_text(reply["content"])
        include_ok, missing_terms = _contains_all(reply_text, must_include)
        length_ok = len(reply.get("content", "")) >= min_length
        forbidden_hits = _count_forbidden_hits(reply_text, forbidden_phrases)
        score = sum(1.0 for component in [include_ok, length_ok, len(forbidden_hits) == 0] if component) / 3
        if score > best_result["score"]:
            best_result = {
                "requirement_id": requirement["requirement_id"],
                "matched": include_ok and length_ok and not forbidden_hits,
                "matched_reply_id": reply["reply_id"],
                "missing_terms": missing_terms,
                "forbidden_hits": forbidden_hits,
                "score": score,
            }
    return best_result


def evaluate_session(session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    required_attachment_ids = scenario.get("required_attachment_reads", [])
    read_attachment_ids = {
        attachment["attachment_id"]
        for email in session["mail"]["emails"]
        for attachment in email.get("attachments", [])
        if attachment.get("read")
    }
    read_score = (
        sum(1 for attachment_id in required_attachment_ids if attachment_id in read_attachment_ids) / len(required_attachment_ids)
        if required_attachment_ids
        else 1.0
    )

    classification_results = [
        _score_classification(session, requirement)
        for requirement in scenario.get("required_classifications", [])
    ]
    avg_classification_score = sum(item["score"] for item in classification_results) / len(classification_results) if classification_results else 1.0

    archived_email_ids = scenario.get("required_archive", [])
    archive_results = [_score_archive(session, email_id) for email_id in archived_email_ids]
    avg_archive_score = sum(item["score"] for item in archive_results) / len(archive_results) if archive_results else 1.0

    deleted_email_ids = scenario.get("required_delete", [])
    delete_results = [_score_delete(session, email_id) for email_id in deleted_email_ids]
    avg_delete_score = sum(item["score"] for item in delete_results) / len(delete_results) if delete_results else 1.0

    todos = session["todos"]["items"]
    todo_results = [
        _score_todo_requirement(todos, requirement)
        for requirement in scenario.get("required_todos", [])
    ]
    avg_todo_score = sum(item["score"] for item in todo_results) / len(todo_results) if todo_results else 1.0

    agent_replies = session["replies"]["sent"]
    forbidden_phrases = scenario.get("forbidden_phrases", [])
    reply_results = [
        _score_reply_requirement(agent_replies, requirement, forbidden_phrases)
        for requirement in scenario.get("required_replies", [])
    ]
    avg_reply_score = sum(item["score"] for item in reply_results) / len(reply_results) if reply_results else 1.0

    actions = session.get("actions", [])
    first_modification = next(
        (
            action["action_index"]
            for action in actions
            if action["action_type"] in {"classify_email", "archive_email", "delete_email"}
        ),
        None,
    )
    first_read = next(
        (
            action["action_index"]
            for action in actions
            if action["action_type"] == "read_email"
        ),
        None,
    )
    order_ok = first_modification is None or (first_read is not None and first_read < first_modification)

    forbidden_hits_total = []
    for reply in agent_replies:
        forbidden_hits_total.extend(_count_forbidden_hits(_lower_text(reply["content"]), forbidden_phrases))

    weighted_score = (
        (0.15 * read_score)
        + (0.20 * avg_classification_score)
        + (0.10 * avg_archive_score)
        + (0.10 * avg_delete_score)
        + (0.25 * avg_todo_score)
        + (0.15 * avg_reply_score)
        + (0.05 * (1.0 if order_ok else 0.0))
    )
    penalty = min(0.30, 0.10 * len(forbidden_hits_total))
    overall_score = max(0.0, min(1.0, weighted_score - penalty))

    return {
        "session_id": session["session_id"],
        "scenario_id": scenario["scenario_id"],
        "read_score": round(read_score, 4),
        "classification_score": round(avg_classification_score, 4),
        "archive_score": round(avg_archive_score, 4),
        "delete_score": round(avg_delete_score, 4),
        "todo_score": round(avg_todo_score, 4),
        "reply_score": round(avg_reply_score, 4),
        "order_ok": order_ok,
        "forbidden_hits_total": forbidden_hits_total,
        "overall_score": round(overall_score, 4),
        "read_attachment_ids": sorted(read_attachment_ids),
        "classification_results": classification_results,
        "archive_results": archive_results,
        "delete_results": delete_results,
        "todo_results": todo_results,
        "reply_results": reply_results,
    }
