import os
import json
import uuid

REQUIRED_CONTACTS = [
    {"contact_id": "contact_alice", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
    {"contact_id": "contact_bob", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "high"},
    {"contact_id": "contact_hr", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "normal"},
    {"contact_id": "contact_john", "name": "John Manager", "email": "john.manager@company.com", "role": "Manager", "team": "Leadership", "priority": "normal"},
    {"contact_id": "contact_lottery", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
    {"contact_id": "contact_sarah", "name": "Sarah Developer", "email": "sarah.dev@company.com", "role": "Developer", "team": "Engineering", "priority": "normal"},
    {"contact_id": "contact_tech", "name": "Tech Weekly", "email": "newsletter@techweekly.com", "role": "Newsletter", "team": "External", "priority": "low"},
    {"contact_id": "contact_tom", "name": "Tom Friend", "email": "tom.friend@gmail.com", "role": "Friend", "team": "Personal", "priority": "normal"},
]

def build_env():
    # Ensure ops directory exists (will be created by agent, but we create it as seed)
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Write contacts.json
    contacts = {c["contact_id"]: c for c in REQUIRED_CONTACTS}
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # Write accounts.json (simple stub)
    account = {
        "account_id": "account_default",
        "display_name": "Default Mailbox",
        "email_address": "default@company.com",
        "default_signature": "Best regards",
        "auto_classify_enabled": True,
        "reply_templates_enabled": True,
        "task_generation_enabled": True,
        "folders": ["inbox", "work", "personal", "spam", "finance", "hr", "newsletter"]
    }
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": {"account_default": account}}, f, indent=2)

    # Create emails (8 emails, each with different patterns)
    emails = [
        {
            "id": "email_001",
            "thread_id": "thread_001",
            "folder": "spam",
            "sender_id": "contact_alice",
            "subject": "New project proposal - action required",
            "timestamp": "2025-03-10T08:00:00Z",
            "importance": "high",
            "labels": ["external"],
            "has_read": False,
            "body": "Hi team, please review the attached proposal and provide feedback by Friday. Action required: confirm your availability for the kickoff meeting.",
            "attachments": [],
            "auto_classify_suggestion": "spam"
        },
        {
            "id": "email_002",
            "thread_id": "thread_002",
            "folder": "spam",
            "sender_id": "contact_bob",
            "subject": "Invoice overdue",
            "timestamp": "2025-03-09T14:30:00Z",
            "importance": "high",
            "labels": ["finance"],
            "has_read": False,
            "body": "This is a reminder that invoice #1024 is overdue. Please process payment at your earliest convenience.",
            "attachments": [],
            "auto_classify_suggestion": "spam"
        },
        {
            "id": "email_003",
            "thread_id": "thread_003",
            "folder": "spam",
            "sender_id": "contact_lottery",
            "subject": "You won a prize!",
            "timestamp": "2025-03-08T12:00:00Z",
            "importance": "high",
            "labels": [],
            "has_read": False,
            "body": "Congratulations! You have won $1,000,000. Click here to claim.",
            "attachments": [],
            "auto_classify_suggestion": "spam"
        },
        {
            "id": "email_004",
            "thread_id": "thread_004",
            "folder": "work",
            "sender_id": "contact_john",
            "subject": "Quarterly review meeting",
            "timestamp": "2025-03-07T10:00:00Z",
            "importance": "high",
            "labels": ["meeting"],
            "has_read": True,
            "body": "Please prepare slides for the quarterly review. No action required now, just heads up.",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        {
            "id": "email_005",
            "thread_id": "thread_005",
            "folder": "spam",
            "sender_id": "contact_sarah",
            "subject": "Code review request",
            "timestamp": "2025-03-06T16:00:00Z",
            "importance": "low",
            "labels": ["dev"],
            "has_read": False,
            "body": "Could you take a look at the PR when you have time? No rush.",
            "attachments": [],
            "auto_classify_suggestion": "spam"
        },
        {
            "id": "email_006",
            "thread_id": "thread_006",
            "folder": "inbox",
            "sender_id": "contact_alice",
            "subject": "Thank you for the meeting",
            "timestamp": "2025-03-05T09:00:00Z",
            "importance": "normal",
            "labels": ["client"],
            "has_read": True,
            "body": "Thanks for the productive discussion today. Looking forward to next steps.",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        {
            "id": "email_007",
            "thread_id": "thread_007",
            "folder": "spam",
            "sender_id": "contact_tom",
            "subject": "Birthday party invitation",
            "timestamp": "2025-03-04T18:00:00Z",
            "importance": "high",
            "labels": ["personal"],
            "has_read": False,
            "body": "Hey! You are invited to my birthday party this Saturday. Please RSVP.",
            "attachments": [],
            "auto_classify_suggestion": "spam"
        },
        {
            "id": "email_008",
            "thread_id": "thread_008",
            "folder": "spam",
            "sender_id": "contact_hr",
            "subject": "Mandatory training enrollment",
            "timestamp": "2025-03-03T07:00:00Z",
            "importance": "high",
            "labels": ["hr"],
            "has_read": False,
            "body": "All employees must enroll in the new compliance training by next week. Action required: complete registration.",
            "attachments": [],
            "auto_classify_suggestion": "spam"
        }
    ]

    for email in emails:
        file_path = f"data/emails/{email['id']}.json"
        with open(file_path, "w") as f:
            json.dump(email, f, indent=2)

if __name__ == "__main__":
    build_env()
