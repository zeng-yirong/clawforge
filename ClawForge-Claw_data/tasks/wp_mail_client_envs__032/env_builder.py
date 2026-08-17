import os
import json
import shutil

def build_env():
    # Clean and create directories
    base = "."
    for d in ["data/emails", "ops"]:
        os.makedirs(f"{base}/{d}", exist_ok=True)

    # --- Contacts ---
    contacts = [
        {"contact_id": "c1", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "c2", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "high"},
        {"contact_id": "c3", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "normal"},
        {"contact_id": "c4", "name": "John Manager", "email": "john.manager@company.com", "role": "Manager", "team": "Leadership", "priority": "normal"},
        {"contact_id": "c5", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
        {"contact_id": "c6", "name": "Tech Weekly", "email": "newsletter@techweekly.com", "role": "Newsletter", "team": "External", "priority": "low"},
        {"contact_id": "c7", "name": "Tom Friend", "email": "tom.friend@gmail.com", "role": "Friend", "team": "Personal", "priority": "normal"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # --- Accounts (minimal, not really needed for task) ---
    accounts = {
        "accounts": [{
            "account_id": "a1",
            "display_name": "Me",
            "email_address": "me@company.com",
            "default_signature": "",
            "auto_classify_enabled": True,
            "reply_templates_enabled": True,
            "task_generation_enabled": True,
            "folders": ["inbox", "sent", "archive"]
        }]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # --- Emails (the core data) ---
    emails = [
        # 1. Target: Bob Vendor, unread, high -> should be included
        {"id": "e001", "thread_id": "t1", "folder": "inbox", "sender_id": "c2",
         "subject": "Urgent: contract review needed", "timestamp": "2025-04-07T09:00:00Z",
         "importance": "high", "labels": ["vendor"], "has_read": False,
         "body": "Please review the contract and provide feedback by Friday.",
         "attachments": [], "auto_classify_suggestion": "work"},
        # 2. Target: Alice Client, unread, high -> should be included
        {"id": "e002", "thread_id": "t2", "folder": "inbox", "sender_id": "c1",
         "subject": "Q2 report deadline", "timestamp": "2025-04-07T10:30:00Z",
         "importance": "high", "labels": ["client"], "has_read": False,
         "body": "Need the Q2 report by next Tuesday.",
         "attachments": [], "auto_classify_suggestion": "work"},
        # 3. Distractor: HR, unread, high but internal (not client/vendor)
        {"id": "e003", "thread_id": "t3", "folder": "inbox", "sender_id": "c3",
         "subject": "Mandatory training next week", "timestamp": "2025-04-06T14:00:00Z",
         "importance": "high", "labels": ["hr"], "has_read": False,
         "body": "You are required to complete the annual compliance training by April 15.",
         "attachments": [], "auto_classify_suggestion": "hr"},
        # 4. Distractor: Lottery Scam, unread, low
        {"id": "e004", "thread_id": "t4", "folder": "inbox", "sender_id": "c5",
         "subject": "You won a prize!", "timestamp": "2025-04-07T08:00:00Z",
         "importance": "low", "labels": ["spam"], "has_read": False,
         "body": "Click here to claim your $1000 gift card.",
         "attachments": [], "auto_classify_suggestion": "spam"},
        # 5. Distractor: Tech Weekly, read, normal
        {"id": "e005", "thread_id": "t5", "folder": "inbox", "sender_id": "c6",
         "subject": "Your weekly tech digest", "timestamp": "2025-04-06T07:00:00Z",
         "importance": "normal", "labels": ["newsletter"], "has_read": True,
         "body": "Top stories in tech this week...",
         "attachments": [], "auto_classify_suggestion": "newsletter"},
        # 6. Distractor: Tom Friend, unread, normal
        {"id": "e006", "thread_id": "t6", "folder": "inbox", "sender_id": "c7",
         "subject": "Catch up this weekend?", "timestamp": "2025-04-05T18:00:00Z",
         "importance": "normal", "labels": ["personal"], "has_read": False,
         "body": "Hey, want to grab a coffee on Saturday?",
         "attachments": [], "auto_classify_suggestion": "personal"},
        # 7. Distractor: John Manager (internal), unread, high
        {"id": "e007", "thread_id": "t7", "folder": "inbox", "sender_id": "c4",
         "subject": "Team meeting agenda", "timestamp": "2025-04-07T11:00:00Z",
         "importance": "high", "labels": ["work"], "has_read": False,
         "body": "Please prepare slides for tomorrow's meeting.",
         "attachments": [], "auto_classify_suggestion": "work"},
    ]

    for em in emails:
        with open(f"data/emails/{em['id']}.json", "w") as f:
            json.dump(em, f, indent=2)

    # Ensure ops directory is present but empty (agent will create file there)
    # Already created

if __name__ == "__main__":
    build_env()
