from __future__ import annotations

from typing import Any


class ReportEvaluator:
    def __init__(self, scenario: dict[str, Any]):
        self.scenario = scenario
        self.report_weight = scenario.get("report_weight", 0.4)
        self.anomaly_weight = scenario.get("anomaly_weight", 0.3)
        self.notification_weight = scenario.get("notification_weight", 0.3)

    def evaluate(self, session: dict[str, Any]) -> dict[str, Any]:
        report_score = self._evaluate_report_generation(session)
        anomaly_score = self._evaluate_anomaly_detection(session)
        notification_score = self._evaluate_notifications(session)

        total = (
            report_score * self.report_weight +
            anomaly_score * self.anomaly_weight +
            notification_score * self.notification_weight
        )

        return {
            "total_score": round(total, 2),
            "report_score": round(report_score, 2),
            "anomaly_score": round(anomaly_score, 2),
            "notification_score": round(notification_score, 2),
            "weights": {
                "report": self.report_weight,
                "anomaly": self.anomaly_weight,
                "notification": self.notification_weight,
            },
        }

    def _evaluate_report_generation(self, session: dict[str, Any]) -> float:
        actions = session.get("actions", [])
        report_actions = [a for a in actions if a.get("action", "").startswith("generate_")]
        
        if not report_actions:
            return 0.0
        
        has_hourly = any("hourly" in a.get("action", "") for a in report_actions)
        has_daily = any("daily" in a.get("action", "") for a in report_actions)
        has_monthly = any("monthly" in a.get("action", "") for a in report_actions)
        
        score = 0.0
        if has_hourly:
            score += 0.33
        if has_daily:
            score += 0.33
        if has_monthly:
            score += 0.34
        
        return score

    def _evaluate_anomaly_detection(self, session: dict[str, Any]) -> float:
        anomalies = session.get("anomalies", [])
        if not anomalies:
            return 0.0
        
        resolved = sum(1 for a in anomalies if a.get("status") == "resolved")
        acknowledged = sum(1 for a in anomalies if a.get("status") == "acknowledged")
        active = sum(1 for a in anomalies if a.get("status") == "active")
        
        total = len(anomalies)
        if total == 0:
            return 0.0
        
        response_rate = (resolved + acknowledged) / total
        
        high_severity = sum(1 for a in anomalies if a.get("severity") == "high")
        high_response_rate = 0.0
        if high_severity > 0:
            high_resolved = sum(1 for a in anomalies if a.get("severity") == "high" and a.get("status") in ("resolved", "acknowledged"))
            high_response_rate = high_resolved / high_severity
        
        score = (response_rate * 0.5) + (high_response_rate * 0.5)
        return min(score, 1.0)

    def _evaluate_notifications(self, session: dict[str, Any]) -> float:
        notifications = session.get("notifications", [])
        if not notifications:
            return 0.0
        
        sent = sum(1 for n in notifications if n.get("status") == "sent")
        total = len(notifications)
        
        delivery_rate = sent / total if total > 0 else 0.0
        
        high_priority = [n for n in notifications if n.get("priority") in ("high", "critical")]
        if high_priority:
            high_sent = sum(1 for n in high_priority if n.get("status") == "sent")
            high_delivery = high_sent / len(high_priority)
        else:
            high_delivery = 1.0
        
        score = (delivery_rate * 0.5) + (high_delivery * 0.5)
        return min(score, 1.0)
