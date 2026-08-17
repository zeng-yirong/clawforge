import os
import json

def build_env():
    # Create required directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    # Extra dir as distractor
    os.makedirs("backups", exist_ok=True)

    # Device data
    devices = {
        "devices": [
            {"device_id": "ac_001", "device_name": "Living Room AC", "device_type": "ac", "location": "living_room", "settings": {"mode": "cool", "temp": 24}},
            {"device_id": "light_001", "device_name": "Living Room Light", "device_type": "light", "location": "living_room", "settings": {}},
            {"device_id": "humidifier_001", "device_name": "Bedroom Humidifier", "device_type": "humidifier", "location": "bedroom", "settings": {"humidity": 50}}
        ]
    }
    with open("data/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # Schedule data with one genuine conflict (sched_001 turns on, sched_002 turns off overlapping)
    # Plus distractors: missing field, non‑existent device, harmless schedule
    schedules = {
        "schedules": [
            {"schedule_id": "sched_001", "device_id": "ac_001", "action": "turn_on", "start_time": "14:00", "end_time": "15:00", "days": ["mon","tue","wed","thu","fri"]},
            {"schedule_id": "sched_002", "device_id": "ac_001", "action": "turn_off", "start_time": "14:30", "end_time": "15:00", "days": ["mon","tue","wed","thu","fri"]},
            {"schedule_id": "sched_003", "device_id": "light_001", "action": "turn_on", "start_time": "18:00", "end_time": "22:00", "days": ["mon","tue","wed","thu","fri"]},
            {"schedule_id": "sched_004", "device_id": "nonexistent_device", "action": "turn_on", "start_time": "14:00", "end_time": "15:00", "days": ["mon","tue","wed","thu","fri"]},
            # Missing start_time → malformed entry (distractor)
            {"schedule_id": "sched_005", "device_id": "ac_001", "action": "turn_off", "end_time": "16:00", "days": ["mon","tue","wed","thu","fri"]},
            # Harmless schedule for another device
            {"schedule_id": "sched_006", "device_id": "humidifier_001", "action": "turn_on", "start_time": "15:00", "end_time": "16:00", "days": ["mon","tue","wed","thu","fri"]}
        ]
    }
    with open("data/schedules.json", "w") as f:
        json.dump(schedules, f, indent=2)

    # Distractor backup file
    with open("backups/schedules_backup_20240101.json", "w") as f:
        json.dump({"note": "old backup"}, f, indent=2)

    # User log (unrelated)
    with open("user_log.txt", "w") as f:
        f.write("2024-02-15 14:05: Living Room AC turned on but turned off at 14:35.\n")
        f.write("2024-02-16 14:02: Same issue happened.\n")

if __name__ == "__main__":
    build_env()
