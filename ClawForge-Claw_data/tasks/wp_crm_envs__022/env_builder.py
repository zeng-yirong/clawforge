import json
import os

def build_env():
    # 1. 创建 data 目录及其子目录
    os.makedirs("data/tags", exist_ok=True)
    os.makedirs("data/reminders", exist_ok=True)
    os.makedirs("output", exist_ok=True)  # 预先创建，agent 可以直接写

    # 2. 写入当前基准日期
    with open("data/current_date.txt", "w") as f:
        f.write("2024-06-15")

    # 3. 联系人数据 (8个，包含干扰)
    contacts = [
        {
            "contact_id": "ct_001",
            "first_name": "Alice",
            "last_name": "Johnson",
            "full_name": "Alice Johnson",
            "email": "alice.johnson@techcorp.com",
            "phone": "+1-555-0101",
            "company_id": "cmp_001",
            "job_title": "CEO",
            "department": "Leadership",
            "contact_type": "business",
            "folder": "business",
            "tags": ["vip"],
            "birthday": "2024-07-01"
        },
        {
            "contact_id": "ct_002",
            "first_name": "Bob",
            "last_name": "Smith",
            "full_name": "Bob Smith",
            "email": "bob.smith@clientco.com",
            "phone": "+1-555-0102",
            "company_id": "cmp_002",
            "job_title": "IT Manager",
            "department": "IT",
            "contact_type": "business",
            "folder": "inactive",
            "tags": ["old"],
            "birthday": "2024-06-10"
        },
        {
            "contact_id": "ct_003",
            "first_name": "Carol",
            "last_name": "Williams",
            "full_name": "Carol Williams",
            "email": "carol.w@startup.io",
            "phone": "+1-555-0103",
            "company_id": "cmp_003",
            "job_title": "VP Engineering",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "business",
            "tags": [],
            "birthday": "2024-06-20"
        },
        {
            "contact_id": "ct_004",
            "first_name": "David",
            "last_name": "Brown",
            "full_name": "David Brown",
            "email": "david.brown@email.com",
            "phone": "+1-555-0104",
            "company_id": "cmp_004",
            "job_title": "Account Manager",
            "department": "Sales",
            "contact_type": "personal",
            "folder": "personal",
            "tags": ["personal"],
            "birthday": "2024-08-01"
        },
        {
            "contact_id": "ct_005",
            "first_name": "Emma",
            "last_name": "Davis",
            "full_name": "Emma Davis",
            "email": "emma.davis@partner.net",
            "phone": "+1-555-0105",
            "company_id": "cmp_005",
            "job_title": "Procurement Manager",
            "department": "Operations",
            "contact_type": "business",
            "folder": "business",
            "tags": ["birthday"],
            "birthday": "2024-07-10"
        },
        {
            "contact_id": "ct_006",
            "first_name": "Frank",
            "last_name": "Miller",
            "full_name": "Frank Miller",
            "email": "frank.m@oldclient.com",
            "phone": "+1-555-0106",
            "company_id": "cmp_006",
            "job_title": "Partnership Director",
            "department": "Business Development",
            "contact_type": "business",
            "folder": "inactive",
            "tags": [],
            "birthday": "2024-06-05"
        },
        {
            "contact_id": "ct_007",
            "first_name": "Grace",
            "last_name": "Wilson",
            "full_name": "Grace Wilson",
            "email": "grace.wilson@vendor.co",
            "phone": "+1-555-0107",
            "company_id": "cmp_007",
            "job_title": "CTO",
            "department": "Leadership",
            "contact_type": "personal",
            "folder": "personal",
            "tags": ["vip"],
            "birthday": "2024-07-20"
        },
        {
            "contact_id": "ct_008",
            "first_name": "Henry",
            "last_name": "Taylor",
            "full_name": "Henry Taylor",
            "email": "henry.t@bigcorp.com",
            "phone": "+1-555-0108",
            "company_id": "cmp_008",
            "job_title": "Account Manager",
            "department": "Sales",
            "contact_type": "business",
            "folder": "business",
            "tags": [],
            "birthday": "2024-06-25"
        }
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 4. 标签定义 (包含 birthday 标签)
    tag_defs = [
        {
            "tag_id": "tg_birthday",
            "name": "birthday",
            "color": "#FF0000",
            "description": "Birthday reminder tag",
            "category": "personal"
        },
        {
            "tag_id": "tg_vip",
            "name": "vip",
            "color": "#FFD700",
            "description": "VIP customer",
            "category": "priority"
        },
        {
            "tag_id": "tg_old",
            "name": "old",
            "color": "#888888",
            "description": "Inactive contact",
            "category": "status"
        },
        {
            "tag_id": "tg_important",
            "name": "important",
            "color": "#0000FF",
            "description": "Important contact",
            "category": "priority"
        }
    ]
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump(tag_defs, f, indent=2)

    # 5. 现有提醒 (仅 Alice 和 Bob 的生日提醒)
    reminders = [
        {
            "reminder_id": "rm_001",
            "contact_id": "ct_001",
            "reminder_type": "birthday",
            "title": "Alice Johnson's Birthday",
            "description": "Birthday reminder for Alice Johnson",
            "reminder_date": "2024-07-01",
            "days_before": 1,
            "is_recurring": True,
            "enabled": True
        },
        {
            "reminder_id": "rm_002",
            "contact_id": "ct_002",
            "reminder_type": "birthday",
            "title": "Bob Smith's Birthday",
            "description": "Birthday reminder for Bob Smith",
            "reminder_date": "2024-06-10",
            "days_before": 1,
            "is_recurring": True,
            "enabled": True
        }
    ]
    with open("data/reminders/reminders.json", "w") as f:
        json.dump(reminders, f, indent=2)

    # 6. 额外干扰文件：一个旧版 contacts 副本，里面包含已经过时的数据
    os.makedirs("backups", exist_ok=True)
    old_contacts = [
        {"contact_id": "ct_001", "full_name": "Alice Johnson", "folder": "business", "birthday": "2023-07-01", "tags": []}
    ]
    with open("backups/contacts_backup_2023.json", "w") as f:
        json.dump(old_contacts, f)

if __name__ == "__main__":
    build_env()
