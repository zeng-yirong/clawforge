import os
import json
import random

def build_env():
    # Create directory structure
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/electricity", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/status", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. devices.json
    devices = [
        {
            "device_id": "ac_living",
            "name": "Living Room AC",
            "type": "air_conditioner",
            "location": "living_room",
            "power_watts": 2000,
            "default_settings": {"target_temperature": 24, "mode": "cool"}
        },
        {
            "device_id": "ac_bedroom",
            "name": "Bedroom AC",
            "type": "air_conditioner",
            "location": "bedroom",
            "power_watts": 1500,
            "default_settings": {"target_temperature": 23, "mode": "cool"}
        },
        {
            "device_id": "humidifier_living",
            "name": "Living Room Humidifier",
            "type": "humidifier",
            "location": "living_room",
            "power_watts": 300,
            "default_settings": {"target_humidity": 45}
        },
        {
            "device_id": "humidifier_bedroom",
            "name": "Bedroom Humidifier",
            "type": "humidifier",
            "location": "bedroom",
            "power_watts": 250,
            "default_settings": {"target_humidity": 50}
        },
        {
            "device_id": "plug_desk",
            "name": "Desk Setup Smart Plug",
            "type": "smart_plug",
            "location": "study_room",
            "power_watts": 0,
            "default_settings": {}
        },
        {
            "device_id": "plug_floor_lamp",
            "name": "Floor Lamp Smart Plug",
            "type": "smart_plug",
            "location": "living_room",
            "power_watts": 0,
            "default_settings": {}
        },
        {
            "device_id": "plug_tv",
            "name": "TV Smart Plug",
            "type": "smart_plug",
            "location": "living_room",
            "power_watts": 0,
            "default_settings": {}
        }
    ]
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # 2. electricity rates (distractor)
    rates = [
        {"period": "off_peak", "start_hour": 0, "end_hour": 7, "rate_per_kwh": 0.08, "label": "Off-Peak"},
        {"period": "mid_peak", "start_hour": 7, "end_hour": 17, "rate_per_kwh": 0.15, "label": "Mid-Peak"},
        {"period": "peak", "start_hour": 17, "end_hour": 21, "rate_per_kwh": 0.25, "label": "Peak"},
        {"period": "mid_peak_evening", "start_hour": 21, "end_hour": 24, "rate_per_kwh": 0.15, "label": "Mid-Peak"}
    ]
    with open("data/electricity/rates.json", "w") as f:
        json.dump({"rates": rates}, f, indent=2)

    # 3. weather (distractor)
    weather = {
        "timestamp": "2025-01-15T14:00:00",
        "temperature": 32.0,
        "humidity": 55,
        "conditions": "sunny",
        "feels_like": 34.0,
        "uv_index": 6
    }
    with open("data/weather/weather.json", "w") as f:
        json.dump({"weather_data": weather}, f, indent=2)

    # 4. health.json – two users, Jane with asthma
    users = [
        {
            "user_id": "jane_smith",
            "name": "Jane Smith",
            "age": 34,
            "health_conditions": ["asthma", "allergies"],
            "respiratory_issues": True,
            "cardiovascular_risk": False,
            "temperature_preference": {"min": 22, "max": 25},
            "humidity_preference": {"min": 40, "max": 60},
            "sleep_schedule": {"sleep": "22:00", "wake": "06:00"}
        },
        {
            "user_id": "john_smith",
            "name": "John Smith",
            "age": 36,
            "health_conditions": [],
            "respiratory_issues": False,
            "cardiovascular_risk": False,
            "temperature_preference": {"min": 20, "max": 24},
            "humidity_preference": {"min": 30, "max": 50},
            "sleep_schedule": {"sleep": "23:00", "wake": "07:00"}
        }
    ]
    with open("data/health/health.json", "w") as f:
        json.dump({"users": users}, f, indent=2)

    # 5. device_status.json – current operational state
    # We deliberately set some devices outside Jane's preference to create conflicts
    status_list = [
        {
            "device_id": "ac_living",
            "power_on": True,
            "current_temperature": 24.0,
            "current_humidity": None,   # AC doesn't control humidity
            "target_temperature": 24.0,
            "mode": "cool"
        },
        {
            "device_id": "ac_bedroom",
            "power_on": True,
            "current_temperature": 21.0,   # too low (<22)
            "current_humidity": None,
            "target_temperature": 21.0,
            "mode": "cool"
        },
        {
            "device_id": "humidifier_living",
            "power_on": True,
            "current_temperature": None,
            "current_humidity": 35,       # too low (<40)
            "target_humidity": 35,
            "mode": "auto"
        },
        {
            "device_id": "humidifier_bedroom",
            "power_on": True,
            "current_temperature": None,
            "current_humidity": 55,       # within range (40-60)
            "target_humidity": 55,
            "mode": "auto"
        },
        # Smart plugs have no climate data
        {
            "device_id": "plug_desk",
            "power_on": True,
            "current_temperature": None,
            "current_humidity": None
        },
        {
            "device_id": "plug_floor_lamp",
            "power_on": False,
            "current_temperature": None,
            "current_humidity": None
        },
        {
            "device_id": "plug_tv",
            "power_on": True,
            "current_temperature": None,
            "current_humidity": None
        }
    ]
    with open("data/status/device_status.json", "w") as f:
        json.dump({"statuses": status_list}, f, indent=2)

    # 6. Create some distractor log files
    with open("data/logs/hvac_2025-01.log", "w") as f:
        f.write("dummy log content for distraction")
    with open("data/logs/sensor_calibration.json", "w") as f:
        json.dump({"calibration": "irrelevant"}, f, indent=2)

if __name__ == "__main__":
    build_env()
