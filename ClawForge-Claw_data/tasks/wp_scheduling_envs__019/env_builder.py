import os
import json

def build_env():
    # Create required directories
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- devices.json (with dirty data) ---
    devices = {
        "devices": [
            # Normal humidifiers (under 70)
            {
                "device_id": "d_001",
                "device_name": "Bedroom Humidifier",
                "device_type": "humidifier",
                "location": "bedroom",
                "supported_settings": ["power", "humidity"],
                "settings": {"power": "on", "humidity": 60}
            },
            {
                "device_id": "d_004",
                "device_name": "Kitchen Humidifier",
                "device_type": "humidifier",
                "location": "kitchen",
                "supported_settings": ["power", "humidity"],
                "settings": {"power": "off", "humidity": 45}
            },
            # Over-humidity targets (should be selected)
            {
                "device_id": "d_003",
                "device_name": "Master Bedroom Humidifier",
                "device_type": "humidifier",
                "location": "bedroom",
                "supported_settings": ["power", "humidity"],
                "settings": {"power": "on", "humidity": 80}
            },
            {
                "device_id": "d_005",
                "device_name": "Guest Room Humidifier",
                "device_type": "humidifier",
                "location": "bedroom",
                "supported_settings": ["power", "humidity"],
                "settings": {"power": "on", "humidity": 75}
            },
            # Dirty data: missing humidity field
            {
                "device_id": "d_006",
                "device_name": "Garage Humidifier",
                "device_type": "humidifier",
                "location": "garage",
                "supported_settings": ["power", "humidity"],
                "settings": {"power": "on"}
            },
            # Dirty data: humidity is non-numeric string
            {
                "device_id": "d_007",
                "device_name": "Basement Humidifier",
                "device_type": "humidifier",
                "location": "basement",
                "supported_settings": ["power", "humidity"],
                "settings": {"power": "on", "humidity": "high"}
            },
            # Non-humidifier devices (should be ignored)
            {
                "device_id": "d_002",
                "device_name": "Living Room AC",
                "device_type": "ac",
                "location": "living_room",
                "supported_settings": ["power", "temperature"],
                "settings": {"power": "on", "temperature": 24}
            },
            {
                "device_id": "d_008",
                "device_name": "Living Room Light",
                "device_type": "light",
                "location": "living_room",
                "supported_settings": ["brightness"],
                "settings": {"brightness": 80}
            }
        ]
    }
    with open("data/devices/devices.json", "w") as f:
        json.dump(devices, f, indent=2)

    # --- accounts.json (distractor, not needed for the task) ---
    accounts = {
        "accounts": [
            {
                "account_id": "acc_001",
                "account_name": "Smith",
                "location": "main",
                "devices": ["d_001", "d_002"],
                "schedules": []
            },
            {
                "account_id": "acc_002",
                "account_name": "Johnson",
                "location": "annex",
                "devices": ["d_003", "d_004"],
                "schedules": []
            },
            {
                "account_id": "acc_003",
                "account_name": "Williams",
                "location": "guest",
                "devices": ["d_005", "d_006", "d_007", "d_008"],
                "schedules": []
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

if __name__ == "__main__":
    build_env()
