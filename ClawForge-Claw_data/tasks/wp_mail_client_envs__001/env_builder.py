import os
import json

def build_env():
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- Contacts ---
    contacts = {
        "contacts": [
            {"contact_id": "contact_alice", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
            {"contact_id": "contact_bob", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "normal"},
            {"contact_id": "contact_hr", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "normal"},
            {"contact_id": "contact_tom", "name": "Tom Friend", "email": "tom.friend@gmail.com", "role": "Friend", "team": "Personal", "priority": "low"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # --- Accounts (minimal) ---
    accounts = {
        "accounts": [
            {
                "account_id": "default",
                "display_name": "Support Team",
                "email_address": "support@company.com",
                "default_signature": "Best, Support",
                "auto_classify_enabled": True,
                "reply_templates_enabled": True,
                "task_generation_enabled": True,
                "folders": ["inbox", "work", "personal", "spam"]
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # --- Emails ---
    emails = [
        # 1. Client + URGENT (subject)
        {
            "id": "email_001",
            "thread_id": "thread_001",
            "folder": "inbox",
            "sender_id": "contact_alice",
            "subject": "URGENT: Payment issue",
            "timestamp": "2025-03-20T09:15:00Z",
            "importance": "high",
            "labels": [],
            "has_read": False,
            "body": "Hi, we have an urgent payment issue that needs immediate attention. Please check.",
            "attachments": []
        },
        # 2. Client + ASAP (body)
        {
            "id": "email_002",
            "thread_id": "thread_002",
            "folder": "inbox",
            "sender_id": "contact_alice",
            "subject": "Follow up on quote",
            "timestamp": "2025-03-20T10:00:00Z",
            "importance": "high",
            "labels": [],
            "has_read": False,
            "body": "Please send the quote ASAP. We need it by tomorrow.",
            "attachments": []
        },
        # 3. Client, no keyword (distractor)
        {
            "id": "email_003",
            "thread_id": "thread_003",
            "folder": "inbox",
            "sender_id": "contact_alice",
            "subject": "Monthly report",
            "timestamp": "2025-03-19T14:00:00Z",
            "importance": "normal",
            "labels": [],
            "has_read": False,
            "body": "Please find attached the monthly report.",
            "attachments": []
        },
        # 4. Vendor + URGENT (not client)
        {
            "id": "email_004",
            "thread_id": "thread_004",
            "folder": "inbox",
            "sender_id": "contact_bob",
            "subject": "URGENT: Invoice overdue",
            "timestamp": "2025-03-20T11:30:00Z",
            "importance": "high",
            "labels": [],
            "has_read": False,
            "body": "Please pay the invoice immediately.",
            "attachments": []
        },
        # 5. HR + ASAP (not client)
        {
            "id": "email_005",
            "thread_id": "thread_005",
            "folder": "inbox",
            "sender_id": "contact_hr",
            "subject": "Meeting reminder",
            "timestamp": "2025-03-20T08:00:00Z",
            "importance": "normal",
            "labels": [],
            "has_read": False,
            "body": "Reminder: team meeting tomorrow at 10 AM. RSVP ASAP.",
            "attachments": []
        },
        # 6. Client + URGENT (read, still qualifies)
        {
            "id": "email_006",
            "thread_id": "thread_006",
            "folder": "inbox",
            "sender_id": "contact_alice",
            "subject": "URGENT: Security breach",
            "timestamp": "2025-03-18T16:00:00Z",
            "importance": "high",
            "labels": [],
            "has_read": True,
            "body": "There is a security issue that needs immediate action.",
            "attachments": []
        },
        # 7. Friend, no keyword (distractor)
        {
            "id": "email_007",
            "thread_id": "thread_007",
            "folder": "inbox",
            "sender_id": "contact_tom",
            "subject": "Weekend plans",
            "timestamp": "2025-03-20T12:00:00Z",
            "importance": "low",
            "labels": [],
            "has_read": False,
            "body": "Hey, are you free this weekend?",
            "attachments": []
        }
    ]

    for em in emails:
        with open(f"data/emails/{em['id']}.json", "w") as f:
            json.dump(em, f, indent=2)


if __name__ == "__main__":
    build_env()
