import json
import os

def build_env():
    # Ensure required directories
    os.makedirs("data/contacts", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- zones.json (with intrusion flags) ---
    zones = {
        "zones": [
            {"zone_id": "zone-001", "zone_name": "Main Lobby", "sensors": ["sensor-a1", "sensor-a2"], "intrusion_detected": True},
            {"zone_id": "zone-002", "zone_name": "Garage", "sensors": ["sensor-b1"], "intrusion_detected": False},
            {"zone_id": "zone-003", "zone_name": "Office Room", "sensors": ["sensor-c1", "sensor-c3"], "intrusion_detected": True},
            {"zone_id": "zone-004", "zone_name": "Basement", "sensors": ["sensor-d1"], "intrusion_detected": True},
            {"zone_id": "zone-005", "zone_name": "Backyard", "sensors": ["sensor-e1"], "intrusion_detected": True}
        ]
    }
    with open("data/zones.json", "w") as f:
        json.dump(zones, f, indent=2)

    # --- accounts.json (zone ownership & emergency contacts) ---
    accounts = {
        "accounts": [
            {
                "account_id": "acc-001",
                "account_name": "Main Office",
                "location": "123 Main St",
                "zones": ["zone-001", "zone-002"],
                "emergency_contacts": ["contact-001", "contact-002"]
            },
            {
                "account_id": "acc-002",
                "account_name": "Branch Office",
                "location": "456 Oak Ave",
                "zones": ["zone-003"],
                "emergency_contacts": ["contact-003"]
            },
            {
                "account_id": "acc-003",
                "account_name": "Storage Facility",
                "location": "789 Elm St",
                "zones": ["zone-004"],
                "emergency_contacts": ["contact-004"]
            },
            {
                "account_id": "acc-004",
                "account_name": "Old Warehouse",
                "location": "321 Pine Rd",
                "zones": ["zone-005"],
                "emergency_contacts": ["contact-002"]   # no police role
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # --- contacts/contacts.json (with police & non-police) ---
    contacts = {
        "contacts": [
            {"contact_id": "contact-001", "name": "Local Police Precinct", "role": "Police", "phone": "+1-555-0101", "email": "police.precinct@example.com"},
            {"contact_id": "contact-002", "name": "John Smith", "role": "Security Manager", "phone": "+1-555-0199", "email": "john.smith@example.com"},
            {"contact_id": "contact-003", "name": "Emergency Services", "role": "Police Non-Emergency", "phone": "911", "email": "monitoring@securityco.com"},
            {"contact_id": "contact-004", "name": "Security Company", "role": "Monitoring Service", "phone": "+1-800-555-0123", "email": "monitoring@securityco.com"}
        ]
    }
    with open("data/contacts/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # --- doors.json (decoy, not used in task) ---
    doors = {
        "doors": [
            {"door_id": "door-001", "door_name": "Front Door", "location": "Main Entrance", "zone_id": "zone-001"},
            {"door_id": "door-002", "door_name": "Garage Door", "location": "Garage", "zone_id": "zone-002"}
        ]
    }
    with open("data/doors.json", "w") as f:
        json.dump(doors, f, indent=2)

    # --- decoy files (distractors) ---
    # stale backup
    os.makedirs("backups", exist_ok=True)
    stale_zones = {"zones": [{"zone_id": "zone-001", "intrusion_detected": False}]}
    with open("backups/zones_old.json", "w") as f:
        json.dump(stale_zones, f, indent=2)

    # empty log
    with open("ops/tmp.log", "w") as f:
        f.write("# temporary file\n")
    # unrelated csv
    with open("data/sensors.csv", "w") as f:
        f.write("sensor_id,status\nsensor-a1,ok\n")

if __name__ == "__main__":
    build_env()
