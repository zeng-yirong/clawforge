from __future__ import annotations

from typing import Any


class SecurityEvaluator:
    def __init__(self, scenario: dict[str, Any]):
        self.scenario = scenario
        self.response_weight = scenario.get("response_weight", 0.4)
        self.lock_weight = scenario.get("lock_weight", 0.3)
        self.notification_weight = scenario.get("notification_weight", 0.3)

    def evaluate(self, session: dict[str, Any]) -> dict[str, Any]:
        response_score = self._evaluate_response_speed(session)
        lock_score = self._evaluate_lock_actions(session)
        notification_score = self._evaluate_notification_actions(session)
        evidence_score = self._evaluate_evidence_preservation(session)

        total = (
            response_score * self.response_weight +
            lock_score * self.lock_weight +
            notification_score * self.notification_weight +
            evidence_score * 0.0
        )

        return {
            "total_score": round(total, 2),
            "response_score": round(response_score, 2),
            "lock_score": round(lock_score, 2),
            "notification_score": round(notification_score, 2),
            "evidence_score": round(evidence_score, 2),
            "weights": {
                "response": self.response_weight,
                "lock": self.lock_weight,
                "notification": self.notification_weight,
            },
        }

    def _evaluate_response_speed(self, session: dict[str, Any]) -> float:
        actions = session.get("actions", [])
        if not actions:
            return 0

        alert_creation_time = None
        emergency_call_time = None

        for action in actions:
            if action.get("action") == "create_alert":
                alert_creation_time = action.get("action_index")
            if action.get("action") == "dial_emergency":
                emergency_call_time = action.get("action_index")

        if alert_creation_time is None:
            return 0

        if emergency_call_time is not None:
            time_diff = emergency_call_time - alert_creation_time
            if time_diff <= 2:
                return 100
            elif time_diff <= 5:
                return 80
            elif time_diff <= 10:
                return 60
            else:
                return 40

        return 50

    def _evaluate_lock_actions(self, session: dict[str, Any]) -> float:
        doors = session.get("doors", {})
        actions = session.get("actions", [])

        lock_actions = [a for a in actions if a.get("action") in ("lock_door", "lock_all_doors")]
        if not lock_actions:
            return 0

        exterior_doors = [did for did, d in doors.items() if d.get("door_type") == "exterior"]
        locked_exterior = [did for did in exterior_doors if doors[did].get("locked", False)]

        if len(exterior_doors) == 0:
            return 50

        lock_percentage = len(locked_exterior) / len(exterior_doors)
        return min(lock_percentage * 100, 100)

    def _evaluate_notification_actions(self, session: dict[str, Any]) -> float:
        notifications = session.get("notifications", [])
        if not notifications:
            return 0

        sent_notifications = [n for n in notifications if n.get("status") == "sent"]
        if len(sent_notifications) == 0:
            return 0

        high_priority = [n for n in sent_notifications if n.get("priority") in ("critical", "high")]
        if len(high_priority) > 0:
            return 100

        return 70

    def _evaluate_evidence_preservation(self, session: dict[str, Any]) -> float:
        evidence = session.get("evidence", [])
        if not evidence:
            return 0

        verified_evidence = [e for e in evidence if e.get("integrity_verified", False)]
        if len(evidence) == 0:
            return 0

        verification_ratio = len(verified_evidence) / len(evidence)
        return min(verification_ratio * 100, 100)


def evaluate_session(
    session: dict[str, Any],
    scenario: dict[str, Any],
) -> dict[str, Any]:
    evaluator = SecurityEvaluator(scenario)
    return evaluator.evaluate(session)
