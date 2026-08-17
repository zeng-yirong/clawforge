import os
import json
from datetime import datetime, timezone

# 固定日期：2025-03-15（当作“今天”）
TODAY = "2025-03-15"

def build_env():
    # 创建数据目录
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("backups", exist_ok=True)  # 干扰目录

    # 1. 设备列表
    devices = {
        "light-001": {
            "device_id": "light-001",
            "device_name": "Bedroom Light",
            "device_type": "light",
            "location": "bedroom",
            "supported_settings": ["brightness", "color_temp"],
            "settings": {"brightness": 80, "color_temp": 3000}
        },
        "ac-002": {
            "device_id": "ac-002",
            "device_name": "Living Room AC",
            "device_type": "ac",
            "location": "living_room",
            "supported_settings": ["temperature", "fan_speed"],
            "settings": {"temperature": 24, "fan_speed": "auto"}
        },
        "plug-003": {
            "device_id": "plug-003",
            "device_name": "Coffee Machine Smart Plug",
            "device_type": "smart_plug",
            "location": "kitchen",
            "supported_settings": ["power"],
            "settings": {"power": "off"}
        }
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # 2. 调度列表（包含干扰项）
    schedules = [
        # 冲突对（同一设备、同一时间、相反动作）
        {"schedule_id": "sched-001", "device_id": "light-001", "time": f"{TODAY}T15:30:00", "action": "turn_on"},
        {"schedule_id": "sched-002", "device_id": "light-001", "time": f"{TODAY}T15:30:00", "action": "turn_off"},
        # 同设备同时间 但动作相同 → 不冲突
        {"schedule_id": "sched-003", "device_id": "ac-002", "time": f"{TODAY}T16:00:00", "action": "turn_on"},
        {"schedule_id": "sched-004", "device_id": "ac-002", "time": f"{TODAY}T16:00:00", "action": "turn_on"},
        # 范围内单条
        {"schedule_id": "sched-005", "device_id": "plug-003", "time": f"{TODAY}T15:45:00", "action": "turn_off"},
        {"schedule_id": "sched-009", "device_id": "light-001", "time": f"{TODAY}T16:30:00", "action": "turn_on"},
        # 范围外（干扰）
        {"schedule_id": "sched-006", "device_id": "light-001", "time": f"{TODAY}T14:00:00", "action": "turn_off"},
        {"schedule_id": "sched-007", "device_id": "ac-002", "time": f"{TODAY}T17:30:00", "action": "turn_off"},
        # 设备 ID 无效（不存在于设备列表中）
        {"schedule_id": "sched-008", "device_id": "ghost-device", "time": f"{TODAY}T15:15:00", "action": "turn_on"},
    ]
    with open("data/schedules.json", "w") as f:
        json.dump({"schedules": schedules}, f, indent=2)

    # 干扰文件：备份目录下放一个无关的文件
    with open("backups/old_schedules.json", "w") as f:
        json.dump({"note": "this is an old backup, ignore"}, f)

if __name__ == "__main__":
    build_env()
