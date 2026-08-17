import os
import json
from datetime import datetime, timedelta

def build_env():
    # 设备列表
    devices = [
        {"device_id": "ac_lr_001", "device_name": "Living Room AC", "device_type": "ac", "location": "living_room", "supported_settings": ["mode", "temp", "fan_speed"], "settings": {"mode": "cool", "temp": 24, "fan_speed": "auto"}},
        {"device_id": "plug_coffee_002", "device_name": "Coffee Machine Smart Plug", "device_type": "smart_plug", "location": "living_room", "supported_settings": ["on_off"], "settings": {"on_off": "off"}},
        {"device_id": "light_bed_003", "device_name": "Bedroom Light", "device_type": "light", "location": "bedroom", "supported_settings": ["brightness", "color"], "settings": {"brightness": 80, "color": "warm"}},
        {"device_id": "hum_bed_004", "device_name": "Bedroom Humidifier", "device_type": "humidifier", "location": "bedroom", "supported_settings": ["humidity", "speed"], "settings": {"humidity": 55, "speed": "medium"}},
        {"device_id": "plug_tv_005", "device_name": "TV Smart Plug", "device_type": "smart_plug", "location": "living_room", "supported_settings": ["on_off"], "settings": {"on_off": "off"}},
        # 干扰：一个已废弃的旧空调（同名但不同ID）
        {"device_id": "ac_lr_old_001", "device_name": "Living Room AC", "device_type": "ac", "location": "living_room", "supported_settings": ["mode", "temp"], "settings": {"mode": "heat", "temp": 20}}
    ]
    os.makedirs("data", exist_ok=True)
    with open("data/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # 调度表 —— 包含冲突与干扰
    schedules = [
        # 空调下午时段 15:00-16:00
        {"schedule_id": "sch_ac_afternoon", "device_id": "ac_lr_001", "start": "15:00", "end": "16:00", "day": "weekdays", "active": True},
        # 咖啡机下午时段 15:00-16:00 （冲突）
        {"schedule_id": "sch_coffee_afternoon", "device_id": "plug_coffee_002", "start": "15:00", "end": "16:00", "day": "weekdays", "active": True},
        # 其他不相关的调度
        {"schedule_id": "sch_ac_morning", "device_id": "ac_lr_001", "start": "09:00", "end": "10:00", "day": "weekdays", "active": True},
        {"schedule_id": "sch_light_evening", "device_id": "light_bed_003", "start": "19:00", "end": "22:00", "day": "weekdays", "active": True},
        {"schedule_id": "sch_hum_night", "device_id": "hum_bed_004", "start": "22:00", "end": "06:00", "day": "daily", "active": True},
        # 干扰：旧空调的无效调度（已过期）
        {"schedule_id": "sch_old_ac_afternoon", "device_id": "ac_lr_old_001", "start": "15:00", "end": "16:00", "day": "weekdays", "active": False},
        # 干扰：重复咖啡机调度（但时间不同）
        {"schedule_id": "sch_coffee_dup", "device_id": "plug_coffee_002", "start": "16:30", "end": "17:00", "day": "weekdays", "active": True},
    ]
    with open("data/schedules.json", "w") as f:
        json.dump({"schedules": schedules}, f, indent=2)

    # 创建空目标目录
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
