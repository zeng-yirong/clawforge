import os
import json

def build_env():
    # 创建必要的目录
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/schedules", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # Agent 将在此生成结果文件

    # ---- 设备清单 (data/devices/devices.json) ----
    devices = [
        {
            "device_id": "ac_living",
            "device_name": "Living Room AC",
            "device_type": "ac",
            "location": "living_room",
            "supported_settings": ["temperature", "mode", "power"],
            "settings": {"power_plug": "plug_ac_living"}
        },
        {
            "device_id": "plug_ac_living",
            "device_name": "Living Room AC Smart Plug",
            "device_type": "smart_plug",
            "location": "living_room",
            "supported_settings": ["power"],
            "settings": {}
        },
        {
            "device_id": "plug_tv",
            "device_name": "TV Smart Plug",
            "device_type": "smart_plug",
            "location": "living_room",
            "supported_settings": ["power"],
            "settings": {}
        },
        {
            "device_id": "plug_coffee",
            "device_name": "Coffee Machine Smart Plug",
            "device_type": "smart_plug",
            "location": "kitchen",
            "supported_settings": ["power"],
            "settings": {}
        },
        {
            "device_id": "bed_light",
            "device_name": "Bedroom Light",
            "device_type": "light",
            "location": "bedroom",
            "supported_settings": ["brightness", "color"],
            "settings": {}
        },
        {
            "device_id": "bed_humidifier",
            "device_name": "Bedroom Humidifier",
            "device_type": "humidifier",
            "location": "bedroom",
            "supported_settings": ["humidity_level", "power"],
            "settings": {}
        }
    ]
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # ---- 现行调度 (data/schedules/living_room_ac_schedule.json) ----
    current_schedule = {
        "schedule_id": "sched_001",
        "device_id": "ac_living",
        "action": "turn_on",
        "time": "15:00",
        "control_plug": "plug_tv",          # 错误：应该是 plug_ac_living
        "repeat": "daily"
    }
    with open("data/schedules/living_room_ac_schedule.json", "w") as f:
        json.dump(current_schedule, f, indent=2)

    # ---- 干扰调度 (data/schedules/old_schedule.json) ----
    old_schedule = {
        "schedule_id": "sched_001_old",
        "device_id": "ac_living",
        "action": "turn_on",
        "time": "15:00",
        "control_plug": "plug_coffee",      # 不同且已过期，不应被使用
        "repeat": "daily",
        "valid_from": "2024-01-01",
        "valid_until": "2024-06-30"
    }
    with open("data/schedules/old_schedule.json", "w") as f:
        json.dump(old_schedule, f, indent=2)

    # ---- 账户文件（干扰，agent 可以忽略） ----
    accounts = [
        {
            "account_id": "home1",
            "account_name": "Main Home",
            "location": "Seattle",
            "devices": ["ac_living", "plug_ac_living", "plug_tv", "plug_coffee", "bed_light", "bed_humidifier"],
            "schedules": ["sched_001"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

if __name__ == "__main__":
    build_env()
