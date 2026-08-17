import os, json, copy
from datetime import datetime, timezone

def build_env():
    # Ensure base directories exist (cwd is already )
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/electricity", exist_ok=True)
    os.makedirs("data/accounts", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    # ops directory is created by agent if needed; we don't pre-create

    # --- health.json (two users) ---
    health = {
        "users": [
            {
                "user_id": "user_001",
                "name": "John Smith",
                "age": 42,
                "health_conditions": ["asthma", "allergy"],
                "respiratory_issues": True,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 22, "max": 24},
                "humidity_preference": {"min": 40, "max": 60},
                "sleep_schedule": {"start": "22:00", "end": "07:00"}
            },
            {
                "user_id": "user_002",
                "name": "Jane Smith",
                "age": 38,
                "health_conditions": [],
                "respiratory_issues": False,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 23, "max": 26},
                "humidity_preference": {"min": 30, "max": 50},
                "sleep_schedule": {"start": "23:00", "end": "06:00"}
            }
        ]
    }
    with open("data/health/health.json", "w") as f:
        json.dump(health, f, indent=2)

    # --- weather.json (two timestamps, latest with low humidity) ---
    now = datetime(2025, 7, 15, 14, 0, 0, tzinfo=timezone.utc)
    old = datetime(2025, 6, 1, 10, 0, 0, tzinfo=timezone.utc)
    weather = {
        "weather_data": [
            {
                "timestamp": now.isoformat(),
                "temperature": 32.5,
                "humidity": 20,
                "conditions": "sunny",
                "feels_like": 35.0,
                "uv_index": 8
            },
            {
                "timestamp": old.isoformat(),
                "temperature": 25.0,
                "humidity": 50,
                "conditions": "partly_cloudy",
                "feels_like": 26.0,
                "uv_index": 5
            }
        ]
    }
    with open("data/weather/weather.json", "w") as f:
        json.dump(weather, f, indent=2)

    # --- devices.json (multiple devices, only Bedroom AC is linked to user_001) ---
    devices = {
        "devices": [
            {
                "device_id": "device_001",
                "name": "Bedroom AC",
                "type": "air_conditioner",
                "location": "bedroom",
                "power_watts": 2000,
                "default_settings": {"temperature": 22, "mode": "cool", "fan_speed": "auto"},
                "user_id": "user_001"
            },
            {
                "device_id": "device_002",
                "name": "Living Room AC",
                "type": "air_conditioner",
                "location": "living_room",
                "power_watts": 2800,
                "default_settings": {"temperature": 24, "mode": "cool", "fan_speed": "auto"},
                "user_id": "user_002"
            },
            {
                "device_id": "device_003",
                "name": "Bedroom Humidifier",
                "type": "humidifier",
                "location": "bedroom",
                "power_watts": 50,
                "default_settings": {"humidity_target": 45, "mode": "auto"},
                "user_id": "user_001"
            },
            {
                "device_id": "device_004",
                "name": "Desk Setup Smart Plug",
                "type": "smart_plug",
                "location": "study_room",
                "power_watts": 150,
                "default_settings": {"state": "off"},
                "user_id": None
            },
            {
                "device_id": "device_005",
                "name": "TV Smart Plug",
                "type": "smart_plug",
                "location": "living_room",
                "power_watts": 120,
                "default_settings": {"state": "off"},
                "user_id": None
            }
        ]
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # --- electricity/rates.json (distractor) ---
    rates = {
        "rates": [
            {"period": "off_peak", "start_hour": 23, "end_hour": 7, "rate_per_kwh": 0.08, "label": "Off-Peak"},
            {"period": "mid_peak", "start_hour": 7, "end_hour": 17, "rate_per_kwh": 0.12, "label": "Mid-Peak"},
            {"period": "peak", "start_hour": 17, "end_hour": 21, "rate_per_kwh": 0.20, "label": "Peak"},
            {"period": "high_peak", "start_hour": 21, "end_hour": 23, "rate_per_kwh": 0.25, "label": "High-Peak"}
        ]
    }
    with open("data/electricity/rates.json", "w") as f:
        json.dump(rates, f, indent=2)

    # --- accounts.json (distractor) ---
    accounts = {
        "accounts": [
            {"account_id": "acc_001", "account_name": "John", "email": "john@example.com", "role": "owner", "display_name": "John Smith"},
            {"account_id": "acc_002", "account_name": "Jane", "email": "jane@example.com", "role": "owner", "display_name": "Jane Smith"}
        ]
    }
    with open("data/accounts/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # --- logs (distractor directory with old log file) ---
    with open("logs/system_202506.log", "w") as f:
        f.write("2025-06-15 10:00:00 INFO  Session started\n2025-06-15 10:01:00 WARN  Temperature spike in bedroom\n")
    with open("logs/system_202507.log", "w") as f:
        f.write("2025-07-14 22:00:00 INFO  Night mode engaged\n")

if __name__ == "__main__":
    build_env()
    print("Environment built successfully.")
