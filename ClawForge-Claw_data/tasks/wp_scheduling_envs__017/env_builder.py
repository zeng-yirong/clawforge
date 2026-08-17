import os
import json
import random

def build_env():
    # 确保基础目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ========== 设备清单 (data/devices.json) ==========
    devices = [
        {"device_id": "bedroom_ac_001", "device_name": "Bedroom AC", "device_type": "ac", "location": "bedroom", "supported_settings": ["temperature", "mode"], "settings": {"temperature": 22, "mode": "cool"}},
        {"device_id": "bedroom_humidifier_002", "device_name": "Bedroom Humidifier", "device_type": "humidifier", "location": "bedroom", "supported_settings": ["mode", "humidity_level"], "settings": {"mode": "off", "humidity_level": 55}},
        {"device_id": "plug_003", "device_name": "Coffee Machine Smart Plug", "device_type": "smart_plug", "location": "kitchen", "supported_settings": ["power_state"], "settings": {"power_state": "off"}},
        {"device_id": "living_ac_004", "device_name": "Living Room AC", "device_type": "ac", "location": "living_room", "supported_settings": ["temperature", "mode"], "settings": {"temperature": 25, "mode": "cool"}},
        {"device_id": "living_humidifier_005", "device_name": "Living Room Humidifier", "device_type": "humidifier", "location": "living_room", "supported_settings": ["mode", "humidity_level"], "settings": {"mode": "off", "humidity_level": 50}},
    ]
    with open("data/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # ========== 日程表 (data/schedules.json) ==========
    # 包含干扰项: 过期的日程、无关设备、重复条目
    schedules = [
        {
            "schedule_id": "night_ac",
            "device_id": "bedroom_ac_001",
            "enabled": True,
            "start_time": "22:00",
            "end_time": "06:00",
            "settings": {"temperature": 22, "mode": "cool"}
        },
        {
            "schedule_id": "humidifier_afternoon",
            "device_id": "bedroom_humidifier_002",
            "enabled": True,
            "start_time": "14:00",
            "end_time": "16:00",
            "settings": {"mode": "auto", "humidity_level": 55}
        },
        {
            "schedule_id": "coffee_morning",
            "device_id": "plug_003",
            "enabled": True,
            "start_time": "07:00",
            "end_time": "07:30",
            "settings": {"power_state": "on"}
        },
        {
            "schedule_id": "living_ac_evening",
            "device_id": "living_ac_004",
            "enabled": True,
            "start_time": "18:00",
            "end_time": "23:00",
            "settings": {"temperature": 24, "mode": "cool"}
        },
        # 干扰：已禁用的重复日程（相同设备但已关闭）
        {
            "schedule_id": "night_ac_old",
            "device_id": "bedroom_ac_001",
            "enabled": False,
            "start_time": "22:00",
            "end_time": "06:00",
            "settings": {"temperature": 20, "mode": "cool"}
        },
        # 干扰：来自其他账户的废弃日程（设备不存在）
        {
            "schedule_id": "guest_room_humidifier",
            "device_id": "guest_humidifier_999",
            "enabled": True,
            "start_time": "10:00",
            "end_time": "12:00",
            "settings": {"mode": "auto", "humidity_level": 60}
        },
    ]
    with open("data/schedules.json", "w") as f:
        json.dump(schedules, f, indent=2)

    # ========== 额外干扰文件：旧版备份 ==========
    os.makedirs("backups", exist_ok=True)
    with open("backups/schedules_backup.json", "w") as f:
        json.dump(schedules + [{"schedule_id": "dummy"}], f, indent=2)

    # ========== 脏数据：一个格式错误的 CSV ==========
    with open("data/import_log.csv", "w") as f:
        f.write("device,time,value\nac,2024-01-01,22.5\nhumidifier,2024-01-01,broken\n")

    print("Environment built: devices.json + schedules.json with distractors and dirty data.")

if __name__ == "__main__":
    build_env()
