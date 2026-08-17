from __future__ import annotations

from typing import Any


def query_traffic(query_type: str | None = None) -> dict[str, Any]:
    if query_type == "congestion":
        return {
            "status": "success",
            "data": {
                "congestion_level": "moderate",
                "average_speed_kmh": 35,
                "incidents": [],
            },
        }
    elif query_type == "eta":
        return {
            "status": "success",
            "data": {
                "current_eta_minutes": 25,
                "typical_eta_minutes": 20,
                "delay_minutes": 5,
            },
        }
    elif query_type == "distance":
        return {
            "status": "success",
            "data": {
                "total_distance_km": 15.5,
                "remaining_distance_km": 12.3,
                "traversed_distance_km": 3.2,
            },
        }
    else:
        return {
            "status": "success",
            "data": {
                "traffic_condition": "moderate",
                "congestion_level": "moderate",
                "average_speed_kmh": 35,
                "incidents": [],
                "current_eta_minutes": 25,
                "delay_minutes": 5,
            },
        }


def get_traffic_status() -> dict[str, Any]:
    return {
        "status": "success",
        "data": {
            "traffic_condition": "moderate",
            "description": "Current traffic is moderate with some delays expected",
            "recommendation": "Consider alternative routes if time is critical",
        },
    }
