import os
import json
import random

random.seed(42)

def build_env():
    # Create directory structure
    os.makedirs("data/devices", exist_ok=True)
    os.makedirs("data/schedules", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)

    # ---------- devices ----------
    devices = [
        {
            "device_id": "ac-001",
            "device_name": "Living Room AC",
            "device_type": "ac",
            "location": "living_room",
            "scheduling_disallowed": True,   # <-- critical flag
            "settings": {"mode": "cool", "temp": 24, "fan_speed": "auto"},
            "status": "off"
        },
        {
            "device_id": "light-001",
            "device_name": "Living Room Light",
            "device_type": "light",
            "location": "living_room",
            "scheduling_disallowed": False,
            "settings": {"brightness": 80, "color_temp": 4000},
            "status": "on"
        },
        {
            "device_id": "humid-001",
            "device_name": "Bedroom Humidifier",
            "device_type": "humidifier",
            "location": "bedroom",
            "scheduling_disallowed": False,
            "settings": {"target_humidity": 55, "mode": "auto"},
            "status": "off"
        },
        {
            "device_id": "plug-001",
            "device_name": "Coffee Machine Smart Plug",
            "device_type": "smart_plug",
            "location": "kitchen",
            "scheduling_disallowed": False,
            "settings": {"power_limit": 1500},
            "status": "on"
        }
    ]
    with open("data/devices/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)

    # ---------- schedules ----------
    schedules = [
        {
            "schedule_id": "sch-001",
            "device_id": "light-001",
            "time": "07:00",
            "action": "turn_on",
            "enabled": True,
            "description": "Morning light"
        },
        {
            "schedule_id": "sch-002",
            "device_id": "plug-001",
            "time": "08:00",
            "action": "turn_on",
            "enabled": True,
            "description": "Coffee maker"
        },
        {
            "schedule_id": "sch-003",
            "device_id": "ac-001",          # device with disallowed scheduling
            "time": "16:00",
            "action": "turn_on",
            "enabled": True,                # should be disabled → conflict
            "description": "Alice's AC schedule (should not exist)"
        },
        {
            "schedule_id": "sch-004",
            "device_id": "humid-001",
            "time": "22:00",
            "action": "turn_on",
            "enabled": True,
            "description": "Night humidity"
        },
        {
            "schedule_id": "sch-005",
            "device_id": "nonexistent-device",   # dangling reference – agent should ignore
            "time": "12:00",
            "action": "turn_off",
            "enabled": True,
            "description": "Ghost schedule"
        }
    ]
    with open("data/schedules/schedules.json", "w") as f:
        json.dump({"schedules": schedules}, f, indent=2)

    # ---------- logs (distractor) ----------
    log_lines = [
        "[2025-03-20 15:45] User manual turn-off Living Room AC via app",
        "[2025-03-20 16:00] SCHEDULE turn_on Living Room AC (sch-003) executed",
        "[2025-03-20 16:05] User manual turn-off Living Room AC via app",
        "[2025-03-21 07:00] SCHEDULE turn_on Living Room Light (sch-001) executed",
        "[2025-03-21 08:00] SCHEDULE turn_on Coffee Machine Smart Plug (sch-002) executed",
    ]
    with open("data/logs/activity.log", "w") as f:
        f.write("\n".join(log_lines) + "\n")

if __name__ == "__main__":
    build_env()
