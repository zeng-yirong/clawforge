from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_email_summary(email: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": email["id"],
        "thread_id": email["thread_id"],
        "folder": email["folder"],
        "sender": email["sender"],
        "subject": email["subject"],
        "timestamp": email["timestamp"],
        "importance": email["importance"],
        "labels": email["labels"],
        "read": email["read"],
        "attachment_count": len(email.get("attachments", [])),
    }


def list_emails(
    session: dict[str, Any],
    *,
    query: str = "",
    unread_only: bool = False,
    folder: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query_lower = query.strip().lower()
    folder_lower = folder.strip().lower() if folder else None
    results = []

    for email in session["mail"]["emails"]:
        if unread_only and email["read"]:
            continue
        if folder_lower and email["folder"].lower() != folder_lower:
            continue

        searchable_text = " ".join(
            [
                email["subject"],
                email["body"],
                email["sender"]["name"],
                email["sender"]["email"],
                " ".join(email.get("labels", [])),
            ]
        ).lower()
        if query_lower and query_lower not in searchable_text:
            continue
        results.append(build_email_summary(email))

    results.sort(key=lambda item: item["timestamp"], reverse=True)
    return results[:limit] if limit is not None else results


def read_email(session: dict[str, Any], email_id: str, event_at: str, action_index: int) -> dict[str, Any]:
    for email in session["mail"]["emails"]:
        if email["id"] == email_id:
            email["read"] = True
            email["opened_at"] = event_at
            email["last_action_index"] = action_index
            return deepcopy(email)
    raise KeyError(f"Email not found: {email_id}")


def read_attachment(
    session: dict[str, Any],
    attachment_id: str,
    attachment_content: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    for email in session["mail"]["emails"]:
        for attachment in email.get("attachments", []):
            if attachment["attachment_id"] != attachment_id:
                continue
            attachment["read"] = True
            attachment["read_at"] = event_at
            attachment["last_action_index"] = action_index
            return {
                "attachment_id": attachment["attachment_id"],
                "file_name": attachment["file_name"],
                "mime_type": attachment["mime_type"],
                "tags": attachment.get("tags", []),
                "content": attachment_content,
                "source_email_id": email["id"],
                "source_email_subject": email["subject"],
            }
    raise KeyError(f"Attachment not found: {attachment_id}")
