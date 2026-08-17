import os
import json
import shutil

def build_env():
    # 清理旧数据（如果有）
    for path in ['data', 'ops']:
        if os.path.exists(path):
            shutil.rmtree(path)
    
    # ---------- 设备数据 ----------
    devices = [
        {
            "device_id": "ac_bedroom",
            "name": "Bedroom AC",
            "type": "air_conditioner",
            "location": "bedroom",
            "power_watts": 2000,
            "default_settings": {"temperature": 24, "mode": "cool"}
        },
        {
            "device_id": "ac_living_room",
            "name": "Living Room AC",
            "type": "air_conditioner",
            "location": "living_room",
            "power_watts": 2500,
            "default_settings": {"temperature": 23, "mode": "cool"}
        },
        {
            "device_id": "humidifier_bedroom",
            "name": "Bedroom Humidifier",
            "type": "humidifier",
            "location": "bedroom",
            "power_watts": 500,
            "default_settings": {"humidity": 35}
        },
        {
            "device_id": "humidifier_living",
            "name": "Living Room Humidifier",
            "type": "humidifier",
            "location": "living_room",
            "power_watts": 600,
            "default_settings": {"humidity": 50}
        },
        # 干扰设备：智能插头
        {
            "device_id": "plug_tv",
            "name": "TV Smart Plug",
            "type": "smart_plug",
            "location": "living_room",
            "power_watts": 150,
            "default_settings": {"state": "on"}
        },
        {
            "device_id": "plug_lamp",
            "name": "Floor Lamp Smart Plug",
            "type": "smart_plug",
            "location": "study_room",
            "power_watts": 40,
            "default_settings": {"state": "off"}
        }
    ]
    os.makedirs("data/devices", exist_ok=True)
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # 设备运行状态（模拟当前都在运行）
    running_status = {
        "ac_bedroom": True,
        "ac_living_room": True,
        "humidifier_bedroom": True,
        "humidifier_living": False,  # 干扰：客厅加湿器未运行
        "plug_tv": True,
        "plug_lamp": False
    }
    with open("data/devices/running_status.json", "w") as f:
        json.dump(running_status, f, indent=2)

    # ---------- 健康数据 ----------
    health = [
        {
            "user_id": "jane",
            "name": "Jane Smith",
            "age": 28,
            "health_conditions": ["asthma"],
            "respiratory_issues": True,
            "cardiovascular_risk": False,
            "temperature_preference": {"min": 23, "max": 25},
            "humidity_preference": {"min": 40, "max": 60},
            "sleep_schedule": {"bedtime": "22:00", "wakeup": "07:00"},
            "assigned_locations": ["bedroom"]
        },
        {
            "user_id": "john",
            "name": "John Smith",
            "age": 45,
            "health_conditions": ["hypertension"],
            "respiratory_issues": False,
            "cardiovascular_risk": True,
            "temperature_preference": {"min": 22, "max": 24},
            "humidity_preference": {"min": 20, "max": 80},
            "sleep_schedule": {"bedtime": "23:00", "wakeup": "06:30"},
            "assigned_locations": ["living_room"]
        }
    ]
    os.makedirs("data/health", exist_ok=True)
    with open("data/health/health.json", "w") as f:
        json.dump({"users": health}, f, indent=2)

    # ---------- 电价数据 ----------
    rates = [
        {"period": "high_peak", "start_hour": 9, "end_hour": 12, "rate_per_kwh": 0.8, "label": "High-Peak"},
        {"period": "mid_peak", "start_hour": 12, "end_hour": 17, "rate_per_kwh": 0.5, "label": "Mid-Peak"},
        {"period": "off_peak", "start_hour": 0, "end_hour": 7, "rate_per_kwh": 0.2, "label": "Off-Peak"},
        {"period": "peak", "start_hour": 17, "end_hour": 21, "rate_per_kwh": 0.6, "label": "Peak"}
    ]
    os.makedirs("data/electricity", exist_ok=True)
    with open("data/electricity/rates.json", "w") as f:
        json.dump({"rates": rates}, f, indent=2)

    # ---------- 天气数据 ----------
    weather = {
        "timestamp": "2025-06-15T10:00:00",
        "temperature": 22.0,
        "humidity": 60,
        "conditions": "partly_cloudy",
        "feels_like": 21.5,
        "uv_index": 3
    }
    os.makedirs("data/weather", exist_ok=True)
    with open("data/weather/weather.json", "w") as f:
        json.dump({"weather_data": weather}, f, indent=2)

    # ---------- 干扰文件 ----------
    # 旧版健康数据（过期）
    old_health = [{"user_id":"jane","name":"Jane Smith","temperature_preference":{"min":22,"max":26}}]
    with open("data/health/old_health.json", "w") as f:
        json.dump(old_health, f)
    # 过时的电价备份（不同时段）
    old_rates = [{"period":"peak","start_hour":8,"end_hour":11,"rate_per_kwh":0.9}]
    with open("data/electricity/rates_backup.json", "w") as f:
        json.dump(old_rates, f)
    # 多余的设备状态文件
    os.makedirs("data/devices/extra", exist_ok=True)
    with open("data/devices/extra/ghost_device.json", "w") as f:
        json.dump({"device_id":"ghost","type":"unknown"}, f)
    # 一个空的 ops 目录（确保目录存在，但文件由 agent 创建）
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
