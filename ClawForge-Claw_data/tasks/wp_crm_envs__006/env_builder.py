import os
import json
import random

def build_env():
    # Create directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/tags", exist_ok=True)
    os.makedirs("data/reminders", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Companies
    companies = [
        {"company_id": "comp_001", "name": "TechCorp Industries", "industry": "Technology", "size": "enterprise", "website": "https://techcorp.com", "address": "1 Tech Way", "phone": "+1-555-1000", "tags": ["partner"], "annual_revenue": "100M+", "customer_since": "2019-01-01", "account_manager": "ct_001"},
        {"company_id": "comp_002", "name": "ClientCo Operations", "industry": "Consulting", "size": "mid_market", "website": "https://clientco.com", "address": "2 Client St", "phone": "+1-555-2000", "tags": [], "annual_revenue": "5M-10M", "customer_since": "2020-06-15", "account_manager": "ct_002"},
        {"company_id": "comp_003", "name": "StartupIO", "industry": "Technology", "size": "small", "website": "https://startup.io", "address": "3 Startup Ave", "phone": "+1-555-3000", "tags": ["startup"], "annual_revenue": "1M-5M", "customer_since": "2022-03-01", "account_manager": "ct_005"},
    ]
    with open("data/companies.json", "w") as f:
        json.dump({"companies": companies}, f)

    # Tag definitions (include priority)
    tag_defs = [
        {"tag_id": "tag_001", "name": "priority", "color": "#FF0000", "description": "High priority contact", "category": "priority"},
        {"tag_id": "tag_002", "name": "vip", "color": "#00FF00", "description": "Very important person", "category": "priority"},
        {"tag_id": "tag_003", "name": "startup", "color": "#0000FF", "description": "Startup company", "category": "industry"},
        {"tag_id": "tag_004", "name": "partner", "color": "#FFFF00", "description": "Partner company", "category": "relationship"},
    ]
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump({"tag_definitions": tag_defs}, f)

    # Contacts – carefully designed for unique answer
    # TechCorp (comp_001) business contacts NOT in business folder → need fix
    correct_contacts = [
        {"contact_id": "ct_101", "first_name": "Alice", "last_name": "Johnson", "full_name": "Alice Johnson", "email": "alice@techcorp.com", "phone": "+1-555-0101", "company_id": "comp_001", "job_title": "CTO", "department": "Engineering", "contact_type": "business", "folder": "personal", "tags": []},
        {"contact_id": "ct_102", "first_name": "Bob", "last_name": "Smith", "full_name": "Bob Smith", "email": "bob@techcorp.com", "phone": "+1-555-0102", "company_id": "comp_001", "job_title": "VP Engineering", "department": "Leadership", "contact_type": "business", "folder": "inactive", "tags": ["vip"]},
        {"contact_id": "ct_103", "first_name": "Carol", "last_name": "Williams", "full_name": "Carol Williams", "email": "carol@techcorp.com", "phone": "+1-555-0103", "company_id": "comp_001", "job_title": "Account Manager", "department": "Sales", "contact_type": "business", "folder": "personal", "tags": []},
    ]
    # TechCorp business already in business folder → should NOT be in result
    already_correct = [
        {"contact_id": "ct_104", "first_name": "David", "last_name": "Brown", "full_name": "David Brown", "email": "david@techcorp.com", "phone": "+1-555-0104", "company_id": "comp_001", "job_title": "IT Manager", "department": "IT", "contact_type": "business", "folder": "business", "tags": ["priority"]},
    ]
    # TechCorp personal contacts → should NOT be in result (contact_type=personal)
    personal_tech = [
        {"contact_id": "ct_105", "first_name": "Emma", "last_name": "Davis", "full_name": "Emma Davis", "email": "emma@techcorp.com", "phone": "+1-555-0105", "company_id": "comp_001", "job_title": "CEO", "department": "Leadership", "contact_type": "personal", "folder": "personal", "tags": []},
    ]
    # Non‑TechCorp business contacts → should NOT be in result
    other_company = [
        {"contact_id": "ct_106", "first_name": "Frank", "last_name": "Miller", "full_name": "Frank Miller", "email": "frank@clientco.com", "phone": "+1-555-0106", "company_id": "comp_002", "job_title": "Procurement Manager", "department": "Operations", "contact_type": "business", "folder": "personal", "tags": []},
        {"contact_id": "ct_107", "first_name": "Grace", "last_name": "Wilson", "full_name": "Grace Wilson", "email": "grace@startup.io", "phone": "+1-555-0107", "company_id": "comp_003", "job_title": "CEO", "department": "Leadership", "contact_type": "business", "folder": "inactive", "tags": []},
    ]
    # Another TechCorp business but folder = business and already has priority → already correct
    duplicate_correct = [
        {"contact_id": "ct_108", "first_name": "Henry", "last_name": "Taylor", "full_name": "Henry Taylor", "email": "henry@techcorp.com", "phone": "+1-555-0108", "company_id": "comp_001", "job_title": "Partnership Director", "department": "Business Development", "contact_type": "business", "folder": "business", "tags": ["priority"]},
    ]

    all_contacts = correct_contacts + already_correct + personal_tech + other_company + duplicate_correct
    # Shuffle to obscure order
    random.shuffle(all_contacts)
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": all_contacts}, f)

    # Reminders (dummy, not used in this task but required by schema)
    reminders = []
    with open("data/reminders/reminders.json", "w") as f:
        json.dump({"reminders": reminders}, f)

    # Accounts (dummy)
    accounts = []
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

if __name__ == "__main__":
    build_env()
