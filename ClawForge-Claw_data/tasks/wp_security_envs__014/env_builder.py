import os
import json
import datetime

def build_env():
    # 创建目录
    os.makedirs("data/zones", exist_ok=True)
    os.makedirs("data/doors", exist_ok=True)
    os.makedirs("data/alerts", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 干扰文件：accounts（无关）
    accounts = [
        {"account_id": "acc-001", "account_name": "Main Office", "location": "Building A",
         "zones": ["zone-001","zone-002"], "emergency_contacts": ["contact-001"]},
        {"account_id": "acc-002", "account_name": "Warehouse", "location": "Building B",
         "zones": ["zone-003"], "emergency_contacts": ["contact-002"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 干扰文件：doors（无关）
    doors = [
        {"door_id": "door-001", "door_name": "Front Door", "location": "Main Entrance", "zone_id": "zone-001"},
        {"door_id": "door-002", "door_name": "Office Door", "location": "Office Room", "zone_id": "zone-002"},
        {"door_id": "door-003", "door_name": "Garage Door", "location": "Garage", "zone_id": "zone-003"}
    ]
    with open("data/doors/doors.json", "w") as f:
        json.dump(doors, f, indent=2)

    # 核心区域状态：只有 zone-002 为 true
    zones = [
        {"zone_id": "zone-001", "zone_name": "Main Lobby", "sensors": ["sensor-a1","sensor-a2"], "intrusion_detected": False},
        {"zone_id": "zone-002", "zone_name": "Office Room", "sensors": ["sensor-b1","sensor-b2"], "intrusion_detected": True},
        {"zone_id": "zone-003", "zone_name": "Garage", "sensors": ["sensor-c1"], "intrusion_detected": False},
        {"zone_id": "zone-004", "zone_name": "Backyard", "sensors": ["sensor-d1"], "intrusion_detected": False}  # 额外干扰区
    ]
    with open("data/zones/zones.json", "w") as f:
        json.dump(zones, f, indent=2)

    # 告警记录：包含干扰项，只有 alert-002 对应真实入侵的区域
    alerts = [
        {"alert_id": "alert-001", "zone_id": "zone-001", "severity": "low", "timestamp": "2025-04-01T10:00:00Z"},
        {"alert_id": "alert-002", "zone_id": "zone-002", "severity": "critical", "timestamp": "2025-04-01T10:05:00Z"},
        {"alert_id": "alert-003", "zone_id": "zone-003", "severity": "medium", "timestamp": "2025-04-01T10:10:00Z"},
        {"alert_id": "alert-004", "zone_id": "zone-001", "severity": "high", "timestamp": "2025-04-01T10:15:00Z"},  # 重复区域，但非真入侵
        {"alert_id": "alert-005", "zone_id": "zone-005", "severity": "critical", "timestamp": "2025-04-01T10:20:00Z"}  # 不存在的区域
    ]
    with open("data/alerts/alerts.json", "w") as f:
        json.dump(alerts, f, indent=2)

if __name__ == "__main__":
    build_env()
