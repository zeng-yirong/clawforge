import os
import json
import random

def build_env():
    # Ensure base directories exist
    os.makedirs("data/schedules", exist_ok=True)
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/backup", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- Accounts ---
    accounts = [
        {
            "account_id": "acc_001",
            "account_name": "John Doe",
            "location": "New York",
            "devices": ["dev_light_1", "dev_ac_1", "dev_plug_1"],
            "schedules": ["sch_001", "sch_002", "sch_003"]
        },
        {
            "account_id": "acc_002",
            "account_name": "Jane Smith",
            "location": "Los Angeles",
            "devices": ["dev_ac_2", "dev_humid_1"],
            "schedules": ["sch_004", "sch_005"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # --- Devices ---
    devices = [
        {
            "device_id": "dev_light_1",
            "device_name": "Living Room Light",
            "device_type": "light",
            "location": "living_room",
            "supported_settings": ["brightness", "color"],
            "settings": {"brightness": 80, "color": "warm"}
        },
        {
            "device_id": "dev_ac_1",
            "device_name": "Living Room AC",
            "device_type": "ac",
            "location": "living_room",
            "supported_settings": ["target_temperature", "mode"],
            "settings": {"target_temperature": 22, "mode": "cool"}
        },
        {
            "device_id": "dev_plug_1",
            "device_name": "Coffee Machine Smart Plug",
            "device_type": "smart_plug",
            "location": "kitchen",
            "supported_settings": ["power"],
            "settings": {"power": "off"}
        },
        {
            "device_id": "dev_ac_2",
            "device_name": "Bedroom AC",
            "device_type": "ac",
            "location": "bedroom",
            "supported_settings": ["target_temperature", "mode"],
            "settings": {"target_temperature": 25, "mode": "cool"}
        },
        {
            "device_id": "dev_humid_1",
            "device_name": "Bedroom Humidifier",
            "device_type": "humidifier",
            "location": "bedroom",
            "supported_settings": ["humidity"],
            "settings": {"humidity": 50}
        }
    ]
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # --- Schedules (unique correct answer: sch_003 has target_temperature=18) ---
    schedules = [
        {
            "schedule_id": "sch_001",
            "account_id": "acc_001",
            "device_id": "dev_light_1",
            "start_time": "06:00",
            "end_time": "07:00",
            "repeat": "daily",
            "action": "turn_on",
            "settings": {"brightness": 60}
        },
        {
            "schedule_id": "sch_002",
            "account_id": "acc_001",
            "device_id": "dev_ac_1",
            "start_time": "06:00",
            "end_time": "18:00",
            "repeat": "weekdays",
            "target_temperature": 24,
            "mode": "cool"
        },
        {
            "schedule_id": "sch_003",   # <-- the erroneous one
            "account_id": "acc_001",
            "device_id": "dev_ac_1",
            "start_time": "20:00",
            "end_time": "22:00",
            "repeat": "weekdays",
            "target_temperature": 18,   # too low, should be 24
            "mode": "cool"
        },
        {
            "schedule_id": "sch_004",
            "account_id": "acc_002",
            "device_id": "dev_ac_2",
            "start_time": "21:00",
            "end_time": "23:00",
            "repeat": "daily",
            "target_temperature": 24,
            "mode": "cool"
        },
        {
            "schedule_id": "sch_005",
            "account_id": "acc_002",
            "device_id": "dev_humid_1",
            "start_time": "20:00",
            "end_time": "22:00",
            "repeat": "daily",
            "target_humidity": 45
        }
    ]
    for sch in schedules:
        fname = f"data/schedules/{sch['schedule_id']}.json"
        with open(fname, "w") as f:
            json.dump(sch, f, indent=2)

    # --- Distractors: old backup of schedules (outdated) ---
    old_schedules = [
        {
            "schedule_id": "sch_001",
            "account_id": "acc_001",
            "device_id": "dev_light_1",
            "start_time": "06:00",
            "end_time": "08:00",  # different
            "repeat": "daily",
            "action": "turn_on"
        },
        {
            "schedule_id": "sch_003",
            "account_id": "acc_001",
            "device_id": "dev_ac_1",
            "start_time": "20:00",
            "end_time": "22:00",
            "repeat": "weekdays",
            "target_temperature": 22,  # old value, not the real one
            "mode": "cool"
        }
    ]
    with open("data/backup/schedules_backup.json", "w") as f:
        json.dump({"schedules": old_schedules}, f, indent=2)

    # --- Distractor: log file (irrelevant) ---
    log_lines = [
        "2025-03-20 20:01:23 INFO AC turned on to 18°C",
        "2025-03-20 20:15:47 WARN Power usage spike detected",
        "2025-03-20 22:00:12 INFO AC turned off"
    ]
    with open("data/logs/activity.log", "w") as f:
        f.write("\n".join(log_lines))

    # --- Distractor: empty leftover file ---
    with open("data/README.txt", "w") as f:
        f.write("This directory contains account and device data.\n")

if __name__ == "__main__":
    build_env()
