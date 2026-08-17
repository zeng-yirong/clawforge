import os
import json

def build_env():
    # Create directory structure
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("drafts", exist_ok=True)  # placeholder, will be populated by agent
    os.makedirs("tasks", exist_ok=True)   # placeholder

    # Accounts
    accounts = {
        "accounts": [
            {
                "account_id": "company_main",
                "display_name": "Company Support",
                "email_address": "support@company.com",
                "default_signature": "Best regards,\nCompany Support Team",
                "auto_classify_enabled": True,
                "reply_templates_enabled": True,
                "task_generation_enabled": True,
                "folders": ["inbox", "sent", "drafts", "archive", "spam"]
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # Contacts
    contacts = {
        "contacts": [
            {"contact_id": "alice", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
            {"contact_id": "bob", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "normal"},
            {"contact_id": "hr", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "normal"},
            {"contact_id": "john", "name": "John Manager", "email": "john.manager@company.com", "role": "Manager", "team": "Leadership", "priority": "high"},
            {"contact_id": "lottery", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
            {"contact_id": "sarah", "name": "Sarah Developer", "email": "sarah.dev@company.com", "role": "Developer", "team": "Engineering", "priority": "normal"},
            {"contact_id": "techweekly", "name": "Tech Weekly", "email": "newsletter@techweekly.com", "role": "Newsletter", "team": "External", "priority": "low"},
            {"contact_id": "tom", "name": "Tom Friend", "email": "tom.friend@gmail.com", "role": "Friend", "team": "Personal", "priority": "normal"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # Emails
    emails = [
        {
            "id": "email_001",
            "thread_id": "thread_001",
            "folder": "inbox",
            "sender_id": "alice",
            "subject": "Project Progress",
            "timestamp": "2024-05-20T10:30:00",
            "importance": "high",
            "labels": ["project", "urgent"],
            "has_read": False,
            "body": "Hi Team,\n\nI wanted to check on the progress of the product prototype. We need it by next Friday. Could you please provide an update?\n\nAlso, TODO: 交付产品原型\n\nBest,\nAlice",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        {
            "id": "email_002",
            "thread_id": "thread_002",
            "folder": "inbox",
            "sender_id": "alice",
            "subject": "Meeting Next Week",
            "timestamp": "2024-05-21T09:15:00",
            "importance": "normal",
            "labels": ["meeting"],
            "has_read": False,
            "body": "Hi,\n\nLet's schedule a meeting for next Tuesday to discuss the milestones.\n\nAlice",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        {
            "id": "email_003",
            "thread_id": "thread_003",
            "folder": "inbox",
            "sender_id": "bob",
            "subject": "Invoice #1234",
            "timestamp": "2024-05-19T14:00:00",
            "importance": "normal",
            "labels": ["invoice"],
            "has_read": False,
            "body": "Please find attached invoice for the last month services.",
            "attachments": [],
            "auto_classify_suggestion": "finance"
        },
        {
            "id": "email_004",
            "thread_id": "thread_004",
            "folder": "inbox",
            "sender_id": "lottery",
            "subject": "You Won!",
            "timestamp": "2024-05-22T08:00:00",
            "importance": "low",
            "labels": ["spam"],
            "has_read": False,
            "body": "Congratulations! You have won $1,000,000. Click here to claim.",
            "attachments": [],
            "auto_classify_suggestion": "spam"
        },
        {
            "id": "email_005",
            "thread_id": "thread_005",
            "folder": "inbox",
            "sender_id": "techweekly",
            "subject": "Tech Weekly Digest",
            "timestamp": "2024-05-18T07:00:00",
            "importance": "low",
            "labels": ["newsletter"],
            "has_read": False,
            "body": "This week in tech...",
            "attachments": [],
            "auto_classify_suggestion": "newsletter"
        }
    ]

    for e in emails:
        fname = f"data/emails/{e['id']}.json"
        with open(fname, "w") as f:
            json.dump(e, f, indent=2)

    # Corrupted email file (distraction)
    with open("data/emails/bad_email.json", "w") as f:
        f.write("This is not valid JSON!\n")

    # Extra directory with stale data (distraction)
    os.makedirs("old_emails", exist_ok=True)
    with open("old_emails/stale_001.json", "w") as f:
        json.dump({"dummy": True}, f)

if __name__ == "__main__":
    build_env()
