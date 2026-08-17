import json
import os

def build_env():
    # Create directory structure
    dirs = [
        "data/devices",
        "data/electricity",
        "data/health",
        "data/weather",
        "data/backups",
        "data/logs",
        "ops"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # accounts.json
    accounts = {
        "accounts": [
            {
                "account_id": "acc_john_smith",
                "account_name": "John Smith",
                "email": "john.smith@home.com",
                "role": "owner",
                "display_name": "John"
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # devices.json
    devices = {
        "devices": [
            {
                "device_id": "ac_bedroom_01",
                "name": "Bedroom AC",
                "type": "air_conditioner",
                "location": "bedroom",
                "power_watts": 1500,
                "default_settings": {"mode": "cool", "target_temperature": 18, "fan_speed": "medium"}
            },
            {
                "device_id": "humidifier_bedroom_01",
                "name": "Bedroom Humidifier",
                "type": "humidifier",
                "location": "bedroom",
                "power_watts": 50,
                "default_settings": {"target_humidity": 30, "auto_mode": True}
            },
            {
                "device_id": "ac_living_01",
                "name": "Living Room AC",
                "type": "air_conditioner",
                "location": "living_room",
                "power_watts": 2000,
                "default_settings": {"mode": "cool", "target_temperature": 24, "fan_speed": "auto"}
            },
            {
                "device_id": "plug_desk_01",
                "name": "Desk Setup Smart Plug",
                "type": "smart_plug",
                "location": "study_room",
                "power_watts": 0,
                "default_settings": {"state": "off"}
            },
            {
                "device_id": "plug_floor_lamp_01",
                "name": "Floor Lamp Smart Plug",
                "type": "smart_plug",
                "location": "living_room",
                "power_watts": 60,
                "default_settings": {"state": "off"}
            }
        ]
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # device status (current operational state, may differ from defaults)
    status = {
        "status": [
            {
                "device_id": "ac_bedroom_01",
                "current_temperature": 18,
                "mode": "cool",
                "fan_speed": "high"
            },
            {
                "device_id": "humidifier_bedroom_01",
                "current_humidity": 30,
                "auto_mode": True,
                "water_level_percent": 80
            },
            {
                "device_id": "ac_living_01",
                "current_temperature": 24,
                "mode": "cool",
                "fan_speed": "auto"
            }
        ]
    }
    with open("data/devices/status.json", "w") as f:
        json.dump(status, f, indent=2)

    # electricity rates (distracting, not used in final answer)
    rates = {
        "rates": [
            {"period": "off_peak", "start_hour": 0, "end_hour": 6, "rate_per_kwh": 0.12, "label": "Off-Peak"},
            {"period": "mid_peak", "start_hour": 6, "end_hour": 16, "rate_per_kwh": 0.18, "label": "Mid-Peak"},
            {"period": "peak", "start_hour": 16, "end_hour": 21, "rate_per_kwh": 0.28, "label": "Peak"},
            {"period": "mid_peak_evening", "start_hour": 21, "end_hour": 24, "rate_per_kwh": 0.18, "label": "Mid-Peak"}
        ]
    }
    with open("data/electricity/rates.json", "w") as f:
        json.dump(rates, f, indent=2)

    # health.json – John has asthma; Jane is fine
    health = {
        "users": [
            {
                "user_id": "user_john",
                "name": "John Smith",
                "age": 42,
                "health_conditions": ["asthma", "allergic_rhinitis"],
                "respiratory_issues": True,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 22, "max": 24, "optimal": 23},
                "humidity_preference": {"min": 45, "max": 55, "optimal": 50},
                "sleep_schedule": {"bedtime": "22:00", "wakeup": "06:00"}
            },
            {
                "user_id": "user_jane",
                "name": "Jane Smith",
                "age": 38,
                "health_conditions": [],
                "respiratory_issues": False,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 20, "max": 22, "optimal": 21},
                "humidity_preference": {"min": 40, "max": 50, "optimal": 45},
                "sleep_schedule": {"bedtime": "23:00", "wakeup": "07:00"}
            }
        ]
    }
    with open("data/health/health.json", "w") as f:
        json.dump(health, f, indent=2)

    # weather (distracting)
    weather = {
        "weather_data": [
            {"timestamp": "2025-04-01T12:00:00Z", "temperature": 28.0, "humidity": 65, "conditions": "sunny", "feels_like": 30.0, "uv_index": 7}
        ]
    }
    with open("data/weather/weather.json", "w") as f:
        json.dump(weather, f, indent=2)

    # distraction files
    with open("data/logs/system.log", "w") as f:
        f.write("2025-04-01 22:15:00 INFO Sensor reading: bedroom temp=18.2, humidity=31\n")
        f.write("2025-04-01 22:16:00 WARN Bedroom AC override triggered by app\n")
    with open("data/backups/old_devices.json", "w") as f:
        json.dump({"old_devices": []}, f, indent=2)
    # ops directory is empty – agent will create the output

if __name__ == "__main__":
    build_env()
