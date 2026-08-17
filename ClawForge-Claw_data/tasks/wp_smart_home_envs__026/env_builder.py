import os
import json
import datetime

def build_env():
    # 目录结构
    dirs = ["data", "data/devices", "data/health", "data/electricity", "data/weather", "ops"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 1. 设备清单 data/devices/devices.json
    devices = [
        {"device_id": "bedroom_ac", "name": "Bedroom AC", "type": "air_conditioner", "location": "bedroom",
         "power_watts": 1500, "default_settings": {"mode": "cool", "temperature": 24, "fan_speed": "auto"}},
        {"device_id": "living_ac", "name": "Living Room AC", "type": "air_conditioner", "location": "living_room",
         "power_watts": 2000, "default_settings": {"mode": "cool", "temperature": 24, "fan_speed": "auto"}},
        {"device_id": "bedroom_humid", "name": "Bedroom Humidifier", "type": "humidifier", "location": "bedroom",
         "power_watts": 100, "default_settings": {"target_humidity": 45}},
        {"device_id": "living_humid", "name": "Living Room Humidifier", "type": "humidifier", "location": "living_room",
         "power_watts": 120, "default_settings": {"target_humidity": 40}},
        {"device_id": "desk_plug", "name": "Desk Setup Smart Plug", "type": "smart_plug", "location": "study_room",
         "power_watts": 300, "default_settings": {"state": "on"}},
        {"device_id": "floor_plug", "name": "Floor Lamp Smart Plug", "type": "smart_plug", "location": "living_room",
         "power_watts": 60, "default_settings": {"state": "off"}},
        {"device_id": "tv_plug", "name": "TV Smart Plug", "type": "smart_plug", "location": "living_room",
         "power_watts": 120, "default_settings": {"state": "off"}}
    ]
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # 2. 用户健康档案 data/health/health.json
    users = [
        {"user_id": "jane_smith", "name": "Jane Smith", "age": 32,
         "health_conditions": [], "respiratory_issues": False, "cardiovascular_risk": False,
         "temperature_preference": {"min": 20, "max": 26, "preferred": 23},
         "humidity_preference": {"min": 35, "max": 55, "preferred": 45},
         "sleep_schedule": {"bedtime": "23:00", "wakeup": "07:00"}},
        {"user_id": "john_smith", "name": "John Smith", "age": 35,
         "health_conditions": ["asthma"], "respiratory_issues": True, "cardiovascular_risk": False,
         "temperature_preference": {"min": 22, "max": 24, "preferred": 22},
         "humidity_preference": {"min": 40, "max": 50, "preferred": 45},
         "sleep_schedule": {"bedtime": "22:30", "wakeup": "06:30"}}
    ]
    with open("data/health/health.json", "w") as f:
        json.dump({"users": users}, f, indent=2)

    # 3. 房间分配 data/assignments.json（作为额外文件，但prompt中提到了）
    assignments = [
        {"user_id": "jane_smith", "location": "living_room"},
        {"user_id": "john_smith", "location": "bedroom"}
    ]
    with open("data/assignments.json", "w") as f:
        json.dump({"assignments": assignments}, f, indent=2)

    # 4. 电价表 data/electricity/rates.json（干扰项，但agent可能不需要）
    now = datetime.datetime.now()
    current_hour = now.hour
    rates = [
        {"period": "off_peak", "start_hour": 0, "end_hour": 6, "rate_per_kwh": 0.08, "label": "Off-Peak"},
        {"period": "peak", "start_hour": 6, "end_hour": 12, "rate_per_kwh": 0.20, "label": "Peak"},
        {"period": "mid_peak", "start_hour": 12, "end_hour": 18, "rate_per_kwh": 0.15, "label": "Mid-Peak"},
        {"period": "high_peak", "start_hour": 18, "end_hour": 22, "rate_per_kwh": 0.25, "label": "High-Peak"},
        {"period": "mid_peak_evening", "start_hour": 22, "end_hour": 24, "rate_per_kwh": 0.12, "label": "Mid-Peak"}
    ]
    with open("data/electricity/rates.json", "w") as f:
        json.dump({"rates": rates}, f, indent=2)

    # 5. 天气 data/weather/weather.json（干扰项）
    weather = [
        {"timestamp": f"{now.date().isoformat()}T12:00:00", "temperature": 30.5, "humidity": 60,
         "conditions": "sunny", "feels_like": 32.0, "uv_index": 7}
    ]
    with open("data/weather/weather.json", "w") as f:
        json.dump({"weather_data": weather}, f, indent=2)

    # 6. 当前设备状态 ops/device_status.json （核心数据）
    status = [
        {"device_id": "bedroom_ac", "timestamp": f"{now.isoformat()}",
         "settings": {"mode": "cool", "temperature": 18, "fan_speed": "high"}},
        {"device_id": "living_ac", "timestamp": f"{now.isoformat()}",
         "settings": {"mode": "cool", "temperature": 24, "fan_speed": "auto"}},
        {"device_id": "bedroom_humid", "timestamp": f"{now.isoformat()}",
         "settings": {"target_humidity": 45}},
        {"device_id": "living_humid", "timestamp": f"{now.isoformat()}",
         "settings": {"target_humidity": 40}},
        {"device_id": "desk_plug", "timestamp": f"{now.isoformat()}", "settings": {"state": "on"}},
        {"device_id": "floor_plug", "timestamp": f"{now.isoformat()}", "settings": {"state": "off"}},
        {"device_id": "tv_plug", "timestamp": f"{now.isoformat()}", "settings": {"state": "off"}}
    ]
    with open("ops/device_status.json", "w") as f:
        json.dump({"device_status": status}, f, indent=2)

if __name__ == "__main__":
    build_env()
