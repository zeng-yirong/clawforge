import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 设备列表
    devices = [
        {
            "device_id": "device_001",
            "device_name": "Living Room AC",
            "device_type": "ac",
            "location": "living_room",
            "supported_settings": ["temperature", "mode"],
            "settings": {"temperature": 24, "mode": "cool"}
        },
        {
            "device_id": "device_002",
            "device_name": "Living Room Humidifier",
            "device_type": "humidifier",
            "location": "living_room",
            "supported_settings": ["humidity"],
            "settings": {"humidity": 50}
        },
        {
            "device_id": "device_003",
            "device_name": "Bedroom Light",
            "device_type": "light",
            "location": "bedroom",
            "supported_settings": ["brightness", "color"],
            "settings": {"brightness": 80, "color": "warm"}
        },
        {
            "device_id": "device_004",
            "device_name": "Bedroom Humidifier",
            "device_type": "humidifier",
            "location": "bedroom",
            "supported_settings": ["humidity"],
            "settings": {"humidity": 60}
        },
        {
            "device_id": "device_005",
            "device_name": "Kitchen Light",
            "device_type": "light",
            "location": "kitchen",
            "supported_settings": ["brightness"],
            "settings": {"brightness": 100}
        }
    ]

    # 账户与调度
    accounts = [
        {
            "account_id": "acc_001",
            "account_name": "Home",
            "location": "123 Main St",
            "devices": ["device_001", "device_002", "device_003"],
            "schedules": [
                {
                    "schedule_id": "sch_001",
                    "device_id": "device_001",
                    "time_range": {"start": "22:00", "end": "06:00"},
                    "days": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
                },
                {
                    "schedule_id": "sch_002",
                    "device_id": "device_002",
                    "time_range": {"start": "23:00", "end": "05:00"},
                    "days": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
                },
                {
                    "schedule_id": "sch_003",
                    "device_id": "device_003",
                    "time_range": {"start": "08:00", "end": "10:00"},
                    "days": ["Mon","Tue","Wed","Thu","Fri"]
                }
            ]
        },
        {
            "account_id": "acc_002",
            "account_name": "Office",
            "location": "456 Oak Ave",
            "devices": ["device_004", "device_005"],
            "schedules": [
                {
                    "schedule_id": "sch_004",
                    "device_id": "device_004",
                    "time_range": {"start": "09:00", "end": "17:00"},
                    "days": ["Mon","Tue","Wed","Thu","Fri"]
                },
                {
                    "schedule_id": "sch_005",
                    "device_id": "device_005",
                    "time_range": {"start": "18:00", "end": "22:00"},
                    "days": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
                }
            ]
        }
    ]

    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

if __name__ == "__main__":
    build_env()
