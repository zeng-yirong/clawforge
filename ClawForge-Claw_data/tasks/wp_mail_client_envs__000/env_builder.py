import os
import json

def build_env():
    # Create data directories
    os.makedirs("data/emails", exist_ok=True)
    
    # Contacts
    contacts = [
        {"contact_id": "client_alice", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "client_bob", "name": "Bob Client", "email": "bob.client@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "vendor_bob", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "normal"},
        {"contact_id": "hr_department", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "normal"},
        {"contact_id": "lottery_scam", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
        {"contact_id": "internal_lead", "name": "John Manager", "email": "john.manager@company.com", "role": "Manager", "team": "Leadership", "priority": "high"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)
    
    # Accounts (minimal)
    accounts = [{
        "account_id": "alice_main",
        "display_name": "Alice Frontdesk",
        "email_address": "alice@company.com",
        "default_signature": "Best, Alice",
        "auto_classify_enabled": True,
        "reply_templates_enabled": True,
        "task_generation_enabled": True,
        "folders": ["inbox", "sent", "archive", "spam"]
    }]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)
    
    # Emails – mix of real and distractors
    emails = [
        # Email 001 – target: Client Alice, high, unread
        {"id": "email_001", "thread_id": "thread_1", "folder": "inbox", "sender_id": "client_alice",
         "subject": "Urgent: Q4 report missing", "timestamp": "2025-03-10T08:00:00Z",
         "importance": "high", "labels": [], "has_read": False,
         "body": "Please send the Q4 financial report by today.", "attachments": [],
         "auto_classify_suggestion": "work"},
        # Email 002 – Client Alice but already read
        {"id": "email_002", "thread_id": "thread_1", "folder": "inbox", "sender_id": "client_alice",
         "subject": "Re: previous message", "timestamp": "2025-03-09T10:00:00Z",
         "importance": "high", "labels": [], "has_read": True,
         "body": "Thanks for the update.", "attachments": [],
         "auto_classify_suggestion": "work"},
        # Email 003 – target: Client Bob, high, unread
        {"id": "email_003", "thread_id": "thread_2", "folder": "inbox", "sender_id": "client_bob",
         "subject": "Contract renewal", "timestamp": "2025-03-10T09:30:00Z",
         "importance": "high", "labels": [], "has_read": False,
         "body": "We need to sign the renewal by Friday.", "attachments": [],
         "auto_classify_suggestion": "work"},
        # Email 004 – Vendor, high, unread (wrong role)
        {"id": "email_004", "thread_id": "thread_3", "folder": "inbox", "sender_id": "vendor_bob",
         "subject": "Invoice due", "timestamp": "2025-03-10T07:00:00Z",
         "importance": "high", "labels": [], "has_read": False,
         "body": "Please remit payment for invoice #1234.", "attachments": [],
         "auto_classify_suggestion": "work"},
        # Email 005 – Client Alice, low, unread
        {"id": "email_005", "thread_id": "thread_4", "folder": "inbox", "sender_id": "client_alice",
         "subject": "Hi", "timestamp": "2025-03-10T06:00:00Z",
         "importance": "low", "labels": [], "has_read": False,
         "body": "Just saying hello.", "attachments": [],
         "auto_classify_suggestion": "personal"},
        # Email 006 – HR, high, unread (wrong role)
        {"id": "email_006", "thread_id": "thread_5", "folder": "inbox", "sender_id": "hr_department",
         "subject": "Meeting reminder", "timestamp": "2025-03-10T08:30:00Z",
         "importance": "high", "labels": [], "has_read": False,
         "body": "Town hall at 3pm.", "attachments": [],
         "auto_classify_suggestion": "work"},
        # Email 007 – Spammer, high, unread (wrong role)
        {"id": "email_007", "thread_id": "thread_6", "folder": "inbox", "sender_id": "lottery_scam",
         "subject": "You won!", "timestamp": "2025-03-10T05:00:00Z",
         "importance": "high", "labels": [], "has_read": False,
         "body": "Claim your prize now!", "attachments": [],
         "auto_classify_suggestion": "spam"},
        # Email 008 – target: Client Alice, high, unread (second)
        {"id": "email_008", "thread_id": "thread_7", "folder": "inbox", "sender_id": "client_alice",
         "subject": "Urgent: Need approval", "timestamp": "2025-03-10T10:00:00Z",
         "importance": "high", "labels": [], "has_read": False,
         "body": "Please approve the budget request.", "attachments": [],
         "auto_classify_suggestion": "work"},
    ]
    for email in emails:
        with open(f"data/emails/{email['id']}.json", "w") as f:
            json.dump(email, f, indent=2)

if __name__ == "__main__":
    build_env()
