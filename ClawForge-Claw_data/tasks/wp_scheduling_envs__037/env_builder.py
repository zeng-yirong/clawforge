import os
import json
import shutil

def build_env():
    # 创建必要的子目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("data/old_version", exist_ok=True)

    # --- 当前时间戳 ---
    with open("data/current_time.txt", "w") as f:
        f.write("2025-03-21T23:30:00\n")

    # --- 设备列表 (devices.json) ---
    devices = [
        {
            "device_id": "living_room_ac",
            "device_name": "Living Room AC",
            "device_type": "ac",
            "location": "living_room",
            "status": "on",
            "active": True
        },
        {
            "device_id": "bedroom_light",
            "device_name": "Bedroom Light",
            "device_type": "light",
            "location": "bedroom",
            "status": "off",
            "active": True
        },
        {
            "device_id": "coffee_machine_plug",
            "device_name": "Coffee Machine Smart Plug",
            "device_type": "smart_plug",
            "location": "kitchen",
            "status": "on",
            "active": True
        },
        {
            "device_id": "balcony_light",
            "device_name": "Balcony Light",
            "device_type": "light",
            "location": "balcony",
            "status": "on",
            "active": False  # 已废弃设备，不应操作
        },
        {
            "device_id": "tv_plug",
            "device_name": "TV Smart Plug",
            "device_type": "smart_plug",
            "location": "living_room",
            "status": "off",
            "active": True
        }
    ]
    with open("data/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # --- 最新调度规则 (schedules.json) ---
    schedules = [
        {
            "device_id": "living_room_ac",
            "start": "10:00",
            "end": "22:00",
            "enabled": True
        },
        {
            "device_id": "bedroom_light",
            "start": "18:00",
            "end": "23:00",
            "enabled": True
        },
        {
            "device_id": "coffee_machine_plug",
            "start": "00:00",
            "end": "23:59",
            "enabled": True
        },
        {
            "device_id": "balcony_light",
            "start": "06:00",
            "end": "22:00",
            "enabled": True
        }
    ]
    with open("data/schedules.json", "w") as f:
        json.dump(schedules, f, indent=2)

    # --- 干扰项1：旧版本调度的备份 (old_version/schedules.json) ---
    old_schedules = [
        {
            "device_id": "living_room_ac",
            "start": "10:00",
            "end": "23:00",  # 旧版本结束时间更晚，若用此则会认为不需要关
            "enabled": True
        }
    ]
    with open("data/old_version/schedules.json", "w") as f:
        json.dump(old_schedules, f, indent=2)

    # --- 干扰项2：一个非 JSON 文件，阅读时会抛错 ---
    with open("data/error.json", "w") as f:
        f.write("这不是一个JSON文件，而是一些无意义的文本\n")

    # --- 干扰项3：一个无关的日志文件 ---
    with open("data/irrelevant.log", "w") as f:
        f.write("[2025-03-21 10:00] System startup\n[2025-03-21 22:00] AC auto-off triggered\n")

    # 额外：旧版本目录下放个空文件迷惑
    with open("data/old_version/.keep", "w") as f:
        f.write("")

if __name__ == "__main__":
    build_env()
