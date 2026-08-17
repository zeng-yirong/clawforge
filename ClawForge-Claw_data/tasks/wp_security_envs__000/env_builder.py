import json
import os
import shutil

def build_env():
    # 清理可能存在的旧数据
    if os.path.exists("data"):
        shutil.rmtree("data")
    if os.path.exists("ops"):
        shutil.rmtree("ops")

    # ---------- 构建 zones ----------
    zones = [
        {"zone_id": "zone_01", "zone_name": "Backyard", "sensors": ["sensor_a1", "sensor_a2"], "intrusion_detected": False},
        {"zone_id": "zone_02", "zone_name": "Basement", "sensors": ["sensor_b1"], "intrusion_detected": False},
        {"zone_id": "zone_03", "zone_name": "Garage", "sensors": ["sensor_c1", "sensor_c3"], "intrusion_detected": False},
        {"zone_id": "zone_04", "zone_name": "Main Lobby", "sensors": ["sensor_d1", "sensor_d2", "sensor_d3"], "intrusion_detected": True},
        {"zone_id": "zone_05", "zone_name": "Office Room", "sensors": ["sensor_e1"], "intrusion_detected": False},
    ]
    os.makedirs("data/zones", exist_ok=True)
    with open("data/zones/zones.json", "w") as f:
        json.dump({"zones": zones}, f, indent=2)

    # 干扰项：旧版备份（intrusion_detected 为 False 且 zone_name 不同）
    old_zones = [
        {"zone_id": "zone_04", "zone_name": "Main Lobby", "sensors": ["sensor_d1"], "intrusion_detected": False},
        {"zone_id": "zone_06", "zone_name": "Roof", "sensors": ["sensor_f1"], "intrusion_detected": True},
    ]
    os.makedirs("data/backup", exist_ok=True)
    with open("data/backup/zones_old.json", "w") as f:
        json.dump({"zones": old_zones}, f, indent=2)

    # ---------- 构建 doors ----------
    doors = [
        {"door_id": "door_01", "door_name": "Back Door", "location": "Rear Entrance", "zone_id": "zone_01"},
        {"door_id": "door_02", "door_name": "Basement Door", "location": "Basement", "zone_id": "zone_02"},
        {"door_id": "door_03", "door_name": "Garage Door", "location": "Garage", "zone_id": "zone_03"},
        {"door_id": "door_04", "door_name": "Front Door", "location": "Main Entrance", "zone_id": "zone_04"},
        {"door_id": "door_05", "door_name": "Office Door", "location": "Office Room", "zone_id": "zone_05"},
        # 干扰项：属于 zone_04 但已经废弃的门
        {"door_id": "door_06", "door_name": "Service Entrance", "location": "Side Entrance", "zone_id": "zone_04", "status": "decommissioned"},
    ]
    os.makedirs("data/doors", exist_ok=True)
    with open("data/doors/doors.json", "w") as f:
        json.dump({"doors": doors}, f, indent=2)

    # ---------- 构建 accounts ----------
    accounts = [
        {
            "account_id": "acc_001",
            "account_name": "Headquarters Building",
            "location": "Downtown",
            "zones": ["zone_01", "zone_02", "zone_03", "zone_04", "zone_05"],
            "emergency_contacts": ["contact_02", "contact_04"]
        },
        {
            "account_id": "acc_002",
            "account_name": "Warehouse Annex",
            "location": "Industrial Park",
            "zones": ["zone_06", "zone_07"],
            "emergency_contacts": ["contact_01"]
        },
    ]
    os.makedirs("data/accounts", exist_ok=True)
    with open("data/accounts/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # ---------- 构建 contacts ----------
    contacts = [
        {"contact_id": "contact_01", "name": "Emergency Services", "role": "Monitoring Service", "phone": "+1-555-0101", "email": "monitoring@securityco.com"},
        {"contact_id": "contact_02", "name": "John Smith", "role": "Security Manager", "phone": "+1-555-0199", "email": "john.smith@example.com"},
        {"contact_id": "contact_03", "name": "Local Police Precinct", "role": "Police", "phone": "+1-800-555-0123", "email": "police.precinct@example.com"},
        {"contact_id": "contact_04", "name": "Security Company", "role": "Police Non-Emergency", "phone": "911", "email": "N/A"},
        # 干扰项：重复的联系人（废弃）
        {"contact_id": "contact_02", "name": "John Smith Old", "role": "Security Manager", "phone": "+1-555-0000", "email": "john.old@example.com"},
    ]
    os.makedirs("data/contacts", exist_ok=True)
    with open("data/contacts/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 确保 ops 目录存在（初始为空）
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
