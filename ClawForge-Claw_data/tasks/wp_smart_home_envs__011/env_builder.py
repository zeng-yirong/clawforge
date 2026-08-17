import os
import json
import random

def build_env():
    # 确保目标目录存在
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/electricity", exist_ok=True)
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)
    os.makedirs("state", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 供 agent 写入产物
    os.makedirs("old_data", exist_ok=True)  # 干扰项

    # --- accounts.json ---
    accounts = [
        {"account_id": "acc-01", "account_name": "Jane Smith", "email": "jane@home.local", "role": "owner", "display_name": "Jane"},
        {"account_id": "acc-02", "account_name": "John Smith", "email": "john@home.local", "role": "owner", "display_name": "John"}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # --- devices.json --- (含干扰设备)
    devices = [
        {"device_id": "AC-001", "name": "Bedroom AC", "type": "air_conditioner", "location": "bedroom", "power_watts": 1500, "default_settings": {"mode": "cool", "fan_speed": "high", "target_temperature": 23}},
        {"device_id": "AC-002", "name": "Living Room AC", "type": "air_conditioner", "location": "living_room", "power_watts": 2000, "default_settings": {"mode": "cool", "fan_speed": "auto", "target_temperature": 25}},
        {"device_id": "HUM-001", "name": "Bedroom Humidifier", "type": "humidifier", "location": "bedroom", "power_watts": 50, "default_settings": {"target_humidity": 45, "mode": "auto"}},
        {"device_id": "HUM-002", "name": "Living Room Humidifier", "type": "humidifier", "location": "living_room", "power_watts": 60, "default_settings": {"target_humidity": 40, "mode": "auto"}},
        {"device_id": "PLG-001", "name": "Desk Setup Smart Plug", "type": "smart_plug", "location": "study_room", "power_watts": 200, "default_settings": {"state": "off"}},
        {"device_id": "PLG-002", "name": "Floor Lamp Smart Plug", "type": "smart_plug", "location": "living_room", "power_watts": 100, "default_settings": {"state": "off"}},
        {"device_id": "PLG-003", "name": "TV Smart Plug", "type": "smart_plug", "location": "living_room", "power_watts": 150, "default_settings": {"state": "off"}}
    ]
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # --- rates.json ---
    rates = [
        {"period": "off_peak", "start_hour": 0, "end_hour": 6, "rate_per_kwh": 0.32, "label": "Off-Peak"},
        {"period": "mid_peak", "start_hour": 6, "end_hour": 14, "rate_per_kwh": 0.65, "label": "Mid-Peak"},
        {"period": "high_peak", "start_hour": 14, "end_hour": 17, "rate_per_kwh": 0.98, "label": "High-Peak"},
        {"period": "mid_peak_evening", "start_hour": 17, "end_hour": 21, "rate_per_kwh": 0.72, "label": "Mid-Peak Evening"},
        {"period": "peak", "start_hour": 21, "end_hour": 24, "rate_per_kwh": 0.85, "label": "Peak"}
    ]
    with open("data/electricity/rates.json", "w") as f:
        json.dump({"rates": rates}, f, indent=2)

    # --- health.json ---
    health = [
        {"user_id": "USR-001", "name": "Jane Smith", "age": 28, "health_conditions": ["asthma"], "respiratory_issues": True, "cardiovascular_risk": False,
         "temperature_preference": {"min": 22, "max": 24}, "humidity_preference": {"min": 40, "max": 50}, "sleep_schedule": {"start": "22:00", "end": "07:00"}},
        {"user_id": "USR-002", "name": "John Smith", "age": 32, "health_conditions": ["hypertension"], "respiratory_issues": False, "cardiovascular_risk": True,
         "temperature_preference": {"min": 23, "max": 26}, "humidity_preference": {"min": 30, "max": 45}, "sleep_schedule": {"start": "23:00", "end": "06:00"}}
    ]
    with open("data/health/health.json", "w") as f:
        json.dump({"users": health}, f, indent=2)

    # --- weather.json ---
    weather = [
        {"timestamp": "2025-06-12T14:00:00", "temperature": 35.2, "humidity": 30, "conditions": "sunny", "feels_like": 38.0, "uv_index": 7}
    ]
    with open("data/weather/weather.json", "w") as f:
        json.dump({"weather_data": weather}, f, indent=2)

    # --- state/session.json (当前设备状态，故意制造冲突) ---
    session_state = {
        "session_id": "smh-20250612T140000Z-001",
        "scenario_id": "energy_aware_climate",
        "current_time": "2025-06-12T14:30:00",
        "device_states": {
            "AC-001": {"mode": "cool", "fan_speed": "high", "target_temperature": 18},      # 温度过低，风速高
            "AC-002": {"mode": "cool", "fan_speed": "auto", "target_temperature": 25},
            "HUM-001": {"mode": "off", "target_humidity": 30},                              # 湿度过低，关闭
            "HUM-002": {"mode": "auto", "target_humidity": 40},
            "PLG-001": {"state": "on"},    # 尽管插着电脑，但不涉及健康
            "PLG-002": {"state": "off"},
            "PLG-003": {"state": "on"}
        }
    }
    with open("state/session.json", "w") as f:
        json.dump(session_state, f, indent=2)

    # --- 干扰项：旧备份和日志 ---
    os.makedirs("old_data/versions", exist_ok=True)
    with open("old_data/versions/devices_backup_2025-01.json", "w") as f:
        json.dump({"old_devices": []}, f)
    with open("old_data/versions/rates_2024.json", "w") as f:
        json.dump({"old_rates": []}, f)
    os.makedirs("logs", exist_ok=True)
    with open("logs/system.log", "w") as f:
        f.write("2025-06-12 14:00 ERROR: temperature sensor AC-001 stuck\n")

if __name__ == "__main__":
    build_env()
