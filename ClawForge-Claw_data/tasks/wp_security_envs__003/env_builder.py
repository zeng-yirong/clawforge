import os
import json
import shutil

def build_env():
    # 确保工作区干净
    if os.path.exists("data"):
        shutil.rmtree("data")
    if os.path.exists("ops"):
        shutil.rmtree("ops")

    # 创建目录
    os.makedirs("data/zones")
    os.makedirs("data/accounts")
    os.makedirs("data/contacts")
    os.makedirs("ops")  # 空目录，留给 agent 产出

    # ===== zones =====
    zones = [
        {
            "zone_id": "zone-001",
            "zone_name": "Backyard",
            "sensors": ["sensor-a1"],
            "intrusion_detected": True
        },
        {
            "zone_id": "zone-002",
            "zone_name": "Basement",
            "sensors": ["sensor-b2"],
            "intrusion_detected": True
        },
        {
            "zone_id": "zone-003",
            "zone_name": "Garage",
            "sensors": ["sensor-c3"],
            "intrusion_detected": False
        }
    ]
    with open("data/zones/zones.json", "w") as f:
        json.dump(zones, f, indent=2)

    # ===== accounts =====
    accounts = [
        {
            "account_id": "acc-100",
            "account_name": "Main Office",
            "location": "Building A",
            "zones": ["zone-001", "zone-003"],
            "emergency_contacts": ["contact-001", "contact-002"],
            "active": True
        },
        {
            "account_id": "acc-200",
            "account_name": "Warehouse",
            "location": "Building B",
            "zones": ["zone-002"],
            "emergency_contacts": ["contact-003"],
            "active": False
        },
        {
            "account_id": "acc-300",
            "account_name": "Lab",
            "location": "Building C",
            "zones": [],
            "emergency_contacts": ["contact-001"],
            "active": True
        }
    ]
    with open("data/accounts/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ===== contacts =====
    contacts = [
        {
            "contact_id": "contact-001",
            "name": "Emergency Services",
            "role": "Police",
            "phone": "911",
            "email": "dispatch@example.com"
        },
        {
            "contact_id": "contact-002",
            "name": "John Smith",
            "role": "Security Manager",
            "phone": "+1-555-0101",
            "email": "john.smith@example.com"
        },
        {
            "contact_id": "contact-003",
            "name": "Local Police Precinct",
            "role": "Police Non-Emergency",
            "phone": "+1-800-555-0123",
            "email": "police.precinct@example.com"
        }
    ]
    with open("data/contacts/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ===== 干扰项（无关文件） =====
    os.makedirs("data/doors")
    doors = [
        {"door_id": "door-001", "door_name": "Front Door", "location": "Main Entrance", "zone_id": "zone-001"},
        {"door_id": "door-002", "door_name": "Back Door", "location": "Rear Entrance", "zone_id": "zone-002"}
    ]
    with open("data/doors/doors.json", "w") as f:
        json.dump(doors, f, indent=2)

    # 添加一个无用的日志目录
    os.makedirs("logs")
    with open("logs/history.txt", "w") as f:
        f.write("Old logs – not relevant.\n")

if __name__ == "__main__":
    build_env()
