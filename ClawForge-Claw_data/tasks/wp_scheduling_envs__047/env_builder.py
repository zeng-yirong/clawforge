import os
import json
import csv
import random

def build_env():
    # Accounts
    accounts = [
        {
            "account_id": "home001",
            "account_name": "Main House",
            "location": "house",
            "devices": [
                {"device_id": "hum_bed_01", "room": "bedroom"},
                {"device_id": "ac_bed_01", "room": "bedroom"},
                {"device_id": "light_bed_01", "room": "bedroom"},
                {"device_id": "ac_lr_01", "room": "living_room"}
            ],
            "schedules": [
                {
                    "schedule_id": "s1",
                    "device_id": "hum_bed_01",
                    "start_time": "22:00",
                    "end_time": "22:30",
                    "days": ["mon","tue","wed","thu","fri"]
                },
                {
                    "schedule_id": "s2",
                    "device_id": "ac_bed_01",
                    "start_time": "22:00",
                    "end_time": "23:00",
                    "days": ["mon","tue","wed","thu","fri"],
                    "mode": "dehumidify"
                },
                {
                    "schedule_id": "s3",
                    "device_id": "light_bed_01",
                    "start_time": "20:00",
                    "end_time": "22:30",
                    "days": ["mon","tue","wed","thu","fri"]
                },
                {
                    "schedule_id": "s4",
                    "device_id": "ac_lr_01",
                    "start_time": "21:00",
                    "end_time": "23:00",
                    "days": ["mon","tue","wed","thu","fri"],
                    "mode": "cool"
                }
            ],
            "timezone": "America/New_York"
        }
    ]

    # Devices catalog
    devices = [
        {"device_id": "hum_bed_01", "device_name": "Bedroom Humidifier", "device_type": "humidifier", "location": "bedroom", "supported_settings": ["speed","target_humidity"], "settings": {"speed": "medium", "target_humidity": 50}},
        {"device_id": "ac_bed_01", "device_name": "Bedroom AC", "device_type": "ac", "location": "bedroom", "supported_settings": ["mode","temperature","fan_speed"], "settings": {"mode": "auto", "temperature": 72, "fan_speed": "low"}},
        {"device_id": "light_bed_01", "device_name": "Bedroom Light", "device_type": "light", "location": "bedroom", "supported_settings": ["brightness","color"], "settings": {"brightness": 80, "color": "warm_white"}},
        {"device_id": "ac_lr_01", "device_name": "Living Room AC", "device_type": "ac", "location": "living_room", "supported_settings": ["mode","temperature","fan_speed"], "settings": {"mode": "cool", "temperature": 70, "fan_speed": "auto"}}
    ]

    # Event log (tricky data: some old correct runs, but last night the humidifier didn't run)
    events = [
        {"timestamp": "2025-02-10 22:00:00", "device_id": "ac_bed_01", "event": "start", "mode": "dehumidify"},
        {"timestamp": "2025-02-10 22:00:00", "device_id": "hum_bed_01", "event": "skipped", "reason": "conflict"},
        {"timestamp": "2025-02-09 21:30:00", "device_id": "hum_bed_01", "event": "start"},
        {"timestamp": "2025-02-09 22:00:00", "device_id": "hum_bed_01", "event": "stop"},
        {"timestamp": "2025-02-09 22:00:00", "device_id": "ac_bed_01", "event": "start", "mode": "dehumidify"},
        {"timestamp": "2025-02-08 22:00:00", "device_id": "ac_bed_01", "event": "start", "mode": "dehumidify"},
        {"timestamp": "2025-02-08 22:00:00", "device_id": "hum_bed_01", "event": "start"},
        {"timestamp": "2025-02-08 22:30:00", "device_id": "hum_bed_01", "event": "stop"},
        {"timestamp": "2025-02-08 22:00:00", "device_id": "light_bed_01", "event": "start"},
        {"timestamp": "2025-02-08 22:30:00", "device_id": "light_bed_01", "event": "stop"},
    ]

    # Create directory structure
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    with open("logs/events.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp","device_id","event","mode","reason"])
        writer.writeheader()
        for e in events:
            # Only write non-None keys
            row = {k: e.get(k,"") for k in writer.fieldnames}
            writer.writerow(row)

if __name__ == "__main__":
    build_env()
