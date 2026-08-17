import json
import os

def build_env():
    # 确保 data 目录存在
    os.makedirs("data", exist_ok=True)

    # === 设备清单 ===
    devices = [
        {
            "device_id": "bedroom_humidifier_01",
            "device_name": "Bedroom Humidifier",
            "device_type": "humidifier",
            "location": "bedroom",
            "supported_settings": ["target_humidity"],
            "settings": {}
        },
        {
            "device_id": "bedroom_light_01",
            "device_name": "Bedroom Light",
            "device_type": "light",
            "location": "bedroom",
            "supported_settings": ["brightness"],
            "settings": {}
        },
        {
            "device_id": "coffee_machine_01",
            "device_name": "Coffee Machine Smart Plug",
            "device_type": "smart_plug",
            "location": "kitchen",
            "supported_settings": ["power"],
            "settings": {}
        },
        {
            "device_id": "living_room_ac_01",
            "device_name": "Living Room AC",
            "device_type": "ac",
            "location": "living_room",
            "supported_settings": ["mode", "target_temperature", "target_humidity"],
            "settings": {}
        },
        {
            "device_id": "living_room_light_01",
            "device_name": "Living Room Light",
            "device_type": "light",
            "location": "living_room",
            "supported_settings": ["brightness"],
            "settings": {}
        },
        {
            "device_id": "tv_smart_plug_01",
            "device_name": "TV Smart Plug",
            "device_type": "smart_plug",
            "location": "living_room",
            "supported_settings": ["power"],
            "settings": {}
        }
    ]
    with open("data/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # === 调度计划（包含干扰项 + 唯一冲突）===
    schedules = [
        # 冲突对：humidifier 高湿度 + AC 除湿低湿度，时间重叠
        {
            "device_id": "bedroom_humidifier_01",
            "start_time": "22:00",
            "end_time": "23:00",
            "settings": {"target_humidity": 70}
        },
        {
            "device_id": "living_room_ac_01",
            "start_time": "22:00",
            "end_time": "23:00",
            "settings": {"mode": "dehumidify", "target_humidity": 35}
        },
        # 干扰：卧室灯，时间与 ac/humidifier 部分重叠，但类型不冲突
        {
            "device_id": "bedroom_light_01",
            "start_time": "20:00",
            "end_time": "21:00",
            "settings": {"brightness": 80}
        },
        # 干扰：咖啡机早晨
        {
            "device_id": "coffee_machine_01",
            "start_time": "07:00",
            "end_time": "07:30",
            "settings": {"brew": "normal"}
        },
        # 干扰：电视插头晚上
        {
            "device_id": "tv_smart_plug_01",
            "start_time": "19:00",
            "end_time": "22:30",
            "settings": {"power": "on"}
        },
        # 干扰：加湿器另一次（不冲突，时间不与任何 ac 除湿重叠）
        {
            "device_id": "bedroom_humidifier_01",
            "start_time": "07:30",
            "end_time": "08:00",
            "settings": {"target_humidity": 50}
        },
        # 干扰：空调下午（模式 cool，非除湿）
        {
            "device_id": "living_room_ac_01",
            "start_time": "14:00",
            "end_time": "15:00",
            "settings": {"mode": "cool", "target_temperature": 24}
        }
    ]
    with open("data/schedules.json", "w") as f:
        json.dump(schedules, f, indent=2)

    # 创建干扰目录和文件（增加迷惑性）
    os.makedirs("logs", exist_ok=True)
    with open("logs/app.log", "w") as f:
        f.write("2025-04-07 21:55:00 INFO scheduler: dispatching device bedroom_humidifier_01\n")
        f.write("2025-04-07 21:55:01 INFO scheduler: dispatching device living_room_ac_01\n")
        f.write("2025-04-07 22:00:00 INFO scheduler: started both tasks\n")

if __name__ == "__main__":
    build_env()
