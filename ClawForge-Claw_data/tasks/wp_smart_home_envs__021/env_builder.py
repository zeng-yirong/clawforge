import os
import json
import shutil

def build_env():
    # 创建基础目录
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/electricity", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("backups", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. 设备清单（含干扰：其他空调、加湿器、旧设备等）
    devices = {
        "devices": [
            {
                "device_id": "AC_001",
                "name": "Bedroom AC",
                "type": "air_conditioner",
                "location": "bedroom",
                "power_watts": 1500,
                "default_settings": {"mode": "cool", "target_temp": 20, "fan_speed": "auto"}
            },
            {
                "device_id": "AC_002",
                "name": "Living Room AC",
                "type": "air_conditioner",
                "location": "living_room",
                "power_watts": 2200,
                "default_settings": {"mode": "cool", "target_temp": 24, "fan_speed": "high"}
            },
            {
                "device_id": "AC_003",
                "name": "Guest Room AC",
                "type": "air_conditioner",
                "location": "guest_room",
                "power_watts": 1200,
                "default_settings": {"mode": "cool", "target_temp": 22, "fan_speed": "low"}
            },
            {
                "device_id": "HU_001",
                "name": "Bedroom Humidifier",
                "type": "humidifier",
                "location": "bedroom",
                "power_watts": 30,
                "default_settings": {"target_humidity": 45}
            },
            {
                "device_id": "SP_001",
                "name": "Desk Setup Smart Plug",
                "type": "smart_plug",
                "location": "study_room",
                "power_watts": 200,
                "default_settings": {"schedule": "weekday 09-18"}
            }
        ]
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # 2. 电价表（分时电价，包含高峰、平段、低谷）
    rates = {
        "rates": [
            {"period": "peak", "start_hour": 14, "end_hour": 17, "rate_per_kwh": 0.78, "label": "Peak"},
            {"period": "mid_peak", "start_hour": 10, "end_hour": 14, "rate_per_kwh": 0.52, "label": "Mid-Peak"},
            {"period": "mid_peak_evening", "start_hour": 17, "end_hour": 22, "rate_per_kwh": 0.52, "label": "Mid-Peak"},
            {"period": "off_peak", "start_hour": 22, "end_hour": 6, "rate_per_kwh": 0.19, "label": "Off-Peak"},
            {"period": "off_peak_2", "start_hour": 6, "end_hour": 10, "rate_per_kwh": 0.19, "label": "Off-Peak"}
        ]
    }
    with open("data/electricity/rates.json", "w") as f:
        json.dump(rates, f, indent=2)

    # 3. 天气（当前温度、湿度、预报）
    weather = {
        "weather_data": [
            {
                "timestamp": "2025-06-12T15:00:00Z",
                "temperature": 32.0,
                "humidity": 65,
                "conditions": "partly_cloudy",
                "feels_like": 34.5,
                "uv_index": 6
            },
            {
                "timestamp": "2025-06-12T18:00:00Z",
                "temperature": 29.0,
                "humidity": 60,
                "conditions": "cloudy",
                "feels_like": 30.0,
                "uv_index": 3
            },
            {
                "timestamp": "2025-06-12T22:00:00Z",
                "temperature": 26.0,
                "humidity": 55,
                "conditions": "clear",
                "feels_like": 26.5,
                "uv_index": 0
            }
        ]
    }
    with open("data/weather/weather.json", "w") as f:
        json.dump(weather, f, indent=2)

    # 4. 健康档案（Jane 有哮喘，John 无）
    health = {
        "users": [
            {
                "user_id": "U001",
                "name": "Jane Smith",
                "age": 36,
                "health_conditions": ["asthma", "allergic_rhinitis"],
                "respiratory_issues": True,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 22, "max": 26, "ideal": 23},
                "humidity_preference": {"min": 40, "max": 50},
                "sleep_schedule": {"start": "22:00", "end": "06:00"}
            },
            {
                "user_id": "U002",
                "name": "John Smith",
                "age": 42,
                "health_conditions": [],
                "respiratory_issues": False,
                "cardiovascular_risk": True,
                "temperature_preference": {"min": 24, "max": 28, "ideal": 26},
                "humidity_preference": {"min": 30, "max": 60},
                "sleep_schedule": {"start": "23:00", "end": "07:00"}
            }
        ]
    }
    with open("data/health/health.json", "w") as f:
        json.dump(health, f, indent=2)

    # 5. 干扰文件
    # 旧设备清单（包含过期数据）
    old_devices = {
        "devices": [
            {"device_id": "AC_001", "name": "Bedroom AC", "recommended_temp": 18}
        ]
    }
    with open("backups/old_devices.json", "w") as f:
        json.dump(old_devices, f, indent=2)

    # 旧健康档案（Jane 的旧喜好）
    old_health = {
        "users": [
            {"name": "Jane Smith", "sleep_start": "21:00", "sleep_end": "05:00"}
        ]
    }
    with open("backups/old_health.json", "w") as f:
        json.dump(old_health, f, indent=2)

    # 无关的日志
    with open("logs/irrelevant.log", "w") as f:
        f.write("2025-06-12 14:32:01 INFO Server heartbeat ok\n2025-06-12 14:33:12 WARN Sensor out of range\n")

    # 无关 CSV
    with open("data/irrelevant.csv", "w") as f:
        f.write("id,value\n1,abc\n2,def\n")

if __name__ == "__main__":
    build_env()
