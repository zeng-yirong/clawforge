import os
import json
import random
import string

def build_env():
    # Ensure required directories exist
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("reminders", exist_ok=True)
    # ops directory will be created by agent, not needed now

    # ---------- contacts ----------
    contacts = [
        {
            "contact_id": "ct_001",
            "first_name": "Alice",
            "last_name": "Johnson",
            "full_name": "Alice Johnson",
            "email": "alice.johnson@techcorp.com",
            "phone": "+1-555-0101",
            "birthday": "1990-03-05",
            "company_id": "comp_001",
            "job_title": "Account Manager",
            "department": "Sales",
            "contact_type": "business",
            "folder": "business",
            "tags": ["vip"]
        },
        {
            "contact_id": "ct_002",
            "first_name": "Bob",
            "last_name": "Smith",
            "full_name": "Bob Smith",
            "email": "bob.smith@clientco.com",
            "phone": "+1-555-0102",
            "birthday": "1988-02-10",
            "company_id": "comp_002",
            "job_title": "Procurement Manager",
            "department": "Operations",
            "contact_type": "business",
            "folder": "business",
            "tags": []
        },
        {
            "contact_id": "ct_003",
            "first_name": "Carol",
            "last_name": "Williams",
            "full_name": "Carol Williams",
            "email": "carol.w@startup.io",
            "phone": "+1-555-0103",
            "birthday": "1985-03-15",
            "company_id": "comp_003",
            "job_title": "CTO",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "business",
            "tags": ["priority"]
        },
        {
            "contact_id": "ct_004",
            "first_name": "David",
            "last_name": "Brown",
            "full_name": "David Brown",
            "email": "david.brown@email.com",
            "phone": "+1-555-0104",
            "birthday": "1991-04-20",
            "company_id": "comp_004",
            "job_title": "IT Manager",
            "department": "IT",
            "contact_type": "business",
            "folder": "inactive",
            "tags": []
        },
        {
            "contact_id": "ct_005",
            "first_name": "Emma",
            "last_name": "Davis",
            "full_name": "Emma Davis",
            "email": "emma.davis@partner.net",
            "phone": "+1-555-0105",
            "birthday": "1992-03-25",
            "company_id": "comp_005",
            "job_title": "Partnership Director",
            "department": "Business Development",
            "contact_type": "business",
            "folder": "business",
            "tags": ["vip"]
        },
        {
            "contact_id": "ct_006",
            "first_name": "Frank",
            "last_name": "Miller",
            "full_name": "Frank Miller",
            "email": "frank.m@oldclient.com",
            "phone": "+1-555-0106",
            "birthday": "1987-01-15",
            "company_id": "comp_006",
            "job_title": "CEO",
            "department": "Leadership",
            "contact_type": "business",
            "folder": "business",
            "tags": []
        },
        {
            "contact_id": "ct_007",
            "first_name": "Grace",
            "last_name": "Wilson",
            "full_name": "Grace Wilson",
            "email": "grace.wilson@vendor.co",
            "phone": "+1-555-0107",
            "birthday": "1993-05-05",
            "company_id": "comp_007",
            "job_title": "VP Engineering",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "business",
            "tags": []
        },
        {
            "contact_id": "ct_008",
            "first_name": "Henry",
            "last_name": "Taylor",
            "full_name": "Henry Taylor",
            "email": "henry.t@bigcorp.com",
            "phone": "+1-555-0108",
            "birthday": "1989-06-12",
            "company_id": "comp_008",
            "job_title": "Account Manager",
            "department": "Sales",
            "contact_type": "business",
            "folder": "personal",
            "tags": []
        }
    ]

    with open("raw_data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ---------- reminders ----------
    reminders = [
        {
            "reminder_id": "rm_001",
            "contact_id": "ct_001",
            "reminder_type": "birthday",
            "title": "Alice Johnson's Birthday",
            "description": "Birthday reminder for Alice Johnson",
            "reminder_date": "1990-03-05",
            "days_before": 0,
            "is_recurring": True,
            "enabled": True
        },
        {
            "reminder_id": "rm_002",
            "contact_id": "ct_003",
            "reminder_type": "birthday",
            "title": "Carol Williams's Birthday",
            "description": "Birthday reminder for Carol Williams",
            "reminder_date": "1985-03-15",
            "days_before": 0,
            "is_recurring": True,
            "enabled": False
        },
        {
            "reminder_id": "rm_003",
            "contact_id": "ct_002",
            "reminder_type": "birthday",
            "title": "Bob Smith's Birthday",
            "description": "Birthday reminder for Bob Smith",
            "reminder_date": "1988-02-10",
            "days_before": 0,
            "is_recurring": True,
            "enabled": True
        },
        {
            "reminder_id": "rm_004",
            "contact_id": "ct_004",
            "reminder_type": "birthday",
            "title": "David Brown's Birthday",
            "description": "Birthday reminder for David Brown",
            "reminder_date": "1991-04-20",
            "days_before": 0,
            "is_recurring": True,
            "enabled": False
        }
    ]

    with open("reminders/reminders.json", "w") as f:
        json.dump({"reminders": reminders}, f, indent=2)

    # ---------- interference files (optional) ----------
    # Create a stray CSV to confuse agents
    with open("raw_data/old_export.csv", "w") as f:
        f.write("contact_id,name,birthday\n")
        f.write("ct_001,Alice Johnson,1990-03-05\n")
        f.write("ct_003,Carol Williams,1985-03-15\n")

    # Create a couple of irrelevant tag definition files
    os.makedirs("tags", exist_ok=True)
    with open("tags/tag_definitions.json", "w") as f:
        json.dump({
            "tag_definitions": [
                {"tag_id": "tg_001", "name": "vip", "color": "#FFD700", "category": "priority"},
                {"tag_id": "tg_002", "name": "priority", "color": "#FF4500", "category": "priority"}
            ]
        }, f, indent=2)

if __name__ == "__main__":
    build_env()
