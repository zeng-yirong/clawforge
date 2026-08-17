import os
import json

def build_env():
    # Ensure necessary directories
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # empty ops dir, agent will write file later

    # --- Devices ---
    devices = [
        {
            "device_id": "light-001",
            "device_name": "Living Room Light",
            "device_type": "light",
            "location": "living_room",
            "supported_settings": ["power"],
            "settings": {"power": "off"}
        },
        {
            "device_id": "ac-001",
            "device_name": "Living Room AC",
            "device_type": "ac",
            "location": "living_room",
            "supported_settings": ["power", "temperature"],
            "settings": {"power": "off", "temperature": 22}
        },
        {
            "device_id": "humidifier-001",
            "device_name": "Bedroom Humidifier",
            "device_type": "humidifier",
            "location": "bedroom",
            "supported_settings": ["power", "humidity"],
            "settings": {"power": "off", "humidity": 50}
        },
        {
            "device_id": "plug-001",
            "device_name": "Coffee Machine Smart Plug",
            "device_type": "smart_plug",
            "location": "kitchen",
            "supported_settings": ["power"],
            "settings": {"power": "off"}
        }
    ]
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # --- Schedules ---
    schedules = [
        {
            "schedule_id": "sch-001",
            "device_id": "light-001",
            "time": "07:00",
            "action": "turn_on",
            "enabled": True
        },
        {
            "schedule_id": "sch-002",
            "device_id": "ac-001",
            "time": "18:00",
            "action": "turn_on",
            "settings_override": {"temperature": 22},
            "enabled": True
        },
        {
            # this one uses a device_id that does NOT exist in devices.json
            "schedule_id": "sch-003",
            "device_id": "nonexistent-999",
            "time": "07:00",
            "action": "turn_on",
            "enabled": True
        },
        {
            "schedule_id": "sch-004",
            "device_id": "humidifier-001",
            "time": "22:00",
            "action": "turn_on",
            "settings_override": {"humidity": 60},
            "enabled": True
        }
    ]
    with open("data/schedules.json", "w") as f:
        json.dump({"schedules": schedules}, f, indent=2)

    # --- Optional distraction: accounts.json (ignored by prompt) ---
    accounts = [
        {
            "account_id": "acc-001",
            "account_name": "Alice",
            "location": "Home",
            "devices": ["light-001", "ac-001", "plug-001", "humidifier-001"],
            "schedules": ["sch-001", "sch-002", "sch-003", "sch-004"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # --- An unrelated log file to add noise ---
    os.makedirs("logs", exist_ok=True)
    with open("logs/session_2025.log", "w") as f:
        f.write("[INFO] Session started\n[INFO] Device scheduled events loaded\n[WARN] Schedule sch-003 references unknown device\n")

if __name__ == "__main__":
    build_env()
