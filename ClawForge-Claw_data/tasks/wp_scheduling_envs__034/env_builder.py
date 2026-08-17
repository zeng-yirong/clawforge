import os
import json
from datetime import datetime

def build_env():
    # 确保目录存在
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/old_backups", exist_ok=True)  # 干扰目录

    # 设备清单
    devices = [
        {"device_id": "living_room_ac", "device_name": "Living Room AC", "device_type": "ac", "location": "living_room"},
        {"device_id": "bedroom_ac", "device_name": "Bedroom AC", "device_type": "ac", "location": "bedroom"},
        {"device_id": "kitchen_light", "device_name": "Kitchen Light", "device_type": "light", "location": "kitchen"},
        {"device_id": "bedroom_light", "device_name": "Bedroom Light", "device_type": "light", "location": "bedroom"},
        {"device_id": "coffee_plug", "device_name": "Coffee Machine Smart Plug", "device_type": "smart_plug", "location": "kitchen"},
    ]
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # 账户与调度计划
    schedules = [
        # 正确命中高峰的空调
        {"schedule_id": "s1", "device_id": "living_room_ac", "start_time": "18:00", "end_time": "23:30", "action": "on"},
        {"schedule_id": "s2", "device_id": "bedroom_ac", "start_time": "17:30", "end_time": "19:30", "action": "on"},
        # 干扰：非空调设备在高峰内开启
        {"schedule_id": "s3", "device_id": "kitchen_light", "start_time": "18:00", "end_time": "20:00", "action": "on"},
        {"schedule_id": "s4", "device_id": "bedroom_light", "start_time": "20:00", "end_time": "22:00", "action": "on"},
        {"schedule_id": "s5", "device_id": "coffee_plug", "start_time": "17:00", "end_time": "18:00", "action": "on"},
        # 干扰：空调但不在高峰时段
        {"schedule_id": "s6", "device_id": "bedroom_ac", "start_time": "10:00", "end_time": "12:00", "action": "on"},
        # 干扰：引用不存在的设备
        {"schedule_id": "s7", "device_id": "nonexistent_device", "start_time": "18:00", "end_time": "21:00", "action": "on"},
        # 干扰：时间格式无效
        {"schedule_id": "s8", "device_id": "living_room_ac", "start_time": "invalid_time", "end_time": "20:00", "action": "on"},
    ]

    accounts = [{
        "account_id": "home-001",
        "account_name": "My Home",
        "location": "house",
        "devices": [d["device_id"] for d in devices],
        "schedules": schedules
    }]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # 干扰文件：旧备份
    with open("data/old_backups/legacy_devices.json", "w") as f:
        json.dump({"devices": [{"device_id": "old_ac", "device_type": "ac"}]}, f)

if __name__ == "__main__":
    build_env()
