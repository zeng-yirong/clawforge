import os
import json
import csv
import shutil

def build_env():
    # 清理旧内容（防止重复运行）
    if os.path.exists("ops"):
        shutil.rmtree("ops")
    if os.path.exists("backups"):
        shutil.rmtree("backups")
    for f in ["devices.json", "schedules.json", "sensor_data.csv", "user_preferences.json"]:
        if os.path.exists(f):
            os.remove(f)

    # 设备清单
    devices = {
        "devices": [
            {
                "device_id": "ac_bedroom",
                "device_name": "Bedroom AC",
                "device_type": "ac",
                "location": "bedroom",
                "supported_settings": ["mode", "temperature", "fan_speed"],
                "settings": {"mode": "cool", "temperature": 24, "fan_speed": "auto"}
            },
            {
                "device_id": "ac_living",
                "device_name": "Living Room AC",
                "device_type": "ac",
                "location": "living_room",
                "supported_settings": ["mode", "temperature", "fan_speed"],
                "settings": {"mode": "cool", "temperature": 26, "fan_speed": "low"}
            },
            {
                "device_id": "light_bedroom",
                "device_name": "Bedroom Light",
                "device_type": "light",
                "location": "bedroom",
                "supported_settings": ["brightness", "color_temperature"],
                "settings": {"brightness": 80, "color_temperature": 3000}
            }
        ]
    }
    with open("devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # 现有调度
    schedules = {
        "schedules": [
            {
                "schedule_id": "sch_001",
                "device_id": "ac_bedroom",
                "start_time": "18:00",
                "end_time": "20:00",
                "repeat": "daily",
                "action": {"mode": "cool", "temperature": 24}
            },
            {
                "schedule_id": "sch_002",
                "device_id": "ac_living",
                "start_time": "12:00",
                "end_time": "14:00",
                "repeat": "daily",
                "action": {"mode": "cool", "temperature": 26}
            }
        ]
    }
    with open("schedules.json", "w") as f:
        json.dump(schedules, f, indent=2)

    # 传感器数据（卧室每半小时温度）
    sensor_rows = []
    # 生成 24h 数据，从 00:00 开始
    # 00:00 25.2, 00:30 25.1, 01:00 24.9, 01:30 24.7, 02:00 24.5, 02:30 24.0,
    # 03:00 23.5 ... 白天正常 22-23，晚上从22:00开始超标
    # 关键时段：22:00～02:00 超过 24°C
    times = []
    for hour in range(0, 24):
        for minute in [0, 30]:
            t = f"{hour:02d}:{minute:02d}"
            times.append(t)
    temp_dict = {}
    for t in times:
        h = int(t.split(":")[0])
        m = int(t.split(":")[1])
        # 白天 (6-18) 常温 22-23
        if 6 <= h < 18:
            temp = 22.0 + (m / 60) * 0.2  # 小波动
        else:
            # 夜晚，从 22:00 开始升温
            if h == 22:
                if m == 0:
                    temp = 24.5
                else:
                    temp = 24.6
            elif h == 23:
                if m == 0:
                    temp = 24.8
                else:
                    temp = 25.0
            elif h == 0:
                if m == 0:
                    temp = 25.2
                else:
                    temp = 25.1
            elif h == 1:
                if m == 0:
                    temp = 24.9
                else:
                    temp = 24.7
            elif h == 2:
                if m == 0:
                    temp = 24.5
                else:
                    temp = 24.0
            elif h == 3:
                if m == 0:
                    temp = 23.5
                else:
                    temp = 23.0
            else:
                temp = 22.0
        # 其他房间（living_room）保持 24-25 恒定
        temp_dict[t] = {"bedroom": round(temp, 1), "living_room": 24.5}
    # 写入CSV
    with open("sensor_data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "room", "temperature"])
        for t, rooms in temp_dict.items():
            for r, temp in rooms.items():
                writer.writerow([t, r, temp])

    # 用户偏好
    preferences = {
        "bedroom": {
            "target_temp_min": 22,
            "target_temp_max": 24
        },
        "living_room": {
            "target_temp_min": 24,
            "target_temp_max": 26
        }
    }
    with open("user_preferences.json", "w") as f:
        json.dump(preferences, f, indent=2)

    # 干扰项：备份文件夹、无关日志
    os.makedirs("backups", exist_ok=True)
    with open("backups/schedules_backup.json", "w") as f:
        json.dump({"backup": True, "data": []}, f)
    os.makedirs("logs", exist_ok=True)
    with open("logs/error.log", "w") as f:
        f.write("INFO: No errors today\n")
    # 额外无意义文件
    with open("temp_override.txt", "w") as f:
        f.write("do not use this file")

    # 确保 ops 目录存在（待 agent 创建）
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
