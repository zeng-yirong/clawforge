import os
import json

def build_env():
    # Create directories
    dirs = [
        "data/health",
        "data/devices",
        "data/electricity",
        "data/weather",
        "data/session",
        # ops is left for agent to create
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # health.json – two users, Jane has conflicts, John has no conflicts
    health = {
        "users": [
            {
                "user_id": "jane_smith",
                "name": "Jane Smith",
                "age": 32,
                "health_conditions": ["asthma"],
                "respiratory_issues": True,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 22, "max": 24},
                "humidity_preference": {"min": 40, "max": 60},
                "sleep_schedule": {"bedtime": "22:00", "wakeup": "06:00"}
            },
            {
                "user_id": "john_smith",
                "name": "John Smith",
                "age": 35,
                "health_conditions": [],
                "respiratory_issues": False,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 20, "max": 28},
                "humidity_preference": {"min": 20, "max": 80},
                "sleep_schedule": {"bedtime": "23:00", "wakeup": "07:00"}
            }
        ]
    }
    with open("data/health/health.json", "w") as f:
        json.dump(health, f, indent=2)

    # devices.json – bedroom and living room devices
    devices = {
        "devices": [
            {
                "device_id": "bd_ac_001",
                "name": "Bedroom AC",
                "type": "air_conditioner",
                "location": "bedroom",
                "power_watts": 1500,
                "default_settings": {"temperature": 24, "mode": "cool"}
            },
            {
                "device_id": "bd_hum_001",
                "name": "Bedroom Humidifier",
                "type": "humidifier",
                "location": "bedroom",
                "power_watts": 200,
                "default_settings": {"humidity": 50}
            },
            {
                "device_id": "lr_ac_001",
                "name": "Living Room AC",
                "type": "air_conditioner",
                "location": "living_room",
                "power_watts": 2000,
                "default_settings": {"temperature": 22, "mode": "cool"}
            },
            {
                "device_id": "lr_hum_001",
                "name": "Living Room Humidifier",
                "type": "humidifier",
                "location": "living_room",
                "power_watts": 250,
                "default_settings": {"humidity": 45}
            },
            {
                "device_id": "sp_desk_001",
                "name": "Desk Setup Smart Plug",
                "type": "smart_plug",
                "location": "study_room",
                "power_watts": 300,
                "default_settings": {"on": False}
            },
            {
                "device_id": "sp_floor_001",
                "name": "Floor Lamp Smart Plug",
                "type": "smart_plug",
                "location": "living_room",
                "power_watts": 100,
                "default_settings": {"on": False}
            },
            {
                "device_id": "tv_plug_001",
                "name": "TV Smart Plug",
                "type": "smart_plug",
                "location": "living_room",
                "power_watts": 200,
                "default_settings": {"on": False}
            }
        ]
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # electricity rates – peak at 14-17
    rates = {
        "rates": [
            {"period": "off_peak", "start_hour": 0, "end_hour": 6, "rate_per_kwh": 0.08, "label": "Off-Peak"},
            {"period": "mid_peak", "start_hour": 7, "end_hour": 13, "rate_per_kwh": 0.15, "label": "Mid-Peak"},
            {"period": "peak", "start_hour": 14, "end_hour": 17, "rate_per_kwh": 0.30, "label": "Peak"},
            {"period": "mid_peak_evening", "start_hour": 18, "end_hour": 21, "rate_per_kwh": 0.15, "label": "Mid-Peak"},
            {"period": "off_peak_night", "start_hour": 22, "end_hour": 23, "rate_per_kwh": 0.08, "label": "Off-Peak"}
        ]
    }
    with open("data/electricity/rates.json", "w") as f:
        json.dump(rates, f, indent=2)

    # weather – outdoor hot and dry
    weather = {
        "weather_data": [
            {"timestamp": "2025-06-15T15:30:00Z", "temperature": 35.0, "humidity": 20, "conditions": "sunny", "feels_like": 38.0, "uv_index": 7}
        ]
    }
    with open("data/weather/weather.json", "w") as f:
        json.dump(weather, f, indent=2)

    # session current state – bedroom readings causing conflicts
    session = {
        "session_id": "smh-20250615T153000Z-9999",
        "timestamp": "2025-06-15T15:30:00Z",
        "rooms": [
            {
                "name": "bedroom",
                "temperature": 26.0,
                "humidity": 35,
                "timestamp": "2025-06-15T15:30:00Z"
            },
            {
                "name": "living_room",
                "temperature": 22.0,
                "humidity": 50,
                "timestamp": "2025-06-15T15:30:00Z"
            }
        ]
    }
    with open("data/session/current.json", "w") as f:
        json.dump(session, f, indent=2)

if __name__ == "__main__":
    build_env()
