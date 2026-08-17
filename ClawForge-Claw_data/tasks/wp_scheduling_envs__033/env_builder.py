import os
import json

def build_env():
    # 确保必要目录存在
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/schedules", exist_ok=True)
    os.makedirs("data/accounts", exist_ok=True)
    os.makedirs("raw_logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- 设备数据（含干扰设备） ---
    devices = [
        {
            "device_id": "ac_001",
            "device_name": "Living Room AC",
            "device_type": "ac",
            "location": "living_room",
            "supported_settings": ["mode", "temperature", "fan_speed", "swing"],
            "settings": {"mode": "auto", "temperature": 22, "fan_speed": "auto"}
        },
        {
            "device_id": "ac_002",  # 干扰：卧室空调
            "device_name": "Bedroom AC",
            "device_type": "ac",
            "location": "bedroom",
            "supported_settings": ["mode", "temperature", "fan_speed"],
            "settings": {"mode": "cool", "temperature": 26, "fan_speed": "low"}
        },
        {
            "device_id": "humid_001",
            "device_name": "Bedroom Humidifier",
            "device_type": "humidifier",
            "location": "bedroom",
            "supported_settings": ["mode", "humidity_target"],
            "settings": {"mode": "on", "humidity_target": 50}
        },
        {
            "device_id": "light_001",
            "device_name": "Living Room Light",
            "device_type": "light",
            "location": "living_room",
            "supported_settings": ["brightness", "color_temp"],
            "settings": {"brightness": 80, "color_temp": 4000}
        }
    ]
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # --- 现有调度（包含一个错误的客厅空调调度作为诱饵） ---
    schedules = [
        {
            "schedule_id": "sch_001",
            "device_id": "ac_001",          # 对应客厅空调
            "time_range": "14:00-17:00",
            "action": "turn_on",
            "temperature": 26,               # 错误温度（应为24）
            "mode": "cool"
        },
        {
            "schedule_id": "sch_002",
            "device_id": "humid_001",
            "time_range": "09:00-11:00",
            "action": "turn_on",
            "humidity_target": 45
        },
        {
            "schedule_id": "sch_003",
            "device_id": "light_001",
            "time_range": "18:00-22:00",
            "action": "turn_on",
            "brightness": 60
        }
    ]
    with open("data/schedules/schedules.json", "w") as f:
        json.dump({"schedules": schedules}, f, indent=2)

    # --- 账户数据（干扰） ---
    accounts = [
        {
            "account_id": "home_001",
            "account_name": "John",
            "location": "home",
            "devices": ["ac_001", "humid_001", "light_001"],
            "schedules": ["sch_001", "sch_002", "sch_003"]
        }
    ]
    with open("data/accounts/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # --- 干扰日志文件 ---
    with open("raw_logs/old_schedule_draft.txt", "w") as f:
        f.write("Legacy draft: AC set to 26°C 14-17, ignore this.\n")
    with open("raw_logs/device_notes.txt", "w") as f:
        f.write("Bedroom AC model: XYZ-200\nLiving Room AC needs recalibration?\n")
    # 额外空目录干扰
    os.makedirs("backup", exist_ok=True)
    with open("backup/empty_placeholder.txt", "w") as f:
        f.write("")

if __name__ == "__main__":
    build_env()
