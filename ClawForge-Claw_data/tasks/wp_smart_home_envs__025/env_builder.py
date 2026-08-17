import os
import json
import math
from datetime import datetime, timezone

def build_env():
    # 创建数据目录
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/electricity", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)

    # 设备清单 (包含干扰项：多一个 bathroom heater smart plug)
    devices = [
        {"device_id": "device-001", "name": "Bedroom AC", "type": "air_conditioner", "location": "bedroom", "power_watts": 2000, "default_settings": {"mode": "cool", "temperature": 24}},
        {"device_id": "device-002", "name": "Living Room AC", "type": "air_conditioner", "location": "living_room", "power_watts": 2500, "default_settings": {"mode": "cool", "temperature": 23}},
        {"device_id": "device-003", "name": "Bedroom Humidifier", "type": "humidifier", "location": "bedroom", "power_watts": 50, "default_settings": {"humidity": 45}},
        {"device_id": "device-004", "name": "Living Room Humidifier", "type": "humidifier", "location": "living_room", "power_watts": 60, "default_settings": {"humidity": 45}},
        {"device_id": "device-005", "name": "Desk Setup Smart Plug", "type": "smart_plug", "location": "study_room", "power_watts": 150, "default_settings": {}},
        {"device_id": "device-006", "name": "Floor Lamp Smart Plug", "type": "smart_plug", "location": "living_room", "power_watts": 100, "default_settings": {}},
        {"device_id": "device-007", "name": "TV Smart Plug", "type": "smart_plug", "location": "living_room", "power_watts": 200, "default_settings": {}},
        {"device_id": "device-008", "name": "Bathroom Heater Smart Plug", "type": "smart_plug", "location": "bathroom", "power_watts": 800, "default_settings": {}},
        # 额外干扰: 一个非标准类型的设备（无关）
        {"device_id": "device-009", "name": "Smart Doorbell", "type": "doorbell", "location": "entrance", "power_watts": 5, "default_settings": {}}
    ]
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # 健康档案 (两个用户，Jane 有呼吸道问题)
    users = [
        {"user_id": "user-001", "name": "Jane Smith", "age": 34, "health_conditions": ["asthma"], "respiratory_issues": True, "cardiovascular_risk": False, "temperature_preference": {"min": 22, "max": 24}, "humidity_preference": {"min": 40, "max": 50}, "sleep_schedule": {"start": "22:00", "end": "07:00"}},
        {"user_id": "user-002", "name": "John Smith", "age": 36, "health_conditions": [], "respiratory_issues": False, "cardiovascular_risk": False, "temperature_preference": {"min": 20, "max": 26}, "humidity_preference": {"min": 30, "max": 60}, "sleep_schedule": {"start": "23:00", "end": "06:00"}}
    ]
    with open("data/health/health.json", "w") as f:
        json.dump({"users": users}, f, indent=2)

    # 电价表 (覆盖所有时段)
    rates = [
        {"period": "off_peak", "start_hour": 0, "end_hour": 6, "rate_per_kwh": 0.10, "label": "Off-Peak"},
        {"period": "mid_peak", "start_hour": 6, "end_hour": 10, "rate_per_kwh": 0.18, "label": "Mid-Peak"},
        {"period": "peak", "start_hour": 10, "end_hour": 17, "rate_per_kwh": 0.25, "label": "Peak"},
        {"period": "mid_peak_evening", "start_hour": 17, "end_hour": 22, "rate_per_kwh": 0.18, "label": "Mid-Peak"},
        {"period": "off_peak_night", "start_hour": 22, "end_hour": 24, "rate_per_kwh": 0.10, "label": "Off-Peak"}
    ]
    with open("data/electricity/rates.json", "w") as f:
        json.dump({"rates": rates}, f, indent=2)

    # 天气数据 (只有一条代表当前时间 14:00 UTC)
    weather = [
        {"timestamp": "2025-06-12T14:00:00Z", "temperature": 28.5, "humidity": 35, "conditions": "partly_cloudy", "feels_like": 30.2, "uv_index": 5}
    ]
    with open("data/weather/weather.json", "w") as f:
        json.dump({"weather_data": weather}, f, indent=2)

    print("Workplace environment built successfully. Ready for agent task.")
