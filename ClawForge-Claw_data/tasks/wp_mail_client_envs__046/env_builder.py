import os
import json
import shutil
from datetime import datetime, timezone

def build_env():
    # 创建目录结构
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("archived", exist_ok=True)  # 初始为空，后续由agent归档
    # 干扰项
    os.makedirs("old_backup", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # 创建干扰文件
    with open("README.md", "w") as f:
        f.write("# Mail Dump\nDo not modify manually.\n")
    with open("logs/system.log", "w") as f:
        f.write("2025-03-09 08:00:00 INFO: Mail server started\n")
    with open("old_backup/msg_001.bak", "w") as f:
        f.write('{"id":"msg_001","subject":"old backup"}')

    # 创建accounts.json
    accounts = {
        "accounts": [
            {
                "account_id": "acc_001",
                "display_name": "Zhang Xiao",
                "email_address": "zhang@company.com",
                "default_signature": "Best, Xiao",
                "auto_classify_enabled": True,
                "reply_templates_enabled": True,
                "task_generation_enabled": True,
                "folders": ["inbox", "work", "personal", "spam", "archived"]
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 创建contacts.json
    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
            {"contact_id": "c002", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "normal"},
            {"contact_id": "c003", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "normal"},
            {"contact_id": "c004", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
            {"contact_id": "c005", "name": "Tech Weekly", "email": "newsletter@techweekly.com", "role": "Newsletter", "team": "External", "priority": "low"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 创建5封邮件
    emails = [
        {
            "id": "msg_001",
            "thread_id": "thread_001",
            "folder": "inbox",
            "sender_id": "c001",
            "subject": "[TODO] Review Q3 budget",
            "timestamp": "2025-03-10T09:00:00Z",
            "importance": "high",
            "labels": ["work", "todo"],
            "has_read": False,
            "body": "Please review the Q3 budget attached.",
            "attachments": [{"name": "budget.xlsx", "type": "spreadsheet"}],
            "auto_classify_suggestion": "work"
        },
        {
            "id": "msg_002",
            "thread_id": "thread_002",
            "folder": "inbox",
            "sender_id": "c004",
            "subject": "You won a lottery!",
            "timestamp": "2025-03-10T10:30:00Z",
            "importance": "low",
            "labels": ["spam"],
            "has_read": False,
            "body": "Claim your prize now!",
            "attachments": [],
            "auto_classify_suggestion": "spam"
        },
        {
            "id": "msg_003",
            "thread_id": "thread_003",
            "folder": "inbox",
            "sender_id": "c005",
            "subject": "[TODO] Prepare monthly report",
            "timestamp": "2025-03-11T14:30:00Z",
            "importance": "normal",
            "labels": ["work", "todo"],
            "has_read": False,
            "body": "Don't forget the monthly report due next week.",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        {
            "id": "msg_004",
            "thread_id": "thread_004",
            "folder": "inbox",
            "sender_id": "c001",
            "subject": "[TODO] Update client list",
            "timestamp": "2025-03-12T08:15:00Z",
            "importance": "normal",
            "labels": ["work", "todo"],
            "has_read": False,
            "body": "Please update the client list with new contacts.",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        {
            "id": "msg_005",
            "thread_id": "thread_005",
            "folder": "inbox",
            "sender_id": "c004",
            "subject": "Congratulations!",
            "timestamp": "2025-03-12T12:00:00Z",
            "importance": "low",
            "labels": ["spam"],
            "has_read": False,
            "body": "You have been selected. Click here.",
            "attachments": [],
            "auto_classify_suggestion": "spam"
        }
    ]

    for email in emails:
        filename = f"data/emails/{email['id']}.json"
        with open(filename, "w") as f:
            json.dump(email, f, indent=2)

if __name__ == "__main__":
    build_env()
