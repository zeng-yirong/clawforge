import os
import json
import random
import shutil

def build_env():
    # Clean slate
    for item in os.listdir('.'):
        if os.path.isdir(item):
            shutil.rmtree(item)
        else:
            os.remove(item)

    # Create directory structure
    dirs = [
        'data/devices', 'data/health', 'data/weather', 'data/electricity',
        'data/backups', 'logs', 'temp', 'old_versions'
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # ---------- accounts.json ----------
    accounts = [
        {"account_id": "acc_john", "account_name": "John Smith", "email": "john@home", "role": "resident", "display_name": "John"},
        {"account_id": "acc_jane", "account_name": "Jane Smith", "email": "jane@home", "role": "resident", "display_name": "Jane"}
    ]
    with open('data/accounts.json', 'w') as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # ---------- devices/devices.json ----------
    devices = [
        {"device_id": "ac_bedroom_01", "name": "Bedroom AC", "type": "air_conditioner", "location": "bedroom", "power_watts": 1500, "default_settings": {"mode": "cool", "target_temp_c": 23, "fan_speed": "auto"}},
        {"device_id": "ac_living_01", "name": "Living Room AC", "type": "air_conditioner", "location": "living_room", "power_watts": 2000, "default_settings": {"mode": "cool", "target_temp_c": 26, "fan_speed": "low"}},
        {"device_id": "hum_bedroom_01", "name": "Bedroom Humidifier", "type": "humidifier", "location": "bedroom", "power_watts": 50, "default_settings": {"target_humidity": 60, "mode": "auto"}},
        {"device_id": "hum_living_01", "name": "Living Room Humidifier", "type": "humidifier", "location": "living_room", "power_watts": 60, "default_settings": {"target_humidity": 50, "mode": "auto"}},
        {"device_id": "plug_desk_01", "name": "Desk Setup Smart Plug", "type": "smart_plug", "location": "study_room", "power_watts": 300, "default_settings": {"on": False}},
        {"device_id": "plug_floor_01", "name": "Floor Lamp Smart Plug", "type": "smart_plug", "location": "living_room", "power_watts": 100, "default_settings": {"on": True}},
        {"device_id": "tv_01", "name": "TV Smart Plug", "type": "smart_plug", "location": "living_room", "power_watts": 200, "default_settings": {"on": True}}
    ]
    with open('data/devices/devices.json', 'w') as f:
        json.dump({"devices": devices}, f, indent=2)

    # ---------- health/health.json ----------
    health = [
        {"user_id": "user_john", "name": "John Smith", "age": 45, "health_conditions": ["asthma"], "respiratory_issues": True, "cardiovascular_risk": False,
         "temperature_preference": {"min": 20, "max": 22}, "humidity_preference": {"min": 30, "max": 50}, "sleep_schedule": {"start": "22:00", "end": "06:00"}},
        {"user_id": "user_jane", "name": "Jane Smith", "age": 42, "health_conditions": [], "respiratory_issues": False, "cardiovascular_risk": False,
         "temperature_preference": {"min": 22, "max": 24}, "humidity_preference": {"min": 40, "max": 60}, "sleep_schedule": {"start": "23:00", "end": "07:00"}}
    ]
    with open('data/health/health.json', 'w') as f:
        json.dump({"users": health}, f, indent=2)

    # ---------- weather/weather.json ----------
    weather = {
        "timestamp": "2025-06-12T14:00:00Z",
        "temperature": 32.5,
        "humidity": 55,
        "conditions": "sunny",
        "feels_like": 34.0,
        "uv_index": 7
    }
    with open('data/weather/weather.json', 'w') as f:
        json.dump({"weather_data": weather}, f, indent=2)

    # ---------- electricity/rates.json ----------
    rates = [
        {"period": "off_peak", "start_hour": 0, "end_hour": 6, "rate_per_kwh": 0.05, "label": "Off-Peak"},
        {"period": "mid_peak", "start_hour": 6, "end_hour": 12, "rate_per_kwh": 0.12, "label": "Mid-Peak"},
        {"period": "peak", "start_hour": 12, "end_hour": 15, "rate_per_kwh": 0.25, "label": "Peak"},
        {"period": "mid_peak_evening", "start_hour": 15, "end_hour": 20, "rate_per_kwh": 0.15, "label": "Mid-Peak"},
        {"period": "high_peak", "start_hour": 20, "end_hour": 23, "rate_per_kwh": 0.20, "label": "High-Peak"}
    ]
    with open('data/electricity/rates.json', 'w') as f:
        json.dump({"rates": rates}, f, indent=2)

    # ---------- room_assignments.json (mapping location -> user) ----------
    room_assignments = {
        "bedroom": "user_john",
        "living_room": "user_jane",
        "study_room": "user_john"
    }
    with open('data/room_assignments.json', 'w') as f:
        json.dump(room_assignments, f, indent=2)

    # ---------- current_status.json (simulated current device settings) ----------
    current_status = {
        "ac_bedroom_01": {"mode": "cool", "target_temp_c": 23, "fan_speed": "auto", "power_watts": 1500},
        "ac_living_01": {"mode": "cool", "target_temp_c": 26, "fan_speed": "low", "power_watts": 2000},
        "hum_bedroom_01": {"target_humidity": 60, "mode": "auto", "power_watts": 50},
        "hum_living_01": {"target_humidity": 50, "mode": "auto", "power_watts": 60},
        "plug_desk_01": {"on": False, "power_watts": 0},
        "plug_floor_01": {"on": True, "power_watts": 100},
        "tv_01": {"on": True, "power_watts": 200}
    }
    with open('data/current_status.json', 'w') as f:
        json.dump(current_status, f, indent=2)

    # ---------- Interference files ----------
    # A stale backup copy of devices (outdated)
    stale_devices = [
        {"device_id": "ac_bedroom_01", "name": "Bedroom AC", "type": "air_conditioner", "location": "bedroom", "power_watts": 1500, "default_settings": {"mode": "cool", "target_temp_c": 20}},
        {"device_id": "hum_bedroom_01", "name": "Old Humidifier", "type": "humidifier", "location": "bedroom", "power_watts": 45, "default_settings": {"target_humidity": 70}}
    ]
    with open('data/backups/devices_backup_2024.json', 'w') as f:
        json.dump({"devices": stale_devices}, f, indent=2)

    # A random log in logs/
    with open('logs/system.log', 'w') as f:
        f.write("2025-06-12 13:45:23 INFO ClimateControl started\n")
        f.write("2025-06-12 13:47:01 WARN Humidity sensor bedroom_01 drift > 5%\n")
        f.write("2025-06-12 13:50:12 ERROR AC compressor overcurrent, auto-restart\n")

    # A temp file with partial data
    with open('temp/partial_health.json', 'w') as f:
        json.dump({"user_id": "user_john", "name": "John Smith"}, f)

    # An old_versions directory with irrelevant CSV
    with open('old_versions/device_log_2023.csv', 'w') as f:
        f.write("device_id,power,time\nac_bedroom_01,1500,2023-01-01\n")

if __name__ == "__main__":
    build_env()
