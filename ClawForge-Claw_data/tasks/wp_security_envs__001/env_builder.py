import os
import json

def build_env():
    # 确保目录存在
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 写 accounts.json
    accounts = {
        "accounts": [
            {
                "account_id": "ACC-001",
                "account_name": "Main Office",
                "location": "123 Main St",
                "zones": ["Main Lobby", "Office Room"],
                "emergency_contacts": ["CONTACT-001"]
            },
            {
                "account_id": "ACC-002",
                "account_name": "Garage Facility",
                "location": "456 Garage Ave",
                "zones": ["Garage"],
                "emergency_contacts": ["CONTACT-002", "CONTACT-003"]
            },
            {
                "account_id": "ACC-003",
                "account_name": "Basement Storage",
                "location": "789 Basement Rd",
                "zones": ["Basement"],
                "emergency_contacts": ["CONTACT-004"]
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 写 contacts.json
    contacts = {
        "contacts": [
            {
                "contact_id": "CONTACT-001",
                "name": "John Smith",
                "role": "Security Manager",
                "phone": "+1-555-0101",
                "email": "john.smith@example.com"
            },
            {
                "contact_id": "CONTACT-002",
                "name": "Emergency Services",
                "role": "Monitoring Service",
                "phone": "911",
                "email": "monitoring@securityco.com"
            },
            {
                "contact_id": "CONTACT-003",
                "name": "Local Police Precinct",
                "role": "Police",
                "phone": "+1-555-0199",
                "email": "police.precinct@example.com"
            },
            {
                "contact_id": "CONTACT-004",
                "name": "Security Company",
                "role": "Security Manager",
                "phone": "+1-800-555-0123",
                "email": "john.smith@example.com"
            }
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 写 logs/sensor_events.csv 作为干扰
    csv_content = """timestamp,zone,sensor_id,status
2024-01-15 03:00:00,Garage,SENSOR-01,triggered
2024-01-15 03:01:00,Main Lobby,SENSOR-02,normal
2024-01-15 03:02:00,Basement,SENSOR-03,triggered
"""
    with open("logs/sensor_events.csv", "w") as f:
        f.write(csv_content)

if __name__ == "__main__":
    build_env()
