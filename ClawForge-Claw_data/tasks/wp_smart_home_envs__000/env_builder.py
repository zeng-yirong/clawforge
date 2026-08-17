import os
import json
from datetime import datetime, timezone

def build_env():
    # === 目录结构 ===
    dirs = [
        "data/devices",
        "data/electricity",
        "data/health",
        "data/weather",
        "data/status",
        "ops",           # 空目录，让 agent 写入
        "logs",          # 干扰目录
        "backup"         # 干扰目录
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # === 当前时间（下午3点） ===
    with open("current_time.txt", "w") as f:
        f.write("15:00")

    # === 设备列表（主数据） ===
    devices = {
        "devices": [
            {
                "device_id": "ac_bedroom_01",
                "name": "Bedroom AC",
                "type": "air_conditioner",
                "location": "bedroom",
                "power_watts": 1500,
                "default_settings": {"temperature": 24, "mode": "cool"}
            },
            {
                "device_id": "humid_bedroom_01",
                "name": "Bedroom Humidifier",
                "type": "humidifier",
                "location": "bedroom",
                "power_watts": 300,
                "default_settings": {"humidity": 55, "mode": "auto"}
            },
            {
                "device_id": "ac_living_01",
                "name": "Living Room AC",
                "type": "air_conditioner",
                "location": "living_room",
                "power_watts": 2000,
                "default_settings": {"temperature": 26, "mode": "cool"}
            },
            {
                "device_id": "humid_living_01",
                "name": "Living Room Humidifier",
                "type": "humidifier",
                "location": "living_room",
                "power_watts": 400,
                "default_settings": {"humidity": 50, "mode": "auto"}
            },
            {
                "device_id": "plug_desk_01",
                "name": "Desk Setup Smart Plug",
                "type": "smart_plug",
                "location": "study_room",
                "power_watts": 0,   # 仅作开关
                "default_settings": {}
            },
            {
                "device_id": "plug_floor_lamp_01",
                "name": "Floor Lamp Smart Plug",
                "type": "smart_plug",
                "location": "living_room",
                "power_watts": 60,
                "default_settings": {}
            },
            {
                "device_id": "plug_tv_01",
                "name": "TV Smart Plug",
                "type": "smart_plug",
                "location": "living_room",
                "power_watts": 150,
                "default_settings": {}
            }
        ]
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # === 设备状态（当前运行状态） ===
    device_status = {
        "status": [
            {"device_id": "ac_bedroom_01", "power_on": True,  "current_settings": {"temperature": 24, "mode": "cool"}},
            {"device_id": "humid_bedroom_01", "power_on": False, "current_settings": {}},
            {"device_id": "ac_living_01", "power_on": True,  "current_settings": {"temperature": 26, "mode": "cool"}},
            {"device_id": "humid_living_01", "power_on": True,  "current_settings": {"humidity": 50, "mode": "auto"}},
            {"device_id": "plug_desk_01", "power_on": True,  "current_settings": {}},
            {"device_id": "plug_floor_lamp_01", "power_on": False, "current_settings": {}},
            {"device_id": "plug_tv_01", "power_on": True,  "current_settings": {}}
        ]
    }
    with open("data/status/device_status.json", "w") as f:
        json.dump(device_status, f, indent=2)

    # === 电价时段 ===
    rates = {
        "rates": [
            {"period": "off_peak",    "start_hour": 0,  "end_hour": 6,  "rate_per_kwh": 0.05, "label": "Off-Peak"},
            {"period": "mid_peak",    "start_hour": 7,  "end_hour": 13, "rate_per_kwh": 0.08, "label": "Mid-Peak"},
            {"period": "high_peak",   "start_hour": 14, "end_hour": 17, "rate_per_kwh": 0.12, "label": "High-Peak"},
            {"period": "mid_peak_evening", "start_hour": 18, "end_hour": 21, "rate_per_kwh": 0.08, "label": "Mid-Peak"},
            {"period": "off_peak",    "start_hour": 22, "end_hour": 23, "rate_per_kwh": 0.05, "label": "Off-Peak"}
        ]
    }
    with open("data/electricity/rates.json", "w") as f:
        json.dump(rates, f, indent=2)

    # === 用户健康信息 ===
    health = {
        "users": [
            {
                "user_id": "jane_smith",
                "name": "Jane Smith",
                "age": 32,
                "health_conditions": ["asthma"],
                "respiratory_issues": True,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 22, "max": 25, "optimal": 24},
                "humidity_preference": {"min": 50, "max": 60, "optimal": 55},
                "sleep_schedule": {"wake": "07:00", "sleep": "22:00"}
            },
            {
                "user_id": "john_smith",
                "name": "John Smith",
                "age": 34,
                "health_conditions": [],
                "respiratory_issues": False,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 23, "max": 27, "optimal": 25},
                "humidity_preference": {"min": 40, "max": 55, "optimal": 45},
                "sleep_schedule": {"wake": "06:30", "sleep": "23:00"}
            }
        ]
    }
    with open("data/health/health.json", "w") as f:
        json.dump(health, f, indent=2)

    # === 天气数据 ===
    weather = {
        "weather_data": {
            "timestamp": "2025-06-12T15:00:00Z",
            "temperature": 30.0,
            "humidity": 40,
            "conditions": "sunny",
            "feels_like": 32.0,
            "uv_index": 6
        }
    }
    with open("data/weather/weather.json", "w") as f:
        json.dump(weather, f, indent=2)

    # === 干扰项：旧版本设备列表 ===
    old_devices = {
        "devices": [
            {"device_id": "ac_bedroom_01", "name": "Bedroom AC", "type": "air_conditioner", "location": "bedroom", "power_watts": 1500, "version": "v1.0"},
            {"device_id": "humid_bedroom_01", "name": "Bedroom Humidifier", "type": "humidifier", "location": "bedroom", "power_watts": 300, "version": "v1.0"}
        ]
    }
    with open("data/devices/backup/devices_v1.json", "w") as f:
        json.dump(old_devices, f, indent=2)

    # === 干扰项：无关日志 ===
    with open("logs/system_monitor.log", "w") as f:
        f.write("[INFO] 2025-06-12 14:55 System health check passed\n[WARN] 2025-06-12 14:58 CPU temperature 72°C\n")

if __name__ == "__main__":
    build_env()
