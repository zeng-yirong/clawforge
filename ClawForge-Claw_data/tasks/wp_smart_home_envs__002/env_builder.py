import os
import json
import random

def build_env():
    # Ensure base directories exist
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/electricity", exist_ok=True)
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)
    
    # Accounts (decoration, unused in task)
    accounts = [
        {"account_id": "acc_001", "account_name": "Smith Family", "email": "smith@example.com", "role": "owner", "display_name": "Smiths"},
        {"account_id": "acc_002", "account_name": "Guest IoT", "email": "guest@iot.com", "role": "viewer", "display_name": "Guest"}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)
    
    # Devices: two air conditioners, two humidifiers, some smart plugs
    devices = [
        {"device_id": "ac_bedroom", "name": "Bedroom AC", "type": "air_conditioner", "location": "bedroom", "power_watts": 2000, "default_settings": {"temperature": 24, "mode": "cool"}},
        {"device_id": "ac_living", "name": "Living Room AC", "type": "air_conditioner", "location": "living_room", "power_watts": 2500, "default_settings": {"temperature": 22, "mode": "cool"}},
        {"device_id": "humid_bedroom", "name": "Bedroom Humidifier", "type": "humidifier", "location": "bedroom", "power_watts": 300, "default_settings": {"humidity": 45}},
        {"device_id": "humid_living", "name": "Living Room Humidifier", "type": "humidifier", "location": "living_room", "power_watts": 400, "default_settings": {"humidity": 50}},
        {"device_id": "plug_desk", "name": "Desk Setup Smart Plug", "type": "smart_plug", "location": "study_room", "power_watts": 150, "default_settings": {"state": "off"}},
        {"device_id": "plug_floor_lamp", "name": "Floor Lamp Smart Plug", "type": "smart_plug", "location": "living_room", "power_watts": 60, "default_settings": {"state": "off"}},
        {"device_id": "plug_tv", "name": "TV Smart Plug", "type": "smart_plug", "location": "living_room", "power_watts": 120, "default_settings": {"state": "off"}}
    ]
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)
    
    # Electricity rates: current time is 14:30 -> high_peak (14-17)
    rates = [
        {"period": "high_peak", "start_hour": 14, "end_hour": 17, "rate_per_kwh": 0.45, "label": "High-Peak"},
        {"period": "mid_peak", "start_hour": 10, "end_hour": 14, "rate_per_kwh": 0.25, "label": "Mid-Peak"},
        {"period": "mid_peak_evening", "start_hour": 17, "end_hour": 20, "rate_per_kwh": 0.25, "label": "Mid-Peak"},
        {"period": "off_peak", "start_hour": 0, "end_hour": 10, "rate_per_kwh": 0.12, "label": "Off-Peak"},
        {"period": "peak", "start_hour": 20, "end_hour": 24, "rate_per_kwh": 0.35, "label": "Peak"}
    ]
    with open("data/electricity/rates.json", "w") as f:
        json.dump({"rates": rates}, f, indent=2)
    
    # Health profiles: Jane (respiratory issues, prefers high humidity), John (cardiovascular risk, prefers cool)
    health = [
        {
            "user_id": "user_jane",
            "name": "Jane Smith",
            "age": 34,
            "health_conditions": ["asthma", "allergies"],
            "respiratory_issues": True,
            "cardiovascular_risk": False,
            "temperature_preference": {"min": 22, "max": 24, "unit": "C"},
            "humidity_preference": {"min": 50, "max": 60, "unit": "%"},
            "sleep_schedule": {"bedtime": "22:00", "wakeup": "06:00"}
        },
        {
            "user_id": "user_john",
            "name": "John Smith",
            "age": 45,
            "health_conditions": ["hypertension"],
            "respiratory_issues": False,
            "cardiovascular_risk": True,
            "temperature_preference": {"min": 20, "max": 22, "unit": "C"},
            "humidity_preference": {"min": 40, "max": 50, "unit": "%"},
            "sleep_schedule": {"bedtime": "23:00", "wakeup": "07:00"}
        }
    ]
    with open("data/health/health.json", "w") as f:
        json.dump({"users": health}, f, indent=2)
    
    # Weather: hot and dry
    weather = [
        {"timestamp": "2025-07-15T14:30:00Z", "temperature": 30.0, "humidity": 40, "conditions": "sunny", "feels_like": 32.0, "uv_index": 7}
    ]
    with open("data/weather/weather.json", "w") as f:
        json.dump({"weather_data": weather}, f, indent=2)
    
    # Distractor files
    distractor_dir = "data/old_backups"
    os.makedirs(distractor_dir, exist_ok=True)
    with open(f"{distractor_dir}/devices_2024.json", "w") as f:
        json.dump({"devices": [{"device_id": "old_ac", "name": "Old AC", "type": "air_conditioner"}]}, f, indent=2)
    with open("data/maintenance_log.txt", "w") as f:
        f.write("2025-06-01: HVAC serviced\n2025-07-10: Filter replaced in living room AC\n")
    
    # Create a dummy recommendations file (should be overwritten by agent)
    with open("recommendations.json", "w") as f:
        json.dump({"message": "placeholder"}, f, indent=2)

if __name__ == "__main__":
    build_env()
