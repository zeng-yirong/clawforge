import os
import json

def build_env():
    # 确保相对路径从工作区根开始
    # data 目录
    os.makedirs("data/accounts", exist_ok=True)
    os.makedirs("data/devices/status", exist_ok=True)
    os.makedirs("data/electricity", exist_ok=True)
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 干扰项目录
    os.makedirs("data/backup", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("tmp", exist_ok=True)

    # 1. accounts.json
    accounts = {
        "accounts": [
            {
                "account_id": "acc_jane",
                "account_name": "Jane Smith",
                "email": "jane@example.com",
                "role": "owner",
                "display_name": "Jane"
            },
            {
                "account_id": "acc_john",
                "account_name": "John Smith",
                "email": "john@example.com",
                "role": "member",
                "display_name": "John"
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 2. devices.json
    devices = {
        "devices": [
            {
                "device_id": "bedroom_ac",
                "name": "Bedroom AC",
                "type": "air_conditioner",
                "location": "bedroom",
                "power_watts": 1500,
                "default_settings": {"mode": "cool", "temperature": 26}
            },
            {
                "device_id": "bedroom_humidifier",
                "name": "Bedroom Humidifier",
                "type": "humidifier",
                "location": "bedroom",
                "power_watts": 300,
                "default_settings": {"target_humidity": 45}
            },
            {
                "device_id": "living_room_ac",
                "name": "Living Room AC",
                "type": "air_conditioner",
                "location": "living_room",
                "power_watts": 2000,
                "default_settings": {"mode": "cool", "temperature": 24}
            },
            {
                "device_id": "living_room_humidifier",
                "name": "Living Room Humidifier",
                "type": "humidifier",
                "location": "living_room",
                "power_watts": 400,
                "default_settings": {"target_humidity": 50}
            }
        ]
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # 3. 设备状态（每个设备一个文件）
    # 卧室空调：当前关机，室内温度30度，设置温度28（用户之前调的）
    bedroom_ac_status = {
        "device_id": "bedroom_ac",
        "power_state": "off",
        "current_temperature": 30.0,
        "set_temperature": 28,
        "mode": "cool",
        "fan_speed": "auto"
    }
    with open("data/devices/status/bedroom_ac.json", "w") as f:
        json.dump(bedroom_ac_status, f, indent=2)

    # 卧室加湿器：关机，当前湿度 25%
    bedroom_humidifier_status = {
        "device_id": "bedroom_humidifier",
        "power_state": "off",
        "current_humidity": 25,
        "target_humidity": None,
        "water_level": "ok"
    }
    with open("data/devices/status/bedroom_humidifier.json", "w") as f:
        json.dump(bedroom_humidifier_status, f, indent=2)

    # 客厅空调：已开启，设置24度，室内温度24度
    living_room_ac_status = {
        "device_id": "living_room_ac",
        "power_state": "on",
        "current_temperature": 24.0,
        "set_temperature": 24,
        "mode": "cool",
        "fan_speed": "low"
    }
    with open("data/devices/status/living_room_ac.json", "w") as f:
        json.dump(living_room_ac_status, f, indent=2)

    # 客厅加湿器：已开启，目标湿度50%，当前湿度49%
    living_room_humidifier_status = {
        "device_id": "living_room_humidifier",
        "power_state": "on",
        "current_humidity": 49,
        "target_humidity": 50,
        "water_level": "ok"
    }
    with open("data/devices/status/living_room_humidifier.json", "w") as f:
        json.dump(living_room_humidifier_status, f, indent=2)

    # 干扰：一个格式错误的状态文件
    with open("data/devices/status/faulty_sensor.json", "w") as f:
        f.write("{invalid json}")

    # 4. electricity rates.json
    rates = {
        "rates": [
            {"period": "off_peak", "start_hour": 22, "end_hour": 6, "rate_per_kwh": 0.08, "label": "Off-Peak"},
            {"period": "mid_peak", "start_hour": 6, "end_hour": 18, "rate_per_kwh": 0.12, "label": "Mid-Peak"},
            {"period": "peak", "start_hour": 18, "end_hour": 20, "rate_per_kwh": 0.20, "label": "Peak"},
            {"period": "mid_peak_evening", "start_hour": 20, "end_hour": 22, "rate_per_kwh": 0.15, "label": "Mid-Peak Evening"}
        ]
    }
    with open("data/electricity/rates.json", "w") as f:
        json.dump(rates, f, indent=2)

    # 5. health.json
    health = {
        "users": [
            {
                "user_id": "user_jane",
                "name": "Jane Smith",
                "age": 32,
                "health_conditions": ["allergic_rhinitis", "asthma"],
                "respiratory_issues": True,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 24, "max": 26},
                "humidity_preference": {"min": 40, "max": 60},
                "sleep_schedule": {"start": "22:00", "end": "07:00"}
            },
            {
                "user_id": "user_john",
                "name": "John Smith",
                "age": 34,
                "health_conditions": ["hypertension"],
                "respiratory_issues": False,
                "cardiovascular_risk": True,
                "temperature_preference": {"min": 22, "max": 25},
                "humidity_preference": {"min": 30, "max": 50},
                "sleep_schedule": {"start": "23:00", "end": "08:00"}
            }
        ]
    }
    with open("data/health/health.json", "w") as f:
        json.dump(health, f, indent=2)

    # 干扰：旧的健康备份
    old_health = { "users": [{"user_id": "user_jane", "name": "Jane Smith", "respiratory_issues": False}] }
    with open("data/backup/health_old.json", "w") as f:
        json.dump(old_health, f, indent=2)

    # 6. weather.json
    weather = {
        "weather_data": [
            {
                "timestamp": "2025-06-12T17:00:00",
                "temperature": 35.0,
                "humidity": 20,
                "conditions": "sunny",
                "feels_like": 37.0,
                "uv_index": 8
            },
            {
                "timestamp": "2025-06-12T18:00:00",
                "temperature": 34.0,
                "humidity": 22,
                "conditions": "partly_cloudy",
                "feels_like": 36.0,
                "uv_index": 5
            }
        ]
    }
    with open("data/weather/weather.json", "w") as f:
        json.dump(weather, f, indent=2)

    # 干扰：日志文件
    with open("data/logs/system.log", "w") as f:
        f.write("2025-06-12 17:30:15 INFO Device bedroom_ac status check passed\n")
        f.write("2025-06-12 17:31:02 WARN Living room humidity slightly high\n")

    # 额外干扰：tmp 目录下的临时文件
    with open("tmp/scratch.json", "w") as f:
        json.dump({"unrelated": True}, f)

if __name__ == "__main__":
    build_env()
