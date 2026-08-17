import os
import json
from datetime import datetime, timedelta

BASE = "."  # cwd is .

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def build_env():
    # 1. accounts.json
    accounts = [
        {
            "account_id": "john.manager@company.com",
            "display_name": "John Manager",
            "email_address": "john.manager@company.com",
            "default_signature": "Best, John Manager",
            "auto_classify_enabled": True,
            "reply_templates_enabled": True,
            "task_generation_enabled": True,
            "folders": ["inbox", "work", "personal"]
        },
        {
            "account_id": "sarah.dev@company.com",
            "display_name": "Sarah Developer",
            "email_address": "sarah.dev@company.com",
            "default_signature": "Cheers, Sarah",
            "auto_classify_enabled": True,
            "reply_templates_enabled": False,
            "task_generation_enabled": False,
            "folders": ["inbox", "work"]
        }
    ]
    write_json("data/accounts.json", accounts)

    # 2. contacts.json
    contacts = [
        {"contact_id": "alice", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "bob", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "normal"},
        {"contact_id": "hr_dept", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "normal"},
        {"contact_id": "john", "name": "John Manager", "email": "john.manager@company.com", "role": "Manager", "team": "Leadership", "priority": "normal"},
        {"contact_id": "lottery", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
        {"contact_id": "sarah_dev", "name": "Sarah Developer", "email": "sarah.dev@company.com", "role": "Developer", "team": "Engineering", "priority": "high"},
        {"contact_id": "tech_weekly", "name": "Tech Weekly", "email": "newsletter@techweekly.com", "role": "Newsletter", "team": "External", "priority": "low"},
        {"contact_id": "tom", "name": "Tom Friend", "email": "tom.friend@gmail.com", "role": "Friend", "team": "Personal", "priority": "normal"}
    ]
    write_json("data/contacts.json", contacts)

    # 3. emails - 多封邮件，不同账户、重要性、已读、标签
    base_time = datetime(2025, 6, 1, 10, 0, 0)

    emails = [
        # 1) John's unread high-importance from Alice -> should be replied
        {
            "id": "msg001",
            "thread_id": "th001",
            "folder": "inbox",
            "sender_id": "alice",
            "subject": "Q3 budget proposal review",
            "timestamp": (base_time - timedelta(hours=3)).isoformat(),
            "importance": "high",
            "labels": ["work", "urgent"],
            "has_read": False,
            "body": "John, please review the Q3 budget proposal attached. Need your approval by Friday.",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        # 2) John's unread high-importance from Sarah (developer) -> should be replied
        {
            "id": "msg002",
            "thread_id": "th002",
            "folder": "inbox",
            "sender_id": "sarah_dev",
            "subject": "Code review request for PR #42",
            "timestamp": (base_time - timedelta(hours=5)).isoformat(),
            "importance": "high",
            "labels": ["work", "code-review"],
            "has_read": False,
            "body": "Hi John, can you review my pull request #42 when you get a chance? It's for the new logging subsystem.",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        # 3) John's unread high-importance with label "todo"/"action" -> extract TODO
        {
            "id": "msg003",
            "thread_id": "th003",
            "folder": "inbox",
            "sender_id": "hr_dept",
            "subject": "Mandatory compliance training deadline",
            "timestamp": (base_time - timedelta(hours=1)).isoformat(),
            "importance": "high",
            "labels": ["action", "hr", "training"],
            "has_read": False,
            "body": "John, you need to complete the annual compliance training by June 15. Please sign up at the training portal.",
            "attachments": [],
            "auto_classify_suggestion": "hr"
        },
        # 4) John's read high-importance -> should NOT be replied (already read)
        {
            "id": "msg004",
            "thread_id": "th004",
            "folder": "inbox",
            "sender_id": "bob",
            "subject": "Vendor contract renewal",
            "timestamp": (base_time - timedelta(days=2)).isoformat(),
            "importance": "high",
            "labels": ["work", "contract"],
            "has_read": True,
            "body": "Reminder: the vendor contract expires next month. Please review and sign.",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        # 5) John's unread low-importance -> should NOT be replied, but should be archived (low importance + read? no, unread low -> not archived per rules? archived only read low or spam. So keep unread low, not archived)
        {
            "id": "msg005",
            "thread_id": "th005",
            "folder": "inbox",
            "sender_id": "tech_weekly",
            "subject": "Tech Weekly: AI trends in 2025",
            "timestamp": (base_time - timedelta(hours=12)).isoformat(),
            "importance": "low",
            "labels": ["newsletter"],
            "has_read": False,
            "body": "Check out the latest AI trends...",
            "attachments": [],
            "auto_classify_suggestion": "newsletter"
        },
        # 6) John's read low-importance -> should be archived
        {
            "id": "msg006",
            "thread_id": "th006",
            "folder": "inbox",
            "sender_id": "tom",
            "subject": "Thanks for the dinner invite",
            "timestamp": (base_time - timedelta(days=7)).isoformat(),
            "importance": "low",
            "labels": ["personal", "social"],
            "has_read": True,
            "body": "Thanks for the dinner! Let's do it again soon.",
            "attachments": [],
            "auto_classify_suggestion": "personal"
        },
        # 7) John's unread spam -> should be archived (spam label)
        {
            "id": "msg007",
            "thread_id": "th007",
            "folder": "spam",
            "sender_id": "lottery",
            "subject": "You won a prize!",
            "timestamp": (base_time - timedelta(minutes=30)).isoformat(),
            "importance": "low",
            "labels": ["spam"],
            "has_read": False,
            "body": "Click here to claim your prize...",
            "attachments": [],
            "auto_classify_suggestion": "spam"
        },
        # 8) Sarah's unread high-importance -> should NOT be processed (not John's account)
        {
            "id": "msg008",
            "thread_id": "th008",
            "folder": "inbox",
            "sender_id": "alice",
            "subject": "For Sarah: project update",
            "timestamp": base_time.isoformat(),
            "importance": "high",
            "labels": ["work"],
            "has_read": False,
            "body": "Sarah, the client wants a status update for the dashboard.",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        # 9) Duplicate/induced: John's read spam? Not needed.
    ]

    # Determine account for each email: assign sender's account? Actually email belongs to recipient. We need to know recipient. For simplicity, all emails are received by John except msg008 which is received by Sarah. But we didn't store recipient. We can add a field "recipient" or infer from context. Let's add a "recipient_id" field to each email so agent can identify whose inbox it is.
    # According to schema, there is no recipient, but we can add it. Or we can treat emails as in John's inbox by default, except msg008 where we set recipient_id to sarah.dev. To be realistic, let's add recipient field. Schema says data/emails/<id>.json has keys: id, thread_id, folder, sender_id, subject, timestamp, importance, labels, has_read, body, attachments, auto_classify_suggestion. It does not explicitly include recipient. But for this task, we need to identify which account receives. We can add a key "recipient_id" as extra. That's fine.
    for email in emails:
        if email["id"] == "msg008":
            email["recipient_id"] = "sarah.dev@company.com"
        else:
            email["recipient_id"] = "john.manager@company.com"
        write_json(f"data/emails/{email['id']}.json", email)

    # 4. Create ops directory (empty)
    os.makedirs("ops", exist_ok=True)

    # 5. Create some distractor files
    with open("README.txt", "w") as f:
        f.write("This is a test email environment.\n")
    with open("config.json", "w") as f:
        json.dump({"version": "1.0", "environment": "mail"}, f)

if __name__ == "__main__":
    build_env()
