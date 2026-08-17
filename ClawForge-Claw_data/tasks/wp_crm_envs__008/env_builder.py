import json
import os

def build_env():
    os.makedirs("data", exist_ok=True)
    os.makedirs("reminders", exist_ok=True)
    os.makedirs("tags", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Companies
    companies = [
        {"company_id": "comp_001", "name": "ClientCo Operations", "industry": "Consulting", "size": "mid_market", "website": "https://clientco.com", "address": "123 Client St", "phone": "+1-555-1000", "tags": ["client", "active"], "annual_revenue": "5M-10M", "customer_since": "2020-01-15", "account_manager": "ct_001"},
        {"company_id": "comp_002", "name": "Global Partners LLC", "industry": "Logistics", "size": "enterprise", "website": "https://globalpartners.com", "address": "456 Global Ave", "phone": "+1-555-2000", "tags": ["partner", "vip"], "annual_revenue": "100M+", "customer_since": "2019-06-01", "account_manager": "ct_002"},
        {"company_id": "comp_003", "name": "TechCorp Industries", "industry": "Technology", "size": "enterprise", "website": "https://techcorp.com", "address": "789 Tech Blvd", "phone": "+1-555-3000", "tags": ["tech", "vip"], "annual_revenue": "50M-100M", "customer_since": "2018-03-20", "account_manager": "ct_003"},
        {"company_id": "comp_004", "name": "StartupIO", "industry": "Technology", "size": "small", "website": "https://startup.io", "address": "101 Startup Way", "phone": "+1-555-4000", "tags": ["startup"], "annual_revenue": "1M-5M", "customer_since": "2023-11-01", "account_manager": "ct_005"},
        {"company_id": "comp_005", "name": "OldClient Services", "industry": "Consulting", "size": "mid_market", "website": "https://oldclient.com", "address": "202 Old Rd", "phone": "+1-555-5000", "tags": ["inactive"], "annual_revenue": "5M-10M", "customer_since": "2015-05-10", "account_manager": "ct_007"},
    ]

    # Contacts
    contacts = [
        # TechCorp contacts
        {"contact_id": "ct_101", "first_name": "Alice", "last_name": "Johnson", "full_name": "Alice Johnson", "email": "alice.johnson@techcorp.com", "phone": "+1-555-0101", "company_id": "comp_003", "job_title": "VP Engineering", "department": "Engineering", "contact_type": "business", "folder": "business", "tags": ["tech"]},
        {"contact_id": "ct_102", "first_name": "Bob", "last_name": "Smith", "full_name": "Bob Smith", "email": "bob.smith@techcorp.com", "phone": "+1-555-0102", "company_id": "comp_003", "job_title": "CTO", "department": "Leadership", "contact_type": "business", "folder": "business", "tags": []},
        {"contact_id": "ct_103", "first_name": "Carol", "last_name": "Williams", "full_name": "Carol Williams", "email": "carol.w@techcorp.com", "phone": "+1-555-0103", "company_id": "comp_003", "job_title": "IT Manager", "department": "IT", "contact_type": "business", "folder": "business", "tags": ["vip"]},
        {"contact_id": "ct_104", "first_name": "David", "last_name": "Brown", "full_name": "David Brown", "email": "david.brown@techcorp.com", "phone": "+1-555-0104", "company_id": "comp_003", "job_title": "Account Manager", "department": "Sales", "contact_type": "business", "folder": "inactive", "tags": []},
        # Other company contacts (distractors)
        {"contact_id": "ct_201", "first_name": "Emma", "last_name": "Davis", "full_name": "Emma Davis", "email": "emma.davis@partner.net", "phone": "+1-555-0105", "company_id": "comp_001", "job_title": "Partnership Director", "department": "Business Development", "contact_type": "business", "folder": "business", "tags": []},
        {"contact_id": "ct_202", "first_name": "Frank", "last_name": "Miller", "full_name": "Frank Miller", "email": "frank.m@oldclient.com", "phone": "+1-555-0106", "company_id": "comp_005", "job_title": "CEO", "department": "Leadership", "contact_type": "business", "folder": "inactive", "tags": []},
        {"contact_id": "ct_203", "first_name": "Grace", "last_name": "Wilson", "full_name": "Grace Wilson", "email": "grace.wilson@vendor.co", "phone": "+1-555-0107", "company_id": "comp_004", "job_title": "Procurement Manager", "department": "Operations", "contact_type": "business", "folder": "business", "tags": ["startup"]},
        {"contact_id": "ct_204", "first_name": "Henry", "last_name": "Taylor", "full_name": "Henry Taylor", "email": "henry.t@bigcorp.com", "phone": "+1-555-0108", "company_id": "comp_002", "job_title": "Account Manager", "department": "Sales", "contact_type": "business", "folder": "personal", "tags": []},
    ]

    # Birthday reminders
    reminders = [
        # ct_101 has active reminder
        {"reminder_id": "rem_101", "contact_id": "ct_101", "reminder_type": "birthday", "title": "Alice Johnson's Birthday", "description": "Birthday reminder for Alice Johnson", "reminder_date": "2025-04-15", "days_before": 7, "is_recurring": True, "enabled": True},
        # ct_102 has reminder but disabled
        {"reminder_id": "rem_102", "contact_id": "ct_102", "reminder_type": "birthday", "title": "Bob Smith's Birthday", "description": "Birthday reminder for Bob Smith", "reminder_date": "2025-05-20", "days_before": 3, "is_recurring": True, "enabled": False},
        # ct_103 has no reminder entry
        # ct_104 archived, no reminder
        # ct_201 has active reminder (distractor)
        {"reminder_id": "rem_201", "contact_id": "ct_201", "reminder_type": "birthday", "title": "Emma Davis's Birthday", "description": "Birthday reminder for Emma Davis", "reminder_date": "2025-06-10", "days_before": 5, "is_recurring": True, "enabled": True},
    ]

    # Tag definitions (distractor)
    tag_definitions = [
        {"tag_id": "tag_001", "name": "tech", "color": "#00aaff", "description": "Technology related", "category": "industry"},
        {"tag_id": "tag_002", "name": "vip", "color": "#ffaa00", "description": "Very important person", "category": "priority"},
        {"tag_id": "tag_003", "name": "birthday", "color": "#ff66cc", "description": "Birthday reminder tag", "category": "personal"},
        {"tag_id": "tag_004", "name": "inactive", "color": "#cccccc", "description": "Inactive contact", "category": "status"},
    ]

    with open("data/companies.json", "w") as f:
        json.dump({"companies": companies}, f, indent=2)
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)
    with open("reminders/reminders.json", "w") as f:
        json.dump({"reminders": reminders}, f, indent=2)
    with open("tags/tag_definitions.json", "w") as f:
        json.dump({"tag_definitions": tag_definitions}, f, indent=2)

if __name__ == "__main__":
    build_env()
