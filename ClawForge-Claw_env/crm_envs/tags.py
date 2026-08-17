from __future__ import annotations

from typing import Any


def list_tag_definitions(session: dict[str, Any], *, category: str | None = None) -> list[dict[str, Any]]:
    tag_defs = session.get("tag_definitions", {})
    results = []

    for tag_id, tag_def in tag_defs.items():
        if category and tag_def.get("category", "").lower() != category.strip().lower():
            continue
        results.append({
            "tag_id": tag_id,
            "name": tag_def["name"],
            "color": tag_def["color"],
            "description": tag_def["description"],
            "category": tag_def["category"],
        })

    results.sort(key=lambda item: item["name"].lower())
    return results


def get_tag_definition(session: dict[str, Any], tag_name: str) -> dict[str, Any] | None:
    tag_lower = tag_name.strip().lower()
    tag_defs = session.get("tag_definitions", {})

    for tag_id, tag_def in tag_defs.items():
        if tag_def["name"].lower() == tag_lower:
            return {
                "tag_id": tag_id,
                "name": tag_def["name"],
                "color": tag_def["color"],
                "description": tag_def["description"],
                "category": tag_def["category"],
            }
    return None


def get_or_create_tag(
    session: dict[str, Any],
    tag_name: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    tag_lower = tag_name.strip().lower()
    tag_defs = session.get("tag_definitions", {})

    for tag_id, tag_def in tag_defs.items():
        if tag_def["name"].lower() == tag_lower:
            return {
                "tag_id": tag_id,
                "name": tag_def["name"],
                "created": False,
            }

    tag_id = f"tag_custom_{len(tag_defs) + 1}"
    tag_defs[tag_id] = {
        "tag_id": tag_id,
        "name": tag_name.strip(),
        "color": "#3498db",
        "description": f"Custom tag: {tag_name}",
        "category": "custom",
    }
    session["tag_definitions"][tag_id] = tag_defs[tag_id]
    return {
        "tag_id": tag_id,
        "name": tag_name.strip(),
        "created": True,
    }
