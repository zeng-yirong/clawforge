import os
import json
import shutil
from datetime import datetime, timedelta

def build_env():
    # Clean slate
    if os.path.exists("emails"):
        shutil.rmtree("emails")
    if os.path.exists("ops"):
        shutil.rmtree("ops")
    if os.path.exists("accounts.json"):
        os.remove("accounts.json")
    if os.path.exists("contacts.json"):
        os.remove("contacts.json")

    # Contacts
    contacts = [
        {"contact_id": "contact_001", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "contact_002", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "normal"},
        {"contact_id": "contact_003", "name": "Sarah Developer", "email": "sarah.dev@company.com", "role": "Developer", "team": "Engineering", "priority": "high"},
        {"contact_id": "contact_004", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "normal"},
        {"contact_id": "contact_005", "name": "Tech Weekly", "email": "newsletter@techweekly.com", "role": "Newsletter", "team": "External", "priority": "low"},
        {"contact_id": "contact_006", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
    ]
    os.makedirs("emails", exist_ok=True)
    with open("contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

    # Accounts (just one account for simplicity)
    accounts = [
        {
            "account_id": "account_001",
            "display_name": "John Manager",
            "email_address": "john.manager@company.com",
            "default_signature": "Best, John",
            "auto_classify_enabled": True,
            "reply_templates_enabled": True,
            "task_generation_enabled": True,
            "folders": ["INBOX", "work", "personal", "spam", "newsletter", "finance", "hr"]
        }
    ]
    with open("accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    # Emails: 12 total, mix of conditions
    emails = [
        # 1 - Alice, not read, should get reply
        {
            "id": "email_001",
            "thread_id": "thread_001",
            "folder": "INBOX",
            "sender_id": "contact_001",
            "subject": "Project update",
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
            "importance": "high",
            "labels": ["client"],
            "has_read": False,
            "body": "Hi John, just following up on the proposal. Regards, Alice",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        # 2 - Alice, already read, should NOT get reply (since already read)
        {
            "id": "email_002",
            "thread_id": "thread_002",
            "folder": "INBOX",
            "sender_id": "contact_001",
            "subject": "Meeting notes",
            "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
            "importance": "normal",
            "labels": ["client", "read"],
            "has_read": True,
            "body": "Thanks for the meeting. -Alice",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        # 3 - Sarah, urgent title, should create TODO
        {
            "id": "email_003",
            "thread_id": "thread_003",
            "folder": "INBOX",
            "sender_id": "contact_003",
            "subject": "URGENT: Login bug in production",
            "timestamp": (datetime.now() - timedelta(hours=5)).isoformat(),
            "importance": "high",
            "labels": ["bug"],
            "has_read": False,
            "body": "John, we have a critical bug in the login page. Please assign someone to fix it ASAP. -Sarah",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        # 4 - Sarah, contains "bug" in body, should create TODO
        {
            "id": "email_004",
            "thread_id": "thread_004",
            "folder": "INBOX",
            "sender_id": "contact_003",
            "subject": "Code review feedback",
            "timestamp": (datetime.now() - timedelta(days=2)).isoformat(),
            "importance": "normal",
            "labels": ["code"],
            "has_read": True,
            "body": "I found a minor bug in the auth module. Could you look at it? -Sarah",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        # 5 - Newsletter, read, should archive
        {
            "id": "email_005",
            "thread_id": "thread_005",
            "folder": "newsletter",
            "sender_id": "contact_005",
            "subject": "Tech Weekly Issue #42",
            "timestamp": (datetime.now() - timedelta(days=3)).isoformat(),
            "importance": "low",
            "labels": ["newsletter", "read"],
            "has_read": True,
            "body": "This week's tech news...",
            "attachments": [],
            "auto_classify_suggestion": "newsletter"
        },
        # 6 - Newsletter, not read (should NOT archive because not read)
        {
            "id": "email_006",
            "thread_id": "thread_006",
            "folder": "newsletter",
            "sender_id": "contact_005",
            "subject": "Tech Weekly Issue #41",
            "timestamp": (datetime.now() - timedelta(weeks=1)).isoformat(),
            "importance": "low",
            "labels": ["newsletter"],
            "has_read": False,
            "body": "Last week's news...",
            "attachments": [],
            "auto_classify_suggestion": "newsletter"
        },
        # 7 - Spam, read, should archive
        {
            "id": "email_007",
            "thread_id": "thread_007",
            "folder": "spam",
            "sender_id": "contact_006",
            "subject": "You won a lottery!",
            "timestamp": (datetime.now() - timedelta(hours=12)).isoformat(),
            "importance": "low",
            "labels": ["spam", "read"],
            "has_read": True,
            "body": "Congratulations! You won 1 million dollars...",
            "attachments": [],
            "auto_classify_suggestion": "spam"
        },
        # 8 - Spam, not read, should NOT archive
        {
            "id": "email_008",
            "thread_id": "thread_008",
            "folder": "spam",
            "sender_id": "contact_006",
            "subject": "Get rich quick",
            "timestamp": (datetime.now() - timedelta(days=5)).isoformat(),
            "importance": "low",
            "labels": ["spam"],
            "has_read": False,
            "body": "Click here to earn money...",
            "attachments": [],
            "auto_classify_suggestion": "spam"
        },
        # 9 - Bob Vendor, read, not archive/reply/todo (irrelevant)
        {
            "id": "email_009",
            "thread_id": "thread_009",
            "folder": "INBOX",
            "sender_id": "contact_002",
            "subject": "Invoice due",
            "timestamp": (datetime.now() - timedelta(days=7)).isoformat(),
            "importance": "normal",
            "labels": ["vendor"],
            "has_read": True,
            "body": "Please pay invoice #1234 by end of month. -Bob",
            "attachments": [],
            "auto_classify_suggestion": "finance"
        },
        # 10 - HR, not read, not archive/reply/todo (no condition)
        {
            "id": "email_010",
            "thread_id": "thread_010",
            "folder": "INBOX",
            "sender_id": "contact_004",
            "subject": "Open enrollment",
            "timestamp": (datetime.now() - timedelta(days=10)).isoformat(),
            "importance": "normal",
            "labels": ["hr"],
            "has_read": False,
            "body": "Health insurance open enrollment ends next week.",
            "attachments": [],
            "auto_classify_suggestion": "hr"
        },
        # 11 - Sarah, subject "urgent" but lowercase? Already have uppercase, fine. Another with "bug" in body but already read -> still create TODO? Prompt says "标题或正文里带“urgent”或“bug”字样的" -> regardless of read status? It says "Sarah 发来的邮件，如果标题或正文里带 urgent 或 bug 字样的，给她记个 TODO"。This includes email_004 (read) and email_003. So both should have TODO. We'll add another to test.
        {
            "id": "email_011",
            "thread_id": "thread_011",
            "folder": "INBOX",
            "sender_id": "contact_003",
            "subject": "Fix for minor bug",
            "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
            "importance": "normal",
            "labels": ["bug"],
            "has_read": True,
            "body": "Found another bug in the dashboard. -Sarah",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        # 12 - Alice, not read, but subject contains "urgent"? No, it's a normal reply candidate. Second one to reply.
        {
            "id": "email_012",
            "thread_id": "thread_012",
            "folder": "INBOX",
            "sender_id": "contact_001",
            "subject": "Contract approval needed",
            "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
            "importance": "high",
            "labels": ["client"],
            "has_read": False,
            "body": "Hi John, please review the attached contract and let me know. Best, Alice",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
    ]

    for mail in emails:
        with open(f"emails/{mail['id']}.json", "w") as f:
            json.dump(mail, f)

    # Also create a few dummy files to confuse: .bak, .tmp
    with open("emails/email_013.json.bak", "w") as f:
        f.write("{}")
    with open("emails/.DS_Store", "w") as f:
        f.write("")
    with open("emails/old_data.csv", "w") as f:
        f.write("id,subject\n")
    
    # Create ops directory (empty initially)
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
