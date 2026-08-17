import os
import json
import datetime

def build_env():
    # ---- data/emails/ ----
    os.makedirs("data/emails", exist_ok=True)

    emails = [
        {
            "id": "email_001",
            "thread_id": "thread_001",
            "folder": "inbox",
            "sender_id": "bob",
            "subject": "URGENT: SSL certificate expiring in 3 days",
            "timestamp": "2025-03-01T08:00:00Z",
            "importance": "high",
            "labels": ["work", "critical"],
            "has_read": False,
            "body": "Hi, our server SSL certificate will expire on 2025-03-04. Please renew immediately.",
            "attachments": []
        },
        {
            "id": "email_002",
            "thread_id": "thread_001",
            "folder": "inbox",
            "sender_id": "bob",
            "subject": "RE: URGENT: SSL certificate expiring",
            "timestamp": "2025-03-01T09:00:00Z",
            "importance": "high",
            "labels": ["work"],
            "has_read": False,
            "body": "Just following up, we need action ASAP.",
            "attachments": []
        },
        {
            "id": "email_003",
            "thread_id": "thread_002",
            "folder": "inbox",
            "sender_id": "alice",
            "subject": "Proposal for Q2 project",
            "timestamp": "2025-03-02T10:00:00Z",
            "importance": "normal",
            "labels": ["work"],
            "has_read": True,
            "body": "Please review attached proposal.",
            "attachments": [{"filename": "proposal.pdf", "content": "fake content"}]
        },
        {
            "id": "email_004",
            "thread_id": "thread_003",
            "folder": "inbox",
            "sender_id": "tech_weekly",
            "subject": "Tech Weekly: AI Trends 2025",
            "timestamp": "2025-03-03T06:00:00Z",
            "importance": "normal",
            "labels": ["newsletter"],
            "has_read": False,
            "body": "Read the latest trends in AI...",
            "attachments": []
        },
        {
            "id": "email_005",
            "thread_id": "thread_003",
            "folder": "inbox",
            "sender_id": "tech_weekly",
            "subject": "Tech Weekly: Cloud Security",
            "timestamp": "2025-03-04T06:00:00Z",
            "importance": "normal",
            "labels": ["newsletter"],
            "has_read": True,
            "body": "Cloud security best practices...",
            "attachments": []
        },
        {
            "id": "email_006",
            "thread_id": "thread_004",
            "folder": "spam",
            "sender_id": "lottery",
            "subject": "You won a prize!",
            "timestamp": "2025-03-05T12:00:00Z",
            "importance": "low",
            "labels": [],
            "has_read": False,
            "body": "Click here to claim your prize...",
            "attachments": []
        },
        {
            "id": "email_007",
            "thread_id": "thread_005",
            "folder": "inbox",
            "sender_id": "bob",
            "subject": "Invoice for February",
            "timestamp": "2025-03-06T14:00:00Z",
            "importance": "low",
            "labels": ["finance"],
            "has_read": True,
            "body": "Please pay the invoice.",
            "attachments": []
        },
        {
            "id": "email_008",
            "thread_id": "thread_006",
            "folder": "inbox",
            "sender_id": "john",
            "subject": "Team meeting tomorrow",
            "timestamp": "2025-03-07T09:00:00Z",
            "importance": "normal",
            "labels": ["work"],
            "has_read": False,
            "body": "Meeting at 10am.",
            "attachments": []
        }
    ]

    for email in emails:
        path = f"data/emails/{email['id']}.json"
        with open(path, "w") as f:
            json.dump(email, f)

    # ---- data/contacts.json ----
    contacts = [
        {"contact_id": "bob", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "high"},
        {"contact_id": "alice", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "tech_weekly", "name": "Tech Weekly", "email": "newsletter@techweekly.com", "role": "Newsletter", "team": "External", "priority": "normal"},
        {"contact_id": "hr", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "normal"},
        {"contact_id": "john", "name": "John Manager", "email": "john.manager@company.com", "role": "Manager", "team": "Leadership", "priority": "high"},
        {"contact_id": "lottery", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

    # ---- data/accounts.json ----
    account = {
        "account_id": "me",
        "display_name": "Assistant",
        "email_address": "assistant@company.com",
        "default_signature": "--\nAssistant Bot",
        "auto_classify_enabled": True,
        "reply_templates_enabled": True,
        "task_generation_enabled": True,
        "folders": ["inbox", "work", "personal", "spam", "newsletter", "finance", "hr"]
    }
    with open("data/accounts.json", "w") as f:
        f.write(json.dumps({"accounts": [account]}, indent=2))

if __name__ == "__main__":
    build_env()
