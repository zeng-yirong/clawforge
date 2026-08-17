from __future__ import annotations

from copy import deepcopy
from typing import Any


class SmartHomeEvaluator:
    def __init__(self, scenario: dict[str, Any]):
        self.scenario = scenario
        self.comfort_weight = scenario.get("comfort_weight", 0.4)
        self.energy_weight = scenario.get("energy_weight", 0.3)
        self.health_weight = scenario.get("health_weight", 0.3)

    def evaluate(self, session: dict[str, Any]) -> dict[str, Any]:
        comfort_score = self._evaluate_comfort(session)
        energy_score = self._evaluate_energy_efficiency(session)
        health_score = self._evaluate_health_compliance(session)
        action_score = self._evaluate_action_quality(session)

        total = (
            comfort_score * self.comfort_weight +
            energy_score * self.energy_weight +
            health_score * self.health_weight +
            action_score * 0.0
        )

        return {
            "total_score": round(total, 2),
            "comfort_score": round(comfort_score, 2),
            "energy_score": round(energy_score, 2),
            "health_score": round(health_score, 2),
            "action_score": round(action_score, 2),
            "weights": {
                "comfort": self.comfort_weight,
                "energy": self.energy_weight,
                "health": self.health_weight,
            },
        }

    def _evaluate_comfort(self, session: dict[str, Any]) -> float:
        devices = session.get("devices", {})
        score = 50.0

        for device_id, device in devices.items():
            if device.get("type") == "air_conditioner" and device.get("state") == "on":
                temp = device.get("settings", {}).get("temperature", 22)
                if 20 <= temp <= 26:
                    score += 15
                elif 18 <= temp < 20 or 26 < temp <= 28:
                    score += 5

            elif device.get("type") == "humidifier" and device.get("state") == "on":
                humidity = device.get("settings", {}).get("humidity_level", 50)
                if 40 <= humidity <= 60:
                    score += 10
                elif 30 <= humidity < 40 or 60 < humidity <= 70:
                    score += 5

        return min(score, 100)

    def _evaluate_energy_efficiency(self, session: dict[str, Any]) -> float:
        actions = session.get("actions", [])
        off_peak_actions = sum(1 for a in actions if self._is_off_peak_action(a, session))
        total_actions = len(actions)

        if total_actions == 0:
            return 50.0

        timing_score = (off_peak_actions / total_actions) * 50
        optimization_score = self._evaluate_cost_optimization(session)

        return min(timing_score + optimization_score, 100)

    def _is_off_peak_action(self, action: dict[str, Any], session: dict[str, Any]) -> bool:
        from .electricity import get_electricity_rate

        timestamp = action.get("timestamp")
        if not timestamp:
            return False

        rate_info = get_electricity_rate(session, timestamp)
        period = rate_info.get("period", "mid_peak")
        return period in ["off_peak"]

    def _evaluate_cost_optimization(self, session: dict[str, Any]) -> float:
        score = 25.0

        from .electricity import get_electricity_rate

        current_time = session.get("meta", {}).get("current_time")
        if current_time:
            rate_info = get_electricity_rate(session, current_time)
            period = rate_info.get("period", "mid_peak")

            if period == "off_peak":
                score += 25
            elif period == "mid_peak":
                score += 15
            elif period == "peak":
                score += 5
            elif period == "high_peak":
                score += 0

        return score

    def _evaluate_health_compliance(self, session: dict[str, Any]) -> float:
        user_id = self.scenario.get("user_id", "user_001")
        health_profiles = session.get("health_data", {})
        user_health = health_profiles.get(user_id, {})

        score = 50.0

        if user_health.get("respiratory_issues"):
            score += self._evaluate_respiratory_comfort(session)

        if user_health.get("cardiovascular_risk"):
            score += self._evaluate_cardiovascular_comfort(session)

        temperature_alert = session.get("alerts", {}).get("temperature")
        if temperature_alert:
            score -= 20

        humidity_alert = session.get("alerts", {}).get("humidity")
        if humidity_alert:
            score -= 15

        return max(min(score, 100), 0)

    def _evaluate_respiratory_comfort(self, session: dict[str, Any]) -> float:
        devices = session.get("devices", {})
        score = 0

        for device_id, device in devices.items():
            if device.get("type") == "humidifier" and device.get("state") == "on":
                humidity = device.get("settings", {}).get("humidity_level", 50)
                if 45 <= humidity <= 55:
                    score += 25

            if device.get("type") == "air_conditioner" and device.get("state") == "on":
                temp = device.get("settings", {}).get("temperature", 22)
                if 22 <= temp <= 26:
                    score += 15

        return score

    def _evaluate_cardiovascular_comfort(self, session: dict[str, Any]) -> float:
        devices = session.get("devices", {})
        score = 0

        for device_id, device in devices.items():
            if device.get("type") == "air_conditioner" and device.get("state") == "on":
                temp = device.get("settings", {}).get("temperature", 22)
                if 24 <= temp <= 28:
                    score += 25

        return score

    def _evaluate_action_quality(self, session: dict[str, Any]) -> float:
        actions = session.get("actions", [])
        if not actions:
            return 0

        score = 50.0

        for action in actions:
            action_type = action.get("action", "")
            if action_type in ["set_ac", "set_humidifier", "set_smart_plug"]:
                score += 5

        return min(score, 100)


def evaluate_session(
    session: dict[str, Any],
    scenario: dict[str, Any],
) -> dict[str, Any]:
    evaluator = SmartHomeEvaluator(scenario)
    return evaluator.evaluate(session)
