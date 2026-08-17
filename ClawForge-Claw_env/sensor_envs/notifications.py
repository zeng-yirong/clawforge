from __future__ import annotations

from copy import deepcopy
from typing import Any


def create_notification(
    session: dict[str, Any],
    notification_type: str,
    recipient_name: str,
    recipient_contact: str,
    subject: str,
    body: str,
    priority: str = "normal",
    linked_alert_ids: list[str] | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    notifications = session.setdefault("notifications", [])
    notification_id = f"notif_{len(notifications) + 1:04d}"
    timestamp = session.get("meta", {}).get("current_time")
    
    notification = {
        "notification_id": notification_id,
        "notification_type": notification_type,
        "recipient_name": recipient_name,
        "recipient_contact": recipient_contact,
        "subject": subject,
        "body": body,
        "priority": priority,
        "status": "draft",
        "linked_alert_ids": linked_alert_ids or [],
        "created_at": timestamp,
        "action_index": action_index,
    }
    notifications.append(notification)
    
    action = {
        "action": "create_notification",
        "notification_id": notification_id,
        "notification_type": notification_type,
        "action_index": action_index,
        "timestamp": timestamp,
    }
    session.setdefault("actions", []).append(action)
    
    return deepcopy(notification)


def send_notification(
    session: dict[str, Any],
    notification_id: str,
    action_index: int | None = None,
) -> dict[str, Any]:
    notifications = session.get("notifications", [])
    for notif in notifications:
        if notif.get("notification_id") == notification_id:
            notif["status"] = "sent"
            notif["sent_at"] = session.get("meta", {}).get("current_time")
            notif["action_index"] = action_index
            
            action = {
                "action": "send_notification",
                "notification_id": notification_id,
                "action_index": action_index,
                "timestamp": session.get("meta", {}).get("current_time"),
            }
            session.setdefault("actions", []).append(action)
            
            return deepcopy(notif)
    
    return {"error": f"Notification {notification_id} not found"}


def compose_anomaly_alert_notification(
    session: dict[str, Any],
    recipient_name: str,
    recipient_contact: str,
    anomaly_id: str,
    action_index: int | None = None,
) -> dict[str, Any]:
    anomalies = session.get("anomalies", [])
    anomaly = None
    for a in anomalies:
        if a.get("anomaly_id") == anomaly_id:
            anomaly = a
            break
    
    if not anomaly:
        return {"error": f"Anomaly {anomaly_id} not found"}
    
    severity = anomaly.get("severity", "medium")
    priority = "high" if severity == "high" else "normal" if severity == "medium" else "low"
    
    subject = f"[{severity.upper()}] Sensor Anomaly Detected - {anomaly.get('sensor_id')}"
    body = f"""Sensor Anomaly Alert

An anomaly has been detected that requires attention:

Sensor ID: {anomaly.get('sensor_id')}
Sensor Type: {anomaly.get('sensor_type')}
Location: {anomaly.get('location_id')}
Type: {anomaly.get('anomaly_type')}
Severity: {severity}
Value: {anomaly.get('value')}
Threshold Low: {anomaly.get('threshold_low')}
Threshold High: {anomaly.get('threshold_high')}
Detected At: {anomaly.get('detected_at')}

Please take appropriate action to investigate and resolve this anomaly.
"""
    
    return create_notification(
        session,
        notification_type="anomaly_alert",
        recipient_name=recipient_name,
        recipient_contact=recipient_contact,
        subject=subject,
        body=body,
        priority=priority,
        linked_alert_ids=[anomaly_id],
        action_index=action_index,
    )


def list_notifications(
    session: dict[str, Any],
    status: str | None = None,
    notification_type: str | None = None,
    priority: str | None = None,
    limit: int | None = None,
    action_index: int | None = None,
) -> list[dict[str, Any]]:
    notifications = session.get("notifications", [])
    
    results = []
    for notif in notifications:
        if status and notif.get("status") != status:
            continue
        if notification_type and notif.get("notification_type") != notification_type:
            continue
        if priority and notif.get("priority") != priority:
            continue
        results.append(deepcopy(notif))
    
    results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    if limit:
        results = results[:limit]
    
    return results


def get_notification_stats(
    session: dict[str, Any],
    action_index: int | None = None,
) -> dict[str, Any]:
    notifications = session.get("notifications", [])
    
    total = len(notifications)
    draft = sum(1 for n in notifications if n.get("status") == "draft")
    sent = sum(1 for n in notifications if n.get("status") == "sent")
    
    by_priority = {
        "critical": sum(1 for n in notifications if n.get("priority") == "critical"),
        "high": sum(1 for n in notifications if n.get("priority") == "high"),
        "medium": sum(1 for n in notifications if n.get("priority") == "medium"),
        "normal": sum(1 for n in notifications if n.get("priority") == "normal"),
    }
    
    by_type = {}
    for n in notifications:
        ntype = n.get("notification_type", "unknown")
        by_type[ntype] = by_type.get(ntype, 0) + 1
    
    return {
        "total": total,
        "draft": draft,
        "sent": sent,
        "by_priority": by_priority,
        "by_type": by_type,
    }
