import os
import json

def build_env():
    # 确保目录存在
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/electricity", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 用于输出
    # 干扰目录
    os.makedirs("logs", exist_ok=True)
    os.makedirs("backup", exist_ok=True)

    # 设备数据
    devices = {
        "devices": [
            {
                "device_id": "BD-AC-001",
                "name": "Bedroom AC",
                "type": "air_conditioner",
                "location": "bedroom",
                "power_watts": 1500,
                "default_settings": {
                    "target_temperature": 20,
                    "mode": "cool"
                }
            },
            {
                "device_id": "LR-HM-002",
                "name": "Living Room Humidifier",
                "type": "humidifier",
                "location": "living_room",
                "power_watts": 200,
                "default_settings": {
                    "target_humidity": 60,
                    "mode": "on"
                }
            },
            {
                "device_id": "BD-HM-003",
                "name": "Bedroom Humidifier",
                "type": "humidifier",
                "location": "bedroom",
                "power_watts": 180,
                "default_settings": {
                    "target_humidity": 50,
                    "mode": "on"
                }
            },
            {
                "device_id": "LR-AC-004",
                "name": "Living Room AC",
                "type": "air_conditioner",
                "location": "living_room",
                "power_watts": 2000,
                "default_settings": {
                    "target_temperature": 22,
                    "mode": "cool"
                }
            },
            {
                "device_id": "DS-SP-005",
                "name": "Desk Setup Smart Plug",
                "type": "smart_plug",
                "location": "study_room",
                "power_watts": 100,
                "default_settings": {}
            },
            {
                "device_id": "TV-SP-006",
                "name": "TV Smart Plug",
                "type": "smart_plug",
                "location": "living_room",
                "power_watts": 300,
                "default_settings": {}
            }
        ]
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # 健康数据
    health = {
        "users": [
            {
                "user_id": "JANE001",
                "name": "Jane Smith",
                "age": 32,
                "health_conditions": ["asthma", "allergic_rhinitis"],
                "respiratory_issues": True,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 20, "max": 22},
                "humidity_preference": {"min": 40, "max": 50},
                "sleep_schedule": {"start": "22:00", "end": "07:00"}
            },
            {
                "user_id": "JOHN001",
                "name": "John Smith",
                "age": 35,
                "health_conditions": [],
                "respiratory_issues": False,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 18, "max": 26},
                "humidity_preference": {"min": 30, "max": 60},
                "sleep_schedule": {"start": "23:00", "end": "07:00"}
            }
        ]
    }
    with open("data/health/health.json", "w") as f:
        json.dump(health, f, indent=2)

    # 电价数据（干扰项，但用于营造真实感）
    rates = {
        "rates": [
            {"period": "off_peak", "start_hour": 0, "end_hour": 6, "rate_per_kwh": 0.08, "label": "Off-Peak"},
            {"period": "mid_peak", "start_hour": 6, "end_hour": 14, "rate_per_kwh": 0.12, "label": "Mid-Peak"},
            {"period": "peak", "start_hour": 14, "end_hour": 20, "rate_per_kwh": 0.20, "label": "Peak"},
            {"period": "mid_peak_evening", "start_hour": 20, "end_hour": 24, "rate_per_kwh": 0.12, "label": "Mid-Peak"}
        ]
    }
    with open("data/electricity/rates.json", "w") as f:
        json.dump(rates, f, indent=2)

    # 天气数据（干扰项）
    weather = {
        "weather_data": [
            {
                "timestamp": "2025-06-12T14:00:00Z",
                "temperature": 25.0,
                "humidity": 70,
                "conditions": "sunny",
                "feels_like": 26.0,
                "uv_index": 7
            }
        ]
    }
    with open("data/weather/weather.json", "w") as f:
        json.dump(weather, f, indent=2)

    # 干扰文件：旧版本日志
    with open("logs/old_health_check.log", "w") as f:
        f.write("2025-01-01 INFO: No conflicts found.\n")
    with open("backup/devices_backup.json", "w") as f:
        json.dump({"devices": []}, f)

if __name__ == "__main__":
    build_env()
