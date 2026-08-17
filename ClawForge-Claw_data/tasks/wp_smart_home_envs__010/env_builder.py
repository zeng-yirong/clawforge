import os
import json

def build_env():
    # Ensure directories exist
    dirs = ["data/devices", "data/electricity", "data/weather", "data/health", "ops"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # --- Devices (7 devices, 4 relevant for climate, 3 as distractors) ---
    devices = [
        {"device_id": "Bedroom AC", "name": "Bedroom AC", "type": "air_conditioner", "location": "bedroom", "power_watts": 2000, "default_settings": {"mode": "cool", "temperature": 24}},
        {"device_id": "Bedroom Humidifier", "name": "Bedroom Humidifier", "type": "humidifier", "location": "bedroom", "power_watts": 50, "default_settings": {"target_humidity": 45}},
        {"device_id": "Living Room AC", "name": "Living Room AC", "type": "air_conditioner", "location": "living_room", "power_watts": 2500, "default_settings": {"mode": "cool", "temperature": 25}},
        {"device_id": "Living Room Humidifier", "name": "Living Room Humidifier", "type": "humidifier", "location": "living_room", "power_watts": 60, "default_settings": {"target_humidity": 50}},
        {"device_id": "Desk Setup Smart Plug", "name": "Desk Setup Smart Plug", "type": "smart_plug", "location": "study_room", "power_watts": 100, "default_settings": {}},
        {"device_id": "Floor Lamp Smart Plug", "name": "Floor Lamp Smart Plug", "type": "smart_plug", "location": "living_room", "power_watts": 40, "default_settings": {}},
        {"device_id": "TV Smart Plug", "name": "TV Smart Plug", "type": "smart_plug", "location": "living_room", "power_watts": 150, "default_settings": {}}
    ]
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # --- Electricity Rates ---
    rates = [
        {"period": "peak", "start_hour": 14, "end_hour": 17, "rate_per_kwh": 0.25, "label": "Peak"},
        {"period": "off_peak", "start_hour": 0, "end_hour": 14, "rate_per_kwh": 0.10, "label": "Off-Peak"},
        {"period": "off_peak", "start_hour": 17, "end_hour": 24, "rate_per_kwh": 0.10, "label": "Off-Peak"}
    ]
    with open("data/electricity/rates.json", "w") as f:
        json.dump({"rates": rates}, f, indent=2)

    # --- Weather (current) ---
    weather_current = {
        "timestamp": "2025-06-12T14:00:00",
        "temperature": 32.0,
        "humidity": 65,
        "conditions": "sunny",
        "feels_like": 36.0,
        "uv_index": 7
    }
    with open("data/weather/weather.json", "w") as f:
        json.dump({"weather_data": [weather_current]}, f, indent=2)

    # --- Distractor: old weather ---
    weather_old = {
        "timestamp": "2025-06-11T14:00:00",
        "temperature": 25.0,
        "humidity": 45,
        "conditions": "partly_cloudy",
        "feels_like": 24.0,
        "uv_index": 3
    }
    with open("data/weather/weather_old.json", "w") as f:
        json.dump({"weather_data": [weather_old]}, f, indent=2)

    # --- Health profiles (two users) ---
    health = [
        {
            "user_id": "user_jane",
            "name": "Jane Smith",
            "age": 30,
            "health_conditions": ["asthma"],
            "respiratory_issues": True,
            "cardiovascular_risk": False,
            "temperature_preference": {"min": 22, "max": 25},
            "humidity_preference": {"min": 40, "max": 50},
            "sleep_schedule": {"start": "23:00", "end": "07:00"}
        },
        {
            "user_id": "user_john",
            "name": "John Smith",
            "age": 35,
            "health_conditions": ["hypertension"],
            "respiratory_issues": False,
            "cardiovascular_risk": True,
            "temperature_preference": {"min": 24, "max": 26},
            "humidity_preference": {"min": 50, "max": 60},
            "sleep_schedule": {"start": "22:00", "end": "06:00"}
        }
    ]
    with open("data/health/health.json", "w") as f:
        json.dump({"users": health}, f, indent=2)

    # --- Distractor: backup health (slightly different) ---
    health_backup = [
        {
            "user_id": "user_jane",
            "name": "Jane Smith",
            "age": 31,
            "health_conditions": ["asthma"],
            "respiratory_issues": True,
            "cardiovascular_risk": False,
            "temperature_preference": {"min": 23, "max": 26},
            "humidity_preference": {"min": 45, "max": 55},
            "sleep_schedule": {"start": "23:00", "end": "07:00"}
        }
    ]
    with open("data/health/health_backup.json", "w") as f:
        json.dump({"users": health_backup}, f, indent=2)

    # --- Occupancy ---
    occupancy = {
        "bedroom": "Jane Smith",
        "living_room": "John Smith",
        "study_room": None
    }
    with open("ops/occupancy.json", "w") as f:
        json.dump(occupancy, f, indent=2)

if __name__ == "__main__":
    build_env()
