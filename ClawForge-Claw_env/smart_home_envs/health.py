from __future__ import annotations

from copy import deepcopy
from typing import Any


def get_user_health_profile(session: dict[str, Any], user_id: str) -> dict[str, Any]:
    health_data = session.get("health_data", {})
    if user_id in health_data:
        return deepcopy(health_data[user_id])
    for user in health_data.values():
        if user.get("user_id") == user_id:
            return deepcopy(user)
    raise KeyError(f"Health profile not found: {user_id}")


def get_user_comfort_preferences(session: dict[str, Any], user_id: str) -> dict[str, Any]:
    profile = get_user_health_profile(session, user_id)
    return {
        "user_id": user_id,
        "name": profile.get("name"),
        "temperature_preference": profile.get("temperature_preference", 22),
        "humidity_preference": profile.get("humidity_preference", 50),
        "health_conditions": profile.get("health_conditions", []),
        "health_priority": profile.get("health_priority", "general"),
    }


def analyze_health_comfort_conflicts(
    session: dict[str, Any],
    user_id: str,
    current_temp: float,
    current_humidity: float,
) -> dict[str, Any]:
    profile = get_user_health_profile(session, user_id)
    health_conditions = profile.get("health_conditions", [])
    health_priority = profile.get("health_priority", "general")

    conflicts = []
    recommendations = []

    if "asthma" in health_conditions or "respiratory" in health_priority:
        if current_humidity < 40:
            conflicts.append("Low humidity may trigger respiratory issues")
            recommendations.append("Increase humidity to 40-50% range")
        if current_humidity > 60:
            conflicts.append("High humidity may promote mold and dust mites")
            recommendations.append("Decrease humidity to below 55%")

    if "heart_disease" in health_conditions or "circulatory" in health_priority:
        if current_temp > 26:
            conflicts.append("High temperature increases heart strain")
            recommendations.append("Lower temperature to 24°C or below")
        if current_temp < 18:
            conflicts.append("Low temperature constricts blood vessels")
            recommendations.append("Raise temperature to 20°C or above")

    if "elderly" in health_conditions:
        if current_temp > 25:
            conflicts.append("Elderly are more susceptible to heat")
            recommendations.append("Keep temperature between 20-24°C")
        if current_temp < 19:
            conflicts.append("Elderly lose body heat faster")
            recommendations.append("Maintain temperature above 21°C")

    if "arthritis" in health_conditions:
        if current_humidity > 60:
            conflicts.append("High humidity worsens joint pain")
            recommendations.append("Keep humidity between 40-50%")
        if current_temp < 20:
            conflicts.append("Cold weather can stiffen joints")
            recommendations.append("Maintain temperature above 22°C")

    has_conflicts = len(conflicts) > 0

    return {
        "user_id": user_id,
        "has_conflicts": has_conflicts,
        "conflicts": conflicts,
        "recommendations": recommendations,
        "health_priority": health_priority,
        "comfort_score": _calculate_comfort_score(conflicts),
    }


def _calculate_comfort_score(conflicts: list[str]) -> int:
    if not conflicts:
        return 100
    return max(0, 100 - len(conflicts) * 20)


def get_health_based_recommendations(
    session: dict[str, Any],
    user_id: str,
    weather_conditions: dict[str, Any],
) -> dict[str, Any]:
    profile = get_user_health_profile(session, user_id)
    health_conditions = profile.get("health_conditions", [])
    health_priority = profile.get("health_priority", "general")

    recommendations = []
    min_temp = 18
    max_temp = 28
    min_humidity = 30
    max_humidity = 65

    if "asthma" in health_conditions or "respiratory" in health_priority:
        min_humidity = max(min_humidity, 40)
        max_humidity = min(max_humidity, 55)
        recommendations.append({
            "category": "respiratory",
            "recommendation": "Maintain humidity between 40-55% for respiratory health",
            "priority": "high",
        })

    if "heart_disease" in health_conditions or "circulatory" in health_priority:
        max_temp = min(max_temp, 25)
        min_temp = max(min_temp, 20)
        recommendations.append({
            "category": "circulatory",
            "recommendation": "Keep temperature between 20-25°C to reduce heart strain",
            "priority": "high",
        })

    if "elderly" in health_conditions:
        recommendations.append({
            "category": "elderly",
            "recommendation": "Elderly users should avoid temperature extremes",
            "priority": "medium",
        })

    if "arthritis" in health_conditions:
        recommendations.append({
            "category": "arthritis",
            "recommendation": "Keep humidity below 55% and temperature stable to reduce joint pain",
            "priority": "medium",
        })

    return {
        "user_id": user_id,
        "temperature_range": {"min": min_temp, "max": max_temp},
        "humidity_range": {"min": min_humidity, "max": max_humidity},
        "recommendations": recommendations,
    }


def check_health_alerts(
    session: dict[str, Any],
    user_id: str,
    current_temp: float,
    current_humidity: float,
) -> dict[str, Any]:
    profile = get_user_health_profile(session, user_id)
    health_conditions = profile.get("health_conditions", [])

    alerts = []

    if "asthma" in health_conditions:
        if current_humidity < 30:
            alerts.append({"level": "high", "message": "Humidity critically low - risk of asthma attack"})
        if current_temp > 30:
            alerts.append({"level": "high", "message": "Temperature too high - may trigger asthma symptoms"})

    if "heart_disease" in health_conditions:
        if current_temp > 28:
            alerts.append({"level": "critical", "message": "Temperature dangerous for heart disease patients"})
        if current_temp < 16:
            alerts.append({"level": "high", "message": "Cold temperature increases cardiovascular risk"})

    return {
        "user_id": user_id,
        "has_alerts": len(alerts) > 0,
        "alerts": alerts,
    }


def get_all_user_comfort_zones(session: dict[str, Any]) -> dict[str, Any]:
    health_data = session.get("health_data", {})
    comfort_zones = {}

    for user_id, profile in health_data.items():
        uid = profile.get("user_id", user_id)
        comfort_zones[uid] = {
            "user_id": uid,
            "name": profile.get("name"),
            "temperature_range": [
                profile.get("temperature_preference", 22) - 2,
                profile.get("temperature_preference", 22) + 2,
            ],
            "humidity_range": [
                profile.get("humidity_preference", 50) - 10,
                profile.get("humidity_preference", 50) + 10,
            ],
        }

    return comfort_zones
