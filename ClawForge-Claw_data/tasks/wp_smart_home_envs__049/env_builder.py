import json
import os

def build_env():
    # health data
    health_dir = "data/health"
    os.makedirs(health_dir, exist_ok=True)
    health = {
        "users": [
            {
                "user_id": "usr_001",
                "name": "John Smith",
                "age": 45,
                "health_conditions": ["asthma", "allergic rhinitis"],
                "respiratory_issues": True,
                "cardiovascular_risk": False,
                "room": "bedroom",
                "temperature_preference": {"min": 22, "max": 26},
                "humidity_preference": {"min": 50, "max": 60},
                "sleep_schedule": {"start": "22:00", "end": "07:00"}
            },
            {
                "user_id": "usr_002",
                "name": "Jane Smith",
                "age": 42,
                "health_conditions": ["none"],
                "respiratory_issues": False,
                "cardiovascular_risk": False,
                "room": "living_room",
                "temperature_preference": {"min": 20, "max": 24},
                "humidity_preference": {"min": 40, "max": 50},
                "sleep_schedule": {"start": "23:00", "end": "06:00"}
            }
        ]
    }
    with open(os.path.join(health_dir, "health.json"), "w") as f:
        json.dump(health, f, indent=2)

    # devices data
    devices_dir = "data/devices"
    os.makedirs(devices_dir, exist_ok=True)
    devices = {
        "devices": [
            {
                "device_id": "dev_001",
                "name": "Bedroom AC",
                "type": "air_conditioner",
                "location": "bedroom",
                "power_watts": 1500,
                "default_settings": {"temperature": 20, "mode": "cool"}
            },
            {
                "device_id": "dev_002",
                "name": "Bedroom Humidifier",
                "type": "humidifier",
                "location": "bedroom",
                "power_watts": 50,
                "default_settings": {"target_humidity": 35, "mode": "auto"}
            },
            {
                "device_id": "dev_003",
                "name": "Living Room AC",
                "type": "air_conditioner",
                "location": "living_room",
                "power_watts": 2000,
                "default_settings": {"temperature": 22, "mode": "cool"}
            },
            {
                "device_id": "dev_004",
                "name": "Living Room Humidifier",
                "type": "humidifier",
                "location": "living_room",
                "power_watts": 60,
                "default_settings": {"target_humidity": 45, "mode": "auto"}
            },
            {
                "device_id": "dev_005",
                "name": "Guest Room AC",
                "type": "air_conditioner",
                "location": "guest_room",
                "power_watts": 1200,
                "default_settings": {"temperature": 24, "mode": "cool"}
            },
            {
                "device_id": "dev_006",
                "name": "Desk Setup Smart Plug",
                "type": "smart_plug",
                "location": "study_room",
                "power_watts": 0,
                "default_settings": {"state": "off"}
            }
        ]
    }
    with open(os.path.join(devices_dir, "devices.json"), "w") as f:
        json.dump(devices, f, indent=2)

    # electricity rates (not needed for this task but keep consistency)
    rates_dir = "data/electricity"
    os.makedirs(rates_dir, exist_ok=True)
    rates = {
        "rates": [
            {"period": "off_peak", "start_hour": 0, "end_hour": 6, "rate_per_kwh": 0.08, "label": "Off-Peak"},
            {"period": "mid_peak", "start_hour": 6, "end_hour": 13, "rate_per_kwh": 0.12, "label": "Mid-Peak"},
            {"period": "peak", "start_hour": 13, "end_hour": 17, "rate_per_kwh": 0.20, "label": "Peak"},
            {"period": "mid_peak_evening", "start_hour": 17, "end_hour": 22, "rate_per_kwh": 0.14, "label": "Mid-Peak"},
            {"period": "off_peak", "start_hour": 22, "end_hour": 24, "rate_per_kwh": 0.08, "label": "Off-Peak"}
        ]
    }
    with open(os.path.join(rates_dir, "rates.json"), "w") as f:
        json.dump(rates, f, indent=2)

    # weather data (decoy)
    weather_dir = "data/weather"
    os.makedirs(weather_dir, exist_ok=True)
    weather = {
        "weather_data": [
            {"timestamp": "2025-06-12T14:00:00", "temperature": 31.5, "humidity": 32, "conditions": "sunny", "feels_like": 33.2, "uv_index": 7}
        ]
    }
    with open(os.path.join(weather_dir, "weather.json"), "w") as f:
        json.dump(weather, f, indent=2)

    # prepare output directory
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
