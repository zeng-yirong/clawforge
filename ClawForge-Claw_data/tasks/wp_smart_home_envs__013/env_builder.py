import os
import json

def build_env():
    # Create directories
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/electricity", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)

    # Main health file
    health = {
        "users": [
            {
                "user_id": "user_jane",
                "name": "Jane Smith",
                "age": 32,
                "health_conditions": ["asthma"],
                "respiratory_issues": True,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 22, "max": 25},
                "humidity_preference": {"min": 40, "max": 60},
                "sleep_schedule": {"sleep_start": "22:00", "wake_up": "07:00"}
            }
        ]
    }
    with open("data/health/health.json", "w") as f:
        json.dump(health, f, indent=2)

    # Main devices file
    devices = {
        "devices": [
            {"device_id": "ac_bedroom_01", "name": "Bedroom AC", "type": "air_conditioner", "location": "bedroom", "power_watts": 2000, "default_settings": {"temperature": 20, "mode": "cool", "fan_speed": "auto"}},
            {"device_id": "humidifier_bedroom_01", "name": "Bedroom Humidifier", "type": "humidifier", "location": "bedroom", "power_watts": 500, "default_settings": {"humidity": 30, "mode": "auto"}},
            {"device_id": "ac_living_01", "name": "Living Room AC", "type": "air_conditioner", "location": "living_room", "power_watts": 2500, "default_settings": {"temperature": 24, "mode": "cool", "fan_speed": "low"}},
            {"device_id": "plug_desk_01", "name": "Desk Setup Smart Plug", "type": "smart_plug", "location": "study_room", "power_watts": 300, "default_settings": {"on": False}},
            {"device_id": "plug_floor_lamp_01", "name": "Floor Lamp Smart Plug", "type": "smart_plug", "location": "living_room", "power_watts": 100, "default_settings": {"on": True}}
        ]
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # Device status file
    status = {
        "statuses": [
            {"device_id": "ac_bedroom_01", "on": True, "current_temperature": 20, "current_humidity": 30, "last_updated": "2025-06-12T14:30:00Z"},
            {"device_id": "humidifier_bedroom_01", "on": True, "current_humidity": 30, "last_updated": "2025-06-12T14:30:00Z"},
            {"device_id": "ac_living_01", "on": True, "current_temperature": 24, "current_humidity": 50, "last_updated": "2025-06-12T14:30:00Z"},
            {"device_id": "plug_desk_01", "on": False, "last_updated": "2025-06-12T14:00:00Z"},
            {"device_id": "plug_floor_lamp_01", "on": True, "last_updated": "2025-06-12T14:00:00Z"}
        ]
    }
    with open("data/devices/status.json", "w") as f:
        json.dump(status, f, indent=2)

    # Electricity rates
    rates = {
        "rates": [
            {"period": "peak", "start_hour": 13, "end_hour": 17, "rate_per_kwh": 0.352, "label": "Peak"},
            {"period": "off_peak", "start_hour": 22, "end_hour": 7, "rate_per_kwh": 0.12, "label": "Off-Peak"},
            {"period": "mid_peak", "start_hour": 7, "end_hour": 13, "rate_per_kwh": 0.2, "label": "Mid-Peak"},
            {"period": "mid_peak_evening", "start_hour": 17, "end_hour": 22, "rate_per_kwh": 0.25, "label": "Mid-Peak Evening"}
        ]
    }
    with open("data/electricity/rates.json", "w") as f:
        json.dump(rates, f, indent=2)

    # Weather data
    weather = {
        "weather_data": [
            {"timestamp": "2025-06-12T14:00:00Z", "temperature": 33.5, "humidity": 70, "conditions": "sunny", "feels_like": 36.0, "uv_index": 7}
        ]
    }
    with open("data/weather/weather.json", "w") as f:
        json.dump(weather, f, indent=2)

    # Current time marker
    with open("current_time.txt", "w") as f:
        f.write("14:30")

    # Distraction files
    old_health = {"users": [{"user_id": "guest", "name": "Guest", "age": 40, "health_conditions": [], "respiratory_issues": False, "cardiovascular_risk": True, "temperature_preference": {"min": 20, "max": 26}, "humidity_preference": {"min": 30, "max": 50}}]}
    with open("data/health/health_backup.json", "w") as f:
        json.dump(old_health, f, indent=2)

    old_devices = {"devices": [{"device_id": "old_ac", "name": "Old AC", "type": "air_conditioner"}]}
    with open("data/devices/old_devices.json", "w") as f:
        json.dump(old_devices, f, indent=2)

    rates_draft = {"rates": [{"period": "peak", "start_hour": 10, "end_hour": 14, "rate_per_kwh": 0.4}]}
    with open("data/electricity/rates_draft.json", "w") as f:
        json.dump(rates_draft, f, indent=2)

    forecast = {"weather_data": [{"timestamp": "2025-06-12T18:00:00Z", "temperature": 28.0, "humidity": 60}]}
    with open("data/weather/forecast.json", "w") as f:
        json.dump(forecast, f, indent=2)

    with open("system.log", "w") as f:
        f.write("2025-06-12 14:00:00 INFO Device ac_bedroom_01 started\n2025-06-12 14:01:00 WARN High humidity detected\n")

if __name__ == "__main__":
    build_env()
