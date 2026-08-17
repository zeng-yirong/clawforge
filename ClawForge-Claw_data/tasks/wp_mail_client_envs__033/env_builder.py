import os
import json
from datetime import datetime, timezone

def build_env():
    # Ensure base directories
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Contacts
    contacts = [
        {"contact_id": "hr_dept", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "high"},
        {"contact_id": "bob_vendor", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "normal"},
        {"contact_id": "alice_client", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "lottery_scam", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
        {"contact_id": "sarah_dev", "name": "Sarah Developer", "email": "sarah.dev@company.com", "role": "Developer", "team": "Engineering", "priority": "normal"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # Helper to build email dict
    def make_email(eid, thread, folder, sender, subject, ts_str, importance, labels, has_read, body, attachments, auto_classify):
        return {
            "id": eid,
            "thread_id": thread,
            "folder": folder,
            "sender_id": sender,
            "subject": subject,
            "timestamp": ts_str,
            "importance": importance,
            "labels": labels,
            "has_read": has_read,
            "body": body,
            "attachments": attachments,
            "auto_classify_suggestion": auto_classify
        }

    ts = "2025-03-21T10:00:00Z"
    emails = [
        # Valid HR emails (unread, high/normal, not archived, not spam)
        make_email("em001", "thr001", "inbox", "hr_dept", "Q1 Performance Review", ts, "high", ["performance"], False,
                   "Please review your Q1 goals. This is urgent.", [], "hr"),
        make_email("em002", "thr002", "inbox", "hr_dept", "Holiday Schedule 2025", ts, "normal", ["holiday"], False,
                   "Attached is the holiday schedule for the year.", [], "hr"),
        # HR email but low importance (should be excluded)
        make_email("em003", "thr003", "inbox", "hr_dept", "Office Party Reminder", ts, "low", ["social"], False,
                   "Don't forget the party!", [], "hr"),
        # HR email but archived (should be excluded)
        make_email("em004", "thr004", "archive", "hr_dept", "Old Benefits Info", ts, "high", ["archive"], False,
                   "This is archived.", [], "hr"),
        # HR email but already read (should be excluded)
        make_email("em005", "thr005", "inbox", "hr_dept", "Training Update", ts, "high", ["training"], True,
                   "You've read this.", [], "hr"),
        # Vendor email (not HR)
        make_email("em006", "thr006", "inbox", "bob_vendor", "Contract Renewal", ts, "high", ["contract"], False,
                   "Please sign the renewal.", [], "work"),
        # Spam email (should be excluded)
        make_email("em007", "thr007", "inbox", "lottery_scam", "You Won!", ts, "high", ["spam"], False,
                   "Claim your prize now!", [], "spam"),
        # Another HR email (normal, unread, inbox, body does NOT contain urgent)
        make_email("em008", "thr008", "inbox", "hr_dept", "Company Policy Update", ts, "normal", ["policy"], False,
                   "Please read the updated policy document.", [], "hr"),
        # Developer email (not HR, but importance high, unread – should be excluded)
        make_email("em009", "thr009", "inbox", "sarah_dev", "Code Review Request", ts, "high", ["dev"], False,
                   "Can you review my PR?", [], "work")
    ]

    for email in emails:
        fname = f"data/emails/{email['id']}.json"
        with open(fname, "w") as f:
            json.dump(email, f, indent=2)

if __name__ == "__main__":
    build_env()
