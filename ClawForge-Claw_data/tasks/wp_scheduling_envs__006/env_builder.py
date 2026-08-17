import os
import json

def build_env():
    # 创建 data 目录
    os.makedirs("data", exist_ok=True)
    
    # 创建 devices.json（包含干扰项）
    devices = [
        {"device_id": "ac-001", "device_name": "Living Room AC", "device_type": "ac", "location": "living_room", "settings": {"target_temperature": 24}},
        {"device_id": "ac-002", "device_name": "Bedroom AC", "device_type": "ac", "location": "bedroom", "settings": {"target_temperature": 22}},
        {"device_id": "ac-003", "device_name": "Study AC", "device_type": "ac", "location": "study", "settings": {"target_temperature": 25}},
        {"device_id": "light-001", "device_name": "Living Room Light", "device_type": "light", "location": "living_room", "settings": {}},
        {"device_id": "light-002", "device_name": "Bedroom Light", "device_type": "light", "location": "bedroom", "settings": {}},
        {"device_id": "plug-001", "device_name": "Coffee Machine Smart Plug", "device_type": "smart_plug", "location": "kitchen", "settings": {}},
        {"device_id": "hum-001", "device_name": "Bedroom Humidifier", "device_type": "humidifier", "location": "bedroom", "settings": {}}
    ]
    with open("data/devices.json", "w") as f:
        json.dump(devices, f, indent=2)
    
    # 创建 sensors.csv（含脏数据）
    csv_lines = [
        "# Room Temperature Sensor Log",
        "room,temperature,time",
        "# living_room sample",
        "living_room,26.0,2025-04-16 10:00",
        "living_room,27.0,2025-04-16 10:05",
        "bedroom,21.0,2025-04-16 10:00",
        "bedroom,21.0,2025-04-16 10:05",
        "study,24.5,2025-04-16 10:00",
        "study,25.0,2025-04-16 10:05",
        "# duplicate line",
        "living_room,26.5,2025-04-16 10:10",
        "bedroom,20.5,2025-04-16 10:10",
        "study,24.8,2025-04-16 10:10",
        "# invalid entry",
        "kitchen,,",
        "",
        "# comment only",
        "# more data"
    ]
    with open("data/sensors.csv", "w") as f:
        f.write("\n".join(csv_lines))
    # 不创建 ops 目录，让 agent 自行创建

if __name__ == "__main__":
    build_env()
