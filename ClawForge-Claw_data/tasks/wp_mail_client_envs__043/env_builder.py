import os
import json
from datetime import datetime, timedelta

def build_env():
    # 创建目录结构
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("data/backups", exist_ok=True)
    
    # 账户信息（仅一个账户）
    accounts = [{
        "account_id": "acc_001",
        "display_name": "Work Account",
        "email_address": "me@company.com",
        "default_signature": "Best",
        "auto_classify_enabled": True,
        "reply_templates_enabled": True,
        "task_generation_enabled": True,
        "folders": ["inbox", "sent", "drafts", "trash", "archive", "work", "personal", "spam"]
    }]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f)
    
    # 联系人列表（8个）
    contacts = [
        {"contact_id": "c001", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "c002", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "normal"},
        {"contact_id": "c003", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "normal"},
        {"contact_id": "c004", "name": "John Manager", "email": "john.manager@company.com", "role": "Manager", "team": "Leadership", "priority": "high"},
        {"contact_id": "c005", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
        {"contact_id": "c006", "name": "Sarah Developer", "email": "sarah.dev@company.com", "role": "Developer", "team": "Engineering", "priority": "normal"},
        {"contact_id": "c007", "name": "Tech Weekly", "email": "newsletter@techweekly.com", "role": "Newsletter", "team": "External", "priority": "low"},
        {"contact_id": "c008", "name": "Tom Friend", "email": "tom.friend@gmail.com", "role": "Friend", "team": "Personal", "priority": "normal"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f)
    
    # 生成邮件（含干扰）
    base_time = datetime(2025, 3, 20, 10, 0, 0)
    email_records = [
        ("c001", "high", "Project proposal"),
        ("c001", "high", "Meeting follow-up"),
        ("c002", "high", "Invoice due"),
        ("c003", "high", "Annual review reminder"),
        ("c004", "high", "Quarterly targets"),
        ("c005", "high", "You won!"),
        ("c006", "high", "Code review request"),
        ("c007", "low",  "Tech newsletter #42"),
        ("c008", "normal", "Dinner invitation"),
        ("c001", "low",  "Thank you"),
        ("c002", "low",  "Service update"),
        ("c006", "low",  "Bug report"),
    ]
    for i, (sender, imp, subj) in enumerate(email_records):
        email_id = f"msg_{i:04d}"
        thread_id = f"thread_{i}"
        timestamp_str = (base_time + timedelta(hours=i)).isoformat()
        email = {
            "id": email_id,
            "thread_id": thread_id,
            "folder": "inbox",
            "sender_id": sender,
            "subject": subj,
            "timestamp": timestamp_str,
            "importance": imp,
            "labels": [],
            "has_read": True,
            "body": f"Body of {subj}",
            "attachments": [],
            "auto_classify_suggestion": "work"
        }
        with open(f"data/emails/{email_id}.json", "w") as f:
            json.dump(email, f)
    
    # 干扰文件
    with open("data/backups/msg_0001.json.bak", "w") as f:
        f.write('{"id":"msg_0001","subject":"old"}')
    with open("data/emails/deleted_list.txt", "w") as f:
        f.write("msg_001, msg_002")
    with open("data/emails/.DS_Store", "w") as f:
        f.write("")

if __name__ == "__main__":
    build_env()
