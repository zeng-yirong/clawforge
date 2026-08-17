import os
import json

def build_env():
    # Create directories
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/electricity", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # Distraction: log file
    with open("logs/system.log", "w") as f:
        f.write("2025-02-15 14:23:45 [INFO] System health check passed\n")

    # Devices data
    devices = {
        "devices": [
            {
                "device_id": "ac_bedroom_1",
                "name": "Bedroom AC",
                "type": "air_conditioner",
                "location": "bedroom",
                "power_watts": 1500,
                "default_settings": {"target_temperature": 24.0, "mode": "cool"}
            },
            {
                "device_id": "ac_living_1",
                "name": "Living Room AC",
                "type": "air_conditioner",
                "location": "living_room",
                "power_watts": 2000,
                "default_settings": {"target_temperature": 24.0, "mode": "cool"}   # ← conflict for John
            },
            {
                "device_id": "hum_bedroom_1",
                "name": "Bedroom Humidifier",
                "type": "humidifier",
                "location": "bedroom",
                "power_watts": 300,
                "default_settings": {"target_humidity": 35}   # ← conflict for Jane
            },
            {
                "device_id": "hum_living_1",
                "name": "Living Room Humidifier",
                "type": "humidifier",
                "location": "living_room",
                "power_watts": 350,
                "default_settings": {"target_humidity": 45}
            },
            {
                "device_id": "plug_desk_1",
                "name": "Desk Setup Smart Plug",
                "type": "smart_plug",
                "location": "study_room",
                "power_watts": 100,
                "default_settings": {"on": True}
            },
            {
                "device_id": "plug_floor_lamp",
                "name": "Floor Lamp Smart Plug",
                "type": "smart_plug",
                "location": "living_room",
                "power_watts": 60,
                "default_settings": {"on": False}
            }
        ]
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # Distraction: old devices backup
    with open("data/devices/old_devices.json", "w") as f:
        json.dump({"devices": [{"device_id": "ac_old"}]}, f)

    # Health data
    health = {
        "users": [
            {
                "user_id": "user_jane",
                "name": "Jane Smith",
                "age": 32,
                "health_conditions": ["asthma"],
                "respiratory_issues": True,
                "cardiovascular_risk": False,
                "temperature_preference": {"min_temp": 22.0, "max_temp": 25.0},
                "humidity_preference": {"min_humidity": 40, "max_humidity": 60},
                "sleep_schedule": {"start": "22:00", "end": "07:00"},
                "room": "bedroom"
            },
            {
                "user_id": "user_john",
                "name": "John Smith",
                "age": 35,
                "health_conditions": ["hypertension"],
                "respiratory_issues": False,
                "cardiovascular_risk": True,
                "temperature_preference": {"min_temp": 20.0, "max_temp": 23.0},
                "humidity_preference": {"min_humidity": 30, "max_humidity": 50},
                "sleep_schedule": {"start": "23:00", "end": "06:00"},
                "room": "living_room"
            }
        ]
    }
    with open("data/health/health.json", "w") as f:
        json.dump(health, f, indent=2)

    # Electricity rates (distraction, not used in verification)
    rates = {
        "rates": [
            {"period": "off_peak", "start_hour": 0, "end_hour": 6, "rate_per_kwh": 0.10, "label": "Off-Peak"},
            {"period": "mid_peak", "start_hour": 6, "end_hour": 17, "rate_per_kwh": 0.15, "label": "Mid-Peak"},
            {"period": "peak", "start_hour": 17, "end_hour": 21, "rate_per_kwh": 0.25, "label": "Peak"},
            {"period": "mid_peak_evening", "start_hour": 21, "end_hour": 24, "rate_per_kwh": 0.15, "label": "Mid-Peak"}
        ]
    }
    with open("data/electricity/rates.json", "w") as f:
        json.dump(rates, f, indent=2)

    # Weather data (distraction)
    weather = {
        "weather_data": [
            {"timestamp": "2025-02-15T14:00:00Z", "temperature": 28.0, "humidity": 70, "conditions": "sunny", "feels_like": 31.0, "uv_index": 7}
        ]
    }
    with open("data/weather/weather.json", "w") as f:
        json.dump(weather, f, indent=2)

if __name__ == "__main__":
    build_env()
