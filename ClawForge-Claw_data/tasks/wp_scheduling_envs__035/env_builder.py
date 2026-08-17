import os
import json
import csv
from datetime import datetime

def build_env():
    # ---- data/devices.json ----
    devices = [
        {"device_id": "d001", "device_name": "Bedroom Light", "device_type": "light", "location": "bedroom", "supported_settings": ["brightness"], "settings": {"brightness": 80}},
        {"device_id": "d002", "device_name": "Living Room AC", "device_type": "ac", "location": "living_room", "supported_settings": ["temperature"], "settings": {"temperature": 24}},
        {"device_id": "d003", "device_name": "Bedroom Humidifier", "device_type": "humidifier", "location": "bedroom", "supported_settings": ["humidity"], "settings": {"humidity": 50}},
        {"device_id": "d004", "device_name": "Living Room Light", "device_type": "light", "location": "living_room", "supported_settings": ["brightness"], "settings": {"brightness": 100}},
        {"device_id": "d005", "device_name": "Coffee Machine Smart Plug", "device_type": "smart_plug", "location": "kitchen", "supported_settings": ["power"], "settings": {"power": "on"}},
        {"device_id": "d006", "device_name": "TV Smart Plug", "device_type": "smart_plug", "location": "living_room", "supported_settings": ["power"], "settings": {"power": "on"}},
    ]
    os.makedirs("data", exist_ok=True)
    with open("data/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # ---- data/schedules.json （包含有效、无效、过期等） ----
    # 用时间字符串，方便解析：YYYY-MM-DD HH:00
    schedules = [
        {"id": "s001", "device_id": "d001", "room": "bedroom", "datetime": "2025-03-15 02:00", "valid": True},
        {"id": "s002", "device_id": "d003", "room": "bedroom", "datetime": "2025-03-15 02:00", "valid": True},   # 冲突1：bedroom 02:00 有d001和d003
        {"id": "s003", "device_id": "d002", "room": "living_room", "datetime": "2025-03-15 02:00", "valid": True},
        {"id": "s004", "device_id": "d004", "room": "living_room", "datetime": "2025-03-15 02:00", "valid": True}, # 冲突2：living_room 02:00 有d002,d004,d006
        {"id": "s005", "device_id": "d006", "room": "living_room", "datetime": "2025-03-15 02:00", "valid": True},
        {"id": "s006", "device_id": "d001", "room": "bedroom", "datetime": "2025-03-15 03:00", "valid": True},
        {"id": "s007", "device_id": "d003", "room": "bedroom", "datetime": "2025-03-15 03:00", "valid": True},  # 冲突3：bedroom 03:00 有d001,d003
        {"id": "s008", "device_id": "d002", "room": "living_room", "datetime": "2025-03-15 03:00", "valid": True},
        {"id": "s009", "device_id": "d005", "room": "kitchen", "datetime": "2025-03-15 03:00", "valid": True},  # kitchen只有一个，不冲突
        # 干扰：过期日期（2024年）
        {"id": "s010", "device_id": "d001", "room": "bedroom", "datetime": "2024-12-01 02:00", "valid": True},
        {"id": "s011", "device_id": "d003", "room": "bedroom", "datetime": "2024-12-01 02:00", "valid": True},
        # 干扰：valid false
        {"id": "s012", "device_id": "d004", "room": "living_room", "datetime": "2025-03-15 04:00", "valid": False},
        {"id": "s013", "device_id": "d006", "room": "living_room", "datetime": "2025-03-15 04:00", "valid": False},
        # 干扰：无效设备ID (不在devices.json中)
        {"id": "s014", "device_id": "d999", "room": "bedroom", "datetime": "2025-03-15 05:00", "valid": True},
        # 干扰：同一房间同一小时但只有一个有效设备（d001有效，d999无效）
        {"id": "s015", "device_id": "d001", "room": "bedroom", "datetime": "2025-03-15 06:00", "valid": True},
        # 加上一些其他不冲突的
        {"id": "s016", "device_id": "d005", "room": "kitchen", "datetime": "2025-03-15 07:00", "valid": True},
    ]
    with open("data/schedules.json", "w") as f:
        json.dump({"schedules": schedules}, f, indent=2)

    # ---- logs/ 目录，包含干扰文件 ----
    os.makedirs("logs", exist_ok=True)
    # 正常日志（无关）
    with open("logs/device_log.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["device_id", "timestamp", "event"])
        writer.writerow(["d001", "2025-03-15 02:00", "turn_on"])
        writer.writerow(["d003", "2025-03-15 02:00", "turn_on"])
    # 干扰日志（带_bak后缀）
    with open("logs/device_log_bak.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["device_id", "timestamp", "event"])
        writer.writerow(["d001", "2024-12-01 02:00", "turn_on"])  # 旧数据
    # 另一个干扰CSV
    with open("logs/old_export.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["device_id", "timestamp", "remark"])
        writer.writerow(["d002", "2025-03-15 02:00", "test"])

    # ---- 创建 ops 目录（空，留给agent写结果） ----
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
