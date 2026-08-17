import os
import json

def build_env():
    # Create directory structure
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/status", exist_ok=True)

    # Health data for two users (only Jane's will be relevant)
    health = [
        {
            "user_id": "user_001",
            "name": "Jane Smith",
            "age": 34,
            "health_conditions": ["asthma"],
            "respiratory_issues": True,
            "cardiovascular_risk": False,
            "temperature_preference": {"min": 22, "max": 26},
            "humidity_preference": {"min": 40, "max": 50},
            "sleep_schedule": {"start": "22:00", "end": "07:00"}
        },
        {
            "user_id": "user_002",
            "name": "John Smith",
            "age": 36,
            "health_conditions": [],
            "respiratory_issues": False,
            "cardiovascular_risk": False,
            "temperature_preference": {"min": 20, "max": 24},
            "humidity_preference": {"min": 30, "max": 60},
            "sleep_schedule": {"start": "23:00", "end": "06:00"}
        }
    ]
    with open("data/health/health.json", "w") as f:
        json.dump({"users": health}, f, indent=2)

    # Device definitions (including smart plugs as distractors)
    devices = [
        {"device_id": "ac_bedroom", "name": "Bedroom AC", "type": "air_conditioner", "location": "bedroom", "power_watts": 1500, "default_settings": {"temperature": 22, "mode": "cool"}},
        {"device_id": "ac_livingroom", "name": "Living Room AC", "type": "air_conditioner", "location": "living_room", "power_watts": 2000, "default_settings": {"temperature": 24, "mode": "cool"}},
        {"device_id": "hum_bedroom", "name": "Bedroom Humidifier", "type": "humidifier", "location": "bedroom", "power_watts": 300, "default_settings": {"humidity": 55}},
        {"device_id": "hum_livingroom", "name": "Living Room Humidifier", "type": "humidifier", "location": "living_room", "power_watts": 400, "default_settings": {"humidity": 45}},
        {"device_id": "plug_desk", "name": "Desk Setup Smart Plug", "type": "smart_plug", "location": "study_room", "power_watts": 800, "default_settings": {}},
        {"device_id": "plug_floor", "name": "Floor Lamp Smart Plug", "type": "smart_plug", "location": "living_room", "power_watts": 100, "default_settings": {}}
    ]
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # Current device status – contains deliberate conflicts for Jane's preferences
    # Bedroom humidifier humidity=60 -> outside 40-50
    # Living room AC temperature=20 -> outside 22-26
    # Others are within Jane's ranges or irrelevant
    status = [
        {"device_id": "ac_bedroom", "current_temperature": 24, "current_humidity": None},
        {"device_id": "ac_livingroom", "current_temperature": 20, "current_humidity": None},
        {"device_id": "hum_bedroom", "current_temperature": None, "current_humidity": 60},
        {"device_id": "hum_livingroom", "current_temperature": None, "current_humidity": 45},
        {"device_id": "plug_desk", "power_draw": 45},
        {"device_id": "plug_floor", "power_draw": 12}
    ]
    with open("data/status/status.json", "w") as f:
        json.dump({"status": status}, f, indent=2)

if __name__ == "__main__":
    build_env()
