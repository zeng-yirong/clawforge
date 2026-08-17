import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 定义联系人
    contacts = [
        {"contact_id": "client_alice", "name": "Alice Client", "email": "alice@clientcorp.com",
         "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "vendor_bob", "name": "Bob Vendor", "email": "bob@vendor-services.com",
         "role": "Vendor", "team": "External", "priority": "normal"},
        {"contact_id": "lottery_scam", "name": "Lottery Scam", "email": "winner@lottery-scam.com",
         "role": "Spammer", "team": "External", "priority": "low"},
        {"contact_id": "hr_dept", "name": "HR Department", "email": "hr@company.com",
         "role": "HR", "team": "Human Resources", "priority": "normal"},
        {"contact_id": "sarah_dev", "name": "Sarah Developer", "email": "sarah.dev@company.com",
         "role": "Developer", "team": "Engineering", "priority": "normal"},
        {"contact_id": "tom_friend", "name": "Tom Friend", "email": "tom.friend@gmail.com",
         "role": "Friend", "team": "Personal", "priority": "low"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

    # 定义邮件列表
    emails = [
        {
            "id": "email_001",
            "thread_id": "thread_001",
            "folder": "INBOX",
            "sender_id": "client_alice",
            "subject": "Invoice payment pending",
            "timestamp": "2025-04-01T08:30:00Z",
            "importance": "high",
            "labels": [],
            "has_read": False,
            "body": "Please process the invoice asap.",
            "attachments": [],
            "auto_classify_suggestion": "finance"
        },
        {
            "id": "email_002",
            "thread_id": "thread_002",
            "folder": "INBOX",
            "sender_id": "vendor_bob",
            "subject": "Urgent: server down",
            "timestamp": "2025-04-01T09:00:00Z",
            "importance": "high",
            "labels": [],
            "has_read": False,
            "body": "Our main server is down, need immediate assistance.",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        {
            "id": "email_003",
            "thread_id": "thread_003",
            "folder": "INBOX",
            "sender_id": "lottery_scam",
            "subject": "You won a prize!",
            "timestamp": "2025-04-01T10:00:00Z",
            "importance": "high",
            "labels": ["spam"],
            "has_read": False,
            "body": "Claim your prize now!",
            "attachments": [],
            "auto_classify_suggestion": "spam"
        },
        {
            "id": "email_004",
            "thread_id": "thread_004",
            "folder": "INBOX",
            "sender_id": "hr_dept",
            "subject": "New benefits policy",
            "timestamp": "2025-04-01T11:00:00Z",
            "importance": "normal",
            "labels": [],
            "has_read": False,
            "body": "Please review the updated benefits.",
            "attachments": [],
            "auto_classify_suggestion": "hr"
        },
        {
            "id": "email_005",
            "thread_id": "thread_001",
            "folder": "INBOX",
            "sender_id": "client_alice",
            "subject": "Meeting schedule",
            "timestamp": "2025-04-02T08:00:00Z",
            "importance": "normal",
            "labels": [],
            "has_read": True,
            "body": "Let's set up a meeting next week.",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        {
            "id": "email_006",
            "thread_id": "thread_005",
            "folder": "INBOX",
            "sender_id": "sarah_dev",
            "subject": "Code review request",
            "timestamp": "2025-04-02T09:00:00Z",
            "importance": "high",
            "labels": [],
            "has_read": False,
            "body": "Can you review my latest PR?",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        {
            "id": "email_007",
            "thread_id": "thread_006",
            "folder": "INBOX",
            "sender_id": "tom_friend",
            "subject": "Dinner invite",
            "timestamp": "2025-04-02T10:00:00Z",
            "importance": "low",
            "labels": [],
            "has_read": False,
            "body": "Let's grab dinner this weekend.",
            "attachments": [],
            "auto_classify_suggestion": "personal"
        },
        {
            "id": "email_008",
            "thread_id": "thread_007",
            "folder": "INBOX",
            "sender_id": "client_alice",
            "subject": "Contract renewal",
            "timestamp": "2025-04-03T08:00:00Z",
            "importance": "high",
            "labels": [],
            "has_read": True,
            "body": "Please sign the renewal contract.",
            "attachments": [],
            "auto_classify_suggestion": "work"
        }
    ]

    for email in emails:
        with open(f"data/emails/{email['id']}.json", "w") as f:
            json.dump(email, f)

if __name__ == "__main__":
    build_env()
