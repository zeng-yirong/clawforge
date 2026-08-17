import os
import json

def build_env():
    # 创建必要目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/reminders", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 干扰文件
    os.makedirs("old_backup", exist_ok=True)
    with open("old_backup/contacts.json", "w") as f:
        json.dump({"note": "obsolete"}, f)
    with open("notes.txt", "w") as f:
        f.write("Some old scratch notes\n")

    # ---------- tag_definitions ----------
    tag_defs = [
        {
            "tag_id": "tag_vip",
            "name": "VIP",
            "color": "#FFD700",
            "description": "Very Important Person",
            "category": "priority"
        },
        {
            "tag_id": "tag_industry_tech",
            "name": "industry:technology",
            "color": "#3498DB",
            "description": "Technology industry",
            "category": "industry"
        },
        {
            "tag_id": "tag_industry_manu",
            "name": "industry:manufacturing",
            "color": "#2ECC71",
            "description": "Manufacturing industry",
            "category": "industry"
        }
    ]
    with open("data/tag_definitions.json", "w") as f:
        json.dump({"tag_definitions": tag_defs}, f, indent=2)

    # ---------- companies ----------
    companies = [
        {
            "company_id": "comp_tech",
            "name": "TechCorp Industries",
            "industry": "Technology",
            "size": "enterprise",
            "website": "https://techcorp.com",
            "address": "1 Tech Drive, Silicon Valley, CA",
            "phone": "+1-555-5000",
            "tags": ["technology", "enterprise"],
            "annual_revenue": "50M-100M",
            "customer_since": "2018-03-15",
            "account_manager": "ct_001"
        },
        {
            "company_id": "comp_client",
            "name": "ClientCo Operations",
            "industry": "Consulting",
            "size": "mid_market",
            "website": "https://clientco.com",
            "address": "2 Business Ave, New York, NY",
            "phone": "+1-555-1000",
            "tags": ["consulting"],
            "annual_revenue": "25M-50M",
            "customer_since": "2019-07-01",
            "account_manager": "ct_002"
        },
        {
            "company_id": "comp_old",
            "name": "OldClient Services",
            "industry": "Retail",
            "size": "small",
            "website": "https://oldclient.com",
            "address": "3 Main St, Springfield, IL",
            "phone": "+1-555-3000",
            "tags": ["retail"],
            "annual_revenue": "5M-10M",
            "customer_since": "2016-11-20",
            "account_manager": "ct_005"
        }
    ]
    with open("data/companies.json", "w") as f:
        json.dump({"companies": companies}, f, indent=2)

    # ---------- contacts ----------
    contacts = [
        # 正确目标：company=TechCorp, job_title in [CTO,VP Engineering], folder=inactive
        {
            "contact_id": "c001",
            "first_name": "Alice",
            "last_name": "Johnson",
            "full_name": "Alice Johnson",
            "email": "alice.johnson@techcorp.com",
            "phone": "+1-555-0101",
            "company_id": "comp_tech",
            "job_title": "CTO",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "inactive",
            "tags": ["industry:technology"]
        },
        {
            "contact_id": "c002",
            "first_name": "Bob",
            "last_name": "Smith",
            "full_name": "Bob Smith",
            "email": "bob.smith@techcorp.com",
            "phone": "+1-555-0102",
            "company_id": "comp_tech",
            "job_title": "VP Engineering",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "inactive",
            "tags": ["industry:technology"]
        },
        {
            "contact_id": "c008",
            "first_name": "Henry",
            "last_name": "Taylor",
            "full_name": "Henry Taylor",
            "email": "henry.t@techcorp.com",
            "phone": "+1-555-0108",
            "company_id": "comp_tech",
            "job_title": "VP Engineering",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "inactive",
            "tags": ["industry:technology"]
        },
        # 干扰项：已经是business或有VIP标签或职位/公司不符
        {
            "contact_id": "c003",
            "first_name": "Carol",
            "last_name": "Williams",
            "full_name": "Carol Williams",
            "email": "carol.w@techcorp.com",
            "phone": "+1-555-0103",
            "company_id": "comp_tech",
            "job_title": "CTO",
            "department": "Leadership",
            "contact_type": "business",
            "folder": "business",
            "tags": ["VIP", "industry:technology"]
        },
        {
            "contact_id": "c004",
            "first_name": "David",
            "last_name": "Brown",
            "full_name": "David Brown",
            "email": "david.brown@techcorp.com",
            "phone": "+1-555-0104",
            "company_id": "comp_tech",
            "job_title": "IT Manager",
            "department": "IT",
            "contact_type": "business",
            "folder": "inactive",
            "tags": []
        },
        {
            "contact_id": "c005",
            "first_name": "Emma",
            "last_name": "Davis",
            "full_name": "Emma Davis",
            "email": "emma.davis@clientco.com",
            "phone": "+1-555-0105",
            "company_id": "comp_client",
            "job_title": "CTO",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "inactive",
            "tags": []
        },
        {
            "contact_id": "c006",
            "first_name": "Frank",
            "last_name": "Miller",
            "full_name": "Frank Miller",
            "email": "frank.m@techcorp.com",
            "phone": "+1-555-0106",
            "company_id": "comp_tech",
            "job_title": "VP Engineering",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "business",
            "tags": ["industry:technology"]
        },
        {
            "contact_id": "c007",
            "first_name": "Grace",
            "last_name": "Wilson",
            "full_name": "Grace Wilson",
            "email": "grace.wilson@techcorp.com",
            "phone": "+1-555-0107",
            "company_id": "comp_tech",
            "job_title": "CTO",
            "department": "Leadership",
            "contact_type": "business",
            "folder": "inactive",
            "tags": ["industry:technology", "VIP"]
        }
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ---------- accounts (干扰) ----------
    accounts = [
        {
            "account_id": "act_001",
            "display_name": "TechCorp Admin",
            "email": "admin@techcorp.com",
            "default_tag_color": "#3498DB",
            "auto_tagging_enabled": True,
            "birthday_reminders_enabled": True,
            "reminder_days_before": 3,
            "available_folders": ["business", "personal", "archive", "inactive"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # ---------- reminders (空，干扰) ----------
    with open("data/reminders/reminders.json", "w") as f:
        json.dump({"reminders": []}, f, indent=2)

if __name__ == "__main__":
    build_env()
