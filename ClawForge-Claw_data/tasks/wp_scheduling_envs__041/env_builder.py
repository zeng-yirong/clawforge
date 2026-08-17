import os
import json

def build_env():
    # 创建数据目录
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/backup", exist_ok=True)

    # 设备清单（含干扰项）
    devices = [
        {
            "device_id": "dev_light_bedroom",
            "device_name": "Bedroom Light",
            "device_type": "light",
            "location": "bedroom",
            "supported_settings": ["brightness", "color"],
            "settings": {"brightness": 80}
        },
        {
            "device_id": "dev_ac_livingroom",
            "device_name": "Living Room AC",
            "device_type": "ac",
            "location": "living_room",
            "supported_settings": ["temperature", "mode", "fan_speed"],
            "settings": {"temperature": 24, "mode": "cool", "fan_speed": "auto"}
        },
        {
            "device_id": "dev_humidifier_bedroom",
            "device_name": "Bedroom Humidifier",
            "device_type": "humidifier",
            "location": "bedroom",
            "supported_settings": ["humidity", "mode"],
            "settings": {"humidity": 50, "mode": "auto"}
        },
        {
            "device_id": "dev_plug_coffee",
            "device_name": "Coffee Machine Smart Plug",
            "device_type": "smart_plug",
            "location": "kitchen",
            "supported_settings": ["power", "timer"],
            "settings": {"power": "off"}
        }
    ]
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # 调度记录：包含冲突对（sch_002 & sch_005）和干扰/脏数据
    schedules = [
        {"schedule_id": "sch_001", "device_id": "dev_light_bedroom", "start_time": "2024-10-01 18:00", "end_time": "2024-10-01 22:00", "active": True},
        {"schedule_id": "sch_002", "device_id": "dev_ac_livingroom", "start_time": "2024-10-01 20:00", "end_time": "2024-10-01 23:00", "active": True},
        {"schedule_id": "sch_003", "device_id": "dev_light_bedroom", "start_time": "2024-10-01 19:00", "end_time": "2024-10-01 21:00", "active": True},  # 不同设备，不冲突
        {"schedule_id": "sch_004", "device_id": "dev_ac_livingroom", "start_time": "2024-10-02 18:00", "end_time": "2024-10-02 22:00", "active": True},  # 不同日期，不冲突
        {"schedule_id": "sch_005", "device_id": "dev_ac_livingroom", "start_time": "2024-10-01 21:00", "end_time": "2024-10-02 01:00", "active": True},  # 与 sch_002 冲突
        {"schedule_id": "sch_006", "device_id": "dev_humidifier_bedroom", "start_time": "2024-10-01 18:00", "end_time": None, "active": True}  # 脏数据，end_time 缺失
    ]
    with open("data/schedules.json", "w") as f:
        json.dump({"schedules": schedules}, f, indent=2)

    # 干扰：账户信息
    accounts = [
        {
            "account_id": "acct_001",
            "account_name": "Home Owner",
            "location": "home",
            "devices": ["dev_light_bedroom", "dev_ac_livingroom", "dev_humidifier_bedroom", "dev_plug_coffee"],
            "schedules": ["sch_001", "sch_002", "sch_003", "sch_004", "sch_005", "sch_006"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # 干扰：旧备份调度（无冲突）
    old_schedules = [
        {"schedule_id": "sch_100", "device_id": "dev_ac_livingroom", "start_time": "2024-09-30 20:00", "end_time": "2024-09-30 23:00", "active": False}
    ]
    with open("data/backup/schedules_old.json", "w") as f:
        json.dump({"schedules": old_schedules}, f, indent=2)

if __name__ == "__main__":
    build_env()
