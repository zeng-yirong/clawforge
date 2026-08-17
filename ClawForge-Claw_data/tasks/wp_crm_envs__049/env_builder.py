import json
import os
from datetime import date, timedelta

def build_env():
    # 当前日期固定为2025-07-15
    # 创建目录结构
    dirs = ["data", "data/reminders", "data/tags", "db_dumps", "ops"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # ---------- 联系人和公司基础数据 ----------
    accounts = [
        {"account_id": "acc_001", "display_name": "Main", "email": "admin@crm.com",
         "default_tag_color": "#3366FF", "auto_tagging_enabled": True,
         "birthday_reminders_enabled": True, "reminder_days_before": 3,
         "available_folders": ["business", "personal", "archive", "inactive"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    companies = [
        {"company_id": "comp_001", "name": "TechCorp Industries", "industry": "Technology", "size": "enterprise",
         "website": "https://techcorp.com", "address": "1 Tech Dr", "phone": "+1-555-5000",
         "tags": ["tech", "enterprise"], "annual_revenue": "100M+", "customer_since": "2019-03-01",
         "account_manager": "ct_001"},
        {"company_id": "comp_002", "name": "ClientCo Operations", "industry": "Consulting", "size": "mid_market",
         "website": "https://clientco.com", "address": "2 Client Ln", "phone": "+1-555-1000",
         "tags": ["consulting"], "annual_revenue": "5M-10M", "customer_since": "2020-07-12",
         "account_manager": "ct_002"},
        {"company_id": "comp_003", "name": "StartupIO", "industry": "Technology", "size": "small",
         "website": "https://startup.io", "address": "3 Startup Ave", "phone": "+1-555-4000",
         "tags": ["startup", "tech"], "annual_revenue": "1M-5M", "customer_since": "2022-11-01",
         "account_manager": "ct_003"},
        {"company_id": "comp_004", "name": "Global Partners LLC", "industry": "Logistics", "size": "enterprise",
         "website": "https://globalpartners.com", "address": "4 Global Blvd", "phone": "+1-555-2000",
         "tags": ["logistics"], "annual_revenue": "25M-50M", "customer_since": "2018-05-20",
         "account_manager": "ct_005"},
        {"company_id": "comp_005", "name": "OldClient Services", "industry": "Retail", "size": "mid_market",
         "website": "https://oldclient.com", "address": "5 Old St", "phone": "+1-555-3000",
         "tags": ["retail", "inactive"], "annual_revenue": "5M-10M", "customer_since": "2015-09-30",
         "account_manager": "ct_007"},
        {"company_id": "comp_006", "name": "VendorCo Supplies", "industry": "Manufacturing", "size": "small",
         "website": "https://vendorco.com", "address": "6 Vendor Rd", "phone": "+1-555-6000",
         "tags": ["vendor"], "annual_revenue": "1M-5M", "customer_since": "2021-02-14",
         "account_manager": "ct_003"}
    ]
    with open("data/companies.json", "w") as f:
        json.dump({"companies": companies}, f)

    # 联系人：8个，生日分布在7月15日前后
    contacts = [
        {"contact_id": "ct_001", "first_name": "Alice", "last_name": "Johnson", "full_name": "Alice Johnson",
         "email": "alice.johnson@techcorp.com", "phone": "+1-555-0101", "company_id": "comp_001",
         "job_title": "VP Engineering", "department": "Engineering", "contact_type": "business",
         "folder": "business", "tags": ["vip", "tech"]},
        {"contact_id": "ct_002", "first_name": "Bob", "last_name": "Smith", "full_name": "Bob Smith",
         "email": "bob.smith@clientco.com", "phone": "+1-555-0102", "company_id": "comp_002",
         "job_title": "Account Manager", "department": "Sales", "contact_type": "business",
         "folder": "business", "tags": ["manager"]},
        {"contact_id": "ct_003", "first_name": "Carol", "last_name": "Williams", "full_name": "Carol Williams",
         "email": "carol.w@startup.io", "phone": "+1-555-0103", "company_id": "comp_003",
         "job_title": "CEO", "department": "Leadership", "contact_type": "business",
         "folder": "business", "tags": ["ceo"]},
        {"contact_id": "ct_004", "first_name": "David", "last_name": "Brown", "full_name": "David Brown",
         "email": "david.brown@email.com", "phone": "+1-555-0104", "company_id": "comp_004",
         "job_title": "IT Manager", "department": "IT", "contact_type": "business",
         "folder": "business", "tags": ["it"]},
        {"contact_id": "ct_005", "first_name": "Emma", "last_name": "Davis", "full_name": "Emma Davis",
         "email": "emma.davis@partner.net", "phone": "+1-555-0105", "company_id": "comp_005",
         "job_title": "Partnership Director", "department": "Business Development", "contact_type": "business",
         "folder": "business", "tags": ["partner"]},
        {"contact_id": "ct_006", "first_name": "Frank", "last_name": "Miller", "full_name": "Frank Miller",
         "email": "frank.m@oldclient.com", "phone": "+1-555-0106", "company_id": "comp_005",
         "job_title": "Procurement Manager", "department": "Operations", "contact_type": "business",
         "folder": "inactive", "tags": ["old", "inactive"]},
        {"contact_id": "ct_007", "first_name": "Grace", "last_name": "Wilson", "full_name": "Grace Wilson",
         "email": "grace.wilson@vendor.co", "phone": "+1-555-0107", "company_id": "comp_006",
         "job_title": "CEO", "department": "Leadership", "contact_type": "business",
         "folder": "business", "tags": ["ceo", "vendor"]},
        {"contact_id": "ct_008", "first_name": "Henry", "last_name": "Taylor", "full_name": "Henry Taylor",
         "email": "henry.t@bigcorp.com", "phone": "+1-555-0108", "company_id": "comp_001",
         "job_title": "CTO", "department": "Engineering", "contact_type": "personal",
         "folder": "personal", "tags": ["friend"]}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

    # ---------- 生日提醒 ----------
    # 生日日期：ct_001 Alice -> 7月18日 (未来3天)
    #           ct_002 Bob -> 7月20日 (未来5天)
    #           ct_003 Carol -> 7月22日 (未来7天)
    #           ct_004 David -> 7月10日 (已过)
    #           ct_005 Emma -> 8月1日 (远)
    #           ct_006 Frank -> 7月14日 (昨天)
    #           ct_007 Grace -> 12月25日 (远)
    #           ct_008 Henry -> 7月16日 (未来1天)
    # 注意：有些提醒可能已禁用或者不存在
    reminders = [
        {"reminder_id": "rem_001", "contact_id": "ct_001", "reminder_type": "birthday",
         "title": "Alice Johnson's Birthday", "description": "Birthday reminder for Alice Johnson",
         "reminder_date": "2025-07-18", "days_before": 1, "is_recurring": True, "enabled": True},
        {"reminder_id": "rem_002", "contact_id": "ct_002", "reminder_type": "birthday",
         "title": "Bob Smith's Birthday", "description": "Birthday reminder for Bob Smith",
         "reminder_date": "2025-07-20", "days_before": 1, "is_recurring": True, "enabled": False},  # 禁用
        # ct_003 没有提醒 (干扰项，但生日在7月22日，在7天内)
        {"reminder_id": "rem_003", "contact_id": "ct_004", "reminder_type": "birthday",
         "title": "David Brown's Birthday", "description": "Birthday reminder for David Brown",
         "reminder_date": "2025-07-10", "days_before": 1, "is_recurring": True, "enabled": True},  # 已过
        {"reminder_id": "rem_004", "contact_id": "ct_005", "reminder_type": "birthday",
         "title": "Emma Davis's Birthday", "description": "Birthday reminder for Emma Davis",
         "reminder_date": "2025-08-01", "days_before": 1, "is_recurring": True, "enabled": True},
        {"reminder_id": "rem_005", "contact_id": "ct_006", "reminder_type": "birthday",
         "title": "Frank Miller's Birthday", "description": "Birthday reminder for Frank Miller",
         "reminder_date": "2025-07-14", "days_before": 1, "is_recurring": True, "enabled": True},
        {"reminder_id": "rem_006", "contact_id": "ct_007", "reminder_type": "birthday",
         "title": "Grace Wilson's Birthday", "description": "Birthday reminder for Grace Wilson",
         "reminder_date": "2025-12-25", "days_before": 1, "is_recurring": True, "enabled": True},
        # ct_008 Henry 提醒已存在但被禁用
        {"reminder_id": "rem_007", "contact_id": "ct_008", "reminder_type": "birthday",
         "title": "Henry Taylor's Birthday", "description": "Birthday reminder for Henry Taylor",
         "reminder_date": "2025-07-16", "days_before": 1, "is_recurring": True, "enabled": False}
    ]
    with open("data/reminders/reminders.json", "w") as f:
        json.dump({"reminders": reminders}, f)

    # ---------- 标签定义 ----------
    # 已经有一个"birthday"标签（干扰），但没有"birthday-reminder"
    tag_defs = [
        {"tag_id": "tag_001", "name": "vip", "color": "#FFD700", "description": "Very important person", "category": "priority"},
        {"tag_id": "tag_002", "name": "tech", "color": "#00BFFF", "description": "Technology related", "category": "industry"},
        {"tag_id": "tag_003", "name": "manager", "color": "#32CD32", "description": "Manager role", "category": "role"},
        {"tag_id": "tag_004", "name": "ceo", "color": "#FF4500", "description": "CEO", "category": "role"},
        {"tag_id": "tag_005", "name": "it", "color": "#8A2BE2", "description": "IT", "category": "role"},
        {"tag_id": "tag_006", "name": "partner", "color": "#FF69B4", "description": "Partner", "category": "relationship"},
        {"tag_id": "tag_007", "name": "old", "color": "#A9A9A9", "description": "Old contact", "category": "status"},
        {"tag_id": "tag_008", "name": "inactive", "color": "#808080", "description": "Inactive", "category": "status"},
        {"tag_id": "tag_009", "name": "vendor", "color": "#FFA500", "description": "Vendor", "category": "relationship"},
        {"tag_id": "tag_010", "name": "friend", "color": "#FFB6C1", "description": "Personal friend", "category": "personal"},
        {"tag_id": "tag_011", "name": "birthday", "color": "#FF6347", "description": "Birthday tag (old)", "category": "personal"},
        {"tag_id": "tag_012", "name": "consulting", "color": "#9370DB", "description": "Consulting industry", "category": "industry"}
    ]
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump({"tag_definitions": tag_defs}, f)

    # ---------- 其他干扰文件 ----------
    # 一个废弃的旧联系人备份
    with open("db_dumps/contacts_backup_2024.json", "w") as f:
        json.dump({"old_contacts": []}, f)
    # 一个无关的日志文件
    with open("ops/sync_log.txt", "w") as f:
        f.write("2025-07-14 23:59:59 - synced\n")

if __name__ == "__main__":
    build_env()
