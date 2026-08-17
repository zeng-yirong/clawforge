from __future__ import annotations

from copy import deepcopy
from typing import Any


def create_alert(
    session: dict[str, Any],
    alert_type: str,
    severity: str,
    title: str,
    description: str,
    sensor_id: str | None = None,
    location_id: str | None = None,
    linked_anomaly_id: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    alerts = session.setdefault("alerts", [])
    alert_id = f"alert_{len(alerts) + 1:04d}"
    timestamp = session.get("meta", {}).get("current_time")
    
    alert = {
        "alert_id": alert_id,
        "alert_type": alert_type,
        "severity": severity,
        "title": title,
        "description": description,
        "sensor_id": sensor_id,
        "location_id": location_id,
        "linked_anomaly_id": linked_anomaly_id,
        "status": "active",
        "created_at": timestamp,
        "action_index": action_index,
    }
    alerts.append(alert)
    
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


def get_active_alerts(
    session: dict[str, Any],
    severity: str | None = None,
    alert_type: str | None = None,
    action_index: int | None = None,
) -> list[dict[str, Any]]:
    alerts = session.get("alerts", [])
    active_alerts = [a for a in alerts if a.get("status") == "active"]
    
    if severity:
        active_alerts = [a for a in active_alerts if a.get("severity") == severity]
    if alert_type:
        active_alerts = [a for a in active_alerts if a.get("alert_type") == alert_type]
    
    return deepcopy(active_alerts)


def list_alerts(
    session: dict[str, Any],
    status: str | None = None,
    severity: str | None = None,
    alert_type: str | None = None,
    limit: int | None = None,
    action_index: int | None = None,
) -> list[dict[str, Any]]:
    alerts = session.get("alerts", [])
    
    results = []
    for alert in alerts:
        if status and alert.get("status") != status:
            continue
        if severity and alert.get("severity") != severity:
            continue
        if alert_type and alert.get("alert_type") != alert_type:
            continue
        results.append(deepcopy(alert))
    
    results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    if limit:
        results = results[:limit]
    
    return results
