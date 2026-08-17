import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/backup", exist_ok=True)
    os.makedirs("data/trash", exist_ok=True)
    os.makedirs("raw_logs", exist_ok=True)

    # ===== 设备数据 =====
    devices = {
        "devices": [
            {
                "device_id": "device_001",
                "device_name": "Bedroom Humidifier",
                "device_type": "humidifier",
                "location": "bedroom",
                "supported_settings": ["power", "humidity"],
                "settings": {"power": "on", "humidity": 50}
            },
            {
                "device_id": "device_002",
                "device_name": "Living Room AC",
                "device_type": "ac",
                "location": "living_room",
                "supported_settings": ["power", "temperature", "mode"],
                "settings": {"power": "off", "temperature": 24, "mode": "cool"}
            },
            {
                "device_id": "device_003",
                "device_name": "Bedroom Light",
                "device_type": "light",
                "location": "bedroom",
                "supported_settings": ["power", "brightness", "color"],
                "settings": {"power": "on", "brightness": 80, "color": "warm"}
            },
            {
                "device_id": "device_004",
                "device_name": "Coffee Machine Smart Plug",
                "device_type": "smart_plug",
                "location": "kitchen",
                "supported_settings": ["power"],
                "settings": {"power": "off"}
            },
            {
                "device_id": "device_005",
                "device_name": "TV Smart Plug",
                "device_type": "smart_plug",
                "location": "living_room",
                "supported_settings": ["power"],
                "settings": {"power": "on"}
            }
        ]
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # ===== 账户与调度数据 =====
    accounts = {
        "accounts": [
            {
                "account_id": "acc-1001",
                "account_name": "Home Alpha",
                "location": "building A",
                "devices": ["device_001", "device_002", "device_003"],
                "schedules": [
                    {"schedule_id": "sched-1", "device_id": "device_001", "start": "08:00", "end": "09:30"},
                    {"schedule_id": "sched-2", "device_id": "device_001", "start": "14:00", "end": "15:00"},
                    {"schedule_id": "sched-3", "device_id": "device_002", "start": "09:00", "end": "11:00"},
                    {"schedule_id": "sched-4", "device_id": "device_002", "start": "14:30", "end": "16:00"},
                    {"schedule_id": "sched-5", "device_id": "device_003", "start": "18:00", "end": "20:30"},
                    {"schedule_id": "sched-6", "device_id": "device_001", "start": "20:00", "end": "21:00"},
                    # 干扰：开始时间>=结束时间
                    {"schedule_id": "sched-10", "device_id": "device_001", "start": "10:00", "end": "09:00"},
                    # 干扰：设备不存在
                    {"schedule_id": "sched-11", "device_id": "device_invalid", "start": "15:00", "end": "16:00"}
                ]
            },
            {
                "account_id": "acc-1002",
                "account_name": "Home Beta",
                "location": "building B",
                "devices": ["device_004", "device_005"],
                "schedules": [
                    {"schedule_id": "sched-7", "device_id": "device_004", "start": "07:00", "end": "08:30"},
                    {"schedule_id": "sched-8", "device_id": "device_005", "start": "12:00", "end": "14:00"},
                    {"schedule_id": "sched-9", "device_id": "device_005", "start": "10:00", "end": "11:00"}
                ]
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ===== 干扰文件：过期备份 =====
    backup_accounts = {
        "accounts": [
            {
                "account_id": "acc-1001",
                "account_name": "Home Alpha",
                "location": "building A",
                "devices": ["device_001", "device_002", "device_003"],
                "schedules": [
                    {"schedule_id": "sched-1", "device_id": "device_001", "start": "08:00", "end": "09:30"},
                    {"schedule_id": "sched-2", "device_id": "device_001", "start": "14:00", "end": "14:30"}  # 旧版更短
                ]
            }
        ]
    }
    with open("data/backup/accounts_backup.json", "w") as f:
        json.dump(backup_accounts, f, indent=2)

    # ===== 干扰文件：CSV 日志 =====
    open("raw_logs/energy_20240321.csv", "w").write("timestamp,device,power\n2024-03-21 08:15,device_001,120\n")
    open("raw_logs/energy_20240322.csv", "w").write("timestamp,device,power\n2024-03-22 09:00,device_002,1500\n")
    # 无用的空目录
    open("data/trash/.gitkeep", "w").close()

if __name__ == "__main__":
    build_env()
