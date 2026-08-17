import os
import json

def build_env():
    # ----- companies -----
    companies = [
        {"company_id": "comp_001", "name": "TechCorp Industries", "industry": "Technology", "size": "enterprise", "website": "https://techcorp.com", "address": "1 Tech Ave", "phone": "+1-555-5000", "tags": [], "annual_revenue": "100M+", "customer_since": "2020-01-01", "account_manager": "ct_001"},
        {"company_id": "comp_002", "name": "ClientCo Operations", "industry": "Consulting", "size": "mid_market", "website": "https://clientco.com", "address": "2 Market St", "phone": "+1-555-1000", "tags": [], "annual_revenue": "5M-10M", "customer_since": "2019-06-15", "account_manager": "ct_002"},
        {"company_id": "comp_003", "name": "StartupIO", "industry": "Technology", "size": "small", "website": "https://startup.io", "address": "3 Startup Lane", "phone": "+1-555-4000", "tags": [], "annual_revenue": "1M-5M", "customer_since": "2023-03-01", "account_manager": "ct_003"},
        {"company_id": "comp_004", "name": "Global Partners LLC", "industry": "Logistics", "size": "enterprise", "website": "https://globalpartners.com", "address": "4 Global Blvd", "phone": "+1-555-2000", "tags": [], "annual_revenue": "50M-100M", "customer_since": "2018-07-20", "account_manager": "ct_005"},
        {"company_id": "comp_005", "name": "VendorCo Supplies", "industry": "Manufacturing", "size": "mid_market", "website": "https://vendorco.com", "address": "5 Vendor Way", "phone": "+1-555-6000", "tags": [], "annual_revenue": "25M-50M", "customer_since": "2021-11-11", "account_manager": "ct_007"},
        {"company_id": "comp_006", "name": "OldClient Services", "industry": "Retail", "size": "small", "website": "https://oldclient.com", "address": "6 Old Road", "phone": "+1-555-3000", "tags": [], "annual_revenue": "50M-100M", "customer_since": "2017-02-28", "account_manager": "ct_001"},
    ]
    os.makedirs("data", exist_ok=True)
    with open("data/companies.json", "w") as f:
        json.dump({"companies": companies}, f, indent=2)

    # ----- contacts -----
    contacts = [
        {"contact_id": "ct_101", "first_name": "Alice", "last_name": "Johnson", "full_name": "Alice Johnson", "email": "alice.johnson@techcorp.com", "phone": "+1-555-0101", "company_id": "comp_001", "job_title": "CEO", "department": "Leadership", "contact_type": "business", "folder": "business", "tags": []},
        {"contact_id": "ct_102", "first_name": "Bob", "last_name": "Smith", "full_name": "Bob Smith", "email": "bob.smith@clientco.com", "phone": "+1-555-0102", "company_id": "comp_002", "job_title": "IT Manager", "department": "IT", "contact_type": "business", "folder": "business", "tags": []},
        {"contact_id": "ct_103", "first_name": "Carol", "last_name": "Williams", "full_name": "Carol Williams", "email": "carol.w@startup.io", "phone": "+1-555-0103", "company_id": "comp_003", "job_title": "CTO", "department": "Engineering", "contact_type": "personal", "folder": "personal", "tags": []},
        {"contact_id": "ct_104", "first_name": "David", "last_name": "Brown", "full_name": "David Brown", "email": "david.brown@email.com", "phone": "+1-555-0104", "company_id": "comp_004", "job_title": "VP Engineering", "department": "Engineering", "contact_type": "business", "folder": "business", "tags": []},
        {"contact_id": "ct_105", "first_name": "Emma", "last_name": "Davis", "full_name": "Emma Davis", "email": "emma.davis@partner.net", "phone": "+1-555-0105", "company_id": "comp_005", "job_title": "Partnership Director", "department": "Business Development", "contact_type": "business", "folder": "business", "tags": []},
        {"contact_id": "ct_106", "first_name": "Frank", "last_name": "Miller", "full_name": "Frank Miller", "email": "frank.m@oldclient.com", "phone": "+1-555-0106", "company_id": "comp_006", "job_title": "Account Manager", "department": "Sales", "contact_type": "business", "folder": "business", "tags": []},
        {"contact_id": "ct_107", "first_name": "Grace", "last_name": "Wilson", "full_name": "Grace Wilson", "email": "grace.wilson@vendor.co", "phone": "+1-555-0107", "company_id": "comp_001", "job_title": "Procurement Manager", "department": "Operations", "contact_type": "business", "folder": "business", "tags": []},
        {"contact_id": "ct_108", "first_name": "Henry", "last_name": "Taylor", "full_name": "Henry Taylor", "email": "henry.t@bigcorp.com", "phone": "+1-555-0108", "company_id": "comp_002", "job_title": "CEO", "department": "Leadership", "contact_type": "personal", "folder": "personal", "tags": []},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ----- tag definitions (irrelevant) -----
    os.makedirs("data/tags", exist_ok=True)
    tags = [
        {"tag_id": "tag_001", "name": "VIP", "color": "#FFD700", "description": "Very Important Person", "category": "priority"},
        {"tag_id": "tag_002", "name": "Birthday", "color": "#FF69B4", "description": "Birthday reminder", "category": "personal"},
    ]
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump({"tag_definitions": tags}, f, indent=2)

    # ----- reminders (distraction) -----
    os.makedirs("data/reminders", exist_ok=True)
    reminders = [
        {"reminder_id": "rem_001", "contact_id": "ct_101", "reminder_type": "birthday", "title": "Alice Johnson's Birthday", "description": "Birthday reminder for Alice Johnson", "reminder_date": "1990-05-15", "days_before": 3, "is_recurring": True, "enabled": True},
        {"reminder_id": "rem_002", "contact_id": "ct_103", "reminder_type": "birthday", "title": "Carol Williams's Birthday", "description": "Birthday reminder for Carol Williams", "reminder_date": "1985-11-20", "days_before": 3, "is_recurring": True, "enabled": False},
    ]
    with open("data/reminders/reminders.json", "w") as f:
        json.dump({"reminders": reminders}, f, indent=2)

    # ----- extra junk file -----
    with open("data/old_contacts_backup.csv", "w") as f:
        f.write("id,name\n1,Old\n")

if __name__ == "__main__":
    build_env()
