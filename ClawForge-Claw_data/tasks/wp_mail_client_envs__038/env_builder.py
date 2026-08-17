import os
import json

def build_env():
    # 确保目录存在
    os.makedirs("data/emails", exist_ok=True)

    # 固定邮件数据
    emails = [
        # 符合条件的两个
        {"id": "e001", "thread_id": "thread_e001", "folder": "inbox",
         "sender_id": "alice@clientcorp.com", "subject": "Urgent meeting",
         "timestamp": "2025-03-20T08:30:00", "importance": "high",
         "labels": ["action required", "urgent"], "has_read": False,
         "body": "We need to discuss the quarterly report ASAP.",
         "attachments": [], "auto_classify_suggestion": "work"},
        {"id": "e004", "thread_id": "thread_e004", "folder": "inbox",
         "sender_id": "bob@vendor-services.com", "subject": "Action needed",
         "timestamp": "2025-03-20T09:15:00", "importance": "high",
         "labels": ["action required"], "has_read": False,
         "body": "Please approve the contract by end of day.",
         "attachments": [], "auto_classify_suggestion": "work"},
        # 干扰项
        {"id": "e002", "thread_id": "thread_e002", "folder": "inbox",
         "sender_id": "hr@company.com", "subject": "Payroll update",
         "timestamp": "2025-03-19T14:00:00", "importance": "high",
         "labels": ["urgent"], "has_read": False,
         "body": "New payroll cycle starts next week.",
         "attachments": [], "auto_classify_suggestion": "hr"},
        {"id": "e003", "thread_id": "thread_e003", "folder": "inbox",
         "sender_id": "newsletter@techweekly.com", "subject": "Tech Weekly",
         "timestamp": "2025-03-18T10:00:00", "importance": "normal",
         "labels": ["action required"], "has_read": False,
         "body": "Please update your preferences.",
         "attachments": [], "auto_classify_suggestion": "newsletter"},
        {"id": "e005", "thread_id": "thread_e005", "folder": "inbox",
         "sender_id": "sarah.dev@company.com", "subject": "Code review",
         "timestamp": "2025-03-20T07:45:00", "importance": "high",
         "labels": ["work"], "has_read": False,
         "body": "Could you review the PR #42?",
         "attachments": [], "auto_classify_suggestion": "work"},
        {"id": "e006", "thread_id": "thread_e006", "folder": "spam",
         "sender_id": "winner@lottery-scam.com", "subject": "You won!",
         "timestamp": "2025-03-20T06:00:00", "importance": "low",
         "labels": [], "has_read": False,
         "body": "Claim your prize now!",
         "attachments": [], "auto_classify_suggestion": "spam"},
        {"id": "e007", "thread_id": "thread_e007", "folder": "inbox",
         "sender_id": "john.manager@company.com", "subject": "Finance report",
         "timestamp": "2025-03-19T16:30:00", "importance": "high",
         "labels": ["finance"], "has_read": False,
         "body": "Please review the attached budget.",
         "attachments": [], "auto_classify_suggestion": "finance"},
        {"id": "e008", "thread_id": "thread_e008", "folder": "inbox",
         "sender_id": "tom.friend@gmail.com", "subject": "Weekend plans",
         "timestamp": "2025-03-20T10:00:00", "importance": "normal",
         "labels": ["action required", "urgent"], "has_read": False,
         "body": "Let me know if you're free Saturday.",
         "attachments": [], "auto_classify_suggestion": "personal"},
        {"id": "e009", "thread_id": "thread_e009", "folder": "inbox",
         "sender_id": "alice@clientcorp.com", "subject": "Follow-up",
         "timestamp": "2025-03-19T11:00:00", "importance": "high",
         "labels": ["urgent", "work"], "has_read": False,
         "body": "Any updates on the proposal?",
         "attachments": [], "auto_classify_suggestion": "work"},
        {"id": "e010", "thread_id": "thread_e010", "folder": "spam",
         "sender_id": "winner@lottery-scam.com", "subject": "Congratulations",
         "timestamp": "2025-03-20T05:00:00", "importance": "high",
         "labels": ["spam"], "has_read": False,
         "body": "You have won a free vacation!",
         "attachments": [], "auto_classify_suggestion": "spam"},
        {"id": "e011", "thread_id": "thread_e011", "folder": "inbox",
         "sender_id": "newsletter@techweekly.com", "subject": "New issue",
         "timestamp": "2025-03-18T08:00:00", "importance": "normal",
         "labels": ["newsletter"], "has_read": False,
         "body": "Check out this week's articles.",
         "attachments": [], "auto_classify_suggestion": "newsletter"},
        {"id": "e012", "thread_id": "thread_e012", "folder": "inbox",
         "sender_id": "hr@company.com", "subject": "Training required",
         "timestamp": "2025-03-17T15:00:00", "importance": "low",
         "labels": ["action required"], "has_read": False,
         "body": "Complete the compliance training by Friday.",
         "attachments": [], "auto_classify_suggestion": "hr"},
    ]

    for em in emails:
        with open(f"data/emails/{em['id']}.json", "w") as f:
            json.dump(em, f, indent=2)

    # accounts.json
    accounts = [
        {
            "account_id": "acc1",
            "display_name": "Tom",
            "email_address": "tom@company.com",
            "default_signature": "Best, Tom",
            "auto_classify_enabled": True,
            "reply_templates_enabled": True,
            "task_generation_enabled": True,
            "folders": ["inbox", "work", "personal", "spam", "archive"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # contacts.json
    contacts = [
        {"contact_id": "c1", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "c2", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "normal"},
        {"contact_id": "c3", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "normal"},
        {"contact_id": "c4", "name": "John Manager", "email": "john.manager@company.com", "role": "Manager", "team": "Leadership", "priority": "high"},
        {"contact_id": "c5", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
        {"contact_id": "c6", "name": "Sarah Developer", "email": "sarah.dev@company.com", "role": "Developer", "team": "Engineering", "priority": "normal"},
        {"contact_id": "c7", "name": "Tech Weekly", "email": "newsletter@techweekly.com", "role": "Newsletter", "team": "External", "priority": "low"},
        {"contact_id": "c8", "name": "Tom Friend", "email": "tom.friend@gmail.com", "role": "Friend", "team": "Personal", "priority": "normal"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 其他干扰文件
    os.makedirs("logs", exist_ok=True)
    with open("logs/system.log", "w") as f:
        f.write("2025-03-20 08:00:00 INFO Mail sync completed\n")
    with open("logs/backup.log", "w") as f:
        f.write("2025-03-19 23:00:00 INFO Backup successful\n")

if __name__ == "__main__":
    build_env()
