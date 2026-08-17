from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any


def check_anomalies(
    session: dict[str, Any],
    sensor_id: str | None = None,
    severity: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    sensors = session.get("sensors", {})
    sensor_readings = session.get("sensor_readings", {})
    current_time = session.get("meta", {}).get("current_time")
    
    anomalies = session.get("anomalies", [])
    if sensor_id:
        anomalies = [a for a in anomalies if a.get("sensor_id") == sensor_id]
    if severity:
        anomalies = [a for a in anomalies if a.get("severity") == severity]
    
    active_anomalies = [a for a in anomalies if a.get("status") == "active"]
    
    return {
        "total_anomalies": len(anomalies),
        "active_anomalies": len(active_anomalies),
        "anomalies": deepcopy(active_anomalies),
    }


def detect_anomaly(
    session: dict[str, Any],
    sensor_id: str,
    value: float,
    timestamp: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    if timestamp is None:
        timestamp = session.get("meta", {}).get("current_time")
    
    sensors = session.get("sensors", {})
    if sensor_id not in sensors:
        return {"error": f"Sensor {sensor_id} not found"}
    
    sensor_info = sensors[sensor_id]
    threshold_low = sensor_info.get("threshold_low")
    threshold_high = sensor_info.get("threshold_high")
    
    is_anomaly = False
    anomaly_type = None
    severity = "low"
    
    if threshold_low is not None and value < threshold_low:
        is_anomaly = True
        anomaly_type = "below_threshold"
        deviation = threshold_low - value
        if deviation > threshold_low * 0.2:
            severity = "high"
        elif deviation > threshold_low * 0.1:
            severity = "medium"
    
    if threshold_high is not None and value > threshold_high:
        is_anomaly = True
        anomaly_type = "above_threshold"
        deviation = value - threshold_high
        if deviation > threshold_high * 0.2:
            severity = "high"
        elif deviation > threshold_high * 0.1:
            severity = "medium"
    
    if is_anomaly:
        anomalies = session.setdefault("anomalies", [])
        anomaly_id = f"anomaly_{len(anomalies) + 1:04d}"
        
        anomaly = {
            "anomaly_id": anomaly_id,
            "sensor_id": sensor_id,
            "sensor_type": sensor_info.get("sensor_type"),
            "location_id": sensor_info.get("location_id"),
            "value": value,
            "threshold_low": threshold_low,
            "threshold_high": threshold_high,
            "anomaly_type": anomaly_type,
            "severity": severity,
            "status": "active",
            "detected_at": timestamp,
            "action_index": action_index,
        }
        anomalies.append(anomaly)
        
        action = {
            "action": "detect_anomaly",
            "anomaly_id": anomaly_id,
            "sensor_id": sensor_id,
            "anomaly_type": anomaly_type,
            "severity": severity,
            "action_index": action_index,
            "timestamp": timestamp,
        }
        session.setdefault("actions", []).append(action)
        
        return {
            "success": True,
            "anomaly_detected": True,
            "anomaly_id": anomaly_id,
            "anomaly_type": anomaly_type,
            "severity": severity,
        }
    
    return {
        "success": True,
        "anomaly_detected": False,
        "sensor_id": sensor_id,
        "value": value,
    }


def acknowledge_anomaly(
    session: dict[str, Any],
    anomaly_id: str,
    action_index: int | None = None,
) -> dict[str, Any]:
    anomalies = session.get("anomalies", [])
    for anomaly in anomalies:
        if anomaly.get("anomaly_id") == anomaly_id:
            anomaly["status"] = "acknowledged"
            anomaly["acknowledged_at"] = session.get("meta", {}).get("current_time")
            anomaly["action_index"] = action_index
            
            action = {
                "action": "acknowledge_anomaly",
                "anomaly_id": anomaly_id,
                "action_index": action_index,
                "timestamp": session.get("meta", {}).get("current_time"),
            }
            session.setdefault("actions", []).append(action)
            
            return deepcopy(anomaly)
    
    return {"error": f"Anomaly {anomaly_id} not found"}


def resolve_anomaly(
    session: dict[str, Any],
    anomaly_id: str,
    resolution: str,
    action_index: int | None = None,
) -> dict[str, Any]:
    anomalies = session.get("anomalies", [])
    for anomaly in anomalies:
        if anomaly.get("anomaly_id") == anomaly_id:
            anomaly["status"] = "resolved"
            anomaly["resolution"] = resolution
            anomaly["resolved_at"] = session.get("meta", {}).get("current_time")
            anomaly["action_index"] = action_index
            
            action = {
                "action": "resolve_anomaly",
                "anomaly_id": anomaly_id,
                "resolution": resolution,
                "action_index": action_index,
                "timestamp": session.get("meta", {}).get("current_time"),
            }
            session.setdefault("actions", []).append(action)
            
            return deepcopy(anomaly)
    
    return {"error": f"Anomaly {anomaly_id} not found"}


def get_monitoring_summary(
    session: dict[str, Any],
    action_index: int | None = None,
) -> dict[str, Any]:
    sensors = session.get("sensors", {})
    anomalies = session.get("anomalies", [])
    sensor_readings = session.get("sensor_readings", {})
    
    active_anomalies = [a for a in anomalies if a.get("status") == "active"]
    acknowledged_anomalies = [a for a in anomalies if a.get("status") == "acknowledged"]
    
    by_type = {}
    for sensor_id, sensor_info in sensors.items():
        sensor_type = sensor_info.get("sensor_type", "unknown")
        by_type[sensor_type] = by_type.get(sensor_type, 0) + 1
    
    by_severity = {"low": 0, "medium": 0, "high": 0}
    for anomaly in active_anomalies:
        severity = anomaly.get("severity", "low")
        by_severity[severity] = by_severity.get(severity, 0) + 1
    
    return {
        "total_sensors": len(sensors),
        "sensors_by_type": by_type,
        "total_anomalies": len(anomalies),
        "active_anomalies": len(active_anomalies),
        "acknowledged_anomalies": len(acknowledged_anomalies),
        "anomalies_by_severity": by_severity,
        "total_readings": sum(len(r) for r in sensor_readings.values()),
    }
