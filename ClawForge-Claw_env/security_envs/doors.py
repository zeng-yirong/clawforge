from __future__ import annotations

from copy import deepcopy
from typing import Any


def get_door_status(session: dict[str, Any], door_id: str) -> dict[str, Any]:
    doors = session.get("doors", {})
    if door_id not in doors:
        return {"error": f"Door {door_id} not found", "door_id": door_id}

    door = deepcopy(doors[door_id])
    return {"door_id": door_id, **door}


def list_doors(
    session: dict[str, Any],
    query: str = "",
    zone_id: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    doors = session.get("doors", {})
    results = []

    for door_id, door in doors.items():
        if query:
            if query.lower() not in door.get("name", "").lower() and query.lower() not in door_id.lower():
                continue

        if zone_id and door.get("zone_id") != zone_id:
            continue

        results.append({"door_id": door_id, **deepcopy(door)})

    if limit:
        results = results[:limit]

    return results


def lock_door(
    session: dict[str, Any],
    door_id: str,
    action_index: int | None = None,
) -> dict[str, Any]:
    doors = session.setdefault("doors", {})
    if door_id not in doors:
        return {"error": f"Door {door_id} not found", "door_id": door_id}

    doors[door_id]["locked"] = True
    doors[door_id]["last_action_index"] = action_index

    action = {
        "action": "lock_door",
        "door_id": door_id,
        "action_index": action_index,
        "timestamp": session.get("meta", {}).get("current_time"),
    }
    session.setdefault("actions", []).append(action)

    return {
        "door_id": door_id,
        "locked": True,
        "action_index": action_index,
    }


def unlock_door(
    session: dict[str, Any],
    door_id: str,
    action_index: int | None = None,
) -> dict[str, Any]:
    doors = session.setdefault("doors", {})
    if door_id not in doors:
        return {"error": f"Door {door_id} not found", "door_id": door_id}

    doors[door_id]["locked"] = False
    doors[door_id]["last_action_index"] = action_index

    action = {
        "action": "unlock_door",
        "door_id": door_id,
        "action_index": action_index,
        "timestamp": session.get("meta", {}).get("current_time"),
    }
    session.setdefault("actions", []).append(action)

    return {
        "door_id": door_id,
        "locked": False,
        "action_index": action_index,
    }


def lock_all_doors(
    session: dict[str, Any],
    zone_id: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    doors = session.get("doors", {})
    locked_doors = []

    for door_id, door in doors.items():
        if zone_id and door.get("zone_id") != zone_id:
            continue
        doors[door_id]["locked"] = True
        doors[door_id]["last_action_index"] = action_index
        locked_doors.append(door_id)

    action = {
        "action": "lock_all_doors",
        "zone_id": zone_id,
        "locked_count": len(locked_doors),
        "action_index": action_index,
        "timestamp": session.get("meta", {}).get("current_time"),
    }
    session.setdefault("actions", []).append(action)

    return {
        "locked_doors": locked_doors,
        "count": len(locked_doors),
        "action_index": action_index,
    }


def unlock_all_doors(
    session: dict[str, Any],
    zone_id: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    doors = session.get("doors", {})
    unlocked_doors = []

    for door_id, door in doors.items():
        if zone_id and door.get("zone_id") != zone_id:
            continue
        doors[door_id]["locked"] = False
        doors[door_id]["last_action_index"] = action_index
        unlocked_doors.append(door_id)

    action = {
        "action": "unlock_all_doors",
        "zone_id": zone_id,
        "unlocked_count": len(unlocked_doors),
        "action_index": action_index,
        "timestamp": session.get("meta", {}).get("current_time"),
    }
    session.setdefault("actions", []).append(action)

    return {
        "unlocked_doors": unlocked_doors,
        "count": len(unlocked_doors),
        "action_index": action_index,
    }


def get_all_doors_status(session: dict[str, Any]) -> dict[str, Any]:
    doors = session.get("doors", {})
    locked_count = sum(1 for d in doors.values() if d.get("locked", False))
    unlocked_count = len(doors) - locked_count

    return {
        "total_doors": len(doors),
        "locked_count": locked_count,
        "unlocked_count": unlocked_count,
        "doors": [
            {"door_id": did, "name": d.get("name"), "locked": d.get("locked", False), "zone_id": d.get("zone_id")}
            for did, d in doors.items()
        ],
    }
