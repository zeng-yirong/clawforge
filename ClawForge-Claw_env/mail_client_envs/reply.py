from __future__ import annotations

import uuid
from copy import deepcopy
from typing import Any


def build_reply_summary(reply: dict[str, Any]) -> dict[str, Any]:
    return {
        "reply_id": reply["reply_id"],
        "target_email_id": reply["target_email_id"],
        "content": reply["content"],
        "created_at": reply["created_at"],
    }


def list_replies(
    session: dict[str, Any],
    *,
    target_email_id: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    results = []

    for reply in session["replies"]["sent"]:
        if target_email_id and reply["target_email_id"] != target_email_id:
            continue
        results.append(build_reply_summary(reply))

    results.sort(key=lambda item: item["created_at"], reverse=True)
    return results[:limit] if limit is not None else results


def get_reply(session: dict[str, Any], reply_id: str) -> dict[str, Any]:
    for reply in session["replies"]["sent"]:
        if reply["reply_id"] == reply_id:
            return deepcopy(reply)
    raise KeyError(f"Reply not found: {reply_id}")


def create_reply(
    session: dict[str, Any],
    *,
    target_email_id: str,
    content: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    if not content.strip():
        raise ValueError("Reply content must not be empty.")

    target_email = None
    for email in session["mail"]["emails"]:
        if email["id"] == target_email_id:
            target_email = email
            break
    if target_email is None:
        raise KeyError(f"Target email not found: {target_email_id}")

    reply_id = f"reply_{uuid.uuid4().hex[:8]}"
    new_reply = {
        "reply_id": reply_id,
        "target_email_id": target_email_id,
        "content": content.strip(),
        "created_at": event_at,
        "last_action_index": action_index,
    }
    session["replies"]["sent"].insert(0, new_reply)
    target_email["replied"] = True
    target_email["replied_at"] = event_at
    return deepcopy(new_reply)
