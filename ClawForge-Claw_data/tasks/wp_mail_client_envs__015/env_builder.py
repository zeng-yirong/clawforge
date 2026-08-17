import os
import json
import csv

def build_env():
    # Create directory structure
    dirs = ["data/emails", "attachments", "ops"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # Accounts (optional realism)
    accounts = {
        "accounts": [
            {
                "account_id": "acc_001",
                "display_name": "Default User",
                "email_address": "user@company.com",
                "default_signature": "Best regards",
                "auto_classify_enabled": True,
                "reply_templates_enabled": True,
                "task_generation_enabled": True,
                "folders": ["inbox", "sent", "archived", "work", "personal", "finance", "hr"]
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # Contacts (optional realism)
    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
            {"contact_id": "c002", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "normal"},
            {"contact_id": "c003", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "high"},
            {"contact_id": "c004", "name": "Tom Friend", "email": "tom.friend@gmail.com", "role": "Friend", "team": "Personal", "priority": "low"},
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # --- Email 1: The one the agent needs (URGENT finance) ---
    email_urgent = {
        "id": "email_001",
        "thread_id": "thread_001",
        "folder": "inbox",
        "sender_id": "c003",  # HR Department
        "subject": "URGENT: Update Vendor Payment Information",
        "timestamp": "2025-03-20T08:30:00Z",
        "importance": "high",
        "labels": ["finance", "urgent", "action-required"],
        "has_read": False,
        "body": "Hi,\n\nPlease update the vendor payment details as follows:\n1. Change vendor VEND-003 (Bob Ltd) payment method from 'check' to 'wire_transfer'.\n2. Remove vendor VEND-007 (Dodgy Co) – it has been terminated.\n\nSave the updated CSV to ops/updated_payments.csv and keep all other records unchanged.\n\nThanks,\nLin (Finance)",
        "attachments": [
            {
                "filename": "vendor_payments.csv",
                "path": "attachments/vendor_payments.csv"
            }
        ]
    }
    with open("data/emails/email_finance_update.json", "w") as f:
        json.dump(email_urgent, f, indent=2)

    # --- Distractor emails ---
    # Newsletter
    email_news = {
        "id": "email_002",
        "thread_id": "thread_002",
        "folder": "inbox",
        "sender_id": "c005",  # not in contacts but valid
        "subject": "Tech Weekly – March Special",
        "timestamp": "2025-03-19T14:00:00Z",
        "importance": "low",
        "labels": ["newsletter"],
        "has_read": False,
        "body": "Read the latest tech news...",
        "attachments": []
    }
    with open("data/emails/email_newsletter.json", "w") as f:
        json.dump(email_news, f, indent=2)

    # Personal
    email_personal = {
        "id": "email_003",
        "thread_id": "thread_003",
        "folder": "inbox",
        "sender_id": "c004",
        "subject": "Dinner this weekend?",
        "timestamp": "2025-03-18T18:30:00Z",
        "importance": "normal",
        "labels": ["personal"],
        "has_read": False,
        "body": "Hey, want to grab dinner on Saturday?",
        "attachments": []
    }
    with open("data/emails/email_personal.json", "w") as f:
        json.dump(email_personal, f, indent=2)

    # Spam / Lottery scam
    email_spam = {
        "id": "email_004",
        "thread_id": "thread_004",
        "folder": "inbox",
        "sender_id": "c006",  # not in contacts
        "subject": "You have won $1,000,000!",
        "timestamp": "2025-03-20T06:00:00Z",
        "importance": "high",
        "labels": ["spam"],
        "has_read": False,
        "body": "Claim your prize now...",
        "attachments": []
    }
    with open("data/emails/email_spam.json", "w") as f:
        json.dump(email_spam, f, indent=2)

    # Old finance email (distractor – similar but different requirements)
    email_old_finance = {
        "id": "email_005",
        "thread_id": "thread_005",
        "folder": "inbox",
        "sender_id": "c003",
        "subject": "RE: Vendor payment review (old)",
        "timestamp": "2025-03-15T10:00:00Z",
        "importance": "normal",
        "labels": ["finance"],
        "has_read": False,
        "body": "Please ignore this old request – the changes were already applied last week.",
        "attachments": [
            {
                "filename": "vendor_payments_old.csv",
                "path": "attachments/vendor_payments_old.csv"
            }
        ]
    }
    with open("data/emails/email_finance_old.json", "w") as f:
        json.dump(email_old_finance, f, indent=2)

    # --- Create the actual CSV attachments ---
    # Main CSV (used by the correct email)
    rows = [
        ["vendor_id", "name", "payment_method", "bank_account", "status"],
        ["VEND-001", "Alice Corp", "check", "12345", "active"],
        ["VEND-003", "Bob Ltd", "check", "67890", "active"],
        ["VEND-005", "Charlie Inc", "wire_transfer", "11111", "active"],
        ["VEND-007", "Dodgy Co", "check", "22222", "active"],
        ["VEND-009", "Eve LLC", "wire_transfer", "33333", "active"],
    ]
    with open("attachments/vendor_payments.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    # Distractor old CSV
    old_rows = [
        ["vendor_id", "name", "payment_method", "bank_account", "status"],
        ["VEND-003", "Bob Ltd", "check", "67890", "active"],
        ["VEND-007", "Dodgy Co", "check", "22222", "active"],
    ]
    with open("attachments/vendor_payments_old.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(old_rows)

if __name__ == "__main__":
    build_env()
