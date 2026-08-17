import os
import json

def build_env():
    # Create data directory
    os.makedirs("data", exist_ok=True)
    # Create ops directory (empty, agent should create the file inside)
    os.makedirs("ops", exist_ok=True)

    # Health data for two users
    health = [
        {
            "user_id": "jane",
            "name": "Jane Smith",
            "age": 30,
            "health_conditions": [],
            "respiratory_issues": False,
            "cardiovascular_risk": False,
            "temperature_preference": {"target": 24.0, "min": 22, "max": 25},
            "humidity_preference": {"target": 45, "min": 40, "max": 50},
            "sleep_schedule": {"bedtime": "22:00", "wakeup": "07:00"},
            "location": "bedroom"
        },
        {
            "user_id": "john",
            "name": "John Smith",
            "age": 32,
            "health_conditions": ["seasonal_allergies"],
            "respiratory_issues": False,
            "cardiovascular_risk": False,
            "temperature_preference": {"target": 24.0, "min": 22, "max": 25},
            "humidity_preference": {"target": 40, "min": 35, "max": 45},
            "sleep_schedule": {"bedtime": "23:00", "wakeup": "07:30"},
            "location": "living_room"
        }
    ]
    with open("data/health.json", "w") as f:
        json.dump({"users": health}, f, indent=2)

    # Devices list with multiple types, only AC matters
    devices = [
        {
            "device_id": "ac_bedroom_01",
            "name": "Bedroom AC",
            "type": "air_conditioner",
            "location": "bedroom",
            "power_watts": 1500,
            "default_settings": {"mode": "cool", "temperature": 24}
        },
        {
            "device_id": "ac_living_01",
            "name": "Living Room AC",
            "type": "air_conditioner",
            "location": "living_room",
            "power_watts": 2000,
            "default_settings": {"mode": "cool", "temperature": 20}
        },
        {
            "device_id": "humidifier_bedroom",
            "name": "Bedroom Humidifier",
            "type": "humidifier",
            "location": "bedroom",
            "power_watts": 50,
            "default_settings": {"humidity": 50}
        },
        {
            "device_id": "humidifier_living",
            "name": "Living Room Humidifier",
            "type": "humidifier",
            "location": "living_room",
            "power_watts": 60,
            "default_settings": {"humidity": 35}
        },
        {
            "device_id": "plug_desk",
            "name": "Desk Setup Smart Plug",
            "type": "smart_plug",
            "location": "study_room",
            "power_watts": 300,
            "default_settings": {"state": "off"}
        }
    ]
    with open("data/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # Electricity rates (optional distractor)
    rates = [
        {"period": "off_peak", "start_hour": 0, "end_hour": 6, "rate_per_kwh": 0.10, "label": "Off-Peak"},
        {"period": "mid_peak", "start_hour": 6, "end_hour": 12, "rate_per_kwh": 0.15, "label": "Mid-Peak"},
        {"period": "peak", "start_hour": 12, "end_hour": 18, "rate_per_kwh": 0.25, "label": "Peak"},
        {"period": "mid_peak_evening", "start_hour": 18, "end_hour": 22, "rate_per_kwh": 0.18, "label": "Mid-Peak Evening"},
        {"period": "high_peak", "start_hour": 22, "end_hour": 24, "rate_per_kwh": 0.30, "label": "High-Peak"}
    ]
    with open("data/rates.json", "w") as f:
        json.dump({"rates": rates}, f, indent=2)

    # Weather snapshot (distractor)
    weather = [
        {"timestamp": "2025-04-12T14:00:00Z", "temperature": 28.5, "humidity": 65, "conditions": "sunny", "feels_like": 30.0, "uv_index": 7}
    ]
    with open("data/weather.json", "w") as f:
        json.dump({"weather_data": weather}, f, indent=2)

if __name__ == "__main__":
    build_env()
