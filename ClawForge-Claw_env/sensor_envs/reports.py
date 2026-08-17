from __future__ import annotations

from copy import deepcopy
from typing import Any


def generate_hourly_report(
    session: dict[str, Any],
    location_id: str | None = None,
    sensor_type: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    sensor_readings = session.get("sensor_readings", {})
    sensors = session.get("sensors", {})
    current_time = session.get("meta", {}).get("current_time")
    
    filtered_sensors = {}
    for sensor_id, sensor_info in sensors.items():
        if location_id and sensor_info.get("location_id") != location_id:
            continue
        if sensor_type and sensor_info.get("sensor_type") != sensor_type:
            continue
        filtered_sensors[sensor_id] = sensor_info
    
    hourly_data = {}
    for sensor_id in filtered_sensors:
        if sensor_id not in sensor_readings:
            continue
        for ts, reading in sensor_readings[sensor_id].items():
            hour_key = ts[:13]
            if hour_key not in hourly_data:
                hourly_data[hour_key] = {"count": 0, "values": []}
            hourly_data[hour_key]["count"] += 1
            hourly_data[hour_key]["values"].append(reading.get("value"))
    
    report_entries = []
    for hour, data in sorted(hourly_data.items()):
        values = data["values"]
        report_entries.append({
            "period": hour,
            "reading_count": data["count"],
            "min": min(values) if values else None,
            "max": max(values) if values else None,
            "avg": sum(values) / len(values) if values else None,
        })
    
    action = {
        "action": "generate_hourly_report",
        "report_type": "hourly",
        "location_id": location_id,
        "sensor_type": sensor_type,
        "action_index": action_index,
        "timestamp": current_time,
    }
    session.setdefault("actions", []).append(action)
    
    return {
        "success": True,
        "report_type": "hourly",
        "period_start": min(hourly_data.keys()) if hourly_data else None,
        "period_end": max(hourly_data.keys()) if hourly_data else None,
        "entries_count": len(report_entries),
        "data": report_entries,
    }


def generate_daily_report(
    session: dict[str, Any],
    location_id: str | None = None,
    sensor_type: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    sensor_readings = session.get("sensor_readings", {})
    sensors = session.get("sensors", {})
    current_time = session.get("meta", {}).get("current_time")
    
    filtered_sensors = {}
    for sensor_id, sensor_info in sensors.items():
        if location_id and sensor_info.get("location_id") != location_id:
            continue
        if sensor_type and sensor_info.get("sensor_type") != sensor_type:
            continue
        filtered_sensors[sensor_id] = sensor_info
    
    daily_data = {}
    for sensor_id in filtered_sensors:
        if sensor_id not in sensor_readings:
            continue
        for ts, reading in sensor_readings[sensor_id].items():
            day_key = ts[:10]
            if day_key not in daily_data:
                daily_data[day_key] = {"count": 0, "values": []}
            daily_data[day_key]["count"] += 1
            daily_data[day_key]["values"].append(reading.get("value"))
    
    report_entries = []
    for day, data in sorted(daily_data.items()):
        values = data["values"]
        report_entries.append({
            "period": day,
            "reading_count": data["count"],
            "min": min(values) if values else None,
            "max": max(values) if values else None,
            "avg": sum(values) / len(values) if values else None,
        })
    
    action = {
        "action": "generate_daily_report",
        "report_type": "daily",
        "location_id": location_id,
        "sensor_type": sensor_type,
        "action_index": action_index,
        "timestamp": current_time,
    }
    session.setdefault("actions", []).append(action)
    
    return {
        "success": True,
        "report_type": "daily",
        "period_start": min(daily_data.keys()) if daily_data else None,
        "period_end": max(daily_data.keys()) if daily_data else None,
        "entries_count": len(report_entries),
        "data": report_entries,
    }


def generate_monthly_report(
    session: dict[str, Any],
    location_id: str | None = None,
    sensor_type: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    sensor_readings = session.get("sensor_readings", {})
    sensors = session.get("sensors", {})
    current_time = session.get("meta", {}).get("current_time")
    
    filtered_sensors = {}
    for sensor_id, sensor_info in sensors.items():
        if location_id and sensor_info.get("location_id") != location_id:
            continue
        if sensor_type and sensor_info.get("sensor_type") != sensor_type:
            continue
        filtered_sensors[sensor_id] = sensor_info
    
    monthly_data = {}
    for sensor_id in filtered_sensors:
        if sensor_id not in sensor_readings:
            continue
        for ts, reading in sensor_readings[sensor_id].items():
            month_key = ts[:7]
            if month_key not in monthly_data:
                monthly_data[month_key] = {"count": 0, "values": []}
            monthly_data[month_key]["count"] += 1
            monthly_data[month_key]["values"].append(reading.get("value"))
    
    report_entries = []
    for month, data in sorted(monthly_data.items()):
        values = data["values"]
        report_entries.append({
            "period": month,
            "reading_count": data["count"],
            "min": min(values) if values else None,
            "max": max(values) if values else None,
            "avg": sum(values) / len(values) if values else None,
        })
    
    action = {
        "action": "generate_monthly_report",
        "report_type": "monthly",
        "location_id": location_id,
        "sensor_type": sensor_type,
        "action_index": action_index,
        "timestamp": current_time,
    }
    session.setdefault("actions", []).append(action)
    
    return {
        "success": True,
        "report_type": "monthly",
        "period_start": min(monthly_data.keys()) if monthly_data else None,
        "period_end": max(monthly_data.keys()) if monthly_data else None,
        "entries_count": len(report_entries),
        "data": report_entries,
    }


def generate_anomaly_report(
    session: dict[str, Any],
    start_time: str | None = None,
    end_time: str | None = None,
    severity: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    anomalies = session.get("anomalies", [])
    current_time = session.get("meta", {}).get("current_time")
    
    filtered_anomalies = []
    for anomaly in anomalies:
        detected_at = anomaly.get("detected_at", "")
        if start_time and detected_at < start_time:
            continue
        if end_time and detected_at > end_time:
            continue
        if severity and anomaly.get("severity") != severity:
            continue
        filtered_anomalies.append(anomaly)
    
    by_severity = {"low": 0, "medium": 0, "high": 0}
    by_type = {}
    by_sensor = {}
    
    for anomaly in filtered_anomalies:
        sev = anomaly.get("severity", "low")
        by_severity[sev] = by_severity.get(sev, 0) + 1
        anomaly_type = anomaly.get("anomaly_type", "unknown")
        by_type[anomaly_type] = by_type.get(anomaly_type, 0) + 1
        sensor_id = anomaly.get("sensor_id", "unknown")
        by_sensor[sensor_id] = by_sensor.get(sensor_id, 0) + 1
    
    action = {
        "action": "generate_anomaly_report",
        "report_type": "anomaly",
        "start_time": start_time,
        "end_time": end_time,
        "action_index": action_index,
        "timestamp": current_time,
    }
    session.setdefault("actions", []).append(action)
    
    return {
        "success": True,
        "report_type": "anomaly",
        "total_anomalies": len(filtered_anomalies),
        "anomalies_by_severity": by_severity,
        "anomalies_by_type": by_type,
        "anomalies_by_sensor": by_sensor,
        "anomalies": deepcopy(filtered_anomalies[:50]),
    }


def generate_energy_report(
    session: dict[str, Any],
    location_id: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    sensor_readings = session.get("sensor_readings", {})
    sensors = session.get("sensors", {})
    current_time = session.get("meta", {}).get("current_time")
    
    energy_sensors = {}
    for sensor_id, sensor_info in sensors.items():
        if sensor_info.get("sensor_type") == "energy":
            if location_id and sensor_info.get("location_id") != location_id:
                continue
            energy_sensors[sensor_id] = sensor_info
    
    total_energy = 0.0
    period_data = {}
    
    for sensor_id in energy_sensors:
        if sensor_id not in sensor_readings:
            continue
        for ts, reading in sensor_readings[sensor_id].items():
            if start_time and ts < start_time:
                continue
            if end_time and ts > end_time:
                continue
            value = reading.get("value", 0)
            total_energy += value
            day_key = ts[:10]
            if day_key not in period_data:
                period_data[day_key] = 0.0
            period_data[day_key] += value
    
    daily_breakdown = [
        {"date": day, "energy": round(val, 3)}
        for day, val in sorted(period_data.items())
    ]
    
    action = {
        "action": "generate_energy_report",
        "report_type": "energy",
        "location_id": location_id,
        "action_index": action_index,
        "timestamp": current_time,
    }
    session.setdefault("actions", []).append(action)
    
    return {
        "success": True,
        "report_type": "energy",
        "total_energy": round(total_energy, 3),
        "unit": "kWh",
        "days_count": len(daily_breakdown),
        "daily_breakdown": daily_breakdown,
    }
