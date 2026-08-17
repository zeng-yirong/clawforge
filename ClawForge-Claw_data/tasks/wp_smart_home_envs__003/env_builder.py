import os
import json
import shutil

def build_env():
    # 确保工作区干净
    if os.path.exists("data"):
        shutil.rmtree("data")
    if os.path.exists("ops"):
        shutil.rmtree("ops")
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/electricity", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 设备列表
    devices = [
        {
            "device_id": "ac_bedroom_01",
            "name": "Bedroom AC",
            "type": "air_conditioner",
            "location": "bedroom",
            "power_watts": 1500,
            "default_settings": {"mode": "cool", "temperature": 30, "fan_speed": "auto"}
        },
        {
            "device_id": "humidifier_bedroom_01",
            "name": "Bedroom Humidifier",
            "type": "humidifier",
            "location": "bedroom",
            "power_watts": 500,
            "default_settings": {"mode": "on", "humidity": 70}
        },
        {
            "device_id": "ac_living_01",
            "name": "Living Room AC",
            "type": "air_conditioner",
            "location": "living_room",
            "power_watts": 2000,
            "default_settings": {"mode": "cool", "temperature": 26, "fan_speed": "low"}
        },
        {
            "device_id": "plug_desk_01",
            "name": "Desk Setup Smart Plug",
            "type": "smart_plug",
            "location": "study_room",
            "power_watts": 100,
            "default_settings": {"state": "off"}
        }
    ]
    devices_wrapper = {"devices": devices}
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices_wrapper, f, indent=2)

    # 用户健康数据
    users = [
        {
            "user_id": "jane_smith",
            "name": "Jane Smith",
            "age": 35,
            "health_conditions": ["asthma"],
            "respiratory_issues": True,
            "cardiovascular_risk": False,
            "temperature_preference": {"min": 20, "max": 24},
            "humidity_preference": {"min": 40, "max": 60},
            "sleep_schedule": {"bedtime": "22:00", "wakeup": "07:00"}
        },
        {
            "user_id": "john_smith",
            "name": "John Smith",
            "age": 38,
            "health_conditions": [],
            "respiratory_issues": False,
            "cardiovascular_risk": False,
            "temperature_preference": {"min": 18, "max": 26},
            "humidity_preference": {"min": 30, "max": 70},
            "sleep_schedule": {"bedtime": "23:00", "wakeup": "06:30"}
        }
    ]
    health_wrapper = {"users": users}
    with open("data/health/health.json", "w") as f:
        json.dump(health_wrapper, f, indent=2)

    # 电价表（干扰项：包含多个时段）
    rates = [
        {"period": "off_peak", "start_hour": 0, "end_hour": 6, "rate_per_kwh": 0.10, "label": "Off-Peak"},
        {"period": "mid_peak", "start_hour": 6, "end_hour": 12, "rate_per_kwh": 0.15, "label": "Mid-Peak"},
        {"period": "peak", "start_hour": 12, "end_hour": 18, "rate_per_kwh": 0.30, "label": "Peak"},
        {"period": "high_peak", "start_hour": 18, "end_hour": 22, "rate_per_kwh": 0.50, "label": "High-Peak"},
        {"period": "off_peak", "start_hour": 22, "end_hour": 24, "rate_per_kwh": 0.10, "label": "Off-Peak"}
    ]
    rates_wrapper = {"rates": rates}
    with open("data/electricity/rates.json", "w") as f:
        json.dump(rates_wrapper, f, indent=2)

    # 天气数据（当前高温高湿，触发冲突）
    weather = [
        {
            "timestamp": "2025-07-15T14:00:00Z",
            "temperature": 35.0,
            "humidity": 80,
            "conditions": "sunny",
            "feels_like": 38.0,
            "uv_index": 8
        }
    ]
    weather_wrapper = {"weather_data": weather}
    with open("data/weather/weather.json", "w") as f:
        json.dump(weather_wrapper, f, indent=2)

    # 干扰文件：旧的健康备份
    old_health = [
        {"user_id": "jane_smith", "name": "Jane Smith", "respiratory_issues": False}  # 误导
    ]
    with open("data/health/health_backup.json", "w") as f:
        json.dump(old_health, f, indent=2)

    # 干扰文件：一个额外的临时日志
    with open("data/tmp_log.txt", "w") as f:
        f.write("Device status check running...")

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
