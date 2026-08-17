import json
import os

def build_env():
    # 创建数据目录
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/electricity", exist_ok=True)
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)
    os.makedirs("data/old", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # ---------- 设备清单 ----------
    devices = [
        {
            "device_id": "ac_bedroom",
            "name": "Bedroom AC",
            "type": "air_conditioner",
            "location": "bedroom",
            "power_watts": 2000,
            "default_settings": {"mode": "cool", "temperature": 24}
        },
        {
            "device_id": "humid_bedroom",
            "name": "Bedroom Humidifier",
            "type": "humidifier",
            "location": "bedroom",
            "power_watts": 500,
            "default_settings": {"humidity": 45}
        },
        {
            "device_id": "ac_living",
            "name": "Living Room AC",
            "type": "air_conditioner",
            "location": "living_room",
            "power_watts": 2500,
            "default_settings": {"mode": "cool", "temperature": 24}
        },
        {
            "device_id": "humid_living",
            "name": "Living Room Humidifier",
            "type": "humidifier",
            "location": "living_room",
            "power_watts": 400,
            "default_settings": {"humidity": 40}
        },
        {
            "device_id": "plug_tv",
            "name": "TV Smart Plug",
            "type": "smart_plug",
            "location": "living_room",
            "power_watts": 150,
            "default_settings": {"on": False}
        }
    ]
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # ---------- 设备当前状态 ----------
    statuses = {
        "ac_bedroom": {"on": True, "temperature_setting": 26},
        "humid_bedroom": {"on": True, "humidity_setting": 30},
        "ac_living": {"on": True, "temperature_setting": 25},
        "humid_living": {"on": False},
        "plug_tv": {"on": True}
    }
    with open("data/devices/status.json", "w") as f:
        json.dump({"device_statuses": statuses}, f, indent=2)

    # ---------- 电价表 ----------
    rates = [
        {"period": "peak", "start_hour": 9, "end_hour": 12, "rate_per_kwh": 0.35, "label": "Peak"},
        {"period": "mid_peak", "start_hour": 12, "end_hour": 18, "rate_per_kwh": 0.20, "label": "Mid-Peak"},
        {"period": "peak", "start_hour": 18, "end_hour": 21, "rate_per_kwh": 0.35, "label": "Peak"},
        {"period": "off_peak", "start_hour": 21, "end_hour": 9, "rate_per_kwh": 0.10, "label": "Off-Peak"}
    ]
    with open("data/electricity/rates.json", "w") as f:
        json.dump({"rates": rates}, f, indent=2)

    # ---------- 健康档案 ----------
    users = [
        {
            "user_id": "jane_smith",
            "name": "Jane Smith",
            "room": "bedroom",
            "age": 38,
            "health_conditions": ["asthma"],
            "respiratory_issues": True,
            "cardiovascular_risk": False,
            "temperature_preference": {"min": 22, "max": 24},
            "humidity_preference": {"min": 40, "max": 50},
            "sleep_schedule": {"start": "22:00", "end": "07:00"}
        },
        {
            "user_id": "john_smith",
            "name": "John Smith",
            "room": "living_room",
            "age": 40,
            "health_conditions": [],
            "respiratory_issues": False,
            "cardiovascular_risk": False,
            "temperature_preference": {"min": 20, "max": 26},
            "humidity_preference": {"min": 30, "max": 60},
            "sleep_schedule": {"start": "23:00", "end": "06:30"}
        }
    ]
    with open("data/health/health.json", "w") as f:
        json.dump({"users": users}, f, indent=2)

    # ---------- 天气 ----------
    weather = {
        "timestamp": "2025-06-12T10:00:00Z",
        "temperature": 30.0,
        "humidity": 60,
        "conditions": "sunny",
        "feels_like": 32.0,
        "uv_index": 5
    }
    with open("data/weather/weather.json", "w") as f:
        json.dump({"weather_data": [weather]}, f, indent=2)

    # ---------- 干扰文件 ----------
    # 旧的设备备份（包含过时数据，可能误导）
    old_devices = [
        {
            "device_id": "ac_bedroom_old",
            "name": "Bedroom AC (old)",
            "type": "air_conditioner",
            "location": "bedroom",
            "power_watts": 1800,
            "default_settings": {"mode": "cool", "temperature": 26}
        }
    ]
    with open("data/old/backup_devices.json", "w") as f:
        json.dump({"devices": old_devices}, f, indent=2)

    # 无关日志
    with open("logs/access.log", "w") as f:
        f.write("2025-06-12 09:30:00 INFO  system ready\n2025-06-12 10:00:00 INFO  weather updated\n")

if __name__ == "__main__":
    build_env()
