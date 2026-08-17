import json
import os

def build_env():
    # ---- accounts.json ----
    accounts = {
        "accounts": [
            {"account_id": "ct_001", "display_name": "Alice Johnson", "email": "alice@techcorp.com",
             "default_tag_color": "#3498db", "auto_tagging_enabled": True, "birthday_reminders_enabled": False,
             "reminder_days_before": 3, "available_folders": ["business", "inactive", "personal"]},
            {"account_id": "ct_002", "display_name": "Bob Smith", "email": "bob@clientco.com",
             "default_tag_color": "#e74c3c", "auto_tagging_enabled": True, "birthday_reminders_enabled": True,
             "reminder_days_before": 5, "available_folders": ["business", "inactive", "personal"]},
        ]
    }
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ---- companies.json ----
    companies = {
        "companies": [
            {"company_id": "comp_001", "name": "TechCorp Industries", "industry": "Technology", "size": "enterprise",
             "website": "https://techcorp.com", "address": "1 Tech Lane, SV", "phone": "+1-555-5000",
             "tags": ["tag_industry_tech"], "annual_revenue": "100M+", "customer_since": "2019-03-01", "account_manager": "ct_001"},
            {"company_id": "comp_002", "name": "ClientCo Operations", "industry": "Consulting", "size": "mid_market",
             "website": "https://clientco.com", "address": "100 Client St, NY", "phone": "+1-555-1000",
             "tags": ["tag_industry_consulting"], "annual_revenue": "25M-50M", "customer_since": "2020-07-15", "account_manager": "ct_002"},
            {"company_id": "comp_003", "name": "Global Partners LLC", "industry": "Logistics", "size": "small",
             "website": "https://globalpartners.com", "address": "50 Global Ave, LA", "phone": "+1-555-2000",
             "tags": ["tag_industry_logistics"], "annual_revenue": "5M-10M", "customer_since": "2021-11-01", "account_manager": "ct_001"},
            {"company_id": "comp_004", "name": "OldClient Services", "industry": "Retail", "size": "mid_market",
             "website": "https://oldclient.com", "address": "22 Old Rd, Chicago", "phone": "+1-555-3000",
             "tags": ["tag_industry_retail"], "annual_revenue": "1M-5M", "customer_since": "2018-02-20", "account_manager": "ct_003"},
            {"company_id": "comp_005", "name": "StartupIO", "industry": "Technology", "size": "small",
             "website": "https://startup.io", "address": "99 Innovation Dr, SF", "phone": "+1-555-4000",
             "tags": ["tag_industry_tech"], "annual_revenue": "5M-10M", "customer_since": "2023-01-10", "account_manager": "ct_005"},
            {"company_id": "comp_006", "name": "VendorCo Supplies", "industry": "Manufacturing", "size": "enterprise",
             "website": "https://vendorco.com", "address": "77 Factory Rd, Detroit", "phone": "+1-555-6000",
             "tags": ["tag_industry_manufacturing"], "annual_revenue": "100M+", "customer_since": "2017-06-05", "account_manager": "ct_007"},
        ]
    }
    with open("data/companies.json", "w") as f:
        json.dump(companies, f, indent=2)

    # ---- contacts.json ----   (干扰项: 重复email、部分已有vendor标签、非VendorCo公司也带vendor标签)
    contacts = {
        "contacts": [
            {"contact_id": "c001", "first_name": "Alice", "last_name": "Johnson", "full_name": "Alice Johnson",
             "email": "alice.johnson@techcorp.com", "phone": "+1-555-0101", "company_id": "comp_001",
             "job_title": "CTO", "department": "Engineering", "contact_type": "business", "folder": "business", "tags": []},
            {"contact_id": "c002", "first_name": "Bob", "last_name": "Smith", "full_name": "Bob Smith",
             "email": "bob.smith@clientco.com", "phone": "+1-555-0102", "company_id": "comp_002",
             "job_title": "CEO", "department": "Leadership", "contact_type": "business", "folder": "business", "tags": ["tag_priority_vip"]},
            {"contact_id": "c003", "first_name": "Carol", "last_name": "Williams", "full_name": "Carol Williams",
             "email": "carol.w@startup.io", "phone": "+1-555-0103", "company_id": "comp_005",
             "job_title": "VP Engineering", "department": "Engineering", "contact_type": "business", "folder": "business", "tags": []},
            # VendorCo 员工 - 部分已打vendor标签
            {"contact_id": "c004", "first_name": "David", "last_name": "Brown", "full_name": "David Brown",
             "email": "david.brown@vendor.co", "phone": "+1-555-0104", "company_id": "comp_006",
             "job_title": "IT Manager", "department": "IT", "contact_type": "business", "folder": "business", "tags": ["tag_vendor_001"]},
            {"contact_id": "c005", "first_name": "Emma", "last_name": "Davis", "full_name": "Emma Davis",
             "email": "emma.davis@vendor.co", "phone": "+1-555-0105", "company_id": "comp_006",
             "job_title": "Procurement Manager", "department": "Operations", "contact_type": "business", "folder": "business", "tags": []},
            {"contact_id": "c006", "first_name": "Frank", "last_name": "Miller", "full_name": "Frank Miller",
             "email": "frank.m@oldclient.com", "phone": "+1-555-0106", "company_id": "comp_004",
             "job_title": "Account Manager", "department": "Sales", "contact_type": "business", "folder": "inactive", "tags": ["tag_vendor_001"]},  # 干扰: 非vendorco但有vendor标签
            {"contact_id": "c007", "first_name": "Grace", "last_name": "Wilson", "full_name": "Grace Wilson",
             "email": "grace.wilson@vendor.co", "phone": "+1-555-0107", "company_id": "comp_006",
             "job_title": "CEO", "department": "Leadership", "contact_type": "business", "folder": "business", "tags": []},
            {"contact_id": "c008", "first_name": "Henry", "last_name": "Taylor", "full_name": "Henry Taylor",
             "email": "henry.t@bigcorp.com", "phone": "+1-555-0108", "company_id": "comp_006",
             "job_title": "VP Engineering", "department": "Engineering", "contact_type": "personal", "folder": "personal", "tags": ["tag_friend"]},  # 无vendor标签
            {"contact_id": "c009", "first_name": "Ivy", "last_name": "Clark", "full_name": "Ivy Clark",
             "email": "ivy.clark@vendor.co", "phone": "+1-555-0109", "company_id": "comp_006",
             "job_title": "Procurement Manager", "department": "Operations", "contact_type": "business", "folder": "business", "tags": []},
            {"contact_id": "c010", "first_name": "Jack", "last_name": "Lee", "full_name": "Jack Lee",
             "email": "jack.lee@vendor.co", "phone": "+1-555-0110", "company_id": "comp_006",
             "job_title": "IT Support", "department": "IT", "contact_type": "business", "folder": "business", "tags": ["tag_vendor_001"]},  # 已有
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ---- tags/tag_definitions.json ----
    os.makedirs("data/tags", exist_ok=True)
    tag_defs = {
        "tag_definitions": [
            {"tag_id": "tag_industry_tech", "name": "technology", "color": "#3498db", "description": "Tech industry tag", "category": "industry"},
            {"tag_id": "tag_industry_consulting", "name": "consulting", "color": "#2ecc71", "description": "Consulting industry", "category": "industry"},
            {"tag_id": "tag_industry_logistics", "name": "logistics", "color": "#f1c40f", "description": "Logistics industry", "category": "industry"},
            {"tag_id": "tag_industry_retail", "name": "retail", "color": "#9b59b6", "description": "Retail industry", "category": "industry"},
            {"tag_id": "tag_industry_manufacturing", "name": "manufacturing", "color": "#e67e22", "description": "Manufacturing industry", "category": "industry"},
            {"tag_id": "tag_priority_vip", "name": "vip", "color": "#e74c3c", "description": "VIP customer", "category": "priority"},
            {"tag_id": "tag_vendor_001", "name": "vendor", "color": "#1abc9c", "description": "Vendor partner contact", "category": "relationship"},
            {"tag_id": "tag_friend", "name": "friend", "color": "#95a5a6", "description": "Personal friend", "category": "personal"},
        ]
    }
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump(tag_defs, f, indent=2)

    # ---- 空目录 ops/ 用于放置输出 ----
    os.makedirs("ops", exist_ok=True)

    # ---- 干扰文件：日志、旧备份等 ----
    os.makedirs("log", exist_ok=True)
    with open("log/backup.log", "w") as f:
        f.write("No errors\n")
    os.makedirs("old_data", exist_ok=True)
    with open("old_data/contacts_backup.json", "w") as f:
        json.dump({"old_contacts": []}, f)

    # ---- reminders 目录留空防止查错顺序----
    os.makedirs("data/reminders", exist_ok=True)
    with open("data/reminders/reminders.json", "w") as f:
        json.dump({"reminders": []}, f)

if __name__ == "__main__":
    build_env()
