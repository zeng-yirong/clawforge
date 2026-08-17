from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any


def get_weather_at_time(session: dict[str, Any], timestamp: str) -> dict[str, Any]:
    weather_data = session.get("weather_data", {})
    if timestamp in weather_data:
        return deepcopy(weather_data[timestamp])
    timestamps = sorted(weather_data.keys())
    for ts in timestamps:
        if ts >= timestamp:
            return deepcopy(weather_data[ts])
    if timestamps:
        return deepcopy(weather_data[timestamps[-1]])
    return {}


def get_current_weather(session: dict[str, Any]) -> dict[str, Any]:
    current_time = session.get("meta", {}).get("current_time")
    if current_time:
        return get_weather_at_time(session, current_time)
    weather_data = session.get("weather_data", {})
    if weather_data:
        timestamps = sorted(weather_data.keys())
        return deepcopy(weather_data[timestamps[-1]])
    return {}


def analyze_weather_comfort(
    temperature: float,
    humidity: float,
) -> dict[str, Any]:
    comfort_score = 100
    reasons = []

    if temperature < 18:
        comfort_score -= (18 - temperature) * 3
        reasons.append("Temperature too cold")
    elif temperature > 26:
        comfort_score -= (temperature - 26) * 4
        reasons.append("Temperature too hot")

    if humidity < 30:
        comfort_score -= (30 - humidity) * 1.5
        reasons.append("Air too dry")
    elif humidity > 60:
        comfort_score -= (humidity - 60) * 2
        reasons.append("Air too humid")

    return {
        "comfort_score": max(0, comfort_score),
        "comfort_level": _get_comfort_level(comfort_score),
        "reasons": reasons,
    }


def _get_comfort_level(score: float) -> str:
    if score >= 80:
        return "comfortable"
    elif score >= 60:
        return "acceptable"
    elif score >= 40:
        return "uncomfortable"
    else:
        return "very_uncomfortable"


def calculate_recommended_temperature(
    current_temp: float,
    current_humidity: float,
    user_health_priority: str,
) -> dict[str, Any]:
    base_temp = 22.0

    if user_health_priority == "respiratory":
        if current_humidity < 40:
            base_temp = 21.0
        elif current_humidity > 55:
            base_temp = 23.0

    elif user_health_priority == "circulatory":
        if current_temp > 25:
            base_temp = 20.0
        elif current_temp < 20:
            base_temp = 24.0

    elif user_health_priority == "elderly":
        if current_temp > 24:
            base_temp = 21.0
        elif current_temp < 19:
            base_temp = 23.0

    if current_humidity < 35:
        recommended_humidity = 45
    elif current_humidity > 60:
        recommended_humidity = 50
    else:
        recommended_humidity = current_humidity

    return {
        "recommended_temperature": base_temp,
        "recommended_humidity": recommended_humidity,
        "rationale": f"Based on {user_health_priority} health priority",
    }


def get_weather_forecast(
    session: dict[str, Any],
    hours_ahead: int = 24,
) -> list[dict[str, Any]]:
    weather_data = session.get("weather_data", {})
    current_time_str = session.get("meta", {}).get("current_time")

    if not current_time_str:
        return []

    try:
        current_dt = datetime.fromisoformat(current_time_str.replace("Z", "+00:00"))
    except:
        return []

    forecast = []
    for timestamp, data in weather_data.items():
        try:
            ts_dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            hours_diff = (ts_dt - current_dt).total_seconds() / 3600
            if 0 <= hours_diff <= hours_ahead:
                forecast.append({
                    "timestamp": timestamp,
                    "temperature": data.get("temperature"),
                    "humidity": data.get("humidity"),
                    "conditions": data.get("conditions"),
                    "hours_ahead": int(hours_diff),
                })
        except:
            continue

    return sorted(forecast, key=lambda x: x["hours_ahead"])


def check_extreme_weather(
    session: dict[str, Any],
) -> dict[str, Any]:
    current = get_current_weather(session)
    temp = current.get("temperature", 22)
    humidity = current.get("humidity", 50)

    alerts = []

    if temp > 35:
        alerts.append("Extreme heat warning")
    elif temp < 5:
        alerts.append("Extreme cold warning")

    if humidity < 20:
        alerts.append("Very low humidity warning")
    elif humidity > 80:
        alerts.append("High humidity warning")

    return {
        "has_extreme_weather": len(alerts) > 0,
        "alerts": alerts,
        "current_conditions": current,
    }
