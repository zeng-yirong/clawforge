import os
import json

def build_env():
    # 创建目录结构
    os.makedirs('data/sensors', exist_ok=True)
    os.makedirs('data/locations', exist_ok=True)
    os.makedirs('data/accounts', exist_ok=True)
    os.makedirs('ops', exist_ok=True)

    # ---- 传感器主数据 ----
    sensors = {
        "S001": {
            "sensor_id": "S001",
            "sensor_name": "南区温度传感器A",
            "sensor_type": "temperature",
            "location_id": "L001",
            "unit": "celsius",
            "threshold_low": 15.0,
            "threshold_high": 35.0,
            "current_value": 38.5,
            "status": "active"
        },
        "S002": {
            "sensor_id": "S002",
            "sensor_name": "南区湿度传感器B",
            "sensor_type": "humidity",
            "location_id": "L001",
            "unit": "percent",
            "threshold_low": 30.0,
            "threshold_high": 70.0,
            "current_value": 60.0,
            "status": "active"
        },
        "S003": {
            "sensor_id": "S003",
            "sensor_name": "南区能耗传感器C",
            "sensor_type": "energy",
            "location_id": "L002",
            "unit": "kwh",
            "threshold_low": 100.0,
            "threshold_high": 300.0,
            "current_value": 500.0,
            "status": "inactive"
        },
        "S004": {
            "sensor_id": "S004",
            "sensor_name": "服务器机房温度D",
            "sensor_type": "temperature",
            "location_id": "L002",
            "unit": "celsius",
            "threshold_low": 10.0,
            "threshold_high": 30.0,
            "current_value": 25.0,
            "status": "active"
        },
        "S005": {
            "sensor_id": "S005",
            "sensor_name": "仓库空气质量E",
            "sensor_type": "air_quality",
            "location_id": "L003",
            "unit": "aqi",
            "threshold_low": 0.0,
            "threshold_high": 100.0,
            "current_value": 120.0,
            "status": "active"
        }
    }
    with open('data/sensors/sensors.json', 'w') as f:
        json.dump({"sensors": sensors}, f, indent=2)

    # ---- 干扰项：旧版本传感器数据（已过期，阈值不同）----
    old_sensors = {
        "S001": dict(sensors["S001"], current_value=36.0, threshold_high=40.0),
        "S003": dict(sensors["S003"], current_value=480.0, threshold_high=320.0)
    }
    with open('data/sensors/sensors_old.json', 'w') as f:
        json.dump({"sensors_old": old_sensors}, f, indent=2)

    # ---- 干扰项：不完整的备份（缺少必要字段）----
    bad_sensor = {"sensor_id": "S006", "sensor_name": "坏数据", "status": "active"}
    with open('data/sensors/sensors_bad.json', 'w') as f:
        json.dump({"bad": [bad_sensor]}, f, indent=2)

    # ---- 位置数据 ----
    locations = {
        "L001": {
            "location_id": "L001",
            "location_name": "Main Lobby",
            "floor": 1,
            "sensors": ["S001", "S002"]
        },
        "L002": {
            "location_id": "L002",
            "location_name": "Server Room",
            "floor": 2,
            "sensors": ["S003", "S004"]
        },
        "L003": {
            "location_id": "L003",
            "location_name": "Warehouse",
            "floor": 1,
            "sensors": ["S005"]
        }
    }
    with open('data/locations/locations.json', 'w') as f:
        json.dump({"locations": locations}, f, indent=2)

    # ---- 账户数据 ----
    accounts = {
        "A001": {
            "account_id": "A001",
            "account_name": "Alpha分部",
            "location": "L001",
            "locations": ["L001"],
            "sensors": ["S001", "S002"],
            "notification_contacts": ["ops-alpha@corp.com"]
        },
        "A002": {
            "account_id": "A002",
            "account_name": "Beta分部",
            "location": "L002",
            "locations": ["L002", "L003"],
            "sensors": ["S003", "S004", "S005"],
            "notification_contacts": ["ops-beta@corp.com"]
        }
    }
    with open('data/accounts/accounts.json', 'w') as f:
        json.dump({"accounts": accounts}, f, indent=2)

if __name__ == '__main__':
    build_env()
