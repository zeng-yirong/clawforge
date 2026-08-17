import os
import json
import csv
import random
from datetime import datetime, timedelta

def build_env():
    # 创建目录
    os.makedirs("schedules", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. 设备清单 (devices.json)
    devices = {
        "devices": [
            {"device_id": "device_001", "device_name": "Living Room AC", "device_type": "ac", "location": "living_room"},
            {"device_id": "device_002", "device_name": "Bedroom AC", "device_type": "ac", "location": "bedroom"},
            {"device_id": "device_003", "device_name": "Bedroom Humidifier", "device_type": "humidifier", "location": "bedroom"},
            {"device_id": "device_004", "device_name": "Living Room Light", "device_type": "light", "location": "living_room"},
            {"device_id": "device_005", "device_name": "Coffee Machine Smart Plug", "device_type": "smart_plug", "location": "kitchen"}
        ]
    }
    with open("devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # 2. 规则文件 (rules.conf) - 包含两条关键规则
    rules_content = """# Energy Saving Rules
# Rule 1: AC must NOT run between 13:00 and 15:00 on weekdays (peak hours)
# Rule 2: In the same room, AC and humidifier must NOT run simultaneously
# (Other rules are for future use)
"""
    with open("rules.conf", "w") as f:
        f.write(rules_content)

    # 3. 调度文件 (schedules/)
    # 各调度的时间段，注意模拟周一（weekday）
    # 我们固定当前日期为 2025-03-17 周一，这样时间比较方便
    today = datetime(2025, 3, 17, 0, 0, 0)  # Monday

    schedules_data = [
        # 合法调度：早上8-10点运行空调 (living room) - 合法
        {"schedule_id": "sched_001", "device_id": "device_001", "start": "08:00", "end": "10:00", "days": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "enabled": True},
        # 违规1：卧室空调在周一14:00-15:00运行 (违反规则1 peak hours)
        {"schedule_id": "sched_002", "device_id": "device_002", "start": "14:00", "end": "15:00", "days": ["Monday"], "enabled": True},
        # 合法：加湿器单独运行 (早上6-7点)
        {"schedule_id": "sched_003", "device_id": "device_003", "start": "06:00", "end": "07:00", "days": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "enabled": True},
        # 违规2：卧室空调和加湿器同时运行 (上午9-10点，空调也是卧室的) - 违反规则2
        # 注意 device_002 是 Bedroom AC，我们再加一个空调调度同时段与加湿器冲突
        {"schedule_id": "sched_004", "device_id": "device_002", "start": "09:00", "end": "10:00", "days": ["Monday"], "enabled": True},
        # 干扰项：已经禁用的调度 (不启用)
        {"schedule_id": "sched_005", "device_id": "device_005", "start": "14:00", "end": "15:00", "days": ["Monday"], "enabled": False},
        # 干扰项：加湿器合法调度 (晚上)
        {"schedule_id": "sched_006", "device_id": "device_003", "start": "20:00", "end": "21:00", "days": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "enabled": True}
    ]
    for sched in schedules_data:
        with open(f"schedules/{sched['schedule_id']}.json", "w") as f:
            json.dump(sched, f, indent=2)

    # 4. 能耗日志 (logs/energy_usage.csv) — 添加一些干扰但不需要精确匹配，只是作为背景
    with open("logs/energy_usage.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "device_id", "power_watts"])
        # 生成一些随机数据，包含违规时段的记录
        base = datetime(2025, 3, 17, 0, 0, 0)
        for hour in range(0, 24):
            for device in ["device_001","device_002","device_003"]:
                if random.random() < 0.3:  # 30%概率有记录
                    watt = random.randint(500, 2000)
                    writer.writerow([base.replace(hour=hour).isoformat(), device, watt])

    # 5. 创建一些干扰目录/文件 (例如旧的备份)
    os.makedirs("backups", exist_ok=True)
    with open("backups/old_schedules.json", "w") as f:
        json.dump({"deprecated": True}, f)

    # 注意：不创建 ops/overrides.json，因为那是预期产出

if __name__ == "__main__":
    build_env()
