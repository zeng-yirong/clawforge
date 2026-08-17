import json
import os

def build_env():
    # --- data/accounts.json (irrelevant but present) ---
    accounts = [
        {"account_id": "acc001", "account_name": "Smith Family", "email": "smith@home.local", "role": "owner", "display_name": "Smith"},
        {"account_id": "acc002", "account_name": "Guest", "email": "guest@home.local", "role": "guest", "display_name": "Guest"}
    ]
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # --- data/devices/devices.json (6 devices + 1 obsolete as distraction) ---
    devices = [
        {"device_id": "bedroom_ac", "name": "Bedroom AC", "type": "air_conditioner", "location": "bedroom", "power_watts": 1500, "default_settings": {"mode": "cool", "temperature": 22}},
        {"device_id": "bedroom_humidifier", "name": "Bedroom Humidifier", "type": "humidifier", "location": "bedroom", "power_watts": 300, "default_settings": {"humidity": 40}},
        {"device_id": "living_room_ac", "name": "Living Room AC", "type": "air_conditioner", "location": "living_room", "power_watts": 2000, "default_settings": {"mode": "cool", "temperature": 24}},
        {"device_id": "living_room_humidifier", "name": "Living Room Humidifier", "type": "humidifier", "location": "living_room", "power_watts": 350, "default_settings": {"humidity": 45}},
        {"device_id": "desk_plug", "name": "Desk Setup Smart Plug", "type": "smart_plug", "location": "study_room", "power_watts": 100, "default_settings": {"on": True}},
        {"device_id": "tv_plug", "name": "TV Smart Plug", "type": "smart_plug", "location": "living_room", "power_watts": 120, "default_settings": {"on": True}}
    ]
    # distract: an old device entry with missing power_watts
    devices.append({"device_id": "floor_lamp", "name": "Floor Lamp Smart Plug", "type": "smart_plug", "location": "living_room", "power_watts": 60, "default_settings": {"on": False}})  # valid but we'll ignore in answer? Actually it's valid, but we include it.
    os.makedirs("data/devices", exist_ok=True)
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # --- data/electricity/rates.json (peak hours 13-17) ---
    rates = [
        {"period": "peak", "start_hour": 13, "end_hour": 17, "rate_per_kwh": 0.25, "label": "Peak"},
        {"period": "off_peak", "start_hour": 0, "end_hour": 6, "rate_per_kwh": 0.10, "label": "Off-Peak"},
        {"period": "mid_peak", "start_hour": 6, "end_hour": 13, "rate_per_kwh": 0.18, "label": "Mid-Peak"},
        {"period": "mid_peak_evening", "start_hour": 17, "end_hour": 24, "rate_per_kwh": 0.18, "label": "Mid-Peak"}
    ]
    os.makedirs("data/electricity", exist_ok=True)
    with open("data/electricity/rates.json", "w") as f:
        json.dump({"rates": rates}, f, indent=2)

    # --- data/health/health.json (two users, Jane with strict preferences) ---
    users = [
        {
            "user_id": "jane",
            "name": "Jane Smith",
            "age": 30,
            "health_conditions": ["asthma", "hypertension"],
            "respiratory_issues": True,
            "cardiovascular_risk": True,
            "temperature_preference": {"min": 22, "max": 24},
            "humidity_preference": {"min": 40, "max": 50},
            "sleep_schedule": {"bedtime": "22:00", "wakeup": "06:00"}
        },
        {
            "user_id": "john",
            "name": "John Smith",
            "age": 35,
            "health_conditions": ["none"],
            "respiratory_issues": False,
            "cardiovascular_risk": False,
            "temperature_preference": {"min": 20, "max": 26},
            "humidity_preference": {"min": 30, "max": 60},
            "sleep_schedule": {"bedtime": "23:00", "wakeup": "07:00"}
        }
    ]
    os.makedirs("data/health", exist_ok=True)
    with open("data/health/health.json", "w") as f:
        json.dump({"users": users}, f, indent=2)

    # --- data/weather/weather.json (current hot, dry) ---
    weather = [
        {"timestamp": "2025-06-12T14:00:00Z", "temperature": 35.0, "humidity": 30, "conditions": "sunny", "feels_like": 37.0, "uv_index": 8}
    ]
    os.makedirs("data/weather", exist_ok=True)
    with open("data/weather/weather.json", "w") as f:
        json.dump({"weather_data": weather}, f, indent=2)

    # --- extra distraction: a stale backup file ---
    with open("data/weather/weather_old.json", "w") as f:
        json.dump({"weather_data": [{"timestamp": "2025-06-11T14:00:00Z", "temperature": 28.0, "humidity": 50, "conditions": "partly_cloudy"}]}, f, indent=2)

    # ensure ops dir exists (agent will write there)
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
