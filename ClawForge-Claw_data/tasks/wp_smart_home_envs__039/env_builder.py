import os
import json

def build_env():
    # Ensure base directories exist
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/electricity/archived", exist_ok=True)
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- accounts.json (distractor, not needed for task) ---
    accounts = [
        {"account_id": "acc_001", "account_name": "Smith Family", "email": "smith@home.com", "role": "owner", "display_name": "Smith"},
        {"account_id": "acc_002", "account_name": "Johnson Family", "email": "johnson@home.com", "role": "owner", "display_name": "Johnson"}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    # --- devices.json (main device catalog) ---
    devices = [
        {"device_id": "ac_bedroom_01", "name": "Bedroom AC", "type": "air_conditioner", "location": "bedroom", "power_watts": 1500, "default_settings": {"mode": "cool", "temp": 22}},
        {"device_id": "humidifier_bedroom_01", "name": "Bedroom Humidifier", "type": "humidifier", "location": "bedroom", "power_watts": 500, "default_settings": {"target_humidity": 45}},
        {"device_id": "ac_living_01", "name": "Living Room AC", "type": "air_conditioner", "location": "living_room", "power_watts": 2000, "default_settings": {"mode": "cool", "temp": 24}},
        {"device_id": "humidifier_living_01", "name": "Living Room Humidifier", "type": "humidifier", "location": "living_room", "power_watts": 600, "default_settings": {"target_humidity": 50}},
        {"device_id": "tv_plug_01", "name": "TV Smart Plug", "type": "smart_plug", "location": "living_room", "power_watts": 100, "default_settings": {}},
        {"device_id": "floor_lamp_plug_01", "name": "Floor Lamp Smart Plug", "type": "smart_plug", "location": "living_room", "power_watts": 60, "default_settings": {}},
        {"device_id": "desk_plug_01", "name": "Desk Setup Smart Plug", "type": "smart_plug", "location": "study_room", "power_watts": 300, "default_settings": {}},
        {"device_id": "bedroom_plug_01", "name": "Bedroom Desk Smart Plug", "type": "smart_plug", "location": "bedroom", "power_watts": 150, "default_settings": {}}  # bedside lamp – deliberately placed in bedroom to test discrimination
    ]
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f)

    # --- device statuses (current snapshot) ---
    device_statuses = [
        {"device_id": "ac_bedroom_01", "status": "on", "current_temperature": 25, "current_humidity": 35},
        {"device_id": "humidifier_bedroom_01", "status": "on", "current_humidity": 35},
        {"device_id": "ac_living_01", "status": "on", "current_temperature": 27, "current_humidity": 50},
        {"device_id": "humidifier_living_01", "status": "off", "current_humidity": 50},
        {"device_id": "tv_plug_01", "status": "on"},
        {"device_id": "floor_lamp_plug_01", "status": "on"},
        {"device_id": "desk_plug_01", "status": "on"},
        {"device_id": "bedroom_plug_01", "status": "on"}
    ]
    with open("data/devices/status.json", "w") as f:
        json.dump({"device_statuses": device_statuses}, f)

    # --- electricity rates (official) ---
    rates = [
        {"period": "high_peak", "start_hour": 14, "end_hour": 17, "rate_per_kwh": 0.35, "label": "High-Peak"},
        {"period": "mid_peak", "start_hour": 10, "end_hour": 14, "rate_per_kwh": 0.20, "label": "Mid-Peak"},
        {"period": "off_peak", "start_hour": 0, "end_hour": 7, "rate_per_kwh": 0.10, "label": "Off-Peak"},
        {"period": "peak", "start_hour": 17, "end_hour": 21, "rate_per_kwh": 0.30, "label": "Peak"},
        {"period": "mid_peak_evening", "start_hour": 21, "end_hour": 24, "rate_per_kwh": 0.15, "label": "Mid-Peak"}
    ]
    with open("data/electricity/rates.json", "w") as f:
        json.dump({"rates": rates}, f)

    # --- outdated rates as distractor ---
    old_rates = [
        {"period": "peak", "start_hour": 14, "end_hour": 16, "rate_per_kwh": 0.40, "label": "Peak"},
        {"period": "off_peak", "start_hour": 16, "end_hour": 24, "rate_per_kwh": 0.08, "label": "Off-Peak"}
    ]
    with open("data/electricity/archived/rates_old.json", "w") as f:
        json.dump({"rates": old_rates}, f)

    # --- health profiles ---
    health = [
        {"user_id": "user_jane", "name": "Jane Smith", "age": 34, "health_conditions": ["asthma"], "respiratory_issues": True, "cardiovascular_risk": False,
         "temperature_preference": {"min": 22, "max": 24}, "humidity_preference": {"min": 40, "max": 50},
         "sleep_schedule": {"bedtime": "22:00", "wakeup": "06:00"}},
        {"user_id": "user_john", "name": "John Smith", "age": 36, "health_conditions": ["none"], "respiratory_issues": False, "cardiovascular_risk": False,
         "temperature_preference": {"min": 20, "max": 26}, "humidity_preference": {"min": 30, "max": 60},
         "sleep_schedule": {"bedtime": "23:00", "wakeup": "07:00"}}
    ]
    with open("data/health/health.json", "w") as f:
        json.dump({"users": health}, f)

    # --- weather data (contextual, not directly needed for decision) ---
    weather = [
        {"timestamp": "2025-06-12T15:00:00Z", "temperature": 30.0, "humidity": 60, "conditions": "sunny", "feels_like": 32.0, "uv_index": 6}
    ]
    with open("data/weather/weather.json", "w") as f:
        json.dump({"weather_data": weather}, f)

if __name__ == "__main__":
    build_env()
