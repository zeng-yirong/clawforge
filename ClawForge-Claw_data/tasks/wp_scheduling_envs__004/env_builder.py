import os
import json
import random

def build_env():
    # 确保目录存在
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 固定随机种子以保证确定性
    random.seed(42)

    # 合法的设备列表（正确答案）
    valid_devices = [
        {"device_id": "ac_living_01", "device_name": "Living Room AC", "device_type": "ac", "location": "living_room", "settings": {"mode": "cool", "temperature": 24}},
        {"device_id": "light_bedroom_01", "device_name": "Bedroom Light", "device_type": "light", "location": "bedroom", "settings": {"brightness": 80}},
        {"device_id": "humidifier_bedroom_01", "device_name": "Bedroom Humidifier", "device_type": "humidifier", "location": "bedroom", "settings": {"humidity": 50}},
        {"device_id": "plug_coffee_01", "device_name": "Coffee Machine Smart Plug", "device_type": "smart_plug", "location": "kitchen", "settings": {"power": 0}},
        {"device_id": "light_living_01", "device_name": "Living Room Light", "device_type": "light", "location": "living_room", "settings": {"brightness": 60}},
        {"device_id": "tv_plug_01", "device_name": "TV Smart Plug", "device_type": "smart_plug", "location": "living_room", "settings": {"power": 1}},
    ]

    # 干扰记录（重复、无效类型、缺字段等）
    noise_devices = [
        # 重复 device_id，但 type 无效
        {"device_id": "light_bedroom_01", "device_name": "Bedroom Light (duplicate)", "device_type": "lamp", "location": "bedroom", "settings": {"brightness": 100}},
        # 无效 type
        {"device_id": "fridge_01", "device_name": "Fridge", "device_type": "fridge", "location": "kitchen", "settings": {"temp": 4}},
        # 缺少 device_type 字段
        {"device_id": "missing_type_01", "device_name": "Some Device", "location": "living_room", "settings": {}},
        # 缺少 device_id
        {"device_name": "Orphan Light", "device_type": "light", "location": "bedroom", "settings": {"brightness": 50}},
        # 大写 type 变体（不在允许列表中）
        {"device_id": "ac_living_02", "device_name": "Living Room AC (uppercase)", "device_type": "Ac", "location": "living_room", "settings": {}},
    ]

    # 合并并打乱顺序
    all_devices = valid_devices + noise_devices
    random.shuffle(all_devices)

    # 写入原始设备文件
    with open("data/devices.json", "w") as f:
        json.dump(all_devices, f, indent=2)

    # 系统允许的设备类型列表
    allowed_types = ["ac", "humidifier", "light", "smart_plug"]
    with open("data/device_types.json", "w") as f:
        json.dump(allowed_types, f, indent=2)

    # 额外干扰：调度文件（与主任务无关）
    schedules = [
        {"schedule_id": "sched_001", "device_id": "ac_living_01", "action": "turn_on", "time": "06:00", "days": ["weekday"]},
        {"schedule_id": "sched_002", "device_id": "light_bedroom_01", "action": "turn_on", "time": "07:00", "days": ["weekday"]},
        {"schedule_id": "sched_003", "device_id": "fridge_01", "action": "turn_off", "time": "22:00", "days": ["all"]},
    ]
    with open("data/schedules.json", "w") as f:
        json.dump({"schedules": schedules}, f, indent=2)

if __name__ == "__main__":
    build_env()
