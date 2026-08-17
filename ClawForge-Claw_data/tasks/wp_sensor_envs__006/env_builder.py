import os
import json

def build_env():
    """创建传感器监控场景的初始文件树"""
    # 创建 data/sensors 目录
    os.makedirs("data/sensors", exist_ok=True)
    # 创建 ops 目录（空，等待 agent 写入产物）
    os.makedirs("ops", exist_ok=True)

    # 构建传感器列表 – 唯一超限 active 传感器为 sensor_004
    sensors = [
        {
            "sensor_id": "sensor_001",
            "sensor_name": "Main Lobby Temperature",
            "sensor_type": "temperature",
            "location_id": "loc_01",
            "unit": "celsius",
            "threshold_low": 10.0,
            "threshold_high": 35.0,
            "current_value": 24.5,
            "status": "active"
        },
        {
            "sensor_id": "sensor_002",
            "sensor_name": "Server Room Humidity",
            "sensor_type": "humidity",
            "location_id": "loc_02",
            "unit": "percent",
            "threshold_low": 30.0,
            "threshold_high": 70.0,
            "current_value": 65.0,
            "status": "inactive"
        },
        {
            "sensor_id": "sensor_003",
            "sensor_name": "Warehouse Air Quality",
            "sensor_type": "air_quality",
            "location_id": "loc_03",
            "unit": "aqi",
            "threshold_low": 0.0,
            "threshold_high": 100.0,
            "current_value": 80.0,
            "status": "active"
        },
        {
            "sensor_id": "sensor_004",
            "sensor_name": "Server Room Temperature",
            "sensor_type": "temperature",
            "location_id": "loc_02",
            "unit": "celsius",
            "threshold_low": 15.0,
            "threshold_high": 28.0,
            "current_value": 32.0,
            "status": "active"
        },
        {
            "sensor_id": "sensor_005",
            "sensor_name": "Main Lobby Humidity",
            "sensor_type": "humidity",
            "location_id": "loc_01",
            "unit": "percent",
            "threshold_low": 20.0,
            "threshold_high": 60.0,
            "current_value": 55.0,
            "status": "inactive"
        }
    ]

    # 写入 sensors.json（Wrapper 格式，符合领域数据结构）
    with open("data/sensors/sensors.json", "w") as f:
        json.dump({"sensors": sensors}, f, indent=2)

    # 创建干扰文件 – 过时的备份（同一目录下 old 版本，但 agent 不应读取）
    old_sensors = [
        {
            "sensor_id": "sensor_006",
            "sensor_name": "Old Rack Temp",
            "sensor_type": "temperature",
            "location_id": "loc_02",
            "unit": "celsius",
            "threshold_low": 15.0,
            "threshold_high": 28.0,
            "current_value": 35.0,
            "status": "active"
        }
    ]
    with open("data/sensors/sensors_backup.json", "w") as f:
        json.dump({"sensors": old_sensors}, f, indent=2)

    # 创建无关数据文件作为干扰
    os.makedirs("data/locations", exist_ok=True)
    locations = [
        {"location_id": "loc_01", "location_name": "Main Lobby", "floor": 1, "sensors": ["sensor_001","sensor_005"]},
        {"location_id": "loc_02", "location_name": "Server Room", "floor": 2, "sensors": ["sensor_002","sensor_004"]},
        {"location_id": "loc_03", "location_name": "Warehouse", "floor": 0, "sensors": ["sensor_003"]}
    ]
    with open("data/locations/locations.json", "w") as f:
        json.dump({"locations": locations}, f, indent=2)

    os.makedirs("data/accounts", exist_ok=True)
    accounts = [
        {"account_id": "acct_01", "account_name": "Facility Admin", "location": "HQ", "sensors": ["sensor_001","sensor_002","sensor_003","sensor_004","sensor_005"], "locations": ["loc_01","loc_02","loc_03"], "notification_contacts": ["admin@example.com"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

if __name__ == "__main__":
    build_env()
