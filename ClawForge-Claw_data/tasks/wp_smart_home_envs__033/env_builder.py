import os
import json
import shutil

def build_env():
    # 清理工作区，确保干净
    if os.path.exists("data"):
        shutil.rmtree("data")
    if os.path.exists("ops"):
        shutil.rmtree("ops")
    if os.path.exists("old_backups"):
        shutil.rmtree("old_backups")
    if os.path.exists("logs"):
        shutil.rmtree("logs")

    # 创建目录
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/electricity", exist_ok=True)
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)
    os.makedirs("data/accounts", exist_ok=True)
    os.makedirs("old_backups", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # ===== devices.json =====
    devices = [
        {
            "device_id": "AC-01",
            "name": "Bedroom AC",
            "type": "air_conditioner",
            "location": "bedroom",
            "power_watts": 1500,
            "status": "on",
            "current_settings": {"temperature": 28, "mode": "cool"}
        },
        {
            "device_id": "AC-02",
            "name": "Living Room AC",
            "type": "air_conditioner",
            "location": "living_room",
            "power_watts": 2000,
            "status": "on",
            "current_settings": {"temperature": 24, "mode": "cool"}
        },
        {
            "device_id": "HUM-01",
            "name": "Bedroom Humidifier",
            "type": "humidifier",
            "location": "bedroom",
            "power_watts": 40,
            "status": "on",
            "current_settings": {"humidity": 30}
        },
        {
            "device_id": "HUM-02",
            "name": "Living Room Humidifier",
            "type": "humidifier",
            "location": "living_room",
            "power_watts": 45,
            "status": "on",
            "current_settings": {"humidity": 45}
        },
        {
            "device_id": "PLUG-01",
            "name": "Desk Setup Smart Plug",
            "type": "smart_plug",
            "location": "study_room",
            "power_watts": 0,
            "status": "off",
            "current_settings": {}
        },
        {
            "device_id": "AC-03",
            "name": "Study Room AC",
            "type": "air_conditioner",
            "location": "study_room",
            "power_watts": 1200,
            "status": "off",
            "current_settings": {"temperature": 22, "mode": "cool"}
        }
    ]
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # ===== health.json =====
    users = [
        {
            "user_id": "user-001",
            "name": "John Smith",
            "age": 70,
            "room": "bedroom",
            "health_conditions": ["asthma"],
            "respiratory_issues": True,
            "cardiovascular_risk": False,
            "temperature_preference": {"min": 22, "max": 24},
            "humidity_preference": {"min": 40, "max": 50},
            "sleep_schedule": {"start": 22, "end": 7}
        },
        {
            "user_id": "user-002",
            "name": "Jane Smith",
            "age": 65,
            "room": "living_room",
            "health_conditions": ["hypertension"],
            "respiratory_issues": False,
            "cardiovascular_risk": True,
            "temperature_preference": {"min": 20, "max": 26},
            "humidity_preference": {"min": 30, "max": 60},
            "sleep_schedule": {"start": 23, "end": 6}
        }
    ]
    with open("data/health/health.json", "w") as f:
        json.dump({"users": users}, f, indent=2)

    # ===== rates.json =====
    rates = [
        {"period": "peak", "start_hour": 14, "end_hour": 17, "rate_per_kwh": 0.45, "label": "Peak"},
        {"period": "mid_peak", "start_hour": 10, "end_hour": 14, "rate_per_kwh": 0.30, "label": "Mid-Peak"},
        {"period": "mid_peak_evening", "start_hour": 17, "end_hour": 20, "rate_per_kwh": 0.30, "label": "Mid-Peak"},
        {"period": "off_peak", "start_hour": 0, "end_hour": 6, "rate_per_kwh": 0.15, "label": "Off-Peak"},
        {"period": "high_peak", "start_hour": 6, "end_hour": 10, "rate_per_kwh": 0.50, "label": "High-Peak"}
    ]
    with open("data/electricity/rates.json", "w") as f:
        json.dump({"rates": rates}, f, indent=2)

    # ===== weather.json =====
    weather = [
        {
            "timestamp": "2025-06-12T15:00:00",
            "temperature": 35.0,
            "humidity": 20,
            "conditions": "sunny",
            "feels_like": 37.0,
            "uv_index": 8
        }
    ]
    with open("data/weather/weather.json", "w") as f:
        json.dump({"weather_data": weather}, f, indent=2)

    # ===== accounts.json (干扰) =====
    accounts = [
        {"account_id": "acc-01", "account_name": "Smith Family", "email": "smith@home.com", "role": "owner", "display_name": "Smith Home"}
    ]
    with open("data/accounts/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # ===== 旧备份干扰 =====
    with open("old_backups/devices_2024.json", "w") as f:
        json.dump({"devices": []}, f)
    with open("old_backups/rates_old.json", "w") as f:
        json.dump({"rates": []}, f)

    # ===== logs 干扰 =====
    with open("logs/system.log", "w") as f:
        f.write("INFO: system started\n")
        f.write("ERROR: sensor timeout\n")

    # 创建 ops 目录（只需存在，agent 会写文件）
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
