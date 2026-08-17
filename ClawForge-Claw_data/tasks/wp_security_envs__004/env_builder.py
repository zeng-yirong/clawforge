import os
import json
import csv
import random
from datetime import datetime, timedelta

def build_env():
    # ---- 1. zones.json (主数据) ----
    zones = [
        {"zone_id": "zone_main_lobby", "zone_name": "Main Lobby", "sensors": ["sensor_lobby_01", "sensor_lobby_02"], "intrusion_detected": True},
        {"zone_id": "zone_garage", "zone_name": "Garage", "sensors": ["sensor_garage_01"], "intrusion_detected": False},
        {"zone_id": "zone_backyard", "zone_name": "Backyard", "sensors": ["sensor_backyard_01"], "intrusion_detected": False},
    ]
    os.makedirs("data", exist_ok=True)
    with open("data/zones.json", "w") as f:
        json.dump({"zones": zones}, f, indent=2)

    # ---- 2. 过时的 zones_backup.json (干扰) ----
    old_zones = [
        {"zone_id": "zone_main_lobby", "zone_name": "Main Lobby", "sensors": ["sensor_lobby_01", "sensor_lobby_02"], "intrusion_detected": False},
        {"zone_id": "zone_garage", "zone_name": "Garage", "sensors": ["sensor_garage_01"], "intrusion_detected": True},
    ]
    with open("data/zones_backup.json", "w") as f:
        json.dump({"zones": old_zones}, f, indent=2)

    # ---- 3. doors.json ----
    doors = [
        {"door_id": "door_001", "door_name": "Front Door", "location": "Main Entrance", "zone_id": "zone_main_lobby"},
        {"door_id": "door_002", "door_name": "Garage Door", "location": "Garage", "zone_id": "zone_garage"},
        {"door_id": "door_003", "door_name": "Back Door", "location": "Rear Entrance", "zone_id": "zone_backyard"},
    ]
    with open("data/doors.json", "w") as f:
        json.dump({"doors": doors}, f, indent=2)

    # ---- 4. accounts.json (干扰用, 但不会影响答案) ----
    accounts = [
        {"account_id": "acc_001", "account_name": "Main Building", "location": "100 Main St", "zones": ["zone_main_lobby", "zone_garage"], "emergency_contacts": ["contact_01", "contact_02"]},
        {"account_id": "acc_002", "account_name": "Warehouse", "location": "200 Industrial Ave", "zones": ["zone_backyard"], "emergency_contacts": ["contact_03"]},
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # ---- 5. contacts.json (干扰) ----
    contacts = [
        {"contact_id": "contact_01", "name": "Emergency Services", "role": "Monitoring Service", "phone": "+1-800-555-0123", "email": "monitoring@securityco.com"},
        {"contact_id": "contact_02", "name": "Local Police Precinct", "role": "Police", "phone": "911", "email": "police.precinct@example.com"},
        {"contact_id": "contact_03", "name": "John Smith", "role": "Security Manager", "phone": "+1-555-0101", "email": "john.smith@example.com"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ---- 6. logs/ 传感器时间序列 (确认入侵的唯一证据) ----
    os.makedirs("logs", exist_ok=True)
    # 生成一个真实的 sensor 日志，包含 Main Lobby 入侵时的异常读数
    base_time = datetime(2025, 3, 15, 3, 0, 0)
    log_lines = []
    for i in range(10):
        ts = base_time + timedelta(seconds=i*5)
        if i < 5:
            # 前5秒正常
            lines = [
                f"{ts.isoformat()} sensor_lobby_01 NORMAL 22.5\n",
                f"{ts.isoformat()} sensor_lobby_02 NORMAL 21.8\n",
                f"{ts.isoformat()} sensor_garage_01 NORMAL 18.0\n",
                f"{ts.isoformat()} sensor_backyard_01 NORMAL 12.0\n",
            ]
        else:
            # 第6秒开始 Main Lobby 异常
            lines = [
                f"{ts.isoformat()} sensor_lobby_01 ANOMALY 78.3\n",
                f"{ts.isoformat()} sensor_lobby_02 ANOMALY 82.1\n",
                f"{ts.isoformat()} sensor_garage_01 NORMAL 18.1\n",
                f"{ts.isoformat()} sensor_backyard_01 NORMAL 12.1\n",
            ]
        log_lines.extend(lines)
    with open("logs/sensor_timeline.txt", "w") as f:
        f.writelines(log_lines)

    # 7. 一个伪造的旧警报 CSV (干扰：标记了 garage 入侵)
    with open("logs/alerts.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "zone_id", "severity", "description"])
        writer.writerow(["2025-03-15T02:55:00", "zone_garage", "low", "Garage door sensor glitch (probably false)"])
        writer.writerow(["2025-03-15T03:00:05", "zone_main_lobby", "critical", "Main Lobby motion & glass break detected"])
        writer.writerow(["2025-03-15T03:00:10", "zone_garage", "medium", "Garage air pressure drop (maintenance)"])

    # 8. 创建输出目录 ops (agent 需写入此目录)
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
