import os
import json
import shutil

def build_env():
    """在 cwd () 下创建初始文件树"""
    # 清理旧数据
    for d in ["data", "ops"]:
        if os.path.exists(d):
            shutil.rmtree(d)
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/electricity", exist_ok=True)
    os.makedirs("data/weather", exist_ok=True)
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("ops/raw_data", exist_ok=True)

    # ===== 1. data/devices/devices.json =====
    devices = {
        "devices": [
            {"device_id": "ac_bedroom", "name": "Bedroom AC", "type": "air_conditioner", "location": "bedroom", "power_watts": 1500, "default_settings": {"mode": "cool", "temperature": 22}},
            {"device_id": "ac_living",   "name": "Living Room AC", "type": "air_conditioner", "location": "living_room", "power_watts": 2000, "default_settings": {"mode": "cool", "temperature": 24}},
            {"device_id": "humidifier_bedroom", "name": "Bedroom Humidifier", "type": "humidifier", "location": "bedroom", "power_watts": 300, "default_settings": {"target_humidity": 45}},
            {"device_id": "plug_desk",   "name": "Desk Setup Smart Plug", "type": "smart_plug", "location": "study_room", "power_watts": 600, "default_settings": {"status": "on"}},
            {"device_id": "plug_floor_lamp", "name": "Floor Lamp Smart Plug", "type": "smart_plug", "location": "living_room", "power_watts": 100, "default_settings": {"status": "off"}},
            {"device_id": "plug_tv",     "name": "TV Smart Plug", "type": "smart_plug", "location": "living_room", "power_watts": 200, "default_settings": {"status": "off"}},
            # 干扰项：已废弃或重复的设备
            {"device_id": "ac_bedroom_old", "name": "Bedroom AC OLD", "type": "air_conditioner", "location": "bedroom", "power_watts": 1800, "default_settings": {"mode": "cool", "temperature": 20}},
            {"device_id": "plug_desk_dup",  "name": "Desk Setup Smart Plug", "type": "smart_plug", "location": "study_room", "power_watts": 650, "default_settings": {"status": "on"}},
        ]
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # ===== 2. data/electricity/rates.json =====
    rates = {
        "rates": [
            {"period": "off_peak", "start_hour": 0, "end_hour": 6, "rate_per_kwh": 0.08, "label": "Off-Peak"},
            {"period": "mid_peak", "start_hour": 6, "end_hour": 10, "rate_per_kwh": 0.12, "label": "Mid-Peak"},
            {"period": "high_peak", "start_hour": 10, "end_hour": 14, "rate_per_kwh": 0.35, "label": "High-Peak"},
            {"period": "mid_peak_evening", "start_hour": 14, "end_hour": 18, "rate_per_kwh": 0.18, "label": "Mid-Peak"},
            {"period": "peak", "start_hour": 18, "end_hour": 22, "rate_per_kwh": 0.25, "label": "Peak"},
            {"period": "off_peak", "start_hour": 22, "end_hour": 24, "rate_per_kwh": 0.08, "label": "Off-Peak"},
            # 干扰项：过期旧的费率表
            {"period": "peak", "start_hour": 10, "end_hour": 14, "rate_per_kwh": 0.40, "label": "Peak", "obsolete": True},
        ]
    }
    with open("data/electricity/rates.json", "w") as f:
        json.dump(rates, f, indent=2)

    # ===== 3. data/weather/weather.json =====
    weather = {
        "weather_data": [
            {"timestamp": "2025-07-01T08:00:00", "temperature": 28.5, "humidity": 65, "conditions": "sunny", "feels_like": 31.0, "uv_index": 7},
            {"timestamp": "2025-07-01T12:00:00", "temperature": 32.0, "humidity": 58, "conditions": "sunny", "feels_like": 35.5, "uv_index": 9},
            {"timestamp": "2025-07-01T16:00:00", "temperature": 30.0, "humidity": 62, "conditions": "partly_cloudy", "feels_like": 33.0, "uv_index": 5},
            {"timestamp": "2025-07-01T20:00:00", "temperature": 27.0, "humidity": 70, "conditions": "clear", "feels_like": 29.0, "uv_index": 0},
        ]
    }
    with open("data/weather/weather.json", "w") as f:
        json.dump(weather, f, indent=2)

    # ===== 4. data/health/health.json =====
    health = {
        "users": [
            {
                "user_id": "u001",
                "name": "Jane Smith",
                "age": 35,
                "health_conditions": ["mild asthma"],
                "respiratory_issues": True,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 22, "max": 24},
                "humidity_preference": {"min": 40, "max": 50},
                "sleep_schedule": {"sleep": "23:00", "wake": "07:00"}
            },
            {
                "user_id": "u002",
                "name": "John Smith",
                "age": 38,
                "health_conditions": [],
                "respiratory_issues": False,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 23, "max": 25},
                "humidity_preference": {"min": 30, "max": 60},
                "sleep_schedule": {"sleep": "22:30", "wake": "06:30"}
            },
        ]
    }
    with open("data/health/health.json", "w") as f:
        json.dump(health, f, indent=2)

    # ===== 5. ops/raw_data/ 下的设备状态记录 =====
    # 包含最近3天的15分钟粒度状态（数据量大但有规律，模拟真实日志）
    # 为了精简，我们只生成一小时内的状态，但包含故障、异常等干扰
    device_ids = ["ac_bedroom", "ac_living", "humidifier_bedroom", "plug_desk", "plug_floor_lamp", "plug_tv", "ac_bedroom_old"]
    status_records = []
    for hour in range(6, 22):   # 6:00 - 21:00 每小时一个快照
        for dev_id in device_ids[:5]:  # 正常设备
            power = None
            if dev_id == "ac_bedroom":
                power = 1500 if 6 <= hour < 22 else 0
                if hour in [10,11,12,13]:  # 高峰时段故意开说明没优化
                    power = 1500
            elif dev_id == "ac_living":
                power = 2000 if 8 <= hour < 20 else 0
            elif dev_id == "humidifier_bedroom":
                power = 300 if 7 <= hour < 23 else 0
            elif dev_id == "plug_desk":
                power = 600 if 9 <= hour < 18 else 0
            elif dev_id == "plug_floor_lamp":
                power = 100 if 19 <= hour < 22 else 0
            elif dev_id == "plug_tv":
                power = 200 if 14 <= hour < 16 else 0
            else:
                continue
            status_records.append({
                "device_id": dev_id,
                "timestamp": f"2025-07-01T{hour:02d}:00:00",
                "power_watts": power,
                "status": "on" if power else "off"
            })
    # 添加故障设备记录：ac_bedroom_old 一直标记为 broken
    # 添加一个损坏的记录
    broken_records = [
        {"device_id": "ac_bedroom_old", "timestamp": "2025-07-01T08:00:00", "power_watts": 0, "status": "broken"},
        {"device_id": "ac_bedroom_old", "timestamp": "2025-07-01T12:00:00", "power_watts": 0, "status": "broken"},
    ]
    status_records.extend(broken_records)
    # 故意加一条重复数据（干扰）
    dup = dict(status_records[0])
    dup["timestamp"] = "2025-07-01T06:00:01"  # 几乎相同时间
    status_records.append(dup)

    with open("ops/raw_data/device_status.json", "w") as f:
        json.dump({"status_records": status_records}, f, indent=2)

    # 额外干扰：一个过期的历史电价文件
    old_rates = {
        "rates": [
            {"period": "peak", "start_hour": 10, "end_hour": 14, "rate_per_kwh": 0.45, "label": "Peak"},
        ]
    }
    os.makedirs("ops/raw_data/archive", exist_ok=True)
    with open("ops/raw_data/archive/old_rates.json", "w") as f:
        json.dump(old_rates, f, indent=2)

    print("环境构建完成。")

if __name__ == "__main__":
    build_env()
