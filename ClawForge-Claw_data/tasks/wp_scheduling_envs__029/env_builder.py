import os
import json

def build_env():
    # data directory
    os.makedirs("data", exist_ok=True)
    # accounts.json
    accounts = {
        "accounts": [
            {
                "account_id": "acc_001",
                "account_name": "Home",
                "location": "bedroom",
                "devices": ["dev_hum_01", "dev_light_02"],
                "schedules": ["sch_001", "sch_002", "sch_003"]
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # devices.json
    devices = {
        "devices": [
            {"device_id": "dev_hum_01", "device_name": "Bedroom Humidifier", "device_type": "humidifier", "location": "bedroom", "supported_settings": ["power", "humidity"], "settings": {"power": "off", "humidity": 50}},
            {"device_id": "dev_light_02", "device_name": "Bedroom Light", "device_type": "light", "location": "bedroom", "supported_settings": ["brightness", "color"], "settings": {"brightness": 80, "color": "warm"}},
            {"device_id": "dev_ac_03", "device_name": "Living Room AC", "device_type": "ac", "location": "living_room", "supported_settings": ["temperature", "mode"], "settings": {"temperature": 24, "mode": "cool"}}
        ]
    }
    with open("data/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # schedules directory and schedules.json
    os.makedirs("schedules", exist_ok=True)
    schedules = {
        "schedules": [
            {
                "schedule_id": "sch_001",
                "account_id": "acc_001",
                "device_id": "dev_hum_01",
                "time": "22:00",
                "action": "turn_on",
                "created_at": "2024-01-01T10:00:00Z"
            },
            {
                "schedule_id": "sch_002",
                "account_id": "acc_001",
                "device_id": "dev_light_02",
                "time": "06:00",
                "action": "turn_on",
                "created_at": "2024-01-02T08:00:00Z"
            },
            {
                "schedule_id": "sch_003",
                "account_id": "acc_001",
                "device_id": "dev_hum_01",
                "time": "22:00",
                "action": "turn_on",
                "created_at": "2024-01-03T12:00:00Z"
            }
        ]
    }
    with open("schedules/schedules.json", "w") as f:
        json.dump(schedules, f, indent=2)

    # ops directory (empty initially)
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
