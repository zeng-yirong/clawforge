import os
import json

def build_env():
    # 确保基础目录
    os.makedirs("data/health", exist_ok=True)
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/occupancy", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 空目录供 agent 写入

    # 健康数据 —— 两个住户
    health = {
        "users": [
            {
                "user_id": "u_jane",
                "name": "Jane Smith",
                "age": 32,
                "health_conditions": ["asthma"],
                "respiratory_issues": True,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 22, "max": 24},
                "humidity_preference": {"min": 40, "max": 50},
                "sleep_schedule": {"start": "22:00", "end": "06:00"}
            },
            {
                "user_id": "u_john",
                "name": "John Smith",
                "age": 35,
                "health_conditions": ["allergies"],
                "respiratory_issues": False,
                "cardiovascular_risk": False,
                "temperature_preference": {"min": 20, "max": 22},
                "humidity_preference": {"min": 30, "max": 40},
                "sleep_schedule": {"start": "23:00", "end": "07:00"}
            }
        ]
    }
    with open("data/health/health.json", "w") as f:
        json.dump(health, f, indent=2)

    # 设备数据 —— 包含干扰项（无用户房间的设备、不带温湿度设置的智能插头）
    devices = {
        "devices": [
            {
                "device_id": "ac_bedroom_01",
                "name": "Bedroom AC",
                "type": "air_conditioner",
                "location": "bedroom",
                "power_watts": 2000,
                "default_settings": {"target_temperature": 23, "target_humidity": 45}
            },
            {
                "device_id": "humidifier_bedroom_01",
                "name": "Bedroom Humidifier",
                "type": "humidifier",
                "location": "bedroom",
                "power_watts": 500,
                "default_settings": {"target_humidity": 55}  # 湿度太高 → 冲突
            },
            {
                "device_id": "ac_living_01",
                "name": "Living Room AC",
                "type": "air_conditioner",
                "location": "living_room",
                "power_watts": 2500,
                "default_settings": {"target_temperature": 21, "target_humidity": 35}
            },
            {
                "device_id": "humidifier_living_01",
                "name": "Living Room Humidifier",
                "type": "humidifier",
                "location": "living_room",
                "power_watts": 600,
                "default_settings": {"target_humidity": 25}  # 湿度太低 → 冲突
            },
            {
                "device_id": "plug_study_01",
                "name": "Desk Setup Smart Plug",
                "type": "smart_plug",
                "location": "study_room",
                "power_watts": 300,
                "default_settings": {}
            },
            {
                "device_id": "plug_living_lamp",
                "name": "Floor Lamp Smart Plug",
                "type": "smart_plug",
                "location": "living_room",
                "power_watts": 100,
                "default_settings": {}
            },
            {
                "device_id": "plug_living_tv",
                "name": "TV Smart Plug",
                "type": "smart_plug",
                "location": "living_room",
                "power_watts": 150,
                "default_settings": {}
            }
        ]
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # 房间-住户映射
    occupancy = {
        "rooms": [
            {"room": "bedroom", "occupant": "Jane Smith"},
            {"room": "living_room", "occupant": "John Smith"}
            # study_room 没有住户，属于干扰
        ]
    }
    with open("data/occupancy/rooms.json", "w") as f:
        json.dump(occupancy, f, indent=2)

if __name__ == "__main__":
    build_env()
