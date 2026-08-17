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
    linked_evidence_ids: list[str] | None = None,
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
        "linked_evidence_ids": linked_evidence_ids or [],
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


def get_notification(session: dict[str, Any], notification_id: str) -> dict[str, Any]:
    notifications = session.get("notifications", [])
    for notif in notifications:
        if notif.get("notification_id") == notification_id:
            return deepcopy(notif)
    return {"error": f"Notification {notification_id} not found"}


def list_notifications(
    session: dict[str, Any],
    query: str = "",
    notification_type: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    notifications = session.get("notifications", [])
    results = []

    for notif in notifications:
        if query:
            if query.lower() not in notif.get("subject", "").lower() and query.lower() not in notif.get("body", "").lower():
                continue

        if notification_type and notif.get("notification_type") != notification_type:
            continue

        if status and notif.get("status") != status:
            continue

        if priority and notif.get("priority") != priority:
            continue

        results.append(deepcopy(notif))

    results.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    if limit:
        results = results[:limit]

    return results


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


def cancel_notification(
    session: dict[str, Any],
    notification_id: str,
    cancellation_reason: str,
    action_index: int | None = None,
) -> dict[str, Any]:
    notifications = session.get("notifications", [])
    for notif in notifications:
        if notif.get("notification_id") == notification_id:
            notif["status"] = "cancelled"
            notif["cancellation_reason"] = cancellation_reason
            notif["cancelled_at"] = session.get("meta", {}).get("current_time")
            notif["action_index"] = action_index

            action = {
                "action": "cancel_notification",
                "notification_id": notification_id,
                "cancellation_reason": cancellation_reason,
                "action_index": action_index,
                "timestamp": session.get("meta", {}).get("current_time"),
            }
            session.setdefault("actions", []).append(action)

            return deepcopy(notif)

    return {"error": f"Notification {notification_id} not found"}


def compose_intrusion_notification(
    session: dict[str, Any],
    recipient_name: str,
    recipient_contact: str,
    alert_id: str,
    action_index: int | None = None,
) -> dict[str, Any]:
    alerts = session.get("alerts", [])
    alert = None
    for a in alerts:
        if a.get("alert_id") == alert_id:
            alert = a
            break

    if not alert:
        return {"error": f"Alert {alert_id} not found"}

    subject = f"[安全告警] {alert.get('alert_type', '入侵检测')} - {alert.get('zone_id', '未知区域')}"
    body = f"""安全告警通知

检测到以下安全事件:

类型: {alert.get('alert_type', '入侵检测')}
区域: {alert.get('zone_id', '未知')}
严重程度: {alert.get('severity', 'medium')}
描述: {alert.get('description', '检测到未授权入侵')}

请立即采取适当的安全措施。

此为系统自动发送的安全告警通知。"""

    linked_evidence = [ev.get("evidence_id") for ev in session.get("evidence", []) if ev.get("linked_alert_ids") and alert_id in ev.get("linked_alert_ids", [])]

    return create_notification(
        session,
        notification_type="intrusion_alert",
        recipient_name=recipient_name,
        recipient_contact=recipient_contact,
        subject=subject,
        body=body,
        priority=alert.get("severity", "medium"),
        linked_alert_ids=[alert_id],
        linked_evidence_ids=linked_evidence,
        action_index=action_index,
    )


def get_notification_stats(session: dict[str, Any]) -> dict[str, Any]:
    notifications = session.get("notifications", [])

    total = len(notifications)
    draft = sum(1 for n in notifications if n.get("status") == "draft")
    sent = sum(1 for n in notifications if n.get("status") == "sent")
    cancelled = sum(1 for n in notifications if n.get("status") == "cancelled")

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
        "cancelled": cancelled,
        "by_priority": by_priority,
        "by_type": by_type,
    }
