import os
import json

def build_env():
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("data/old_backups", exist_ok=True)
    os.makedirs("data/drafts", exist_ok=True)

    contacts = [
        {"contact_id": "alice_001", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "bob_001", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "normal"},
        {"contact_id": "hr_001", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "normal"},
        {"contact_id": "lottery_001", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

    accounts = [
        {"account_id": "admin", "display_name": "Admin", "email_address": "admin@company.com", "default_signature": "Best,\nAdmin", "auto_classify_enabled": True, "reply_templates_enabled": True, "task_generation_enabled": True, "folders": ["inbox", "sent", "trash"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    emails = [
        # 目标邮件：来自Alice，未读，重要性high，标题含URGENT
        {
            "id": "email_001",
            "thread_id": "thread_001",
            "folder": "inbox",
            "sender_id": "alice_001",
            "subject": "URGENT: Project Delay",
            "timestamp": "2025-03-20T09:15:00Z",
            "importance": "high",
            "labels": ["urgent", "project"],
            "has_read": False,
            "body": "Hi, we have a critical issue with the project timeline...",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        # 干扰：另一封来自Alice的已读邮件
        {
            "id": "email_002",
            "thread_id": "thread_002",
            "folder": "inbox",
            "sender_id": "alice_001",
            "subject": "Weekly Check-in",
            "timestamp": "2025-03-19T14:30:00Z",
            "importance": "normal",
            "labels": ["meeting"],
            "has_read": True,
            "body": "Reminder for our weekly sync.",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        # 干扰：其他联系人邮件
        {
            "id": "email_003",
            "thread_id": "thread_003",
            "folder": "inbox",
            "sender_id": "bob_001",
            "subject": "Invoice for March",
            "timestamp": "2025-03-18T11:00:00Z",
            "importance": "normal",
            "labels": ["invoice"],
            "has_read": False,
            "body": "Find attached the March invoice.",
            "attachments": [{"name": "invoice_march.pdf", "size": 1024}],
            "auto_classify_suggestion": "finance"
        },
        {
            "id": "email_004",
            "thread_id": "thread_004",
            "folder": "spam",
            "sender_id": "lottery_001",
            "subject": "You Won!",
            "timestamp": "2025-03-17T08:00:00Z",
            "importance": "low",
            "labels": ["spam"],
            "has_read": True,
            "body": "Congratulations! You won a lottery.",
            "attachments": [],
            "auto_classify_suggestion": "spam"
        },
        {
            "id": "email_005",
            "thread_id": "thread_005",
            "folder": "inbox",
            "sender_id": "hr_001",
            "subject": "New Company Policy",
            "timestamp": "2025-03-16T16:45:00Z",
            "importance": "normal",
            "labels": ["hr"],
            "has_read": True,
            "body": "Review the updated policy.",
            "attachments": [{"name": "policy.pdf", "size": 2048}],
            "auto_classify_suggestion": "hr"
        },
        # 脏数据：缺失字段且importance非法枚举值
        {
            "id": "email_006",
            "thread_id": "thread_006",
            "folder": "inbox",
            "sender_id": "unknown_001",
            "subject": "Test",
            "timestamp": "2025-03-15T12:00:00Z",
            "importance": "critical",          # 非法值
            "has_read": False,
            "body": "Missing labels field.",
            "attachments": [],
            "auto_classify_suggestion": "personal"
        }
    ]

    for email in emails:
        with open(f"data/emails/{email['id']}.json", "w") as f:
            json.dump(email, f)

    # 非JSON文件干扰
    with open("data/emails/readme.txt", "w") as f:
        f.write("This is a text file, not email JSON.")

    # 备份目录中的旧邮件（不会干扰主目录）
    old_email = {
        "id": "email_007",
        "thread_id": "thread_007",
        "folder": "inbox",
        "sender_id": "alice_001",
        "subject": "Old Project Update",
        "timestamp": "2025-02-01T10:00:00Z",
        "importance": "low",
        "labels": [],
        "has_read": True,
        "body": "Old email.",
        "attachments": [],
        "auto_classify_suggestion": "work"
    }
    with open("data/old_backups/email_007.json", "w") as f:
        json.dump(old_email, f)

    # 草稿干扰
    with open("data/drafts/draft_001.json", "w") as f:
        json.dump({"id": "draft_001", "subject": "Draft reply"}, f)

if __name__ == "__main__":
    build_env()
