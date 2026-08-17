import os
import json

def build_env():
    # 创建 data 目录
    os.makedirs("data", exist_ok=True)

    # ========== 设备数据 ==========
    devices = [
        {
            "device_id": "device_001",
            "device_name": "Living Room AC",
            "device_type": "ac",
            "location": "living_room",
            "supported_settings": ["temperature", "fan_speed"],
            "settings": {"temperature": 24, "fan_speed": "auto"}
        },
        {
            "device_id": "device_002",
            "device_name": "Living Room Humidifier",
            "device_type": "humidifier",
            "location": "living_room",
            "supported_settings": ["humidity_level", "mode"],
            "settings": {"humidity_level": 50, "mode": "normal"}
        },
        {
            "device_id": "device_003",
            "device_name": "Bedroom Light",
            "device_type": "light",
            "location": "bedroom",
            "supported_settings": ["brightness", "color"],
            "settings": {"brightness": 80, "color": "warm_white"}
        },
        {
            "device_id": "device_004",
            "device_name": "Coffee Machine Smart Plug",
            "device_type": "smart_plug",
            "location": "kitchen",
            "supported_settings": ["power_state", "timer"],
            "settings": {"power_state": "off", "timer": 30}
        },
        {
            "device_id": "device_005",
            "device_name": "Bedroom Humidifier",
            "device_type": "humidifier",
            "location": "bedroom",
            "supported_settings": ["humidity_level", "mode"],
            "settings": {"humidity_level": 45, "mode": "sleep"}
        }
    ]
    with open("data/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # ========== 调度数据 ==========
    schedules = [
        # 冲突的两个调度（客厅 AC 和加湿器同时22点开）
        {
            "schedule_id": "sch_001",
            "device_id": "device_001",
            "start_time": "22:00",
            "end_time": "23:00",
            "days_of_week": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
            "enabled": True
        },
        {
            "schedule_id": "sch_002",
            "device_id": "device_002",
            "start_time": "22:00",
            "end_time": "23:00",
            "days_of_week": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
            "enabled": True
        },
        # 正常调度
        {
            "schedule_id": "sch_003",
            "device_id": "device_003",
            "start_time": "21:00",
            "end_time": "22:00",
            "days_of_week": ["Mon","Wed","Fri"],
            "enabled": True
        },
        {
            "schedule_id": "sch_004",
            "device_id": "device_004",
            "start_time": "06:00",
            "end_time": "07:00",
            "days_of_week": ["Mon","Tue","Wed","Thu","Fri"],
            "enabled": True
        },
        {
            "schedule_id": "sch_005",
            "device_id": "device_005",
            "start_time": "20:00",
            "end_time": "21:00",
            "days_of_week": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
            "enabled": True
        },
        # 干扰：禁用的重复调度（不冲突）
        {
            "schedule_id": "sch_006",
            "device_id": "device_002",
            "start_time": "14:00",
            "end_time": "15:00",
            "days_of_week": ["Tue","Thu"],
            "enabled": False
        },
        # 干扰：设备不存在的坏记录
        {
            "schedule_id": "sch_007",
            "device_id": "nonexistent_device",
            "start_time": "12:00",
            "end_time": "13:00",
            "days_of_week": ["Mon"],
            "enabled": False
        }
    ]
    with open("data/schedules.json", "w") as f:
        json.dump(schedules, f, indent=2)

if __name__ == "__main__":
    build_env()
