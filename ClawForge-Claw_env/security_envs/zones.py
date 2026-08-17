from __future__ import annotations

from copy import deepcopy
from typing import Any


def get_zone_status(session: dict[str, Any], zone_id: str) -> dict[str, Any]:
    zones = session.get("zones", {})
    if zone_id not in zones:
        return {"error": f"Zone {zone_id} not found", "zone_id": zone_id}

    zone = deepcopy(zones[zone_id])
    return {"zone_id": zone_id, **zone}


def list_zones(
    session: dict[str, Any],
    query: str = "",
    status: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    zones = session.get("zones", {})
    results = []

    for zone_id, zone in zones.items():
        if query:
            if query.lower() not in zone.get("name", "").lower() and query.lower() not in zone_id.lower():
                continue

        if status and zone.get("status") != status:
            continue

        results.append({"zone_id": zone_id, **deepcopy(zone)})

    if limit:
        results = results[:limit]

    return results


def arm_zone(
    session: dict[str, Any],
    zone_id: str,
    action_index: int | None = None,
) -> dict[str, Any]:
    zones = session.setdefault("zones", {})
    if zone_id not in zones:
        return {"error": f"Zone {zone_id} not found", "zone_id": zone_id}

    zones[zone_id]["armed"] = True
    zones[zone_id]["status"] = "armed"
    zones[zone_id]["last_action_index"] = action_index

    action = {
        "action": "arm_zone",
        "zone_id": zone_id,
        "action_index": action_index,
        "timestamp": session.get("meta", {}).get("current_time"),
    }
    session.setdefault("actions", []).append(action)

    return {
        "zone_id": zone_id,
        "armed": True,
        "action_index": action_index,
    }


def disarm_zone(
    session: dict[str, Any],
    zone_id: str,
    action_index: int | None = None,
) -> dict[str, Any]:
    zones = session.setdefault("zones", {})
    if zone_id not in zones:
        return {"error": f"Zone {zone_id} not found", "zone_id": zone_id}

    zones[zone_id]["armed"] = False
    zones[zone_id]["status"] = "disarmed"
    zones[zone_id]["last_action_index"] = action_index

    action = {
        "action": "disarm_zone",
        "zone_id": zone_id,
        "action_index": action_index,
        "timestamp": session.get("meta", {}).get("current_time"),
    }
    session.setdefault("actions", []).append(action)

    return {
        "zone_id": zone_id,
        "armed": False,
        "action_index": action_index,
    }


def arm_all_zones(
    session: dict[str, Any],
    action_index: int | None = None,
) -> dict[str, Any]:
    zones = session.get("zones", {})
    armed_zones = []

    for zone_id, zone in zones.items():
        zones[zone_id]["armed"] = True
        zones[zone_id]["status"] = "armed"
        zones[zone_id]["last_action_index"] = action_index
        armed_zones.append(zone_id)

    action = {
        "action": "arm_all_zones",
        "armed_count": len(armed_zones),
        "action_index": action_index,
        "timestamp": session.get("meta", {}).get("current_time"),
    }
    session.setdefault("actions", []).append(action)

    return {
        "armed_zones": armed_zones,
        "count": len(armed_zones),
        "action_index": action_index,
    }


def check_zone_sensors(session: dict[str, Any], zone_id: str) -> dict[str, Any]:
    zones = session.get("zones", {})
    if zone_id not in zones:
        return {"error": f"Zone {zone_id} not found", "zone_id": zone_id}

    zone = zones[zone_id]
    sensors = zone.get("sensors", [])

    triggered_sensors = [s for s in sensors if s.get("triggered", False)]

    return {
        "zone_id": zone_id,
        "total_sensors": len(sensors),
        "triggered_sensors": triggered_sensors,
        "has_intrusion": len(triggered_sensors) > 0,
    }
