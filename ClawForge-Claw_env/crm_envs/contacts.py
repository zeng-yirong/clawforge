from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_contact_summary(contact: dict[str, Any]) -> dict[str, Any]:
    return {
        "contact_id": contact["contact_id"],
        "full_name": contact["full_name"],
        "email": contact["email"],
        "phone": contact["phone"],
        "company_id": contact["company_id"],
        "job_title": contact["job_title"],
        "contact_type": contact["contact_type"],
        "folder": contact["folder"],
        "tags": contact["tags"],
        "birthday": contact["birthday"],
    }


def list_contacts(
    session: dict[str, Any],
    *,
    query: str = "",
    folder: str | None = None,
    contact_type: str | None = None,
    tag: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query_lower = query.strip().lower()
    folder_lower = folder.strip().lower() if folder else None
    tag_lower = tag.strip().lower() if tag else None
    results = []

    for contact in session["crm"]["contacts"]:
        if folder_lower and contact["folder"].lower() != folder_lower:
            continue
        if contact_type and contact["contact_type"].lower() != contact_type.strip().lower():
            continue
        if tag_lower and tag_lower not in [t.lower() for t in contact.get("tags", [])]:
            continue

        searchable_text = " ".join(
            [
                contact["full_name"],
                contact["email"],
                contact.get("job_title") or "",
                " ".join(contact.get("tags", [])),
            ]
        ).lower()
        if query_lower and query_lower not in searchable_text:
            continue
        results.append(build_contact_summary(contact))

    results.sort(key=lambda item: item["full_name"].lower())
    return results[:limit] if limit is not None else results


def get_contact(session: dict[str, Any], contact_id: str) -> dict[str, Any]:
    for contact in session["crm"]["contacts"]:
        if contact["contact_id"] == contact_id:
            return deepcopy(contact)
    raise KeyError(f"Contact not found: {contact_id}")


def classify_contact(
    session: dict[str, Any],
    contact_id: str,
    target_folder: str,
    target_tags: list[str],
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    for contact in session["crm"]["contacts"]:
        if contact["contact_id"] == contact_id:
            old_folder = contact["folder"]
            old_tags = list(contact["tags"])
            contact["folder"] = target_folder
            contact["tags"] = target_tags
            contact["last_action_index"] = action_index
            return {
                "contact_id": contact_id,
                "old_folder": old_folder,
                "new_folder": target_folder,
                "old_tags": old_tags,
                "new_tags": target_tags,
                "timestamp": event_at,
            }
    raise KeyError(f"Contact not found: {contact_id}")


def add_tags_to_contact(
    session: dict[str, Any],
    contact_id: str,
    tags_to_add: list[str],
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    for contact in session["crm"]["contacts"]:
        if contact["contact_id"] == contact_id:
            old_tags = list(contact["tags"])
            for tag in tags_to_add:
                if tag not in contact["tags"]:
                    contact["tags"].append(tag)
            contact["last_action_index"] = action_index
            return {
                "contact_id": contact_id,
                "old_tags": old_tags,
                "new_tags": contact["tags"],
                "added_tags": tags_to_add,
                "timestamp": event_at,
            }
    raise KeyError(f"Contact not found: {contact_id}")


def remove_tags_from_contact(
    session: dict[str, Any],
    contact_id: str,
    tags_to_remove: list[str],
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    for contact in session["crm"]["contacts"]:
        if contact["contact_id"] == contact_id:
            old_tags = list(contact["tags"])
            contact["tags"] = [t for t in contact["tags"] if t not in tags_to_remove]
            contact["last_action_index"] = action_index
            return {
                "contact_id": contact_id,
                "old_tags": old_tags,
                "new_tags": contact["tags"],
                "removed_tags": tags_to_remove,
                "timestamp": event_at,
            }
    raise KeyError(f"Contact not found: {contact_id}")


def archive_contact(
    session: dict[str, Any],
    contact_id: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    for contact in session["crm"]["contacts"]:
        if contact["contact_id"] == contact_id:
            old_folder = contact["folder"]
            contact["folder"] = "archive"
            contact["archived_at"] = event_at
            contact["last_action_index"] = action_index
            return {
                "contact_id": contact_id,
                "old_folder": old_folder,
                "new_folder": "archive",
                "timestamp": event_at,
            }
    raise KeyError(f"Contact not found: {contact_id}")


def search_contacts(
    session: dict[str, Any],
    *,
    name_query: str = "",
    email_query: str = "",
    company_id: str | None = None,
    tag: str | None = None,
    folder: str | None = None,
) -> list[dict[str, Any]]:
    name_lower = name_query.strip().lower()
    email_lower = email_query.strip().lower()
    tag_lower = tag.strip().lower() if tag else None
    folder_lower = folder.strip().lower() if folder else None

    results = []
    for contact in session["crm"]["contacts"]:
        if folder_lower and contact["folder"].lower() != folder_lower:
            continue
        if tag_lower and tag_lower not in [t.lower() for t in contact.get("tags", [])]:
            continue
        if company_id and contact.get("company_id") != company_id:
            continue

        if name_lower:
            full_name = contact["full_name"].lower()
            if name_lower not in full_name and name_lower not in contact.get("first_name", "").lower() and name_lower not in contact.get("last_name", "").lower():
                continue

        if email_lower:
            if email_lower not in contact["email"].lower():
                continue

        results.append(build_contact_summary(contact))

    return results
