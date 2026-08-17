import os
import json
import shutil

def build_env():
    # Create data directories
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/electricity", exist_ok=True)
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)

    # Devices
    devices = {
        "devices": [
            {
                "device_id": "ac_bedroom_01",
                "name": "Bedroom AC",
                "type": "air_conditioner",
                "location": "bedroom",
                "power_watts": 1500,
                "default_settings": {"mode": "cool", "temperature": 24}
            },
            {
                "device_id": "humidifier_bedroom_01",
                "name": "Bedroom Humidifier",
                "type": "humidifier",
                "location": "bedroom",
                "power_watts": 100,
                "default_settings": {"humidity": 45, "timer_hours": 0}
            },
            {
                "device_id": "humidifier_living_01",
                "name": "Living Room Humidifier",
                "type": "humidifier",
                "location": "living_room",
                "power_watts": 120,
                "default_settings": {"humidity": 50, "timer_hours": 0}
            },
            {
                "device_id": "ac_living_01",
                "name": "Living Room AC",
                "type": "air_conditioner",
                "location": "living_room",
                "power_watts": 2000,
                "default_settings": {"mode": "cool", "temperature": 22}
            },
            {
                "device_id": "plug_desk_01",
                "name": "Desk Setup Smart Plug",
                "type": "smart_plug",
                "location": "study_room",
                "power_watts": 0,
                "default_settings": {"state": "off"}
            }
        ]
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # Electricity rates
    rates = {
        "rates": [
            {"period": "off_peak", "start_hour": 22, "end_hour": 6, "rate_per_kwh": 0.12, "label": "Off-Peak"},
            {"period": "mid_peak", "start_hour": 6, "end_hour": 14, "rate_per_kwh": 0.25, "label": "Mid-Peak"},
            {"period": "peak", "start_hour": 14, "end_hour": 17, "rate_per_kwh": 0.50, "label": "Peak"},
            {"period": "mid_peak_evening", "start_hour": 17, "end_hour": 22, "rate_per_kwh": 0.30, "label": "Mid-Peak Evening"}
        ]
    }
    with open("data/electricity/rates.json", "w") as f:
        json.dump(rates, f, indent=2)

    # Health
    health = {
        "users": [
            {
                "user_id": "user_jane",
                "name": "Jane Smith",
                "age": 32,
                "health_conditions": [],
                "respiratory_issues": False,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 22, "max": 26},
                "humidity_preference": {"min": 30, "max": 50},
                "sleep_schedule": {"start": 23, "end": 7}
            },
            {
                "user_id": "user_john",
                "name": "John Smith",
                "age": 35,
                "health_conditions": ["asthma"],
                "respiratory_issues": True,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 20, "max": 24},
                "humidity_preference": {"min": 40, "max": 60},
                "sleep_schedule": {"start": 22, "end": 6}
            }
        ]
    }
    with open("data/health/health.json", "w") as f:
        json.dump(health, f, indent=2)

    # Weather (current time 15:00)
    weather = {
        "weather_data": [
            {
                "timestamp": "2025-06-12T15:00:00Z",
                "temperature": 28.5,
                "humidity": 30,
                "conditions": "partly_cloudy",
                "feels_like": 30.2,
                "uv_index": 5
            },
            {
                "timestamp": "2025-06-12T06:00:00Z",
                "temperature": 22.0,
                "humidity": 55,
                "conditions": "cloudy",
                "feels_like": 21.5,
                "uv_index": 1
            }
        ]
    }
    with open("data/weather/weather.json", "w") as f:
        json.dump(weather, f, indent=2)

    # Create ops directory (for agent output)
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
