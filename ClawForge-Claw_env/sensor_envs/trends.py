from __future__ import annotations

from copy import deepcopy
from typing import Any


def analyze_trend(
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
    
    sorted_ts = sorted(readings.keys())
    values = [readings[ts].get("value", 0) for ts in sorted_ts]
    
    n = len(values)
    if n < 2:
        return {
            "sensor_id": sensor_id,
            "trend": "insufficient_data",
            "data_points": n,
        }
    
    x_mean = sum(range(n)) / n
    y_mean = sum(values) / n
    
    numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    
    slope = numerator / denominator if denominator != 0 else 0
    
    if slope > 0.1:
        trend_direction = "increasing"
    elif slope < -0.1:
        trend_direction = "decreasing"
    else:
        trend_direction = "stable"
    
    y_intercept = y_mean - slope * x_mean
    
    predicted_next = slope * n + y_intercept
    
    return {
        "sensor_id": sensor_id,
        "trend": trend_direction,
        "slope": round(slope, 4),
        "data_points": n,
        "min_value": min(values),
        "max_value": max(values),
        "avg_value": round(y_mean, 2),
        "predicted_next_value": round(predicted_next, 2),
        "period_start": sorted_ts[0],
        "period_end": sorted_ts[-1],
    }


def calculate_moving_average(
    session: dict[str, Any],
    sensor_id: str,
    window_size: int = 5,
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
    
    sorted_ts = sorted(readings.keys())
    values = [readings[ts].get("value", 0) for ts in sorted_ts]
    
    if len(values) < window_size:
        return {
            "sensor_id": sensor_id,
            "error": f"Not enough data points for window size {window_size}",
            "data_points": len(values),
        }
    
    moving_averages = []
    for i in range(len(values) - window_size + 1):
        window = values[i:i + window_size]
        ma = sum(window) / window_size
        moving_averages.append({
            "timestamp": sorted_ts[i + window_size - 1],
            "moving_average": round(ma, 2),
            "actual_value": values[i + window_size - 1],
        })
    
    return {
        "sensor_id": sensor_id,
        "window_size": window_size,
        "data_points": len(values),
        "moving_averages": moving_averages,
    }


def detect_seasonality(
    session: dict[str, Any],
    sensor_id: str,
    expected_period_hours: int = 24,
    action_index: int | None = None,
) -> dict[str, Any]:
    sensor_readings = session.get("sensor_readings", {})
    if sensor_id not in sensor_readings:
        return {"error": f"No readings found for sensor {sensor_id}"}
    
    readings = sensor_readings[sensor_id]
    if len(readings) < expected_period_hours * 2:
        return {
            "sensor_id": sensor_id,
            "seasonality_detected": False,
            "reason": f"Insufficient data for {expected_period_hours}-hour period detection",
            "data_points": len(readings),
        }
    
    sorted_ts = sorted(readings.keys())
    values = [readings[ts].get("value", 0) for ts in sorted_ts]
    
    if len(values) < 2:
        return {
            "sensor_id": sensor_id,
            "seasonality_detected": False,
            "reason": "Insufficient data",
        }
    
    first_half = values[:len(values)//2]
    second_half = values[len(values)//2:]
    
    first_avg = sum(first_half) / len(first_half)
    second_avg = sum(second_half) / len(second_half)
    
    correlation = abs(first_avg - second_avg) / first_avg if first_avg != 0 else 0
    
    return {
        "sensor_id": sensor_id,
        "seasonality_detected": correlation < 0.3,
        "period_hours": expected_period_hours,
        "correlation_score": round(correlation, 4),
        "first_half_avg": round(first_avg, 2),
        "second_half_avg": round(second_avg, 2),
        "data_points": len(values),
    }


def get_trend_summary(
    session: dict[str, Any],
    location_id: str | None = None,
    sensor_type: str | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    sensors = session.get("sensors", {})
    sensor_readings = session.get("sensor_readings", {})
    
    filtered_sensors = {}
    for sensor_id, sensor_info in sensors.items():
        if location_id and sensor_info.get("location_id") != location_id:
            continue
        if sensor_type and sensor_info.get("sensor_type") != sensor_type:
            continue
        if sensor_id in sensor_readings:
            filtered_sensors[sensor_id] = sensor_info
    
    trends = []
    for sensor_id in filtered_sensors:
        readings = sensor_readings[sensor_id]
        if len(readings) < 2:
            continue
        
        sorted_ts = sorted(readings.keys())
        values = [readings[ts].get("value", 0) for ts in sorted_ts]
        
        n = len(values)
        x_mean = sum(range(n)) / n
        y_mean = sum(values) / n
        
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        if slope > 0.1:
            direction = "increasing"
        elif slope < -0.1:
            direction = "decreasing"
        else:
            direction = "stable"
        
        trends.append({
            "sensor_id": sensor_id,
            "sensor_type": filtered_sensors[sensor_id].get("sensor_type"),
            "trend": direction,
            "slope": round(slope, 4),
            "latest_value": values[-1],
        })
    
    return {
        "total_sensors_analyzed": len(trends),
        "trends": trends,
    }
