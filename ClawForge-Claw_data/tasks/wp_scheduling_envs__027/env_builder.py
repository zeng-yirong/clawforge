import os
import json

def build_env():
    # 确保 data 目录存在
    os.makedirs("data", exist_ok=True)
    
    # 设备数据
    devices = [
        {
            "device_id": "ac_bedroom",
            "device_name": "Bedroom AC",
            "device_type": "ac",
            "location": "bedroom",
            "supported_settings": ["mode", "temperature"],
            "settings": {"mode": "cool", "temperature": 22}
        },
        {
            "device_id": "ac_living",
            "device_name": "Living Room AC",
            "device_type": "ac",
            "location": "living_room",
            "supported_settings": ["mode", "temperature"],
            "settings": {"mode": "cool", "temperature": 24}
        },
        {
            "device_id": "light_bedroom",
            "device_name": "Bedroom Light",
            "device_type": "light",
            "location": "bedroom",
            "supported_settings": ["brightness", "color"],
            "settings": {"brightness": 80, "color": "white"}
        },
        {
            "device_id": "humidifier_bedroom",
            "device_name": "Bedroom Humidifier",
            "device_type": "humidifier",
            "location": "bedroom",
            "supported_settings": ["level"],
            "settings": {"level": 50}
        }
    ]
    
    # 调度数据（包含干扰项）
    schedules = [
        # 需要修复的：卧室空调，深夜时段，制冷
        {
            "schedule_id": "night_bedroom_ac",
            "device_id": "ac_bedroom",
            "start_time": "22:00",
            "end_time": "06:00",
            "mode": "cool",
            "temperature": 22,
            "days": ["mon","tue","wed","thu","fri","sat","sun"]
        },
        # 卧室空调但白天时段，不需要改
        {
            "schedule_id": "day_bedroom_ac",
            "device_id": "ac_bedroom",
            "start_time": "08:00",
            "end_time": "18:00",
            "mode": "cool",
            "temperature": 24,
            "days": ["mon","tue","wed","thu","fri"]
        },
        # 客厅空调深夜时段，但不是卧室，不需要改
        {
            "schedule_id": "night_living_ac",
            "device_id": "ac_living",
            "start_time": "22:00",
            "end_time": "06:00",
            "mode": "cool",
            "temperature": 22,
            "days": ["mon","tue","wed","thu","fri","sat","sun"]
        },
        # 卧室灯深夜时段，不是空调，不需要改
        {
            "schedule_id": "night_bedroom_light",
            "device_id": "light_bedroom",
            "start_time": "22:00",
            "end_time": "06:00",
            "mode": "off",
            "brightness": 0,
            "days": ["mon","tue","wed","thu","fri","sat","sun"]
        },
        # 卧室空调深夜时段但已经是制热，不需要改
        {
            "schedule_id": "night_bedroom_heat",
            "device_id": "ac_bedroom",
            "start_time": "22:00",
            "end_time": "06:00",
            "mode": "heat",
            "temperature": 25,
            "days": ["mon","tue","wed","thu","fri","sat","sun"]
        }
    ]
    
    with open("data/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)
    with open("data/schedules.json", "w") as f:
        json.dump({"schedules": schedules}, f, indent=2)

if __name__ == "__main__":
    build_env()
