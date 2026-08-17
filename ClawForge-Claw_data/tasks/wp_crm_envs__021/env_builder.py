import os
import json
import random

def build_env():
    # 确保 cwd 已是 
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 空目录，供 agent 写入
    os.makedirs("data/reminders", exist_ok=True)
    os.makedirs("data/tags", exist_ok=True)  # 干扰项

    # ----- contacts.json (干扰：个人、格式错误、缺失生日) -----
    contacts = [
        # business 联系人 - 有效的
        {
            "contact_id": "ct_001",
            "first_name": "Alice",
            "last_name": "Johnson",
            "full_name": "Alice Johnson",
            "email": "alice.johnson@techcorp.com",
            "phone": "+1-555-0101",
            "company_id": "comp_001",
            "job_title": "VP Engineering",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "business",
            "tags": ["vip", "tech"],
            "birthday": "2025-12-25"   # 有效，但已有提醒
        },
        {
            "contact_id": "ct_002",
            "first_name": "Bob",
            "last_name": "Smith",
            "full_name": "Bob Smith",
            "email": "bob.smith@clientco.com",
            "phone": "+1-555-0102",
            "company_id": "comp_002",
            "job_title": "CEO",
            "department": "Leadership",
            "contact_type": "business",
            "folder": "business",
            "tags": ["executive"],
            "birthday": "2025-11-15"   # 有效，无提醒 → 唯一答案
        },
        # business 联系人 - 生日缺失
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
            "tags": ["startup"],
            # 没有 birthday 字段
        },
        # business 联系人 - 生日格式错误
        {
            "contact_id": "ct_004",
            "first_name": "David",
            "last_name": "Brown",
            "full_name": "David Brown",
            "email": "david.brown@email.com",
            "phone": "+1-555-0104",
            "company_id": "comp_004",
            "job_title": "IT Manager",
            "department": "IT",
            "contact_type": "business",
            "folder": "business",
            "tags": [],
            "birthday": "1990/01/01"   # 格式错误
        },
        # personal 联系人 - 有效生日但不属于 business
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
            "contact_type": "personal",
            "folder": "personal",
            "tags": ["friend"],
            "birthday": "2025-10-01"
        },
        # personal 联系人 - 无效生日
        {
            "contact_id": "ct_006",
            "first_name": "Frank",
            "last_name": "Miller",
            "full_name": "Frank Miller",
            "email": "frank.m@oldclient.com",
            "phone": "+1-555-0106",
            "company_id": "comp_006",
            "job_title": "Account Manager",
            "department": "Sales",
            "contact_type": "personal",
            "folder": "personal",
            "tags": ["old"],
            "birthday": "unknown"
        },
        # 干扰：重复的 business 联系人（已存在但生日不同，且已有提醒）
        {
            "contact_id": "ct_001",   # 重复ID，但实际是同一个
            "first_name": "Alice",    # 重复，仅用于干扰
            "last_name": "Johnson",
            "full_name": "Alice Johnson",
            "email": "alice.johnson@techcorp.com",
            "phone": "+1-555-0101",
            "company_id": "comp_001",
            "job_title": "VP Engineering",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "business",
            "tags": ["vip", "tech"],
            "birthday": "2025-12-25"   # 与第一个相同
        },
        # 干扰：personal 联系人，生日格式正确但不应入选
        {
            "contact_id": "ct_007",
            "first_name": "Grace",
            "last_name": "Wilson",
            "full_name": "Grace Wilson",
            "email": "grace.wilson@vendor.co",
            "phone": "+1-555-0107",
            "company_id": "comp_007",
            "job_title": "Procurement Manager",
            "department": "Operations",
            "contact_type": "personal",
            "folder": "personal",
            "tags": [],
            "birthday": "2025-09-20"
        }
    ]

    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ----- reminders/reminders.json (已有提醒) -----
    reminders = [
        {
            "reminder_id": "rem_001",
            "contact_id": "ct_001",
            "reminder_type": "birthday",
            "title": "Alice Johnson's Birthday",
            "description": "Birthday reminder for Alice Johnson",
            "reminder_date": "2025-12-25",
            "days_before": 3,
            "is_recurring": True,
            "enabled": True
        },
        # 干扰：另一个 contact 的生日提醒（personal）
        {
            "reminder_id": "rem_002",
            "contact_id": "ct_005",
            "reminder_type": "birthday",
            "title": "Emma Davis's Birthday",
            "description": "Birthday reminder for Emma Davis",
            "reminder_date": "2025-10-01",
            "days_before": 3,
            "is_recurring": True,
            "enabled": True
        }
    ]
    with open("data/reminders/reminders.json", "w") as f:
        json.dump(reminders, f, indent=2)

    # ----- 干扰：tags 目录（无关紧要）-----
    tag_defs = [
        {"tag_id": "tag_vip", "name": "VIP", "color": "#FFD700", "description": "Very important person", "category": "priority"},
        {"tag_id": "tag_exec", "name": "Executive", "color": "#FF5733", "description": "C-level", "category": "role"}
    ]
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump(tag_defs, f, indent=2)

    # ----- 干扰：accounts.json / companies.json（仅目录，可选）-----
    accounts = [
        {"account_id": "acc_001", "display_name": "TechCorp Industries", "email": "admin@techcorp.com",
         "default_tag_color": "#3498db", "auto_tagging_enabled": True, "birthday_reminders_enabled": True,
         "reminder_days_before": 3, "available_folders": ["business","personal","archive","inactive"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    companies = [
        {"company_id": "comp_001", "name": "TechCorp Industries", "industry": "Technology",
         "size": "enterprise", "website": "https://techcorp.com", "address": "1 Tech Plaza",
         "phone": "+1-555-1000", "tags": ["tech"], "annual_revenue": "100M+", "customer_since": "2020-01-01",
         "account_manager": "ct_001"}
    ]
    with open("data/companies.json", "w") as f:
        json.dump({"companies": companies}, f, indent=2)

if __name__ == "__main__":
    build_env()
