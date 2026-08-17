import json
import os
import random

def build_env():
    # Ensure directories exist
    os.makedirs("data/contacts", exist_ok=True)
    os.makedirs("data/companies", exist_ok=True)
    os.makedirs("data/tags", exist_ok=True)
    os.makedirs("data/reminders", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---------- companies ----------
    companies = [
        {"company_id": "comp_techcorp", "name": "TechCorp Industries", "industry": "Technology", "size": "enterprise",
         "website": "https://techcorp.com", "address": "1 Tech Plaza", "phone": "+1-555-5000", "tags": [],
         "annual_revenue": "100M+", "customer_since": "2018-03-15", "account_manager": "ct_001"},
        {"company_id": "comp_clientco", "name": "ClientCo Operations", "industry": "Consulting", "size": "mid_market",
         "website": "https://clientco.com", "address": "2 Business Ave", "phone": "+1-555-1000", "tags": [],
         "annual_revenue": "25M-50M", "customer_since": "2020-06-01", "account_manager": "ct_002"},
        {"company_id": "comp_startupio", "name": "StartupIO", "industry": "Technology", "size": "small",
         "website": "https://startup.io", "address": "3 Innovation Dr", "phone": "+1-555-4000", "tags": [],
         "annual_revenue": "1M-5M", "customer_since": "2022-09-10", "account_manager": "ct_003"},
        {"company_id": "comp_global", "name": "Global Partners LLC", "industry": "Logistics", "size": "enterprise",
         "website": "https://globalpartners.com", "address": "4 Logistics Blvd", "phone": "+1-555-2000", "tags": [],
         "annual_revenue": "50M-100M", "customer_since": "2019-01-20", "account_manager": "ct_005"},
        {"company_id": "comp_vendorco", "name": "VendorCo Supplies", "industry": "Manufacturing", "size": "mid_market",
         "website": "https://vendorco.com", "address": "5 Supply St", "phone": "+1-555-6000", "tags": [],
         "annual_revenue": "5M-10M", "customer_since": "2021-04-05", "account_manager": "ct_007"},
        {"company_id": "comp_oldclient", "name": "OldClient Services", "industry": "Retail", "size": "small",
         "website": "https://oldclient.com", "address": "6 Retail Lane", "phone": "+1-555-3000", "tags": [],
         "annual_revenue": "5M-10M", "customer_since": "2017-11-30", "account_manager": "ct_002"}
    ]
    with open("data/companies.json", "w") as f:
        json.dump({"companies": companies}, f, indent=2)

    # ---------- contacts ----------
    contacts = [
        {"contact_id": "ct_001", "first_name": "Alice", "last_name": "Johnson", "full_name": "Alice Johnson",
         "email": "alice.johnson@techcorp.com", "phone": "+1-555-0101", "company_id": "comp_techcorp",
         "job_title": "CTO", "department": "Engineering", "contact_type": "business", "folder": "business", "tags": []},
        {"contact_id": "ct_002", "first_name": "Bob", "last_name": "Smith", "full_name": "Bob Smith",
         "email": "bob.smith@techcorp.com", "phone": "+1-555-0102", "company_id": "comp_techcorp",
         "job_title": "IT Manager", "department": "IT", "contact_type": "business", "folder": "inactive", "tags": ["old_client"]},
        {"contact_id": "ct_003", "first_name": "Carol", "last_name": "Williams", "full_name": "Carol Williams",
         "email": "carol.w@techcorp.com", "phone": "+1-555-0103", "company_id": "comp_techcorp",
         "job_title": "VP Engineering", "department": "Engineering", "contact_type": "business", "folder": "business", "tags": ["vip"]},
        {"contact_id": "ct_004", "first_name": "David", "last_name": "Brown", "full_name": "David Brown",
         "email": "david.brown@email.com", "phone": "+1-555-0104", "company_id": "comp_clientco",
         "job_title": "Account Manager", "department": "Sales", "contact_type": "business", "folder": "business", "tags": []},
        {"contact_id": "ct_005", "first_name": "Emma", "last_name": "Davis", "full_name": "Emma Davis",
         "email": "emma.davis@partner.net", "phone": "+1-555-0105", "company_id": "comp_global",
         "job_title": "Partnership Director", "department": "Business Development", "contact_type": "business", "folder": "business", "tags": []},
        {"contact_id": "ct_006", "first_name": "Frank", "last_name": "Miller", "full_name": "Frank Miller",
         "email": "frank.m@techcorp.com", "phone": "+1-555-0106", "company_id": "comp_techcorp",
         "job_title": "Procurement Manager", "department": "Operations", "contact_type": "personal", "folder": "personal", "tags": []},
        {"contact_id": "ct_007", "first_name": "Grace", "last_name": "Wilson", "full_name": "Grace Wilson",
         "email": "grace.wilson@vendor.co", "phone": "+1-555-0107", "company_id": "comp_vendorco",
         "job_title": "CEO", "department": "Leadership", "contact_type": "business", "folder": "inactive", "tags": []},
        {"contact_id": "ct_008", "first_name": "Henry", "last_name": "Taylor", "full_name": "Henry Taylor",
         "email": "henry.t@bigcorp.com", "phone": "+1-555-0108", "company_id": None,  # intentionally missing
         "job_title": "IT Manager", "department": "IT", "contact_type": "business", "folder": "business", "tags": []}
    ]
    # Add a duplicate (different id but same email, to test dedup logic – agent should ignore)
    contacts.append({
        "contact_id": "ct_009", "first_name": "Alice", "last_name": "Johnson Dup", "full_name": "Alice Johnson Dup",
        "email": "alice.johnson@techcorp.com", "phone": "+1-555-0199", "company_id": "comp_techcorp",
        "job_title": "CTO", "department": "Engineering", "contact_type": "business", "folder": "business", "tags": []
    })
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ---------- tag definitions ----------
    tag_defs = [
        {"tag_id": "tag_vip", "name": "vip", "color": "#FFD700", "description": "Very important person", "category": "priority"},
        {"tag_id": "tag_old_client", "name": "old_client", "color": "#A9A9A9", "description": "Inactive or former client", "category": "status"},
        {"tag_id": "tag_tech_partner", "name": "tech_partner", "color": "#00BFFF", "description": "Technology partner", "category": "relationship"}
    ]
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump({"tag_definitions": tag_defs}, f, indent=2)

    # ---------- reminders ----------
    # Alice's birthday 2025-04-15 (next month), Carol's birthday 2025-03-10 (already passed), others random
    reminders = [
        {"reminder_id": "rem_001", "contact_id": "ct_001", "reminder_type": "birthday",
         "title": "Alice Johnson's Birthday", "description": "Birthday reminder for Alice Johnson",
         "reminder_date": "2025-04-15", "days_before": 3, "is_recurring": True, "enabled": True},
        {"reminder_id": "rem_002", "contact_id": "ct_003", "reminder_type": "birthday",
         "title": "Carol Williams's Birthday", "description": "Birthday reminder for Carol Williams",
         "reminder_date": "2025-03-10", "days_before": 2, "is_recurring": True, "enabled": True},
        {"reminder_id": "rem_003", "contact_id": "ct_004", "reminder_type": "birthday",
         "title": "David Brown's Birthday", "description": "Birthday reminder for David Brown",
         "reminder_date": "2025-06-21", "days_before": 1, "is_recurring": True, "enabled": True}
    ]
    with open("data/reminders/reminders.json", "w") as f:
        json.dump({"reminders": reminders}, f, indent=2)

    # ---------- context date ----------
    with open("ops/context.txt", "w") as f:
        f.write("2025-03-20")

if __name__ == "__main__":
    build_env()
