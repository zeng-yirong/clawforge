from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any


def create_alert(
    session: dict[str, Any],
    alert_type: str,
    zone_id: str,
    description: str,
    severity: str = "medium",
    source: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    alerts = session.setdefault("alerts", [])

    alert_id = f"alert_{len(alerts) + 1:04d}"
    timestamp = session.get("meta", {}).get("current_time", datetime.now().isoformat())

    alert = {
        "alert_id": alert_id,
        "alert_type": alert_type,
        "zone_id": zone_id,
        "description": description,
        "severity": severity,
        "source": source,
        "status": "active",
        "created_at": timestamp,
        "action_index": action_index,
    }

    alerts.append(alert)
    session.setdefault("active_alerts", {})[alert_id] = alert

    action = {
        "action": "create_alert",
        "alert_id": alert_id,
        "alert_type": alert_type,
        "severity": severity,
        "action_index": action_index,
        "timestamp": timestamp,
    }
    session.setdefault("actions", []).append(action)

    return deepcopy(alert)


def get_alert(session: dict[str, Any], alert_id: str) -> dict[str, Any]:
    alerts = session.get("alerts", [])
    for alert in alerts:
        if alert.get("alert_id") == alert_id:
            return deepcopy(alert)
    return {"error": f"Alert {alert_id} not found"}


def list_alerts(
    session: dict[str, Any],
    query: str = "",
    status: str | None = None,
    severity: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    alerts = session.get("alerts", [])
    results = []

    for alert in alerts:
        if query:
            if query.lower() not in alert.get("description", "").lower():
                continue

        if status and alert.get("status") != status:
            continue

        if severity and alert.get("severity") != severity:
            continue

        results.append(deepcopy(alert))

    results.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    if limit:
        results = results[:limit]

    return results


def acknowledge_alert(
    session: dict[str, Any],
    alert_id: str,
    action_index: int | None = None,
) -> dict[str, Any]:
    alerts = session.get("alerts", [])
    for alert in alerts:
        if alert.get("alert_id") == alert_id:
            alert["status"] = "acknowledged"
            alert["acknowledged_at"] = session.get("meta", {}).get("current_time")
            alert["action_index"] = action_index

            action = {
                "action": "acknowledge_alert",
                "alert_id": alert_id,
                "action_index": action_index,
                "timestamp": session.get("meta", {}).get("current_time"),
            }
            session.setdefault("actions", []).append(action)

            return deepcopy(alert)

    return {"error": f"Alert {alert_id} not found"}


def resolve_alert(
    session: dict[str, Any],
    alert_id: str,
    resolution: str,
    action_index: int | None = None,
) -> dict[str, Any]:
    alerts = session.get("alerts", [])
    for alert in alerts:
        if alert.get("alert_id") == alert_id:
            alert["status"] = "resolved"
            alert["resolution"] = resolution
            alert["resolved_at"] = session.get("meta", {}).get("current_time")
            alert["action_index"] = action_index

            session.setdefault("active_alerts", {}).pop(alert_id, None)

            action = {
                "action": "resolve_alert",
                "alert_id": alert_id,
                "resolution": resolution,
                "action_index": action_index,
                "timestamp": session.get("meta", {}).get("current_time"),
            }
            session.setdefault("actions", []).append(action)

            return deepcopy(alert)

    return {"error": f"Alert {alert_id} not found"}


def get_active_alerts(session: dict[str, Any]) -> dict[str, Any]:
    alerts = session.get("alerts", [])
    active = [deepcopy(a) for a in alerts if a.get("status") == "active"]
    acknowledged = [deepcopy(a) for a in alerts if a.get("status") == "acknowledged"]

    critical = sum(1 for a in active if a.get("severity") == "critical")
    high = sum(1 for a in active if a.get("severity") == "high")
    medium = sum(1 for a in active if a.get("severity") == "medium")
    low = sum(1 for a in active if a.get("severity") == "low")

    return {
        "total_active": len(active),
        "total_acknowledged": len(acknowledged),
        "by_severity": {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
        },
        "active_alerts": active,
    }


def check_intrusion_detected(session: dict[str, Any]) -> dict[str, Any]:
    zones = session.get("zones", {})
    doors = session.get("doors", {})

    intrusion_detected = False
    intrusion_zones = []
    intrusion_details = []

    for zone_id, zone in zones.items():
        if zone.get("status") == "intrusion":
            intrusion_detected = True
            intrusion_zones.append(zone_id)
            intrusion_details.append({
                "zone_id": zone_id,
                "zone_name": zone.get("name"),
                "description": zone.get("intrusion_description", "Unknown intrusion"),
            })

    unlocked_exterior_doors = []
    for door_id, door in doors.items():
        if not door.get("locked", True) and door.get("door_type") == "exterior":
            unlocked_exterior_doors.append({
                "door_id": door_id,
                "name": door.get("name"),
            })

    if unlocked_exterior_doors and not intrusion_detected:
        pass

    return {
        "intrusion_detected": intrusion_detected,
        "intrusion_zones": intrusion_zones,
        "intrusion_details": intrusion_details,
        "unlocked_exterior_doors": unlocked_exterior_doors,
        "requires_immediate_action": intrusion_detected or len(unlocked_exterior_doors) > 0,
    }
