import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)
    os.makedirs("data/electricity", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 健康数据
    health_data = {
        "users": [
            {
                "user_id": "jane01",
                "name": "Jane Smith",
                "age": 32,
                "location": "bedroom",
                "health_conditions": ["asthma"],
                "respiratory_issues": True,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 20, "max": 22},
                "humidity_preference": {"min": 40, "max": 50},
                "sleep_schedule": {"start": "22:00", "end": "06:00"}
            },
            {
                "user_id": "john01",
                "name": "John Smith",
                "age": 35,
                "location": "living_room",
                "health_conditions": ["hypertension"],
                "respiratory_issues": False,
                "cardiovascular_risk": True,
                "temperature_preference": {"min": 22, "max": 24},
                "humidity_preference": {"min": 45, "max": 55},
                "sleep_schedule": {"start": "23:00", "end": "07:00"}
            }
        ]
    }
    with open("data/health/health.json", "w") as f:
        json.dump(health_data, f, indent=2)

    # 旧版本健康数据干扰
    old_health = {"users": [{"user_id": "jane01", "temperature_preference": {"min": 18, "max": 25}}]}
    with open("data/health/health_old.json", "w") as f:
        json.dump(old_health, f, indent=2)

    # 设备列表
    devices = {
        "devices": [
            {"device_id": "ac_bedroom", "name": "Bedroom AC", "type": "air_conditioner", "location": "bedroom", "power_watts": 2000, "default_settings": {"temperature": 24, "mode": "cool"}},
            {"device_id": "humidifier_bedroom", "name": "Bedroom Humidifier", "type": "humidifier", "location": "bedroom", "power_watts": 500, "default_settings": {"humidity": 55}},
            {"device_id": "ac_living", "name": "Living Room AC", "type": "air_conditioner", "location": "living_room", "power_watts": 2500, "default_settings": {"temperature": 21, "mode": "cool"}},
            {"device_id": "humidifier_living", "name": "Living Room Humidifier", "type": "humidifier", "location": "living_room", "power_watts": 600, "default_settings": {"humidity": 45}},
            {"device_id": "study_ac", "name": "Study Room AC", "type": "air_conditioner", "location": "study_room", "power_watts": 1500, "default_settings": {"temperature": 20, "mode": "cool"}},
            {"device_id": "desk_plug", "name": "Desk Setup Smart Plug", "type": "smart_plug", "location": "study_room", "power_watts": 300, "default_settings": {"on": False}},
            {"device_id": "floor_plug", "name": "Floor Lamp Smart Plug", "type": "smart_plug", "location": "living_room", "power_watts": 100, "default_settings": {"on": True}}
        ]
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # 设备当前状态
    state = [
        {"device_id": "ac_bedroom", "setting": {"temperature": 25, "mode": "cool"}},
        {"device_id": "humidifier_bedroom", "setting": {"humidity": 60}},
        {"device_id": "ac_living", "setting": {"temperature": 21, "mode": "cool"}},
        {"device_id": "humidifier_living", "setting": {"humidity": 40}},
        {"device_id": "study_ac", "setting": {"temperature": 20, "mode": "cool"}},
        {"device_id": "desk_plug", "setting": {"on": True}},
        {"device_id": "floor_plug", "setting": {"on": False}}
    ]
    with open("data/devices/state.json", "w") as f:
        json.dump(state, f, indent=2)

    # 设备备份干扰
    backup = {"devices": [{"device_id": "ac_bedroom", "default_settings": {"temperature": 22}}]}
    with open("data/devices/devices_backup.json", "w") as f:
        json.dump(backup, f, indent=2)

    # 天气数据
    weather = {
        "weather_data": [
            {"timestamp": "2025-07-15T14:00:00Z", "temperature": 35.0, "humidity": 70, "conditions": "sunny", "feels_like": 38.0, "uv_index": 8}
        ]
    }
    with open("data/weather/latest.json", "w") as f:
        json.dump(weather, f, indent=2)

    # 旧天气干扰
    yesterday = {"weather_data": [{"timestamp": "2025-07-14T14:00:00Z", "temperature": 32.0}]}
    with open("data/weather/yesterday.json", "w") as f:
        json.dump(yesterday, f, indent=2)

    # 电力费率干扰
    rates = {
        "rates": [
            {"period": "peak", "start_hour": 14, "end_hour": 20, "rate_per_kwh": 0.35, "label": "Peak"}
        ]
    }
    with open("data/electricity/rates.json", "w") as f:
        json.dump(rates, f, indent=2)

if __name__ == "__main__":
    build_env()
