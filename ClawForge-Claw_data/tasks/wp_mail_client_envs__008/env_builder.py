import os
import json
import random

def build_env():
    # 确保目录存在
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 账户信息（当前用户）
    accounts = [
        {
            "account_id": "user_001",
            "display_name": "AI Assistant",
            "email_address": "assistant@company.com",
            "default_signature": "Best regards,\nAI Assistant",
            "auto_classify_enabled": True,
            "reply_templates_enabled": True,
            "task_generation_enabled": True,
            "folders": ["inbox", "work", "personal", "spam", "newsletter", "finance", "hr"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # 联系人
    contacts = [
        {
            "contact_id": "c001",
            "name": "John Manager",
            "email": "john.manager@company.com",
            "role": "Manager",
            "team": "Leadership",
            "priority": "high"
        },
        {
            "contact_id": "c002",
            "name": "HR Department",
            "email": "hr@company.com",
            "role": "HR",
            "team": "Human Resources",
            "priority": "normal"
        },
        {
            "contact_id": "c003",
            "name": "Lottery Scam",
            "email": "winner@lottery-scam.com",
            "role": "Spammer",
            "team": "External",
            "priority": "low"
        },
        {
            "contact_id": "c004",
            "name": "Tech Weekly",
            "email": "newsletter@techweekly.com",
            "role": "Newsletter",
            "team": "External",
            "priority": "low"
        }
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 邮件列表（包含干扰项）
    emails = [
        {
            "id": "email_001",
            "thread_id": "thread_001",
            "folder": "inbox",
            "sender_id": "john.manager@company.com",
            "subject": "Q3 Progress Report - Urgent",
            "timestamp": "2025-03-15T09:30:00Z",
            "importance": "high",
            "labels": ["work"],
            "has_read": False,
            "body": "Hi,\n\nPlease prepare the Q3 progress report by March 20. Leadership is expecting it. Let me know if you have any questions.\n\nBest,\nJohn",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        {
            "id": "email_002",
            "thread_id": "thread_002",
            "folder": "archived",
            "sender_id": "hr@company.com",
            "subject": "Upcoming Benefits Deadline",
            "timestamp": "2025-03-10T14:00:00Z",
            "importance": "normal",
            "labels": ["hr"],
            "has_read": True,
            "body": "Don't forget to enroll before March 25.",
            "attachments": [],
            "auto_classify_suggestion": "hr"
        },
        {
            "id": "email_003",
            "thread_id": "thread_003",
            "folder": "inbox",
            "sender_id": "winner@lottery-scam.com",
            "subject": "YOU WON A PRIZE!",
            "timestamp": "2025-03-14T08:00:00Z",
            "importance": "low",
            "labels": ["spam"],
            "has_read": False,
            "body": "Click here to claim your $10,000,000!",
            "attachments": [],
            "auto_classify_suggestion": "spam"
        },
        {
            "id": "email_004",
            "thread_id": "thread_004",
            "folder": "inbox",
            "sender_id": "newsletter@techweekly.com",
            "subject": "Tech Weekly: March Issue",
            "timestamp": "2025-03-13T12:00:00Z",
            "importance": "low",
            "labels": ["newsletter"],
            "has_read": False,
            "body": "Top stories this week...",
            "attachments": [],
            "auto_classify_suggestion": "newsletter"
        },
        {
            "id": "email_005",
            "thread_id": "thread_001",
            "folder": "inbox",
            "sender_id": "john.manager@company.com",
            "subject": "Re: Q3 Progress Report - Urgent",
            "timestamp": "2025-03-15T10:00:00Z",
            "importance": "high",
            "labels": ["work"],
            "has_read": False,
            "body": "Just following up, need this by Monday.",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        {
            "id": "email_006",
            "thread_id": "thread_005",
            "folder": "inbox",
            "sender_id": "hr@company.com",
            "subject": "Team Building Event Reminder",
            "timestamp": "2025-03-12T09:00:00Z",
            "importance": "normal",
            "labels": ["hr"],
            "has_read": True,
            "body": "Don't forget to RSVP by March 18.",
            "attachments": [],
            "auto_classify_suggestion": "hr"
        }
    ]

    for mail in emails:
        fname = f"data/emails/{mail['id']}.json"
        with open(fname, "w") as f:
            json.dump(mail, f, indent=2)

if __name__ == "__main__":
    build_env()
