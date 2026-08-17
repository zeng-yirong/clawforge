from __future__ import annotations

import uuid
from copy import deepcopy
from typing import Any


def _reply_count(post: dict[str, Any]) -> int:
    return len(post.get("replies", []))


def build_post_summary(post: dict[str, Any]) -> dict[str, Any]:
    return {
        "post_id": post["post_id"],
        "platform": post["platform"],
        "community": post.get("community"),
        "author": post["author"],
        "title": post.get("title"),
        "content": post["content"],
        "timestamp": post["timestamp"],
        "needs_response": post.get("needs_response", False),
        "tags": post.get("tags", []),
        "reply_count": _reply_count(post),
        "created_by_agent": post.get("created_by_agent", False),
    }


def list_posts(
    session: dict[str, Any],
    *,
    query: str = "",
    platform: str | None = None,
    needs_response_only: bool = False,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query_lower = query.strip().lower()
    platform_lower = platform.strip().lower() if platform else None
    merged_posts = session["social"]["seed_posts"] + session["social"]["agent_posts"]

    results = []
    for post in merged_posts:
        if platform_lower and post["platform"].lower() != platform_lower:
            continue
        if needs_response_only and not post.get("needs_response", False):
            continue
        searchable = " ".join(
            [
                post.get("title") or "",
                post["content"],
                post.get("author") or "",
                " ".join(post.get("tags", [])),
            ]
        ).lower()
        if query_lower and query_lower not in searchable:
            continue
        results.append(build_post_summary(post))

    results.sort(key=lambda item: item["timestamp"], reverse=True)
    return results[:limit] if limit is not None else results


def view_post(session: dict[str, Any], post_id: str) -> dict[str, Any]:
    for post in session["social"]["seed_posts"] + session["social"]["agent_posts"]:
        if post["post_id"] == post_id:
            return deepcopy(post)
    raise KeyError(f"Post not found: {post_id}")


def publish_post(
    session: dict[str, Any],
    *,
    platform: str,
    content: str,
    title: str | None,
    community: str | None,
    event_at: str,
    author: str,
    action_index: int,
) -> dict[str, Any]:
    platform_lower = platform.strip().lower()
    if platform_lower not in {"x", "reddit"}:
        raise ValueError(f"Unsupported platform: {platform}")
    if not content.strip():
        raise ValueError("Content must not be empty.")
    if platform_lower == "x" and len(content) > 280:
        raise ValueError("X post exceeds 280 characters.")
    if platform_lower == "reddit" and not (title or "").strip():
        raise ValueError("Reddit posts require a title.")

    post_id_prefix = "x_agent" if platform_lower == "x" else "rdt_agent"
    new_post = {
        "post_id": f"{post_id_prefix}_{uuid.uuid4().hex[:8]}",
        "platform": platform_lower,
        "community": community if platform_lower == "reddit" else None,
        "author": author,
        "title": title.strip() if title else None,
        "content": content.strip(),
        "timestamp": event_at,
        "tags": ["agent_generated"],
        "needs_response": False,
        "created_by_agent": True,
        "replies": [],
        "last_action_index": action_index,
    }
    session["social"]["agent_posts"].insert(0, new_post)
    return deepcopy(new_post)


def reply_to_post(
    session: dict[str, Any],
    *,
    post_id: str,
    content: str,
    event_at: str,
    author: str,
    action_index: int,
) -> dict[str, Any]:
    if not content.strip():
        raise ValueError("Reply content must not be empty.")

    parent_post = None
    for post in session["social"]["seed_posts"] + session["social"]["agent_posts"]:
        if post["post_id"] == post_id:
            parent_post = post
            break
    if parent_post is None:
        raise KeyError(f"Post not found: {post_id}")

    reply_prefix = "x_reply" if parent_post["platform"] == "x" else "rdt_reply"
    reply = {
        "reply_id": f"{reply_prefix}_{uuid.uuid4().hex[:8]}",
        "parent_post_id": post_id,
        "platform": parent_post["platform"],
        "author": author,
        "content": content.strip(),
        "timestamp": event_at,
        "created_by_agent": True,
        "last_action_index": action_index,
    }
    parent_post.setdefault("replies", []).append(reply)
    parent_post["needs_response"] = False
    session["social"]["agent_replies"].append(deepcopy(reply))
    return deepcopy(reply)
