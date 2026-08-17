import os
import json
import math

def build_env():
    # 创建数据目录
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/electricity", exist_ok=True)
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 用于存放 agent 输出

    # 1. 设备清单 (devices.json)
    devices = {
        "devices": [
            {
                "device_id": "DEV-AC-LR-001",
                "name": "Living Room AC",
                "type": "air_conditioner",
                "location": "living_room",
                "power_watts": 3500,
                "default_settings": {"mode": "cool", "target_temp": 22}
            },
            {
                "device_id": "DEV-AC-BR-002",
                "name": "Bedroom AC",
                "type": "air_conditioner",
                "location": "bedroom",
                "power_watts": 2000,
                "default_settings": {"mode": "cool", "target_temp": 23}
            },
            {
                "device_id": "DEV-HU-LR-003",
                "name": "Living Room Humidifier",
                "type": "humidifier",
                "location": "living_room",
                "power_watts": 500,
                "default_settings": {"target_humidity": 45}
            },
            {
                "device_id": "DEV-HU-BR-004",
                "name": "Bedroom Humidifier",
                "type": "humidifier",
                "location": "bedroom",
                "power_watts": 300,
                "default_settings": {"target_humidity": 50}
            },
            {
                "device_id": "DEV-SP-DESK-005",
                "name": "Desk Setup Smart Plug",
                "type": "smart_plug",
                "location": "study_room",
                "power_watts": 150,
                "default_settings": {"state": "on"}
            },
            {
                "device_id": "DEV-SP-FLOOR-006",
                "name": "Floor Lamp Smart Plug",
                "type": "smart_plug",
                "location": "study_room",
                "power_watts": 100,
                "default_settings": {"state": "on"}
            },
            {
                "device_id": "DEV-SP-TV-007",
                "name": "TV Smart Plug",
                "type": "smart_plug",
                "location": "living_room",
                "power_watts": 200,
                "default_settings": {"state": "on"}
            }
        ]
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # 2. 电价费率 (rates.json)
    rates = {
        "rates": [
            {"period": "off_peak", "start_hour": 0, "end_hour": 6, "rate_per_kwh": 0.25, "label": "Off-Peak"},
            {"period": "mid_peak", "start_hour": 6, "end_hour": 14, "rate_per_kwh": 0.35, "label": "Mid-Peak"},
            {"period": "peak", "start_hour": 14, "end_hour": 18, "rate_per_kwh": 0.55, "label": "Peak"},
            {"period": "mid_peak_evening", "start_hour": 18, "end_hour": 22, "rate_per_kwh": 0.35, "label": "Mid-Peak"},
            {"period": "off_peak_night", "start_hour": 22, "end_hour": 24, "rate_per_kwh": 0.25, "label": "Off-Peak"}
        ]
    }
    with open("data/electricity/rates.json", "w") as f:
        json.dump(rates, f, indent=2)

    # 3. 健康档案 (health.json)
    health = {
        "users": [
            {
                "user_id": "USR-JANE-001",
                "name": "Jane Smith",
                "age": 32,
                "health_conditions": ["asthma"],
                "respiratory_issues": True,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 22, "max": 24},
                "humidity_preference": {"min": 45, "max": 55},
                "sleep_schedule": {"bedtime": "23:00", "wakeup": "07:00"}
            },
            {
                "user_id": "USR-JOHN-002",
                "name": "John Smith",
                "age": 35,
                "health_conditions": [],
                "respiratory_issues": False,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 20, "max": 26},
                "humidity_preference": {"min": 30, "max": 60},
                "sleep_schedule": {"bedtime": "00:00", "wakeup": "08:00"}
            }
        ]
    }
    with open("data/health/health.json", "w") as f:
        json.dump(health, f, indent=2)

    # 4. 天气数据 (weather.json) —— 模拟今天全天，高峰时段炎热干燥
    # 构造逐小时数据（简化为关键时段）
    weather_data = {
        "weather_data": [
            {"timestamp": "2025-06-15T00:00:00Z", "temperature": 26.0, "humidity": 28, "conditions": "clear", "feels_like": 26.0, "uv_index": 0},
            {"timestamp": "2025-06-15T06:00:00Z", "temperature": 28.5, "humidity": 25, "conditions": "sunny", "feels_like": 29.0, "uv_index": 3},
            {"timestamp": "2025-06-15T08:00:00Z", "temperature": 30.0, "humidity": 24, "conditions": "sunny", "feels_like": 31.0, "uv_index": 5},
            {"timestamp": "2025-06-15T10:00:00Z", "temperature": 31.5, "humidity": 22, "conditions": "sunny", "feels_like": 33.0, "uv_index": 7},
            {"timestamp": "2025-06-15T12:00:00Z", "temperature": 32.0, "humidity": 21, "conditions": "sunny", "feels_like": 34.0, "uv_index": 8},
            {"timestamp": "2025-06-15T14:00:00Z", "temperature": 33.0, "humidity": 20, "conditions": "sunny", "feels_like": 35.0, "uv_index": 9},
            {"timestamp": "2025-06-15T16:00:00Z", "temperature": 33.5, "humidity": 19, "conditions": "sunny", "feels_like": 36.0, "uv_index": 7},
            {"timestamp": "2025-06-15T18:00:00Z", "temperature": 32.0, "humidity": 22, "conditions": "sunny", "feels_like": 33.0, "uv_index": 3},
            {"timestamp": "2025-06-15T20:00:00Z", "temperature": 29.0, "humidity": 25, "conditions": "clear", "feels_like": 30.0, "uv_index": 0},
            {"timestamp": "2025-06-15T22:00:00Z", "temperature": 27.0, "humidity": 28, "conditions": "clear", "feels_like": 28.0, "uv_index": 0}
        ]
    }
    with open("data/weather/weather.json", "w") as f:
        json.dump(weather_data, f, indent=2)

    # 5. 账户数据 (accounts.json) —— 干扰项，不参与核心计算
    accounts = {
        "accounts": [
            {"account_id": "ACT-SMITH-001", "account_name": "Smith Family", "email": "smith@home.com", "role": "owner", "display_name": "John Smith"},
            {"account_id": "ACT-SMITH-002", "account_name": "Smith Family (Jane)", "email": "jane@home.com", "role": "member", "display_name": "Jane Smith"}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

if __name__ == "__main__":
    build_env()
