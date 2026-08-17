import os
import json

def build_env():
    # Create data directory structure
    os.makedirs("data/reminders", exist_ok=True)
    os.makedirs("data/tags", exist_ok=True)
    os.makedirs("ops", exist_ok=False)  # do not create ops yet, agent should create it

    # --- companies.json ---
    companies = {
        "companies": [
            {
                "company_id": "comp_001",
                "name": "Global Partners LLC",
                "industry": "Logistics",
                "size": "mid_market",
                "website": "https://globalpartners.com",
                "address": "456 Market St, San Francisco, CA",
                "phone": "+1-555-2000",
                "tags": ["partner"],
                "annual_revenue": "25M-50M",
                "customer_since": "2021-03-15",
                "account_manager": "ct_002"
            },
            {
                "company_id": "comp_002",
                "name": "TechCorp Industries",
                "industry": "Technology",
                "size": "enterprise",
                "website": "https://techcorp.com",
                "address": "123 Tech Ave, San Jose, CA",
                "phone": "+1-555-5000",
                "tags": ["vip"],
                "annual_revenue": "100M+",
                "customer_since": "2019-01-10",
                "account_manager": "ct_001"
            },
            {
                "company_id": "comp_003",
                "name": "OldClient Services",
                "industry": "Consulting",
                "size": "small",
                "website": "https://oldclient.com",
                "address": "789 Old Rd, Austin, TX",
                "phone": "+1-555-3000",
                "tags": ["inactive"],
                "annual_revenue": "5M-10M",
                "customer_since": "2018-07-22",
                "account_manager": "ct_005"
            }
        ]
    }
    with open("data/companies.json", "w") as f:
        json.dump(companies, f, indent=2)

    # --- contacts.json ---
    contacts = {
        "contacts": [
            # Global Partners LLC contacts
            {
                "contact_id": "contact_001",
                "first_name": "Bob",
                "last_name": "Smith",
                "full_name": "Bob Smith",
                "email": "bob.smith@clientco.com",
                "phone": "+1-555-0102",
                "company_id": "comp_001",
                "job_title": "Procurement Manager",
                "department": "Operations",
                "contact_type": "business",
                "folder": "business",
                "tags": ["manager"]
            },
            {
                "contact_id": "contact_002",
                "first_name": "Carol",
                "last_name": "Williams",
                "full_name": "Carol Williams",
                "email": "carol.w@startup.io",
                "phone": "+1-555-0103",
                "company_id": "comp_001",
                "job_title": "CEO",
                "department": "Leadership",
                "contact_type": "business",
                "folder": "business",
                "tags": ["executive"]
            },
            {
                "contact_id": "contact_003",
                "first_name": "David",
                "last_name": "Brown",
                "full_name": "David Brown",
                "email": "david.brown@email.com",
                "phone": "+1-555-0104",
                "company_id": "comp_001",
                "job_title": "CTO",
                "department": "Engineering",
                "contact_type": "business",
                "folder": "business",
                "tags": ["tech"]
            },
            # 干扰：其他公司联系人
            {
                "contact_id": "contact_004",
                "first_name": "Alice",
                "last_name": "Johnson",
                "full_name": "Alice Johnson",
                "email": "alice.johnson@techcorp.com",
                "phone": "+1-555-0101",
                "company_id": "comp_002",
                "job_title": "IT Manager",
                "department": "IT",
                "contact_type": "business",
                "folder": "business",
                "tags": ["vip"]
            },
            {
                "contact_id": "contact_005",
                "first_name": "Emma",
                "last_name": "Davis",
                "full_name": "Emma Davis",
                "email": "emma.davis@partner.net",
                "phone": "+1-555-0105",
                "company_id": "comp_003",
                "job_title": "Partnership Director",
                "department": "Business Development",
                "contact_type": "business",
                "folder": "inactive",
                "tags": ["old"]
            },
            # 脏数据：联系人 company_id 不存在
            {
                "contact_id": "contact_006",
                "first_name": "Frank",
                "last_name": "Miller",
                "full_name": "Frank Miller",
                "email": "frank.m@oldclient.com",
                "phone": "+1-555-0106",
                "company_id": "comp_999",
                "job_title": "VP Engineering",
                "department": "Engineering",
                "contact_type": "business",
                "folder": "business",
                "tags": []
            }
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # --- reminders.json ---
    reminders = {
        "reminders": [
            # 已有 birthday 提醒（contact_001 和 contact_003）
            {
                "reminder_id": "rem_001",
                "contact_id": "contact_001",
                "reminder_type": "birthday",
                "title": "Bob Smith's Birthday",
                "description": "Birthday reminder for Bob Smith",
                "reminder_date": "2025-06-20",
                "days_before": 1,
                "is_recurring": True,
                "enabled": True
            },
            {
                "reminder_id": "rem_003",
                "contact_id": "contact_003",
                "reminder_type": "birthday",
                "title": "David Brown's Birthday",
                "description": "Birthday reminder for David Brown",
                "reminder_date": "2025-07-15",
                "days_before": 2,
                "is_recurring": True,
                "enabled": True
            },
            # 干扰：其他类型提醒（非 birthday）
            {
                "reminder_id": "rem_099",
                "contact_id": "contact_002",
                "reminder_type": "meeting",
                "title": "Carol Williams Meeting",
                "description": "Quarterly review",
                "reminder_date": "2025-05-01",
                "days_before": 1,
                "is_recurring": False,
                "enabled": True
            },
            # 脏数据：联系人不存在的提醒
            {
                "reminder_id": "rem_666",
                "contact_id": "contact_999",
                "reminder_type": "birthday",
                "title": "Ghost Birthday",
                "description": "No contact",
                "reminder_date": "2025-08-01",
                "days_before": 0,
                "is_recurring": True,
                "enabled": False
            }
        ]
    }
    with open("data/reminders/reminders.json", "w") as f:
        json.dump(reminders, f, indent=2)

    # --- tag_definitions.json (干扰，但任务不需要) ---
    tags = {
        "tag_definitions": [
            {"tag_id": "tag_001", "name": "vip", "color": "gold", "description": "Very Important Person", "category": "priority"},
            {"tag_id": "tag_002", "name": "manager", "color": "blue", "description": "Management level", "category": "role"}
        ]
    }
    os.makedirs("data/tags", exist_ok=True)
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump(tags, f, indent=2)

if __name__ == "__main__":
    build_env()
