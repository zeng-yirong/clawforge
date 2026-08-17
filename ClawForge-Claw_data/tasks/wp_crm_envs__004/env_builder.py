import os
import json

def build_env():
    # Ensure directories exist
    os.makedirs("data", exist_ok=True)

    # ----- contacts.json (核心数据) -----
    contacts = [
        {
            "contact_id": "ct_001",
            "first_name": "Alice",
            "last_name": "Johnson",
            "full_name": "Alice Johnson",
            "email": "alice.johnson@techcorp.com",
            "phone": "+1-555-0101",
            "company_id": "comp_001",
            "job_title": "CEO",
            "department": "Leadership",
            "contact_type": "business",
            "folder": "business",
            "tags": ["vip"],
            "birthday": "1990-04-15"
        },
        {
            "contact_id": "ct_002",
            "first_name": "Bob",
            "last_name": "Smith",
            "full_name": "Bob Smith",
            "email": "bob.smith@clientco.com",
            "phone": "+1-555-0102",
            "company_id": "comp_002",
            "job_title": "IT Manager",
            "department": "IT",
            "contact_type": "business",
            "folder": "business",
            "tags": ["it"],
            "birthday": "1985-03-20"
        },
        {
            "contact_id": "ct_003",
            "first_name": "Carol",
            "last_name": "Williams",
            "full_name": "Carol Williams",
            "email": "carol.w@startup.io",
            "phone": "+1-555-0103",
            "company_id": "comp_003",
            "job_title": "CTO",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "business",
            "tags": ["engineering"],
            "birthday": "1992-04-01"
        },
        {
            "contact_id": "ct_004",
            "first_name": "David",
            "last_name": "Brown",
            "full_name": "David Brown",
            "email": "david.brown@email.com",
            "phone": "+1-555-0104",
            "company_id": "comp_004",
            "job_title": "Account Manager",
            "department": "Sales",
            "contact_type": "personal",
            "folder": "personal",
            "tags": [],
            "birthday": "1980-05-10"
        },
        {
            "contact_id": "ct_005",
            "first_name": "Emma",
            "last_name": "Davis",
            "full_name": "Emma Davis",
            "email": "emma.davis@partner.net",
            "phone": "+1-555-0105",
            "company_id": "comp_005",
            "job_title": "Partnership Director",
            "department": "Business Development",
            "contact_type": "business",
            "folder": "business",
            "tags": ["partner"],
            "birthday": "1975-04-30"
        },
        {
            "contact_id": "ct_006",
            "first_name": "Frank",
            "last_name": "Miller",
            "full_name": "Frank Miller",
            "email": "frank.m@oldclient.com",
            "phone": "+1-555-0106",
            "company_id": "comp_006",
            "job_title": "Procurement Manager",
            "department": "Operations",
            "contact_type": "business",
            "folder": "inactive",
            "tags": ["old"],
            "birthday": "1988-06-15"
        },
        {
            "contact_id": "ct_007",
            "first_name": "Grace",
            "last_name": "Wilson",
            "full_name": "Grace Wilson",
            "email": "grace.wilson@vendor.co",
            "phone": "+1-555-0107",
            "company_id": "comp_007",
            "job_title": "VP Engineering",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "business",
            "tags": ["vip", "engineering"],
            "birthday": "1995-04-22"
        },
        {
            "contact_id": "ct_008",
            "first_name": "Henry",
            "last_name": "Taylor",
            "full_name": "Henry Taylor",
            "email": "henry.t@bigcorp.com",
            "phone": "+1-555-0108",
            "company_id": "comp_008",
            "job_title": "IT Manager",
            "department": "IT",
            "contact_type": "business",
            "folder": "business",
            "tags": [],
            "birthday": ""  # 无效空值，应被忽略
        }
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ----- 背景文件（仅用于丰富环境，不影响答案）-----
    # accounts.json
    accounts = {
        "accounts": [
            {"account_id": "acc_001", "display_name": "TechCorp", "email": "admin@techcorp.com",
             "default_tag_color": "#1a73e8", "auto_tagging_enabled": True,
             "birthday_reminders_enabled": True, "reminder_days_before": 7,
             "available_folders": ["business", "personal", "archive", "inactive"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # companies.json
    companies = {
        "companies": [
            {"company_id": "comp_001", "name": "TechCorp Industries", "industry": "Technology",
             "size": "enterprise", "website": "https://techcorp.com",
             "address": "123 Tech St", "phone": "+1-555-1000", "tags": [],
             "annual_revenue": "100M+", "customer_since": "2018-01-15", "account_manager": "ct_001"}
        ]
    }
    with open("data/companies.json", "w") as f:
        json.dump(companies, f, indent=2)

    # tags/tag_definitions.json
    os.makedirs("data/tags", exist_ok=True)
    tags = {
        "tag_definitions": [
            {"tag_id": "tag_001", "name": "vip", "color": "#FFD700",
             "description": "Very important person", "category": "priority"}
        ]
    }
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump(tags, f, indent=2)

if __name__ == "__main__":
    build_env()
