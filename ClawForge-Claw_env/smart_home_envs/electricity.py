from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any


def get_electricity_rate(session: dict[str, Any], timestamp: str | None = None) -> dict[str, Any]:
    rates = session.get("electricity_rates", {})
    if timestamp is None:
        timestamp = session.get("meta", {}).get("current_time")

    if timestamp in rates:
        return deepcopy(rates[timestamp])

    if timestamp is None:
        return {"period": "unknown", "rate_per_kwh": 0.12, "label": "standard"}

    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        hour = dt.hour
    except:
        return {"period": "unknown", "rate_per_kwh": 0.12, "label": "standard"}

    if 0 <= hour < 7:
        period = "off_peak"
    elif 7 <= hour < 11:
        period = "mid_peak"
    elif 11 <= hour < 17:
        period = "peak"
    elif 17 <= hour < 21:
        period = "high_peak"
    else:
        period = "mid_peak"

    rate_config = {
        "off_peak": {"rate_per_kwh": 0.08, "label": "Off-Peak", "period": "off_peak"},
        "mid_peak": {"rate_per_kwh": 0.12, "label": "Mid-Peak", "period": "mid_peak"},
        "peak": {"rate_per_kwh": 0.18, "label": "Peak", "period": "peak"},
        "high_peak": {"rate_per_kwh": 0.22, "label": "High-Peak", "period": "high_peak"},
    }

    return deepcopy(rate_config.get(period, rate_config["mid_peak"]))


def calculate_device_energy_cost(
    power_watts: float,
    hours: float,
    rate_per_kwh: float,
) -> dict[str, Any]:
    energy_kwh = (power_watts / 1000) * hours
    cost = energy_kwh * rate_per_kwh

    return {
        "power_watts": power_watts,
        "hours": hours,
        "energy_kwh": round(energy_kwh, 3),
        "rate_per_kwh": rate_per_kwh,
        "cost": round(cost, 4),
    }


def get_optimal_operation_window(
    session: dict[str, Any],
    duration_hours: float,
    preferred_start: str | None = None,
) -> dict[str, Any]:
    current_time = session.get("meta", {}).get("current_time")
    rates = session.get("electricity_rates", {})

    if not current_time:
        return {"optimal_start": None, "estimated_cost": 0, "period": "unknown"}

    try:
        current_dt = datetime.fromisoformat(current_time.replace("Z", "+00:00"))
    except:
        return {"optimal_start": None, "estimated_cost": 0, "period": "unknown"}

    windows = []
    for test_hour in range(24):
        test_dt = current_dt.replace(hour=test_hour, minute=0, second=0)
        if test_dt < current_dt:
            continue

        rate_info = get_electricity_rate(session, test_dt.isoformat())
        rate = rate_info.get("rate_per_kwh", 0.12)

        power_watts = 1500
        cost = (power_watts / 1000) * duration_hours * rate

        windows.append({
            "start_hour": test_hour,
            "rate": rate,
            "estimated_cost": round(cost, 4),
            "period": rate_info.get("label", "standard"),
        })

    if not windows:
        return {"optimal_start": None, "estimated_cost": 0, "period": "unknown"}

    windows.sort(key=lambda x: x["estimated_cost"])
    best = windows[0]

    return {
        "optimal_start": f"{best['start_hour']:02d}:00",
        "estimated_cost": best["estimated_cost"],
        "period": best["period"],
        "alternative_windows": windows[:3],
    }


def calculate_total_energy_cost(
    session: dict[str, Any],
    device_operations: list[dict[str, Any]],
) -> dict[str, Any]:
    total_cost = 0.0
    total_energy = 0.0
    by_period = {}

    for op in device_operations:
        power_watts = op.get("power_watts", 0)
        hours = op.get("hours", 0)
        timestamp = op.get("timestamp")

        rate_info = get_electricity_rate(session, timestamp)
        rate = rate_info.get("rate_per_kwh", 0.12)
        period = rate_info.get("label", "unknown")

        energy_kwh = (power_watts / 1000) * hours
        cost = energy_kwh * rate

        total_cost += cost
        total_energy += energy_kwh

        if period not in by_period:
            by_period[period] = {"cost": 0, "energy_kwh": 0}
        by_period[period]["cost"] += cost
        by_period[period]["energy_kwh"] += energy_kwh

    return {
        "total_cost": round(total_cost, 4),
        "total_energy_kwh": round(total_energy, 3),
        "by_period": {k: {"cost": round(v["cost"], 4), "energy_kwh": round(v["energy_kwh"], 3)} for k, v in by_period.items()},
    }


def get_daily_rate_schedule(session: dict[str, Any]) -> list[dict[str, Any]]:
    current_time = session.get("meta", {}).get("current_time")

    if not current_time:
        return []

    try:
        base_dt = datetime.fromisoformat(current_time.replace("Z", "+00:00"))
        base_dt = base_dt.replace(hour=0, minute=0, second=0)
    except:
        return []

    schedule = []
    for hour in range(24):
        dt = base_dt.replace(hour=hour)
        rate_info = get_electricity_rate(session, dt.isoformat())
        schedule.append({
            "hour": hour,
            "period": rate_info.get("period", "mid_peak"),
            "label": rate_info.get("label", "Standard"),
            "rate_per_kwh": rate_info.get("rate_per_kwh", 0.12),
        })

    return schedule


def check_cost_saving_opportunity(
    session: dict[str, Any],
    device_type: str,
    current_setting: dict[str, Any],
) -> dict[str, Any]:
    opportunities = []

    current_time = session.get("meta", {}).get("current_time")
    rate_info = get_electricity_rate(session, current_time)
    current_period = rate_info.get("period", "mid_peak")
    current_rate = rate_info.get("rate_per_kwh", 0.12)

    if current_period in ["peak", "high_peak"]:
        opportunities.append({
            "type": "shift_operation",
            "message": f"Current rate is {current_period} (${current_rate}/kWh). Consider shifting operation to off-peak hours.",
            "potential_savings_percent": 50 if current_period == "high_peak" else 30,
        })

    if device_type == "air_conditioner":
        if current_setting.get("temperature", 22) < 24:
            opportunities.append({
                "type": "temperature_adjustment",
                "message": "Room temperature is below 24°C. Raising to 24°C could save energy.",
                "potential_savings_percent": 15,
            })

    elif device_type == "humidifier":
        if current_setting.get("humidity_level", 50) > 55:
            opportunities.append({
                "type": "humidity_adjustment",
                "message": "Humidity is above 55%. Reducing could save energy.",
                "potential_savings_percent": 10,
            })

    return {
        "has_opportunities": len(opportunities) > 0,
        "opportunities": opportunities,
        "current_period": current_period,
        "current_rate": current_rate,
    }
