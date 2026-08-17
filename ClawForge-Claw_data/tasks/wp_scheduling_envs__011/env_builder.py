import os
import json
import random

def build_env():
    # 创建目录结构
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 设备数据
    devices = [
        {"device_id": "ac_living_01", "device_name": "Living Room AC", "device_type": "ac", "location": "living_room", "supported_settings": ["temperature", "mode"], "settings": {"temperature": 24, "mode": "cool"}},
        {"device_id": "ac_living_02", "device_name": "Living Room AC 2", "device_type": "ac", "location": "living_room", "supported_settings": ["temperature", "mode"], "settings": {"temperature": 22, "mode": "cool"}},
        {"device_id": "ac_bedroom_01", "device_name": "Bedroom AC", "device_type": "ac", "location": "bedroom", "supported_settings": ["temperature", "mode"], "settings": {"temperature": 26, "mode": "fan"}},
        {"device_id": "light_living_01", "device_name": "Living Room Light", "device_type": "light", "location": "living_room", "supported_settings": ["brightness"], "settings": {"brightness": 80}},
        {"device_id": "plug_coffee", "device_name": "Coffee Machine Smart Plug", "device_type": "smart_plug", "location": "kitchen", "supported_settings": ["power"], "settings": {"power": "on"}},
    ]
    with open("data/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # 调度数据（包含干扰项）
    schedules = [
        # 客厅 AC 冲突组（周三下午重叠）
        {"schedule_id": "sched_001", "device_id": "ac_living_01", "day_of_week": "Wednesday", "start_hour": 14, "end_hour": 16, "active": True},
        {"schedule_id": "sched_002", "device_id": "ac_living_02", "day_of_week": "Wednesday", "start_hour": 15, "end_hour": 17, "active": True},
        # 另一个只和sched_002部分重叠，但仍在周三
        {"schedule_id": "sched_003", "device_id": "ac_living_01", "day_of_week": "Wednesday", "start_hour": 15, "end_hour": 16, "active": True},  # 与001,002都重叠
        # 周三但active=false（干扰）
        {"schedule_id": "sched_004", "device_id": "ac_living_01", "day_of_week": "Wednesday", "start_hour": 14, "end_hour": 15, "active": False},
        # 客厅 AC 但周二（干扰）
        {"schedule_id": "sched_005", "device_id": "ac_living_01", "day_of_week": "Tuesday", "start_hour": 14, "end_hour": 16, "active": True},
        # 卧室 AC 周三（地点错误）
        {"schedule_id": "sched_006", "device_id": "ac_bedroom_01", "day_of_week": "Wednesday", "start_hour": 14, "end_hour": 16, "active": True},
        # 非AC设备调度（干扰）
        {"schedule_id": "sched_007", "device_id": "light_living_01", "day_of_week": "Wednesday", "start_hour": 18, "end_hour": 22, "active": True},
        # 另一个客厅AC调度但不重叠（周三早）
        {"schedule_id": "sched_008", "device_id": "ac_living_02", "day_of_week": "Wednesday", "start_hour": 8, "end_hour": 10, "active": True},
        # 完全相同的时段（还是重叠）
        {"schedule_id": "sched_009", "device_id": "ac_living_02", "day_of_week": "Wednesday", "start_hour": 14, "end_hour": 16, "active": True},  # 与001,002,003重叠
    ]
    with open("data/schedules.json", "w") as f:
        json.dump({"schedules": schedules}, f, indent=2)

    # 日志文件（干扰，但可忽略）
    with open("logs/system.log", "w") as f:
        f.write("2025-03-12 14:23:45 WARNING: Living Room AC temperature oscillation detected\n")
        f.write("2025-03-12 15:10:12 INFO: Schedule sched_001 triggered\n")
        f.write("2025-03-12 15:00:30 INFO: Schedule sched_002 also triggered\n")
    with open("logs/access.log", "w") as f:
        f.write("192.168.1.100 - - [12/Mar/2025:14:00:00 +0000] \"POST /api/turn-on\" 200\n")
    # 一个无关的CSV文件（干扰）
    with open("data/temperatures.csv", "w") as f:
        f.write("time,living_room,bedroom\n")
        f.write("14:00,24.5,26.1\n")
        f.write("15:00,25.2,26.3\n")

    # 正确答案：所有在周三、active=true、地点living room、ac设备、时间区间重叠的调度ID
    # 分析：
    # 符合条件的设备ID: ac_living_01, ac_living_02
    # 符合条件的调度中有：
    # sched_001 (14-16), sched_002 (15-17), sched_003 (15-16), sched_008 (8-10不重叠), sched_009 (14-16)
    # 重叠定义为存在时间区间交集（非完全包含也算）
    # 分组检查：
    # 14-16 与 15-17 重叠；14-16 与 15-16重叠；15-17 与 15-16重叠；15-17 与14-16重叠；14-16与14-16（sched_009）重叠。
    # 实际上所有14-16,15-17,15-16,14-16这些全部互相重叠（因为区间有共同部分）。
    # 所以冲突的调度ID：sched_001, sched_002, sched_003, sched_009
    # 注意sched_008是8-10，不重叠。
    # 预期列表排序后：["sched_001","sched_002","sched_003","sched_009"]
    # 存储用于验证
    expected = sorted(["sched_001","sched_002","sched_003","sched_009"])
    with open("ops/.expected.json", "w") as f:
        json.dump(expected, f)

if __name__ == "__main__":
    build_env()
