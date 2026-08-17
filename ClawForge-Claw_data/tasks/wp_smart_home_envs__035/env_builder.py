import os
import json

def build_env():
    # 创建工作目录结构
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/electricity", exist_ok=True)
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)
    os.makedirs("data/accounts", exist_ok=True)  # 干扰项

    # 1. devices.json
    devices = {
        "devices": [
            {
                "device_id": "ac-001",
                "name": "Bedroom AC",
                "type": "air_conditioner",
                "location": "bedroom",
                "power_watts": 2000,
                "default_settings": {"mode": "cool", "temp": 24}
            },
            {
                "device_id": "ac-002",
                "name": "Living Room AC",
                "type": "air_conditioner",
                "location": "living_room",
                "power_watts": 3500,
                "default_settings": {"mode": "cool", "temp": 22}
            },
            {
                "device_id": "hm-001",
                "name": "Bedroom Humidifier",
                "type": "humidifier",
                "location": "bedroom",
                "power_watts": 500,
                "default_settings": {"humidity": 55}
            },
            {
                "device_id": "hm-002",
                "name": "Living Room Humidifier",
                "type": "humidifier",
                "location": "living_room",
                "power_watts": 700,
                "default_settings": {"humidity": 50}
            },
            {
                "device_id": "sp-001",
                "name": "Desk Setup Smart Plug",
                "type": "smart_plug",
                "location": "study_room",
                "power_watts": 1500,
                "default_settings": {"auto_off": True}
            },
            {
                "device_id": "sp-002",
                "name": "Floor Lamp Smart Plug",
                "type": "smart_plug",
                "location": "living_room",
                "power_watts": 300,
                "default_settings": {"auto_off": False}
            },
            {
                "device_id": "sp-003",
                "name": "TV Smart Plug",
                "type": "smart_plug",
                "location": "living_room",
                "power_watts": 5000,  # 大功率诱饵
                "default_settings": {"auto_off": True}
            }
        ]
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # 2. rates.json
    rates = {
        "rates": [
            {
                "period": "high_peak",
                "start_hour": 10,
                "end_hour": 14,
                "rate_per_kwh": 0.45,
                "label": "High-Peak"
            },
            {
                "period": "mid_peak",
                "start_hour": 7,
                "end_hour": 10,
                "rate_per_kwh": 0.25,
                "label": "Mid-Peak"
            },
            {
                "period": "off_peak",
                "start_hour": 0,
                "end_hour": 7,
                "rate_per_kwh": 0.15,
                "label": "Off-Peak"
            }
        ]
    }
    with open("data/electricity/rates.json", "w") as f:
        json.dump(rates, f, indent=2)

    # 3. health.json (干扰)
    health = {
        "users": [
            {
                "user_id": "usr-001",
                "name": "Jane Smith",
                "age": 34,
                "health_conditions": ["asthma"],
                "respiratory_issues": True,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 22, "max": 24},
                "humidity_preference": {"min": 40, "max": 60},
                "sleep_schedule": {"start": "22:00", "end": "06:00"}
            },
            {
                "user_id": "usr-002",
                "name": "John Smith",
                "age": 36,
                "health_conditions": ["hypertension"],
                "respiratory_issues": False,
                "cardiovascular_risk": True,
                "temperature_preference": {"min": 20, "max": 22},
                "humidity_preference": {"min": 45, "max": 55},
                "sleep_schedule": {"start": "23:00", "end": "07:00"}
            }
        ]
    }
    with open("data/health/health.json", "w") as f:
        json.dump(health, f, indent=2)

    # 4. weather.json (干扰)
    weather = {
        "weather_data": [
            {
                "timestamp": "2025-06-12T14:00:00",
                "temperature": 32.5,
                "humidity": 55,
                "conditions": "sunny",
                "feels_like": 35.0,
                "uv_index": 7
            }
        ]
    }
    with open("data/weather/weather.json", "w") as f:
        json.dump(weather, f, indent=2)

    # 5. accounts.json (干扰)
    accounts = {
        "accounts": [
            {"account_id": "acc-001", "account_name": "Smith Family", "email": "smith@home.com", "role": "owner", "display_name": "Jim Smith"}
        ]
    }
    with open("data/accounts/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

if __name__ == "__main__":
    build_env()
