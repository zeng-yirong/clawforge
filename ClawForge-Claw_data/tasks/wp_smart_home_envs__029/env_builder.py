import os
import json
import random

def build_env():
    # 确保目录结构
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---- 1. accounts.json (干扰项：无用但合法) ----
    accounts = {
        "accounts": [
            {"account_id": "acc-001", "account_name": "Li Jie", "email": "li@home.com", "role": "owner", "display_name": "李姐"},
            {"account_id": "acc-002", "account_name": "John Smith", "email": "john@home.com", "role": "member", "display_name": "John"}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ---- 2. data/devices/devices.json (含干扰：两个不相干的设备) ----
    devices = {
        "devices": [
            {"device_id": "ac-bedroom", "name": "Bedroom AC", "type": "air_conditioner", "location": "bedroom", "power_watts": 2000, "default_settings": {"temperature": 24, "mode": "cool"}},
            {"device_id": "humid-bedroom", "name": "Bedroom Humidifier", "type": "humidifier", "location": "bedroom", "power_watts": 300, "default_settings": {"humidity": 45}},
            {"device_id": "ac-livingroom", "name": "Living Room AC", "type": "air_conditioner", "location": "living_room", "power_watts": 2500, "default_settings": {"temperature": 22, "mode": "cool"}},
            {"device_id": "plug-tv", "name": "TV Smart Plug", "type": "smart_plug", "location": "living_room", "power_watts": 150, "default_settings": {"state": "off"}},
            {"device_id": "plug-desk", "name": "Desk Setup Smart Plug", "type": "smart_plug", "location": "study_room", "power_watts": 500, "default_settings": {"state": "off"}},
        ]
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # ---- 3. data/electricity/rates.json ----
    rates = {
        "rates": [
            {"period": "off_peak", "start_hour": 0, "end_hour": 7, "rate_per_kwh": 0.12, "label": "Off-Peak"},
            {"period": "mid_peak", "start_hour": 7, "end_hour": 11, "rate_per_kwh": 0.18, "label": "Mid-Peak"},
            {"period": "mid_peak_evening", "start_hour": 17, "end_hour": 21, "rate_per_kwh": 0.18, "label": "Mid-Peak Evening"},
            {"period": "high_peak", "start_hour": 11, "end_hour": 17, "rate_per_kwh": 0.25, "label": "High-Peak"},
            {"period": "peak", "start_hour": 21, "end_hour": 24, "rate_per_kwh": 0.25, "label": "Peak"}
        ]
    }
    with open("data/electricity/rates.json", "w") as f:
        json.dump(rates, f, indent=2)

    # ---- 4. data/health/health.json ----
    health = {
        "users": [
            {
                "user_id": "user-john",
                "name": "John Smith",
                "age": 42,
                "health_conditions": ["asthma"],
                "respiratory_issues": True,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 22, "max": 24, "unit": "celsius"},
                "humidity_preference": {"min": 40, "max": 60, "unit": "%"},
                "sleep_schedule": {"bedtime": "22:00", "wakeup": "07:00"}
            }
        ]
    }
    with open("data/health/health.json", "w") as f:
        json.dump(health, f, indent=2)

    # ---- 5. data/weather/weather.json (今天实际值，使计算唯一) ----
    weather = {
        "weather_data": [
            {"timestamp": "2025-02-18T20:00:00Z", "temperature": 28.0, "humidity": 70, "conditions": "sunny", "feels_like": 29.5, "uv_index": 0}
        ]
    }
    with open("data/weather/weather.json", "w") as f:
        json.dump(weather, f, indent=2)

    # ---- 6. 干扰项：一个“旧方案”文件，内容为空但存在 ----
    with open("ops/old_plan.json", "w") as f:
        json.dump({"note": "do not use"}, f, indent=2)

    # ---- 7. 一个隐藏的日志文件（无关） ----
    with open("data/activity.log", "w") as f:
        f.write("[INFO] 2025-02-18 20:00: system ready\n")

if __name__ == "__main__":
    build_env()
