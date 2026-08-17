import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/locations", exist_ok=True)
    os.makedirs("data/sensors", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("backups", exist_ok=True)

    # 干扰文件：accounts.json (无用)
    accounts = [
        {"account_id": "acc_001", "account_name": "HQ", "location": "NYC", "sensors": ["sens_001","sens_002"], "locations": ["loc_001","loc_002"], "notification_contacts": ["a@b.com"]},
        {"account_id": "acc_002", "account_name": "DC", "location": "SJC", "sensors": ["sens_003","sens_004","sens_005","sens_006","sens_007","sens_008"], "locations": ["loc_003","loc_004"], "notification_contacts": ["c@d.com"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    # locations.json
    locations = [
        {"location_id": "loc_001", "location_name": "Main Lobby", "floor": 1, "sensors": ["sens_001","sens_002"]},
        {"location_id": "loc_002", "location_name": "Office Area", "floor": 2, "sensors": ["sens_003","sens_004"]},
        {"location_id": "loc_003", "location_name": "Server Room", "floor": 3, "sensors": ["sens_005","sens_006","sens_007"]},
        {"location_id": "loc_004", "location_name": "Warehouse", "floor": 1, "sensors": ["sens_008"]}
    ]
    with open("data/locations/locations.json", "w") as f:
        json.dump({"locations": locations}, f)

    # sensors.json — 精心设计，只有 sens_006 符合条件
    sensors = [
        {"sensor_id": "sens_001", "sensor_name": "Lobby Temp", "sensor_type": "temperature", "location_id": "loc_001", "unit": "celsius", "threshold_low": 18.0, "threshold_high": 28.0, "current_value": 22.5, "status": "active"},
        {"sensor_id": "sens_002", "sensor_name": "Lobby Humidity", "sensor_type": "humidity", "location_id": "loc_001", "unit": "percent", "threshold_low": 30.0, "threshold_high": 70.0, "current_value": 45.0, "status": "active"},
        {"sensor_id": "sens_003", "sensor_name": "Office Temp", "sensor_type": "temperature", "location_id": "loc_002", "unit": "celsius", "threshold_low": 20.0, "threshold_high": 26.0, "current_value": 24.0, "status": "active"},
        {"sensor_id": "sens_004", "sensor_name": "Office Air Quality", "sensor_type": "air_quality", "location_id": "loc_002", "unit": "aqi", "threshold_low": 0, "threshold_high": 100, "current_value": 85, "status": "active"},
        {"sensor_id": "sens_005", "sensor_name": "Server Room Temp", "sensor_type": "temperature", "location_id": "loc_003", "unit": "celsius", "threshold_low": 15.0, "threshold_high": 30.0, "current_value": 22.0, "status": "active"},
        {"sensor_id": "sens_006", "sensor_name": "Server Room Humidity", "sensor_type": "humidity", "location_id": "loc_003", "unit": "percent", "threshold_low": 35.0, "threshold_high": 60.0, "current_value": 68.5, "status": "active"},
        {"sensor_id": "sens_007", "sensor_name": "Server Room Humidity2", "sensor_type": "humidity", "location_id": "loc_003", "unit": "percent", "threshold_low": 30.0, "threshold_high": 70.0, "current_value": 55.0, "status": "inactive"},
        {"sensor_id": "sens_008", "sensor_name": "Warehouse Temp", "sensor_type": "temperature", "location_id": "loc_004", "unit": "celsius", "threshold_low": 10.0, "threshold_high": 35.0, "current_value": 28.0, "status": "active"}
    ]
    with open("data/sensors/sensors.json", "w") as f:
        json.dump({"sensors": sensors}, f)

    # 干扰日志文件
    with open("logs/system.log", "w") as f:
        f.write("2025-03-10 03:15:23 WARN humidity threshold exceeded for sens_006\n")
        f.write("2025-03-10 03:16:10 INFO sensor sens_006 current=68.5 high=60.0\n")
    with open("backups/sensors_old.json", "w") as f:
        json.dump({"sensors": []}, f)

if __name__ == "__main__":
    build_env()
