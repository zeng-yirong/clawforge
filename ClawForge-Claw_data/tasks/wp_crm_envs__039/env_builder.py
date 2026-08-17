import os
import json

def build_env():
    # Ensure directories exist
    os.makedirs("data/reminders", exist_ok=True)
    os.makedirs("data/tags", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # current date
    with open("current_date.txt", "w") as f:
        f.write("2025-03-01\n")

    # contacts.json
    contacts = {
        "contacts": [
            {"contact_id": "c001", "first_name": "Alice", "last_name": "Johnson", "full_name": "Alice Johnson", "email": "alice.johnson@techcorp.com", "phone": "+1-555-0101", "company_id": "comp1", "job_title": "CTO", "department": "Engineering", "contact_type": "business", "folder": "business", "tags": ["vip"], "birthday": "1990-02-01"},
            {"contact_id": "c002", "first_name": "Bob", "last_name": "Smith", "full_name": "Bob Smith", "email": "bob.smith@clientco.com", "phone": "+1-555-0102", "company_id": "comp2", "job_title": "Account Manager", "department": "Sales", "contact_type": "business", "folder": "business", "tags": ["partner"], "birthday": "1995-04-10"},
            {"contact_id": "c003", "first_name": "Carol", "last_name": "Williams", "full_name": "Carol Williams", "email": "carol.w@startup.io", "phone": "+1-555-0103", "company_id": "comp3", "job_title": "CEO", "department": "Leadership", "contact_type": "personal", "folder": "personal", "tags": [], "birthday": "1988-07-22"},
            {"contact_id": "c004", "first_name": "David", "last_name": "Brown", "full_name": "David Brown", "email": "david.brown@email.com", "phone": "+1-555-0104", "company_id": "comp4", "job_title": "IT Manager", "department": "IT", "contact_type": "business", "folder": "inactive", "tags": ["old"], "birthday": "1985-01-15"},
            {"contact_id": "c005", "first_name": "Emma", "last_name": "Davis", "full_name": "Emma Davis", "email": "emma.davis@partner.net", "phone": "+1-555-0105", "company_id": "comp5", "job_title": "Partnership Director", "department": "Business Development", "contact_type": "business", "folder": "business", "tags": ["vip"], "birthday": "1992-05-01"},
            {"contact_id": "c006", "first_name": "Frank", "last_name": "Miller", "full_name": "Frank Miller", "email": "frank.m@oldclient.com", "phone": "+1-555-0106", "company_id": "comp6", "job_title": "Procurement Manager", "department": "Operations", "contact_type": "personal", "folder": "inactive", "tags": [], "birthday": "1987-12-03"},
            {"contact_id": "c007", "first_name": "Grace", "last_name": "Wilson", "full_name": "Grace Wilson", "email": "grace.wilson@vendor.co", "phone": "+1-555-0107", "company_id": "comp7", "job_title": "VP Engineering", "department": "Engineering", "contact_type": "business", "folder": "personal", "tags": ["misplaced"], "birthday": "1993-06-01"},
            {"contact_id": "c008", "first_name": "Henry", "last_name": "Taylor", "full_name": "Henry Taylor", "email": "henry.t@bigcorp.com", "phone": "+1-555-0108", "company_id": "comp8", "job_title": "CEO", "department": "Leadership", "contact_type": "personal", "folder": "personal", "tags": [], "birthday": "1991-09-15"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # reminders.json
    reminders = {
        "reminders": [
            {"reminder_id": "r001", "contact_id": "c001", "reminder_type": "birthday", "title": "Alice Johnson's Birthday", "description": "Birthday reminder for Alice Johnson", "reminder_date": "2025-02-01", "days_before": 0, "is_recurring": True, "enabled": True},
            {"reminder_id": "r002", "contact_id": "c002", "reminder_type": "birthday", "title": "Bob Smith's Birthday", "description": "Birthday reminder for Bob Smith", "reminder_date": "2025-04-10", "days_before": 0, "is_recurring": True, "enabled": False},
            {"reminder_id": "r003", "contact_id": "c005", "reminder_type": "birthday", "title": "Emma Davis's Birthday", "description": "Birthday reminder for Emma Davis", "reminder_date": "2025-05-01", "days_before": 0, "is_recurring": True, "enabled": True},
            {"reminder_id": "r004", "contact_id": "c003", "reminder_type": "birthday", "title": "Carol Williams's Birthday", "description": "Birthday reminder for Carol Williams", "reminder_date": "2025-07-22", "days_before": 0, "is_recurring": True, "enabled": True},
            {"reminder_id": "r005", "contact_id": "c001", "reminder_type": "birthday", "title": "Alice Johnson's Birthday", "description": "Birthday reminder for Alice Johnson", "reminder_date": "2025-02-01", "days_before": 0, "is_recurring": True, "enabled": False},
            {"reminder_id": "r006", "contact_id": "c007", "reminder_type": "birthday", "title": "Grace Wilson's Birthday", "description": "Birthday reminder for Grace Wilson", "reminder_date": "2025-06-01", "days_before": 0, "is_recurring": True, "enabled": True}
        ]
    }
    with open("data/reminders/reminders.json", "w") as f:
        json.dump(reminders, f, indent=2)

    # tag_definitions.json
    tags = {
        "tag_definitions": [
            {"tag_id": "t001", "name": "vip", "color": "gold", "description": "Very important person", "category": "priority"},
            {"tag_id": "t002", "name": "partner", "color": "blue", "description": "Business partner", "category": "relationship"},
            {"tag_id": "t003", "name": "old", "color": "gray", "description": "Old client", "category": "status"},
            {"tag_id": "t004", "name": "misplaced", "color": "red", "description": "Contact in wrong folder", "category": "status"},
            {"tag_id": "t005", "name": "inactive-personal", "color": "purple", "description": "Inactive personal contact", "category": "status"},
            {"tag_id": "t006", "name": "birthday-pending", "color": "green", "description": "Needs birthday reminder", "category": "status"}
        ]
    }
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump(tags, f, indent=2)

    # Distractor files
    with open("data/old_contacts_backup.json", "w") as f:
        json.dump({"old_contacts": []}, f, indent=2)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": []}, f, indent=2)
    with open("data/companies.json", "w") as f:
        json.dump({"companies": []}, f, indent=2)
    with open("data/unused_log.csv", "w") as f:
        f.write("timestamp,level,message\n2025-01-01,INFO,irrelevant\n")

if __name__ == "__main__":
    build_env()
