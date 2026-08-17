from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_reminder_summary(reminder: dict[str, Any]) -> dict[str, Any]:
    return {
        "reminder_id": reminder["reminder_id"],
        "contact_id": reminder["contact_id"],
        "reminder_type": reminder["reminder_type"],
        "title": reminder["title"],
        "reminder_date": reminder["reminder_date"],
        "days_before": reminder["days_before"],
        "is_recurring": reminder["is_recurring"],
        "enabled": reminder["enabled"],
    }


def list_reminders(
    session: dict[str, Any],
    *,
    contact_id: str | None = None,
    reminder_type: str | None = None,
    upcoming_only: bool = False,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    results = []

    for reminder in session["crm"]["reminders"]:
        if contact_id and reminder["contact_id"] != contact_id:
            continue
        if reminder_type and reminder["reminder_type"].lower() != reminder_type.strip().lower():
            continue
        if upcoming_only and not reminder["enabled"]:
            continue
        results.append(build_reminder_summary(reminder))

    results.sort(key=lambda item: item["reminder_date"])
    return results[:limit] if limit is not None else results


def get_reminder(session: dict[str, Any], reminder_id: str) -> dict[str, Any]:
    for reminder in session["crm"]["reminders"]:
        if reminder["reminder_id"] == reminder_id:
            return deepcopy(reminder)
    raise KeyError(f"Reminder not found: {reminder_id}")


def create_birthday_reminder(
    session: dict[str, Any],
    contact_id: str,
    contact_name: str,
    birthday: str,
    days_before: int = 7,
    event_at: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    reminder_id = f"rem_{contact_id}_birthday"
    for existing in session["crm"]["reminders"]:
        if existing["reminder_id"] == reminder_id:
            return deepcopy(existing)

    new_reminder = {
        "reminder_id": reminder_id,
        "contact_id": contact_id,
        "reminder_type": "birthday",
        "title": f"{contact_name}'s Birthday",
        "description": f"Birthday reminder for {contact_name}",
        "reminder_date": birthday,
        "days_before": days_before,
        "is_recurring": True,
        "enabled": True,
        "created_at": event_at,
        "last_action_index": action_index,
    }
    session["crm"]["reminders"].append(new_reminder)
    return deepcopy(new_reminder)


def enable_reminder(
    session: dict[str, Any],
    reminder_id: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    for reminder in session["crm"]["reminders"]:
        if reminder["reminder_id"] == reminder_id:
            reminder["enabled"] = True
            reminder["last_action_index"] = action_index
            return deepcopy(reminder)
    raise KeyError(f"Reminder not found: {reminder_id}")


def disable_reminder(
    session: dict[str, Any],
    reminder_id: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    for reminder in session["crm"]["reminders"]:
        if reminder["reminder_id"] == reminder_id:
            reminder["enabled"] = False
            reminder["last_action_index"] = action_index
            return deepcopy(reminder)
    raise KeyError(f"Reminder not found: {reminder_id}")
