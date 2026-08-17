from __future__ import annotations

from typing import Any


def plan_charging(
    current_charge_percent: float,
    target_charge_percent: float,
    max_stops: int = 3,
    repo: Any | None = None,
) -> dict[str, Any]:
    if target_charge_percent <= current_charge_percent:
        return {
            "status": "error",
            "message": f"Target charge ({target_charge_percent}%) must be greater than current charge ({current_charge_percent}%)",
        }

    if target_charge_percent > 100:
        target_charge_percent = 100.0

    charge_needed = target_charge_percent - current_charge_percent
    
    charging_stations = []
    if repo:
        charging_pois = repo.get_pois(category="charging")
        for poi in charging_pois[:max_stops]:
            charging_stations.append({
                "poi_id": poi.get("poi_id"),
                "name": poi.get("name"),
                "lat": poi.get("lat"),
                "lon": poi.get("lon"),
                "address": poi.get("address"),
                "charge_rate_kw": poi.get("charge_rate_kw", 60),
            })

    est_time_minutes = int(charge_needed * 0.5)

    return {
        "status": "success",
        "message": f"Charging plan: need {charge_needed}% charge, estimated {est_time_minutes} minutes",
        "data": {
            "current_charge_percent": current_charge_percent,
            "target_charge_percent": target_charge_percent,
            "charge_needed_percent": charge_needed,
            "estimated_charging_time_minutes": est_time_minutes,
            "recommended_stops": charging_stations,
        },
    }


def check_range_sufficiency(
    current_charge_percent: float,
    battery_capacity_kwh: float,
    distance_km: float,
    energy_consumption_kwh_per_100km: float = 18.5,
) -> dict[str, Any]:
    available_energy_kwh = (current_charge_percent / 100.0) * battery_capacity_kwh
    estimated_consumption_kwh = (distance_km / 100.0) * energy_consumption_kwh_per_100km
    
    sufficient = available_energy_kwh >= estimated_consumption_kwh
    remaining_energy_kwh = available_energy_kwh - estimated_consumption_kwh
    remaining_range_km = (remaining_energy_kwh / energy_consumption_kwh_per_100km) * 100.0 if sufficient else 0
    
    return {
        "status": "success",
        "data": {
            "sufficient": sufficient,
            "available_energy_kwh": round(available_energy_kwh, 1),
            "estimated_consumption_kwh": round(estimated_consumption_kwh, 1),
            "remaining_energy_kwh": round(remaining_energy_kwh, 1),
            "remaining_range_km": round(remaining_range_km, 1),
            "message": "Range is sufficient" if sufficient else "Range may not be sufficient, consider charging",
        },
    }
