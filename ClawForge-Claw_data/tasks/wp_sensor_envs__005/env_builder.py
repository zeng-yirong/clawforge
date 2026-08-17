import os
import json
import random

def build_env():
    # 创建必要的目录
    os.makedirs("data/sensors", exist_ok=True)
    os.makedirs("data/locations", exist_ok=True)
    os.makedirs("data/accounts", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    
    # 正确的传感器数据（正确答案来源）
    correct_sensors = [
        {"sensor_id": "S-TEMP-001", "sensor_name": "Server Rack A", "sensor_type": "temperature", "location_id": "LOC-SR-01", "unit": "celsius", "threshold_low": 15.0, "threshold_high": 35.0, "current_value": 38.2, "status": "active"},
        {"sensor_id": "S-TEMP-003", "sensor_name": "Server Rack C", "sensor_type": "temperature", "location_id": "LOC-SR-01", "unit": "celsius", "threshold_low": 15.0, "threshold_high": 35.0, "current_value": 36.1, "status": "active"},
        {"sensor_id": "S-HUM-002", "sensor_name": "Hallway Hum", "sensor_type": "humidity", "location_id": "LOC-LB-01", "unit": "percent", "threshold_low": 30.0, "threshold_high": 70.0, "current_value": 45.0, "status": "inactive"},
        {"sensor_id": "S-AQ-001", "sensor_name": "Main Lobby Air", "sensor_type": "air_quality", "location_id": "LOC-LB-01", "unit": "aqi", "threshold_low": 0.0, "threshold_high": 100.0, "current_value": 55.0, "status": "error"},
        {"sensor_id": "S-EN-001", "sensor_name": "Power Meter A", "sensor_type": "energy", "location_id": "LOC-WH-01", "unit": "kwh", "threshold_low": 0.0, "threshold_high": 500.0, "current_value": 320.0, "status": "active"},
    ]
    with open("data/sensors/sensors.json", "w") as f:
        json.dump({"sensors": correct_sensors}, f)
    
    # 干扰项1：过期备份（其中 S-TEMP-001 状态是 inactive，S-EN-001 状态是 inactive）
    backup_sensors = [
        {"sensor_id": "S-TEMP-001", "sensor_name": "Server Rack A", "sensor_type": "temperature", "location_id": "LOC-SR-01", "unit": "celsius", "threshold_low": 15.0, "threshold_high": 35.0, "current_value": 28.0, "status": "inactive"},
        {"sensor_id": "S-EN-001", "sensor_name": "Power Meter A", "sensor_type": "energy", "location_id": "LOC-WH-01", "unit": "kwh", "threshold_low": 0.0, "threshold_high": 500.0, "current_value": 200.0, "status": "inactive"},
    ]
    with open("data/sensors/sensors_backup.json", "w") as f:
        json.dump({"sensors": backup_sensors}, f)
    
    # 干扰项2：脏数据文件（格式混乱，包含一行无效 JSON）
    with open("data/sensors/sensors_dirty.txt", "w") as f:
        f.write('{"sensors": [{"sensor_id": "S-TEMP-002", "status": "active"}]\n')
        f.write('invalid json line\n')
        f.write('{"sensor_id": "S-TEMP-002", "sensor_type": "bad"}\n')
    
    # 干扰项3：locations.json（与传感器有关联但不影响答案）
    locations = [
        {"location_id": "LOC-SR-01", "location_name": "Server Room", "floor": 2, "sensors": ["S-TEMP-001", "S-TEMP-003"]},
        {"location_id": "LOC-LB-01", "location_name": "Main Lobby", "floor": 1, "sensors": ["S-HUM-002", "S-AQ-001"]},
        {"location_id": "LOC-WH-01", "location_name": "Warehouse", "floor": 0, "sensors": ["S-EN-001"]},
    ]
    with open("data/locations/locations.json", "w") as f:
        json.dump({"locations": locations}, f)
    
    # 诱饵：accounts.json（包含无关账户信息，但其中 notification_contacts 可能含有 sensor_id 误导）
    accounts = [
        {"account_id": "ACC-001", "account_name": "IT Dept", "location": "HQ", "sensors": ["S-TEMP-001", "S-EN-001"], "notification_contacts": ["alice@corp.com"]},
    ]
    with open("data/accounts/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)
    
    # 额外干扰：一个名为 "active_ones" 的 CSV 文件，内容故意写几个 sensor_id，但都不是正确答案
    import csv
    with open("data/sensors/active_ones.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["sensor_id", "status"])
        writer.writerow(["S-TEMP-002", "active"])   # 这个 sensor 并不在正确数据中
        writer.writerow(["S-HUM-002", "inactive"])

if __name__ == "__main__":
    build_env()
