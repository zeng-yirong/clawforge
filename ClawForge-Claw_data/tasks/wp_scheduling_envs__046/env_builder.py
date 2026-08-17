import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/schedules", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("backups", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 空目录，等待 agent 写入

    # 设备信息
    devices = {
        "devices": [
            {
                "device_id": "d001",
                "device_name": "Living Room AC",
                "device_type": "ac",
                "location": "living_room",
                "supported_settings": ["power", "temperature_celsius", "mode"],
                "current_settings": {"power": "off", "temperature_celsius": 26, "mode": "cool"}
            },
            {
                "device_id": "d002",
                "device_name": "Bedroom Light",
                "device_type": "light",
                "location": "bedroom",
                "supported_settings": ["power", "brightness"],
                "current_settings": {"power": "off", "brightness": 80}
            },
            {
                "device_id": "d003",
                "device_name": "Coffee Machine Smart Plug",
                "device_type": "smart_plug",
                "location": "kitchen",
                "supported_settings": ["power"],
                "current_settings": {"power": "off"}
            }
        ]
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # 定时任务（含干扰：一个被禁用的下午空调开启任务）
    schedules = {
        "schedules": [
            {
                "schedule_id": "sched_001",
                "device_id": "d001",
                "start_time": "10:00",
                "end_time": "12:00",
                "action": "turn_on",
                "settings": {"temperature_celsius": 24, "mode": "cool"},
                "enabled": True
            },
            {
                "schedule_id": "sched_002",
                "device_id": "d002",
                "start_time": "18:00",
                "end_time": "22:00",
                "action": "turn_on",
                "settings": {"brightness": 50},
                "enabled": True
            },
            {
                "schedule_id": "sched_003",
                "device_id": "d001",
                "start_time": "12:00",
                "end_time": "18:00",
                "action": "turn_on",
                "settings": {"temperature_celsius": 24, "mode": "cool"},
                "enabled": False  # 已禁用，所以下午空调实际上没有自动开启
            }
        ]
    }
    with open("data/schedules/schedules.json", "w") as f:
        json.dump(schedules, f, indent=2)

    # 用户偏好
    prefs = {"preferred_ac_temperature": 24}
    with open("data/user_preferences.json", "w") as f:
        json.dump(prefs, f, indent=2)

    # 温度日志（干扰：下午温度飙升，暗示需要开启空调）
    log_content = "timestamp,temperature_celsius\n14:00,29\n15:00,30\n16:00,31\n17:00,32\n"
    with open("logs/temperature_log.csv", "w") as f:
        f.write(log_content)

    # 历史备份（干扰）
    backup = {
        "schedules": [
            {
                "schedule_id": "old_001",
                "device_id": "d002",
                "start_time": "06:00",
                "end_time": "08:00",
                "action": "turn_on",
                "settings": {"brightness": 100},
                "enabled": True
            }
        ]
    }
    with open("backups/schedules_old.json", "w") as f:
        json.dump(backup, f, indent=2)

if __name__ == "__main__":
    build_env()
