import json
import os

def build_env():
    # 创建目录
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/schedules", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # 设备数据
    devices = [
        {
            "device_id": "bedroom_ac_001",
            "device_name": "Bedroom AC",
            "device_type": "ac",
            "location": "bedroom",
            "supported_settings": ["mode", "temperature", "fan_speed"],
            "settings": {"mode": "cool", "temperature": 22, "fan_speed": "auto"}
        },
        {
            "device_id": "living_light_002",
            "device_name": "Living Room Light",
            "device_type": "light",
            "location": "living_room",
            "supported_settings": ["brightness", "color"],
            "settings": {"brightness": 80, "color": "warm"}
        },
        {
            "device_id": "kitchen_plug_003",
            "device_name": "Coffee Machine Smart Plug",
            "device_type": "smart_plug",
            "location": "kitchen",
            "supported_settings": ["state"],
            "settings": {"state": "off"}
        }
    ]
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # 调度数据（包含冲突和干扰）
    schedules = [
        # 正常调度，无冲突
        {"schedule_id": "sch_001", "device_id": "living_light_002", "start_time": "2025-04-12T18:00:00", "end_time": "2025-04-12T22:00:00", "status": "active"},
        {"schedule_id": "sch_002", "device_id": "kitchen_plug_003", "start_time": "2025-04-12T07:00:00", "end_time": "2025-04-12T08:00:00", "status": "active"},
        # 针对 bedroom_ac_001 的已取消调度（干扰）
        {"schedule_id": "sch_003", "device_id": "bedroom_ac_001", "start_time": "2025-04-12T20:00:00", "end_time": "2025-04-12T23:00:00", "status": "cancelled"},
        # 真正活跃冲突：两个调度时间重叠
        {"schedule_id": "sch_004", "device_id": "bedroom_ac_001", "start_time": "2025-04-12T21:00:00", "end_time": "2025-04-12T23:30:00", "status": "active"},
        {"schedule_id": "sch_005", "device_id": "bedroom_ac_001", "start_time": "2025-04-12T22:00:00", "end_time": "2025-04-13T00:00:00", "status": "active"},
        # 其他设备的已取消冲突（干扰）
        {"schedule_id": "sch_006", "device_id": "living_light_002", "start_time": "2025-04-12T19:00:00", "end_time": "2025-04-12T21:00:00", "status": "cancelled"},
        {"schedule_id": "sch_007", "device_id": "living_light_002", "start_time": "2025-04-12T20:00:00", "end_time": "2025-04-12T22:00:00", "status": "cancelled"},
        # 脏数据：缺少必要字段的条目（应被忽略）
        {"schedule_id": "sch_008", "device_id": "bedroom_ac_001", "start_time": "2025-04-12T12:00:00", "status": "active"}  # missing end_time
    ]
    with open("data/schedules/schedules.json", "w") as f:
        json.dump({"schedules": schedules}, f, indent=2)

    # 干扰文件：无关日志
    with open("logs/activity.log", "w") as f:
        f.write("2025-04-12 10:00:00 INFO: system startup\n2025-04-12 10:01:00 INFO: device bedroom_ac_001 online\n")
    with open("logs/error.log", "w") as f:
        f.write("")

if __name__ == "__main__":
    build_env()
