import os
import json
import shutil

def build_env():
    # Clean slate
    for item in os.listdir('.'):
        if os.path.isfile(item):
            os.remove(item)
        elif os.path.isdir(item):
            shutil.rmtree(item)

    # Create directory structure
    os.makedirs('data/devices', exist_ok=True)
    os.makedirs('data/health', exist_ok=True)
    os.makedirs('data/electricity', exist_ok=True)
    os.makedirs('data/weather', exist_ok=True)
    os.makedirs('ops', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('temp', exist_ok=True)

    # ------------------- devices -------------------
    devices = [
        {
            "device_id": "ac_bedroom",
            "name": "Bedroom AC",
            "type": "air_conditioner",
            "location": "bedroom",
            "power_watts": 1500,
            "default_settings": {"temperature": 23, "mode": "cool"}
        },
        {
            "device_id": "humidifier_bedroom",
            "name": "Bedroom Humidifier",
            "type": "humidifier",
            "location": "bedroom",
            "power_watts": 300,
            "default_settings": {"target_humidity": 55}
        },
        {
            "device_id": "ac_living",
            "name": "Living Room AC",
            "type": "air_conditioner",
            "location": "living_room",
            "power_watts": 2000,
            "default_settings": {"temperature": 22, "mode": "cool"}
        },
        {
            "device_id": "humidifier_living",
            "name": "Living Room Humidifier",
            "type": "humidifier",
            "location": "living_room",
            "power_watts": 350,
            "default_settings": {"target_humidity": 50}
        },
        {
            "device_id": "tv_plug",
            "name": "TV Smart Plug",
            "type": "smart_plug",
            "location": "living_room",
            "power_watts": 100,
            "default_settings": {}
        },
        {
            "device_id": "floor_lamp",
            "name": "Floor Lamp Smart Plug",
            "type": "smart_plug",
            "location": "living_room",
            "power_watts": 60,
            "default_settings": {}
        },
        {
            "device_id": "desk_plug",
            "name": "Desk Setup Smart Plug",
            "type": "smart_plug",
            "location": "study_room",
            "power_watts": 200,
            "default_settings": {}
        }
    ]
    with open('data/devices/devices.json', 'w') as f:
        json.dump({"devices": devices}, f, indent=2)

    # ----------- distraction: backup (old version) -----------
    old_devices = [d.copy() for d in devices]
    old_devices[0]["power_watts"] = 1800  # outdated value
    with open('data/devices/devices_backup.json', 'w') as f:
        json.dump({"devices": old_devices}, f, indent=2)

    # ------------------- health -------------------
    users = [
        {
            "user_id": "jane_smith",
            "name": "Jane Smith",
            "age": 30,
            "health_conditions": ["asthma"],
            "respiratory_issues": True,
            "cardiovascular_risk": False,
            "temperature_preference": {"min": 22, "max": 24},
            "humidity_preference": {"min": 40, "max": 60},
            "sleep_schedule": {"start": "22:00", "end": "07:00"}
        },
        {
            "user_id": "john_smith",
            "name": "John Smith",
            "age": 32,
            "health_conditions": [],
            "respiratory_issues": False,
            "cardiovascular_risk": False,
            "temperature_preference": {"min": 18, "max": 26},
            "humidity_preference": {"min": 30, "max": 70},
            "sleep_schedule": {"start": "23:00", "end": "08:00"}
        }
    ]
    with open('data/health/health.json', 'w') as f:
        json.dump({"users": users}, f, indent=2)

    # ------------------- electricity rates -------------------
    rates = [
        {"period": "high_peak", "start_hour": 18, "end_hour": 21, "rate_per_kwh": 0.45, "label": "High-Peak"},
        {"period": "mid_peak", "start_hour": 6, "end_hour": 18, "rate_per_kwh": 0.25, "label": "Mid-Peak"},
        {"period": "off_peak", "start_hour": 21, "end_hour": 6, "rate_per_kwh": 0.12, "label": "Off-Peak"}
    ]
    with open('data/electricity/rates.json', 'w') as f:
        json.dump({"rates": rates}, f, indent=2)

    # ------------------- weather -------------------
    weather = {
        "weather_data": {
            "timestamp": "2025-06-12T19:00:00",
            "temperature": 28.0,
            "humidity": 70,
            "conditions": "partly_cloudy",
            "feels_like": 30.0,
            "uv_index": 0
        }
    }
    with open('data/weather/weather.json', 'w') as f:
        json.dump(weather, f, indent=2)

    # ------------------- distraction files -------------------
    # irrelevant logs
    with open('logs/system.log', 'w') as f:
        f.write("2025-06-12 19:01:00 INFO system startup\n")
    with open('logs/energy_report_2025-06-11.csv', 'w') as f:
        f.write("device,power\nac_living,2000\n")
    # temp garbage
    with open('temp/.tmp_cache', 'w') as f:
        f.write("garbage\n")
    # another distraction: fake device status (not to be used)
    with open('data/devices/status.json', 'w') as f:
        json.dump({"status": "all_on"}, f, indent=2)

if __name__ == '__main__':
    build_env()
