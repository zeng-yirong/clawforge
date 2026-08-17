import os
import json
import datetime

def build_env():
    # 创建数据目录
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/electricity", exist_ok=True)
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. 设备列表（包含干扰项：inactive 设备）
    devices = [
        {
            "device_id": "ac_lr",
            "name": "Living Room AC",
            "type": "air_conditioner",
            "location": "living_room",
            "power_watts": 2000,
            "default_settings": {"mode": "cool", "temperature": 24, "fan_speed": "auto"},
            "status": "active"
        },
        {
            "device_id": "ac_br",
            "name": "Bedroom AC",
            "type": "air_conditioner",
            "location": "bedroom",
            "power_watts": 1500,
            "default_settings": {"mode": "cool", "temperature": 23, "fan_speed": "auto"},
            "status": "active"
        },
        {
            "device_id": "hum_br",
            "name": "Bedroom Humidifier",
            "type": "humidifier",
            "location": "bedroom",
            "power_watts": 50,
            "default_settings": {"mode": "auto", "target_humidity": 50},
            "status": "active"
        },
        {
            "device_id": "plug_desk",
            "name": "Desk Setup Smart Plug",
            "type": "smart_plug",
            "location": "study_room",
            "power_watts": 100,
            "default_settings": {"state": "on"},
            "status": "active"
        },
        {
            "device_id": "plug_floor",
            "name": "Floor Lamp Smart Plug",
            "type": "smart_plug",
            "location": "living_room",
            "power_watts": 60,
            "default_settings": {"state": "on"},
            "status": "active"
        },
        {
            "device_id": "plug_tv",
            "name": "TV Smart Plug",
            "type": "smart_plug",
            "location": "living_room",
            "power_watts": 80,
            "default_settings": {"state": "on"},
            "status": "active"
        },
        {
            "device_id": "ac_study",
            "name": "Study Room AC",
            "type": "air_conditioner",
            "location": "study_room",
            "power_watts": 1000,
            "default_settings": {"mode": "cool", "temperature": 22, "fan_speed": "auto"},
            "status": "active"
        },
        {
            "device_id": "hum_br_old",
            "name": "Old Bedroom Humidifier",
            "type": "humidifier",
            "location": "bedroom",
            "power_watts": 60,
            "default_settings": {"mode": "off"},
            "status": "inactive"   # 干扰项：已停用
        }
    ]
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # 2. 电价表
    rates = [
        {"period": "peak", "start_hour": 17, "end_hour": 20, "rate_per_kwh": 0.35, "label": "Peak"},
        {"period": "off_peak", "start_hour": 20, "end_hour": 24, "rate_per_kwh": 0.10, "label": "Off-Peak"},
        {"period": "off_peak", "start_hour": 0, "end_hour": 7, "rate_per_kwh": 0.08, "label": "Off-Peak"},
        {"period": "mid_peak", "start_hour": 7, "end_hour": 17, "rate_per_kwh": 0.20, "label": "Mid-Peak"}
    ]
    with open("data/electricity/rates.json", "w") as f:
        json.dump({"rates": rates}, f, indent=2)

    # 3. 健康数据
    health = [
        {
            "user_id": "user_john",
            "name": "John Smith",
            "age": 35,
            "health_conditions": ["asthma"],
            "respiratory_issues": True,
            "cardiovascular_risk": False,
            "temperature_preference": {"min": 22, "max": 25},
            "humidity_preference": {"min": 40, "max": 60},
            "sleep_schedule": {"room": "bedroom", "start": "22:00", "end": "07:00"}
        },
        {
            "user_id": "user_jane",
            "name": "Jane Smith",
            "age": 32,
            "health_conditions": [],
            "respiratory_issues": False,
            "cardiovascular_risk": False,
            "temperature_preference": {"min": 20, "max": 28},
            "humidity_preference": {"min": 30, "max": 70},
            "sleep_schedule": {"room": "living_room", "start": "23:00", "end": "08:00"}
        }
    ]
    with open("data/health/health.json", "w") as f:
        json.dump({"users": health}, f, indent=2)

    # 4. 天气数据（设置为下午6点，peak时段）
    weather = [
        {
            "timestamp": "2025-06-15T18:00:00",
            "temperature": 28.5,
            "humidity": 30,
            "conditions": "sunny",
            "feels_like": 30.0,
            "uv_index": 6
        }
    ]
    with open("data/weather/weather.json", "w") as f:
        json.dump({"weather_data": weather}, f, indent=2)

if __name__ == "__main__":
    build_env()
