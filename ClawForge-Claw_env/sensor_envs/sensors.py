from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any


def read_sensor_data(
    session: dict[str, Any],
    sensor_id: str,
    timestamp: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    sensor_readings = session.get("sensor_readings", {})
    
    if timestamp is None:
        timestamp = session.get("meta", {}).get("current_time")
    
    if sensor_id in sensor_readings:
        readings = sensor_readings[sensor_id]
        if timestamp in readings:
            return deepcopy(readings[timestamp])
        
        timestamps = sorted(readings.keys())
        for ts in timestamps:
            if ts >= timestamp:
                return deepcopy(readings[ts])
        if timestamps:
            return deepcopy(readings[timestamps[-1]])
    
    sensors = session.get("sensors", {})
    if sensor_id in sensors:
        sensor_info = sensors[sensor_id]
        return {
            "sensor_id": sensor_id,
            "sensor_type": sensor_info.get("sensor_type"),
            "value": sensor_info.get("last_value"),
            "unit": sensor_info.get("unit"),
            "timestamp": timestamp,
            "status": "unknown"
        }
    
    return {"error": f"Sensor {sensor_id} not found"}


def read_all_sensors_current(
    session: dict[str, Any],
    sensor_type: str | None = None,
    location_id: str | None = None,
    action_index: int | None = None,
) -> list[dict[str, Any]]:
    sensors = session.get("sensors", {})
    sensor_readings = session.get("sensor_readings", {})
    current_time = session.get("meta", {}).get("current_time")
    
    results = []
    for sensor_id, sensor_info in sensors.items():
        if sensor_type and sensor_info.get("sensor_type") != sensor_type:
            continue
        if location_id and sensor_info.get("location_id") != location_id:
            continue
        
        value = sensor_info.get("last_value")
        if sensor_id in sensor_readings:
            readings = sensor_readings[sensor_id]
            if current_time in readings:
                value = readings[current_time].get("value")
            else:
                timestamps = sorted(readings.keys())
                for ts in timestamps:
                    if ts <= current_time:
                        value = readings[ts].get("value")
        
        results.append({
            "sensor_id": sensor_id,
            "sensor_name": sensor_info.get("sensor_name"),
            "sensor_type": sensor_info.get("sensor_type"),
            "location_id": sensor_info.get("location_id"),
            "value": value,
            "unit": sensor_info.get("unit"),
            "timestamp": current_time,
        })
    
    return results


def get_sensor_thresholds(
    session: dict[str, Any],
    sensor_id: str,
    action_index: int | None = None,
) -> dict[str, Any]:
    sensors = session.get("sensors", {})
    if sensor_id not in sensors:
        return {"error": f"Sensor {sensor_id} not found"}
    
    sensor_info = sensors[sensor_id]
    return {
        "sensor_id": sensor_id,
        "sensor_type": sensor_info.get("sensor_type"),
        "min_value": sensor_info.get("min_value"),
        "max_value": sensor_info.get("max_value"),
        "threshold_low": sensor_info.get("threshold_low"),
        "threshold_high": sensor_info.get("threshold_high"),
        "unit": sensor_info.get("unit"),
    }


def set_sensor_threshold(
    session: dict[str, Any],
    sensor_id: str,
    threshold_low: float | None = None,
    threshold_high: float | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    sensors = session.get("sensors", {})
    if sensor_id not in sensors:
        return {"error": f"Sensor {sensor_id} not found"}
    
    if threshold_low is not None:
        sensors[sensor_id]["threshold_low"] = threshold_low
    if threshold_high is not None:
        sensors[sensor_id]["threshold_high"] = threshold_high
    
    action = {
        "action": "set_sensor_threshold",
        "sensor_id": sensor_id,
        "threshold_low": threshold_low,
        "threshold_high": threshold_high,
        "action_index": action_index,
        "timestamp": session.get("meta", {}).get("current_time"),
    }
    session.setdefault("actions", []).append(action)
    
    return {
        "success": True,
        "sensor_id": sensor_id,
        "threshold_low": sensors[sensor_id].get("threshold_low"),
        "threshold_high": sensors[sensor_id].get("threshold_high"),
    }


def get_sensors_by_type(
    session: dict[str, Any],
    sensor_type: str,
    action_index: int | None = None,
) -> list[dict[str, Any]]:
    sensors = session.get("sensors", {})
    results = []
    for sensor_id, sensor_info in sensors.items():
        if sensor_info.get("sensor_type") == sensor_type:
            results.append({
                "sensor_id": sensor_id,
                "sensor_name": sensor_info.get("sensor_name"),
                "location_id": sensor_info.get("location_id"),
                "unit": sensor_info.get("unit"),
            })
    return results


def get_sensors_by_location(
    session: dict[str, Any],
    location_id: str,
    action_index: int | None = None,
) -> list[dict[str, Any]]:
    sensors = session.get("sensors", {})
    results = []
    for sensor_id, sensor_info in sensors.items():
        if sensor_info.get("location_id") == location_id:
            results.append({
                "sensor_id": sensor_id,
                "sensor_name": sensor_info.get("sensor_name"),
                "sensor_type": sensor_info.get("sensor_type"),
                "unit": sensor_info.get("unit"),
            })
    return results


def get_sensor_stats(
    session: dict[str, Any],
    sensor_id: str,
    start_time: str | None = None,
    end_time: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    sensor_readings = session.get("sensor_readings", {})
    if sensor_id not in sensor_readings:
        return {"error": f"No readings found for sensor {sensor_id}"}
    
    readings = sensor_readings[sensor_id]
    
    if start_time:
        readings = {k: v for k, v in readings.items() if k >= start_time}
    if end_time:
        readings = {k: v for k, v in readings.items() if k <= end_time}
    
    if not readings:
        return {"error": "No readings in time range"}
    
    values = [r.get("value", 0) for r in readings.values() if r.get("value") is not None]
    if not values:
        return {"error": "No valid values in time range"}
    
    return {
        "sensor_id": sensor_id,
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "avg": sum(values) / len(values),
        "start_time": min(readings.keys()),
        "end_time": max(readings.keys()),
    }
