import os, json

def build():
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    devices = [
        {"device_id": "ac_001", "device_name": "Living Room AC", "device_type": "ac", "location": "living_room"},
        {"device_id": "humidifier_001", "device_name": "Bedroom Humidifier", "device_type": "humidifier", "location": "bedroom"},
        {"device_id": "light_001", "device_name": "Bedroom Light", "device_type": "light", "location": "bedroom"},
        {"device_id": "plug_001", "device_name": "Coffee Machine Smart Plug", "device_type": "smart_plug", "location": "kitchen"},
        {"device_id": "tv_plug_001", "device_name": "TV Smart Plug", "device_type": "smart_plug", "location": "living_room"},
    ]
    with open("data/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    schedules = [
        {"schedule_id": "s001", "device_id": "ac_001", "action": "turn_off", "planned_time": "2025-04-04T22:00", "status": "executed"},
        {"schedule_id": "s002", "device_id": "humidifier_001", "action": "turn_on", "planned_time": "2025-04-05T21:00", "status": "pending"},
        {"schedule_id": "s003", "device_id": "light_001", "action": "turn_on", "planned_time": "2025-04-05T23:00", "status": "pending"},
        {"schedule_id": "s004", "device_id": "plug_001", "action": "turn_off", "planned_time": "2025-04-04T20:00", "status": "missed"},
        {"schedule_id": "s005", "device_id": "ac_001", "action": "turn_on", "planned_time": "2025-04-05T18:00", "status": "executed"},
        {"schedule_id": "s006", "device_id": "tv_plug_001", "action": "turn_on", "planned_time": "2025-04-06T08:00", "status": "pending"},
        {"schedule_id": "s007", "device_id": "light_001", "action": "turn_off", "planned_time": "2025-04-05T20:00", "status": "executed"},
    ]
    with open("data/schedules.json", "w") as f:
        json.dump(schedules, f, indent=2)

    # 仅作为参考，agent 也可以不读这个文件
    with open("ops/current_time.txt", "w") as f:
        f.write("2025-04-05T22:00")

    os.makedirs("data/old_logs", exist_ok=True)
    with open("data/old_logs/schedule_history.csv", "w") as f:
        f.write("old_data\n")

if __name__ == "__main__":
    build()
