from __future__ import annotations

import uuid
from copy import deepcopy
from typing import Any


def build_todo_summary(todo: dict[str, Any]) -> dict[str, Any]:
    return {
        "todo_id": todo["todo_id"],
        "source_email_id": todo["source_email_id"],
        "title": todo["title"],
        "description": todo["description"],
        "priority": todo["priority"],
        "due_date": todo.get("due_date"),
        "completed": todo["completed"],
        "completed_at": todo.get("completed_at"),
        "created_at": todo["created_at"],
    }


def list_todos(
    session: dict[str, Any],
    *,
    completed_only: bool = False,
    pending_only: bool = False,
    priority: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    results = []

    for todo in session["todos"]["items"]:
        if completed_only and not todo["completed"]:
            continue
        if pending_only and todo["completed"]:
            continue
        if priority and todo["priority"].lower() != priority.strip().lower():
            continue
        results.append(build_todo_summary(todo))

    results.sort(key=lambda item: (0 if item["priority"] == "high" else 1, item["created_at"]), reverse=False)
    return results[:limit] if limit is not None else results


def get_todo(session: dict[str, Any], todo_id: str) -> dict[str, Any]:
    for todo in session["todos"]["items"]:
        if todo["todo_id"] == todo_id:
            return deepcopy(todo)
    raise KeyError(f"Todo not found: {todo_id}")


def create_todo(
    session: dict[str, Any],
    *,
    source_email_id: str,
    title: str,
    description: str,
    priority: str = "normal",
    due_date: str | None,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    todo_id = f"todo_{uuid.uuid4().hex[:8]}"
    new_todo = {
        "todo_id": todo_id,
        "source_email_id": source_email_id,
        "title": title.strip(),
        "description": description.strip(),
        "priority": priority.lower(),
        "due_date": due_date,
        "completed": False,
        "completed_at": None,
        "created_at": event_at,
        "last_action_index": action_index,
    }
    session["todos"]["items"].insert(0, new_todo)
    return deepcopy(new_todo)


def complete_todo(
    session: dict[str, Any],
    todo_id: str,
    event_at: str,
    action_index: int,
) -> dict[str, Any]:
    for todo in session["todos"]["items"]:
        if todo["todo_id"] == todo_id:
            todo["completed"] = True
            todo["completed_at"] = event_at
            todo["last_action_index"] = action_index
            return deepcopy(todo)
    raise KeyError(f"Todo not found: {todo_id}")
