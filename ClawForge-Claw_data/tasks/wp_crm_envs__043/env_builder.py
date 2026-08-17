import json, os, random

def build_env():
    # 构建数据目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/tags", exist_ok=True)
    os.makedirs("data/reminders", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 干扰目录

    # 公司数据 (6家)
    companies = [
        {"company_id": "c001", "name": "TechCorp Industries", "industry": "Technology", "size": "enterprise", "website": "https://techcorp.com", "address": "1 Tech Blvd, SV", "phone": "+1-555-1000", "tags": [], "annual_revenue": "100M+", "customer_since": "2018-01-01", "account_manager": "ct_001"},
        {"company_id": "c002", "name": "ClientCo Operations", "industry": "Consulting", "size": "mid_market", "website": "https://clientco.com", "address": "2 Client St, NY", "phone": "+1-555-2000", "tags": [], "annual_revenue": "25M-50M", "customer_since": "2019-03-15", "account_manager": "ct_002"},
        {"company_id": "c003", "name": "StartupIO", "industry": "Technology", "size": "small", "website": "https://startup.io", "address": "3 Startup Ave, SF", "phone": "+1-555-3000", "tags": [], "annual_revenue": "1M-5M", "customer_since": "2021-07-01", "account_manager": "ct_003"},
        {"company_id": "c004", "name": "Global Partners LLC", "industry": "Logistics", "size": "enterprise", "website": "https://globalpartners.com", "address": "4 Global Rd, LA", "phone": "+1-555-4000", "tags": [], "annual_revenue": "50M-100M", "customer_since": "2017-11-20", "account_manager": "ct_005"},
        {"company_id": "c005", "name": "OldClient Services", "industry": "Consulting", "size": "mid_market", "website": "https://oldclient.com", "address": "5 Old Town, CHI", "phone": "+1-555-5000", "tags": [], "annual_revenue": "5M-10M", "customer_since": "2015-06-30", "account_manager": "ct_007"},
        {"company_id": "c006", "name": "VendorCo Supplies", "industry": "Manufacturing", "size": "small", "website": "https://vendorco.com", "address": "6 Vendor Ln, DFW", "phone": "+1-555-6000", "tags": [], "annual_revenue": "10M-25M", "customer_since": "2020-02-14", "account_manager": "ct_001"},
    ]
    with open("data/companies.json", "w") as f:
        json.dump({"companies": companies}, f, indent=2)

    # 联系人数据 (8个，其中5个有行业标签，3个没有；2个公司ID无效作为干扰)
    contacts = [
        {"contact_id": "ct_101", "first_name": "Alice", "last_name": "Johnson", "full_name": "Alice Johnson", "email": "alice.johnson@techcorp.com", "phone": "+1-555-0101", "company_id": "c001", "job_title": "CTO", "department": "Engineering", "contact_type": "business", "folder": "business", "tags": ["Technology"]},  # 已有行业标签
        {"contact_id": "ct_102", "first_name": "Bob", "last_name": "Smith", "full_name": "Bob Smith", "email": "bob.smith@clientco.com", "phone": "+1-555-0102", "company_id": "c002", "job_title": "CEO", "department": "Leadership", "contact_type": "business", "folder": "business", "tags": []},  # 需要添加 Consulting
        {"contact_id": "ct_103", "first_name": "Carol", "last_name": "Williams", "full_name": "Carol Williams", "email": "carol.w@startup.io", "phone": "+1-555-0103", "company_id": "c003", "job_title": "VP Engineering", "department": "Engineering", "contact_type": "business", "folder": "business", "tags": ["Technology"]},  # 已有行业标签
        {"contact_id": "ct_104", "first_name": "David", "last_name": "Brown", "full_name": "David Brown", "email": "david.brown@email.com", "phone": "+1-555-0104", "company_id": "c004", "job_title": "Partnership Director", "department": "Business Development", "contact_type": "business", "folder": "business", "tags": []},  # 需要添加 Logistics
        {"contact_id": "ct_105", "first_name": "Emma", "last_name": "Davis", "full_name": "Emma Davis", "email": "emma.davis@partner.net", "phone": "+1-555-0105", "company_id": "c005", "job_title": "Account Manager", "department": "Sales", "contact_type": "business", "folder": "business", "tags": ["Consulting", "priority"]},  # 已有行业标签(Consulting) + 额外标签
        {"contact_id": "ct_106", "first_name": "Frank", "last_name": "Miller", "full_name": "Frank Miller", "email": "frank.m@oldclient.com", "phone": "+1-555-0106", "company_id": "c005", "job_title": "IT Manager", "department": "IT", "contact_type": "business", "folder": "inactive", "tags": []},  # 需要添加 Consulting (与ct_105同一公司)
        {"contact_id": "ct_107", "first_name": "Grace", "last_name": "Wilson", "full_name": "Grace Wilson", "email": "grace.wilson@vendor.co", "phone": "+1-555-0107", "company_id": "c006", "job_title": "Procurement Manager", "department": "Operations", "contact_type": "business", "folder": "personal", "tags": []},  # 需要添加 Manufacturing
        {"contact_id": "ct_108", "first_name": "Henry", "last_name": "Taylor", "full_name": "Henry Taylor", "email": "henry.t@bigcorp.com", "phone": "+1-555-0108", "company_id": "c999", "job_title": "CEO", "department": "Leadership", "contact_type": "personal", "folder": "personal", "tags": []},  # 公司ID无效，跳过
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 干扰文件：tag_definitions
    tag_defs = {
        "tag_definitions": [
            {"tag_id": "t1", "name": "Technology", "color": "#1E90FF", "description": "Tech industry", "category": "industry"},
            {"tag_id": "t2", "name": "Consulting", "color": "#32CD32", "description": "Consulting industry", "category": "industry"},
            {"tag_id": "t3", "name": "Logistics", "color": "#FFA500", "description": "Logistics industry", "category": "industry"},
            {"tag_id": "t4", "name": "Manufacturing", "color": "#8A2BE2", "description": "Manufacturing industry", "category": "industry"},
            {"tag_id": "t5", "name": "priority", "color": "#FF4500", "description": "Priority contact", "category": "priority"},
        ]
    }
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump(tag_defs, f, indent=2)

    # 干扰文件：reminders 和 accounts
    reminders = {
        "reminders": [
            {"reminder_id": "r1", "contact_id": "ct_101", "reminder_type": "birthday", "title": "Alice Johnson's Birthday", "description": "", "reminder_date": "2025-04-12", "days_before": 3, "is_recurring": True, "enabled": True},
        ]
    }
    with open("data/reminders/reminders.json", "w") as f:
        json.dump(reminders, f, indent=2)

    accounts = {
        "accounts": [
            {"account_id": "a1", "display_name": "Default", "email": "admin@crm.com", "default_tag_color": "#FFFFFF", "auto_tagging_enabled": False, "birthday_reminders_enabled": True, "reminder_days_before": 5, "available_folders": ["business","personal","archive","inactive"]},
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 干扰文件：ops 目录下随便放点东西
    with open("ops/backup_20250328.json", "w") as f:
        json.dump({"dummy": True}, f)

if __name__ == "__main__":
    build_env()
