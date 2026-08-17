import os
import json
import random

def build_env():
    # ---------- Accounts ----------
    accounts = [
        {"account_id": "acc_001", "display_name": "Main Account", "email": "admin@example.com",
         "default_tag_color": "#3366CC", "auto_tagging_enabled": True,
         "birthday_reminders_enabled": True, "reminder_days_before": 1,
         "available_folders": ["business", "personal", "archive", "inactive"]}
    ]
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # ---------- Companies ----------
    companies = [
        {"company_id": "c001", "name": "TechCorp Industries", "industry": "Technology", "size": "enterprise",
         "website": "https://techcorp.com", "address": "123 Tech Lane", "phone": "+1-555-1000",
         "tags": ["client"], "annual_revenue": "100M+", "customer_since": "2020-01-15", "account_manager": "ct_001"},
        {"company_id": "c002", "name": "ClientCo Operations", "industry": "Consulting", "size": "mid_market",
         "website": "https://clientco.com", "address": "456 Business Blvd", "phone": "+1-555-2000",
         "tags": ["client"], "annual_revenue": "25M-50M", "customer_since": "2021-03-22", "account_manager": "ct_002"},
        {"company_id": "c003", "name": "StartupIO", "industry": "Technology", "size": "small",
         "website": "https://startup.io", "address": "789 Innovation Dr", "phone": "+1-555-3000",
         "tags": ["lead"], "annual_revenue": "1M-5M", "customer_since": "2023-08-01", "account_manager": "ct_003"},
        {"company_id": "c004", "name": "Global Partners LLC", "industry": "Logistics", "size": "mid_market",
         "website": "https://globalpartners.com", "address": "321 Supply Chain Ave", "phone": "+1-555-4000",
         "tags": ["partner"], "annual_revenue": "50M-100M", "customer_since": "2019-11-05", "account_manager": "ct_005"},
        {"company_id": "c005", "name": "VendorCo Supplies", "industry": "Manufacturing", "size": "enterprise",
         "website": "https://vendorco.com", "address": "555 Industrial Rd", "phone": "+1-555-6000",
         "tags": ["vendor"], "annual_revenue": "5M-10M", "customer_since": "2022-06-12", "account_manager": "ct_007"}
    ]
    with open("data/companies.json", "w") as f:
        json.dump({"companies": companies}, f, indent=2)

    # ---------- Contacts ----------
    contacts = [
        {"contact_id": "ct_001", "first_name": "Alice", "last_name": "Johnson", "full_name": "Alice Johnson",
         "email": "alice.johnson@techcorp.com", "phone": "+1-555-0101", "company_id": "c001",
         "job_title": "VP Engineering", "department": "Engineering", "contact_type": "business",
         "folder": "business", "tags": ["technical", "decision-maker"], "birthday": "2025-07-10"},
        {"contact_id": "ct_002", "first_name": "Bob", "last_name": "Smith", "full_name": "Bob Smith",
         "email": "bob.smith@clientco.com", "phone": "+1-555-0102", "company_id": "c002",
         "job_title": "Account Manager", "department": "Sales", "contact_type": "business",
         "folder": "business", "tags": ["client"], "birthday": "2025-07-20"},
        {"contact_id": "ct_003", "first_name": "Carol", "last_name": "Williams", "full_name": "Carol Williams",
         "email": "carol.w@startup.io", "phone": "+1-555-0103", "company_id": "c003",
         "job_title": "CEO", "department": "Leadership", "contact_type": "personal",
         "folder": "personal", "tags": ["friend"], "birthday": "2025-07-15"},
        {"contact_id": "ct_004", "first_name": "David", "last_name": "Brown", "full_name": "David Brown",
         "email": "david.brown@email.com", "phone": "+1-555-0104", "company_id": "c004",
         "job_title": "IT Manager", "department": "IT", "contact_type": "business",
         "folder": "business", "tags": ["tech"], "birthday": "2025-08-05"},
        {"contact_id": "ct_005", "first_name": "Emma", "last_name": "Davis", "full_name": "Emma Davis",
         "email": "emma.davis@partner.net", "phone": "+1-555-0105", "company_id": "c005",
         "job_title": "Partnership Director", "department": "Business Development",
         "contact_type": "business", "folder": "business", "tags": ["partner", "executive"],
         "birthday": "2025-07-12"},
        {"contact_id": "ct_006", "first_name": "Frank", "last_name": "Miller", "full_name": "Frank Miller",
         "email": "frank.m@oldclient.com", "phone": "+1-555-0106", "company_id": "c004",
         "job_title": "Procurement Manager", "department": "Operations", "contact_type": "business",
         "folder": "inactive", "tags": ["old_client"], "birthday": None},
        {"contact_id": "ct_007", "first_name": "Grace", "last_name": "Wilson", "full_name": "Grace Wilson",
         "email": "grace.wilson@vendor.co", "phone": "+1-555-0107", "company_id": "c005",
         "job_title": "CTO", "department": "Engineering", "contact_type": "business",
         "folder": "business", "tags": ["vendor", "technical"], "birthday": "2025-07-25"},
        {"contact_id": "ct_008", "first_name": "Henry", "last_name": "Taylor", "full_name": "Henry Taylor",
         "email": "henry.t@bigcorp.com", "phone": "+1-555-0108", "company_id": "c002",
         "job_title": "CEO", "department": "Leadership", "contact_type": "personal",
         "folder": "personal", "tags": ["personal"], "birthday": "2025-07-30"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ---------- Tags ----------
    tag_defs = [
        {"tag_id": "tag_001", "name": "vip", "color": "#FFD700", "description": "Very Important Person",
         "category": "priority"},
        {"tag_id": "tag_002", "name": "technical", "color": "#00BFFF", "description": "Technical contact",
         "category": "role"},
        {"tag_id": "tag_003", "name": "client", "color": "#32CD32", "description": "Client", "category": "relationship"},
        {"tag_id": "tag_004", "name": "partner", "color": "#FF69B4", "description": "Partner", "category": "relationship"},
        {"tag_id": "tag_005", "name": "vendor", "color": "#FFA500", "description": "Vendor", "category": "relationship"},
        {"tag_id": "tag_006", "name": "decision-maker", "color": "#8A2BE2", "description": "Decision maker",
         "category": "role"}
    ]
    os.makedirs("data/tags", exist_ok=True)
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump({"tag_definitions": tag_defs}, f, indent=2)

    # ---------- Existing Reminders ----------
    reminders = [
        {"reminder_id": "r_001", "contact_id": "ct_005", "reminder_type": "birthday",
         "title": "Emma Davis's Birthday",
         "description": "Birthday reminder for Emma Davis",
         "reminder_date": "2025-07-12", "days_before": 1, "is_recurring": True, "enabled": True}
    ]
    os.makedirs("reminders", exist_ok=True)
    with open("reminders/reminders.json", "w") as f:
        json.dump({"reminders": reminders}, f, indent=2)

    # ---------- Distractor files ----------
    os.makedirs("backups", exist_ok=True)
    with open("backups/old_contacts.json", "w") as f:
        json.dump({"contacts": [{"contact_id": "ct_999", "full_name": "Ghost"}]}, f, indent=2)
    with open("readme.txt", "w") as f:
        f.write("CRM data dump – ignore this file.\n")

if __name__ == "__main__":
    build_env()
