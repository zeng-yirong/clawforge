import os
import json
import random
random.seed(42)

def build_env():
    # 创建所有必要的目录
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/electricity", exist_ok=True)
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 用于agent输出

    # 1. accounts.json (干扰项)
    accounts = {
        "accounts": [
            {"account_id": "acc-001", "account_name": "Smith Family", "email": "smith@example.com", "role": "owner", "display_name": "Smith Home"},
            {"account_id": "acc-002", "account_name": "Guest", "email": "guest@example.com", "role": "viewer", "display_name": "Guest"}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 2. devices.json (真实设备 + 干扰设备)
    devices = {
        "devices": [
            # 卧室设备 (Jane重点)
            {"device_id": "bd-ac-01", "name": "Bedroom AC", "type": "air_conditioner", "location": "bedroom", "power_watts": 1500, "default_settings": {"mode": "cool", "temperature": 22, "humidity": 30}},
            {"device_id": "bd-hum-01", "name": "Bedroom Humidifier", "type": "humidifier", "location": "bedroom", "power_watts": 200, "default_settings": {"mode": "auto", "target_humidity": 30}},
            # 客厅设备 (John重点)
            {"device_id": "lr-ac-01", "name": "Living Room AC", "type": "air_conditioner", "location": "living_room", "power_watts": 2000, "default_settings": {"mode": "cool", "temperature": 20, "humidity": 35}},
            {"device_id": "lr-hum-01", "name": "Living Room Humidifier", "type": "humidifier", "location": "living_room", "power_watts": 250, "default_settings": {"mode": "auto", "target_humidity": 40}},
            # 书房干扰设备 (无用户相关)
            {"device_id": "st-plug-01", "name": "Desk Setup Smart Plug", "type": "smart_plug", "location": "study_room", "power_watts": 100, "default_settings": {}},
            {"device_id": "st-plug-02", "name": "Floor Lamp Smart Plug", "type": "smart_plug", "location": "study_room", "power_watts": 60, "default_settings": {}},
            # 额外干扰：已废弃设备（不出现于status）
            {"device_id": "old-ac", "name": "Old AC", "type": "air_conditioner", "location": "bedroom", "power_watts": 1800, "default_settings": {}}
        ]
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # 3. status.json (当前状态) -- 只有部分设备打开
    status = {
        "device_status": [
            # 卧室空调开，温度22°C (预设22，但Jane更喜欢24°C？等一下看health)
            {"device_id": "bd-ac-01", "status": "on", "current_temperature": 22, "current_humidity": 30},
            # 卧室加湿器开，目标湿度30% (与Jane要求的45-55%冲突)
            {"device_id": "bd-hum-01", "status": "on", "current_humidity": 30, "target_humidity": 30},
            # 客厅空调开，温度20°C (John要求>=24°C，冲突)
            {"device_id": "lr-ac-01", "status": "on", "current_temperature": 20, "current_humidity": 35},
            # 客厅加湿器开，目标湿度40% (John的湿度偏好？默认40，John无特别要求，所以不冲突)
            {"device_id": "lr-hum-01", "status": "on", "current_humidity": 40, "target_humidity": 40},
            # 书房两个插头关闭 (不参与)
            {"device_id": "st-plug-01", "status": "off", "power_usage": 0},
            {"device_id": "st-plug-02", "status": "off", "power_usage": 0},
            # 干扰：一个不存在设备的记录
            {"device_id": "ghost-device", "status": "on", "current_temperature": 25}
        ]
    }
    with open("data/status/status.json", "w") as f:
        json.dump(status, f, indent=2)

    # 4. electricity/rates.json (干扰项)
    rates = {
        "rates": [
            {"period": "peak", "start_hour": 14, "end_hour": 20, "rate_per_kwh": 0.25, "label": "Peak"},
            {"period": "off_peak", "start_hour": 20, "end_hour": 14, "rate_per_kwh": 0.10, "label": "Off-Peak"},
            {"period": "mid_peak", "start_hour": 10, "end_hour": 14, "rate_per_kwh": 0.18, "label": "Mid-Peak"},
            {"period": "mid_peak_evening", "start_hour": 20, "end_hour": 22, "rate_per_kwh": 0.18, "label": "Mid-Peak Evening"}
        ]
    }
    with open("data/electricity/rates.json", "w") as f:
        json.dump(rates, f, indent=2)

    # 5. health.json (两个用户)
    health = {
        "users": [
            {
                "user_id": "user-jane",
                "name": "Jane Smith",
                "age": 34,
                "health_conditions": ["asthma", "allergies"],
                "respiratory_issues": True,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 22, "max": 26, "ideal": 24},
                "humidity_preference": {"min": 45, "max": 55, "ideal": 50},
                "sleep_schedule": {"bedtime": "22:00", "wakeup": "07:00"}
            },
            {
                "user_id": "user-john",
                "name": "John Smith",
                "age": 45,
                "health_conditions": ["hypertension"],
                "respiratory_issues": False,
                "cardiovascular_risk": True,
                "temperature_preference": {"min": 24, "max": 28, "ideal": 26},
                "humidity_preference": {"min": 30, "max": 50, "ideal": 40},
                "sleep_schedule": {"bedtime": "23:00", "wakeup": "06:30"}
            }
        ]
    }
    with open("data/health/health.json", "w") as f:
        json.dump(health, f, indent=2)

    # 6. weather.json (干扰项)
    weather = {
        "weather_data": [
            {"timestamp": "2025-06-12T10:00:00Z", "temperature": 32.5, "humidity": 60, "conditions": "sunny", "feels_like": 35.0, "uv_index": 8},
            {"timestamp": "2025-06-12T14:00:00Z", "temperature": 34.0, "humidity": 55, "conditions": "partly_cloudy", "feels_like": 36.5, "uv_index": 6}
        ]
    }
    with open("data/weather/weather.json", "w") as f:
        json.dump(weather, f, indent=2)

if __name__ == "__main__":
    build_env()
