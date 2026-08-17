import os
import json
import random
import uuid

def build_env():
    # Ensure directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---------- contacts.json ----------
    # Business contacts: 8, some have reminder, some don't
    contacts = [
        {
            "contact_id": "ct_001",
            "first_name": "Alice",
            "last_name": "Johnson",
            "full_name": "Alice Johnson",
            "email": "alice.johnson@techcorp.com",
            "phone": "+1-555-0101",
            "company_id": "comp_1",
            "job_title": "CTO",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "business",
            "tags": ["vip", "tech"]
        },
        {
            "contact_id": "ct_002",
            "first_name": "Bob",
            "last_name": "Smith",
            "full_name": "Bob Smith",
            "email": "bob.smith@clientco.com",
            "phone": "+1-555-0102",
            "company_id": "comp_2",
            "job_title": "Procurement Manager",
            "department": "Operations",
            "contact_type": "business",
            "folder": "business",
            "tags": ["procurement", "clientco"]
        },
        {
            "contact_id": "ct_003",
            "first_name": "Carol",
            "last_name": "Williams",
            "full_name": "Carol Williams",
            "email": "carol.w@startup.io",
            "phone": "+1-555-0103",
            "company_id": "comp_3",
            "job_title": "CEO",
            "department": "Leadership",
            "contact_type": "business",
            "folder": "business",
            "tags": ["startup", "vip"]
        },
        {
            "contact_id": "ct_004",
            "first_name": "David",
            "last_name": "Brown",
            "full_name": "David Brown",
            "email": "david.brown@email.com",
            "phone": "+1-555-0104",
            "company_id": "comp_4",
            "job_title": "IT Manager",
            "department": "IT",
            "contact_type": "business",
            "folder": "inactive",   # inactive, not business -> should be ignored
            "tags": ["legacy"]
        },
        {
            "contact_id": "ct_005",
            "first_name": "Emma",
            "last_name": "Davis",
            "full_name": "Emma Davis",
            "email": "emma.davis@partner.net",
            "phone": "+1-555-0105",
            "company_id": "comp_5",
            "job_title": "Partnership Director",
            "department": "Business Development",
            "contact_type": "business",
            "folder": "business",
            "tags": ["partnership", "vip"]
        },
        {
            "contact_id": "ct_006",
            "first_name": "Frank",
            "last_name": "Miller",
            "full_name": "Frank Miller",
            "email": "frank.m@oldclient.com",
            "phone": "+1-555-0106",
            "company_id": "comp_6",
            "job_title": "Account Manager",
            "department": "Sales",
            "contact_type": "business",
            "folder": "business",
            "tags": ["sales", "oldclient"]
        },
        {
            "contact_id": "ct_007",
            "first_name": "Grace",
            "last_name": "Wilson",
            "full_name": "Grace Wilson",
            "email": "grace.wilson@vendor.co",
            "phone": "+1-555-0107",
            "company_id": "comp_7",
            "job_title": "VP Engineering",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "personal",   # personal, not business
            "tags": ["engineering"]
        },
        {
            "contact_id": "ct_008",
            "first_name": "Henry",
            "last_name": "Taylor",
            "full_name": "Henry Taylor",
            "email": "henry.t@bigcorp.com",
            "phone": "+1-555-0108",
            "company_id": "comp_8",
            "job_title": "CEO",
            "department": "Leadership",
            "contact_type": "personal",
            "folder": "personal",
            "tags": ["ceo", "bigcorp"]
        },
        # extra personal contact to confuse
        {
            "contact_id": "ct_009",
            "first_name": "Ivy",
            "last_name": "Clark",
            "full_name": "Ivy Clark",
            "email": "ivy.clark@personal.com",
            "phone": "+1-555-0109",
            "company_id": None,
            "job_title": "Freelancer",
            "department": "Independent",
            "contact_type": "personal",
            "folder": "personal",
            "tags": []
        }
    ]

    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ---------- reminders.json ----------
    # Reminders for ct_001, ct_003, ct_005 (business contacts with reminders)
    # ct_002, ct_006 are missing reminders => they should be in output
    # ct_004 inactive, ct_007 personal, ct_008 personal, ct_009 personal -> not business, ignore
    reminders = [
        {
            "reminder_id": "rem_001",
            "contact_id": "ct_001",
            "reminder_type": "birthday",
            "title": "Alice Johnson's Birthday",
            "description": "Birthday reminder for Alice Johnson",
            "reminder_date": "2027-06-15",
            "days_before": 3,
            "is_recurring": True,
            "enabled": True
        },
        {
            "reminder_id": "rem_003",
            "contact_id": "ct_003",
            "reminder_type": "birthday",
            "title": "Carol Williams's Birthday",
            "description": "Birthday reminder for Carol Williams",
            "reminder_date": "2027-08-20",
            "days_before": 3,
            "is_recurring": True,
            "enabled": True
        },
        {
            "reminder_id": "rem_005",
            "contact_id": "ct_005",
            "reminder_type": "birthday",
            "title": "Emma Davis's Birthday",
            "description": "Birthday reminder for Emma Davis",
            "reminder_date": "2027-04-10",
            "days_before": 3,
            "is_recurring": True,
            "enabled": True
        },
        # extra reminder for a non-existent contact (orphaned data)
        {
            "reminder_id": "rem_orphan",
            "contact_id": "ct_099",
            "reminder_type": "birthday",
            "title": "Unknown's Birthday",
            "description": "Orphan reminder",
            "reminder_date": "2027-01-01",
            "days_before": 3,
            "is_recurring": False,
            "enabled": False
        }
    ]

    os.makedirs("data/reminders", exist_ok=True)
    with open("data/reminders/reminders.json", "w") as f:
        json.dump({"reminders": reminders}, f, indent=2)

    # ---------- decoy files to add noise ----------
    # old dump to confuse
    old_contacts = [
        {"contact_id": "ct_old1", "full_name": "Old Contact", "folder": "business"}
    ]
    with open("data/old_contacts.json", "w") as f:
        json.dump({"contacts": old_contacts}, f, indent=2)

    # dummy csv file
    with open("data/import_batch.csv", "w") as f:
        f.write("id,name,type\n1,Fake,business\n2,Dummy,personal\n")

    # empty tag definitions (just to simulate system)
    os.makedirs("data/tags", exist_ok=True)
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump({"tag_definitions": []}, f, indent=2)

    # placeholder for agent output (not created yet)
    # ensure ops directory exists
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
