import json
import os
from datetime import datetime, timedelta

def build_env():
    # 创建目录
    os.makedirs("data/reminders", exist_ok=True)
    os.makedirs("data/tags", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # 公司数据
    companies = [
        {"company_id": "comp_001", "name": "ClientCo Operations", "industry": "Technology", "size": "enterprise", "tags": []},
        {"company_id": "comp_002", "name": "TechCorp Industries", "industry": "Technology", "size": "mid_market", "tags": []},
        {"company_id": "comp_003", "name": "Global Partners LLC", "industry": "Consulting", "size": "small", "tags": []}
    ]
    with open("data/companies.json", "w") as f:
        json.dump(companies, f, indent=2)

    # 联系人数据 (包含干扰: inactive, 其他公司, 无生日)
    contacts = [
        {"contact_id": "ct_001", "first_name": "Alice", "last_name": "Johnson", "full_name": "Alice Johnson", "email": "alice@clientco.com", "company_id": "comp_001", "folder": "business", "tags": []},
        {"contact_id": "ct_002", "first_name": "Bob", "last_name": "Smith", "full_name": "Bob Smith", "email": "bob@clientco.com", "company_id": "comp_001", "folder": "inactive", "tags": []},
        {"contact_id": "ct_003", "first_name": "Carol", "last_name": "Williams", "full_name": "Carol Williams", "email": "carol@techcorp.com", "company_id": "comp_002", "folder": "business", "tags": []},
        {"contact_id": "ct_004", "first_name": "David", "last_name": "Brown", "full_name": "David Brown", "email": "david@clientco.com", "company_id": "comp_001", "folder": "business", "tags": []},
        {"contact_id": "ct_005", "first_name": "Emma", "last_name": "Davis", "full_name": "Emma Davis", "email": "emma@clientco.com", "company_id": "comp_001", "folder": "business", "tags": []},
        {"contact_id": "ct_006", "first_name": "Frank", "last_name": "Miller", "full_name": "Frank Miller", "email": "frank@globalpartners.com", "company_id": "comp_003", "folder": "business", "tags": []},
        {"contact_id": "ct_007", "first_name": "Grace", "last_name": "Wilson", "full_name": "Grace Wilson", "email": "grace@clientco.com", "company_id": "comp_001", "folder": "business", "tags": []},
        {"contact_id": "ct_008", "first_name": "Henry", "last_name": "Taylor", "full_name": "Henry Taylor", "email": "henry@techcorp.com", "company_id": "comp_002", "folder": "personal", "tags": []}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 生日数据 (包含干扰: 不存在的联系人ID)
    birthdays = {
        "ct_001": "2025-06-15",
        "ct_004": "2025-12-20",
        "ct_005": "2025-03-10",
        "ct_007": "2025-09-25",
        "ct_009": "2025-11-01"  # 该联系人不存在
    }
    with open("data/birthdays.json", "w") as f:
        json.dump(birthdays, f, indent=2)

    # 已有提醒 (包含干扰: 非生日类型, 以及生日提醒)
    reminders = [
        {"reminder_id": "rem_001", "contact_id": "ct_005", "reminder_type": "birthday", "title": "Emma Davis's Birthday", "reminder_date": "2025-03-03", "days_before": 7, "is_recurring": True, "enabled": True},
        {"reminder_id": "rem_002", "contact_id": "ct_003", "reminder_type": "meeting", "title": "Weekly sync", "reminder_date": "2025-06-10", "days_before": 0, "is_recurring": False, "enabled": True}
    ]
    with open("data/reminders/reminders.json", "w") as f:
        json.dump(reminders, f, indent=2)

    # 额外干扰文件: 标签定义、账户、日志
    tags = [
        {"tag_id": "tag_001", "name": "vip", "color": "#FFD700", "description": "VIP客户", "category": "priority"},
        {"tag_id": "tag_002", "name": "inactive", "color": "#808080", "description": "已归档", "category": "status"}
    ]
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump(tags, f, indent=2)

    accounts = [
        {"account_id": "acct_001", "display_name": "Admin", "email": "admin@crm.local", "default_tag_color": "#0000FF", "auto_tagging_enabled": True, "birthday_reminders_enabled": True, "reminder_days_before": 7, "available_folders": ["business", "personal", "archive", "inactive"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 日志文件干扰
    with open("logs/old_access.log", "w") as f:
        f.write("2025-05-01 12:00:00 [INFO] Agent started\n")
        f.write("2025-05-01 12:01:00 [ERROR] Connection timeout\n")

if __name__ == "__main__":
    build_env()
