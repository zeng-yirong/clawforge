import os
import json
import random


def build_env():
    # Ensure base directories
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # -- Accounts --
    accounts = [
        {
            "account_id": "acc_001",
            "display_name": "Alice Johnson",
            "email_address": "alice@company.com",
            "default_signature": "Best, Alice",
            "auto_classify_enabled": True,
            "reply_templates_enabled": True,
            "task_generation_enabled": True,
            "folders": ["inbox", "sent", "spam", "archive"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # -- Contacts --
    contacts = [
        {"contact_id": "cont_001", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "cont_002", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "high"},
        {"contact_id": "cont_003", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "normal"},
        {"contact_id": "cont_004", "name": "John Manager", "email": "john.manager@company.com", "role": "Manager", "team": "Leadership", "priority": "high"},
        {"contact_id": "cont_005", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
        {"contact_id": "cont_006", "name": "Sarah Developer", "email": "sarah.dev@company.com", "role": "Developer", "team": "Engineering", "priority": "normal"},
        {"contact_id": "cont_007", "name": "Tech Weekly", "email": "newsletter@techweekly.com", "role": "Newsletter", "team": "External", "priority": "low"},
        {"contact_id": "cont_008", "name": "Tom Friend", "email": "tom.friend@gmail.com", "role": "Friend", "team": "Personal", "priority": "normal"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # -- Emails (20 total, with one correct) --
    emails = []

    # 1. Correct email from Bob Vendor (id: email_005)
    correct_email = {
        "id": "email_005",
        "thread_id": "thread_003",
        "folder": "inbox",
        "sender_id": "cont_002",
        "subject": "Meeting Confirmation: Project Sync",
        "timestamp": "2025-04-10T09:00:00Z",
        "importance": "high",
        "labels": ["work", "meeting"],
        "has_read": False,
        "body": "Hi Alice,\n\nThis is a confirmation for our project sync meeting scheduled for 2025-04-15 15:00:00 in Conference Room B.\n\nPlease prepare the following:\n- project roadmap\n- budget report\n\nLooking forward to it.\n\nBest regards,\nBob Vendor",
        "attachments": [],
        "auto_classify_suggestion": "work"
    }
    emails.append(correct_email)

    # 2. Bob Vendor – rescheduled (distractor)
    distractor1 = {
        "id": "email_002",
        "thread_id": "thread_003",
        "folder": "inbox",
        "sender_id": "cont_002",
        "subject": "Meeting Rescheduled",
        "timestamp": "2025-04-11T14:00:00Z",
        "importance": "high",
        "labels": ["work", "meeting"],
        "has_read": False,
        "body": "Hi Alice,\n\nDue to a conflict, the project sync has been moved to 2025-04-18 10:00:00 in Room A. Sorry for the change.\n\nBest,\nBob",
        "attachments": [],
        "auto_classify_suggestion": "work"
    }
    emails.append(distractor1)

    # 3. Bob Vendor – out of office (distractor)
    distractor2 = {
        "id": "email_008",
        "thread_id": "thread_006",
        "folder": "inbox",
        "sender_id": "cont_002",
        "subject": "Out of Office",
        "timestamp": "2025-04-12T08:00:00Z",
        "importance": "normal",
        "labels": ["auto"],
        "has_read": True,
        "body": "I'm out of the office until April 14. For urgent matters, please contact Sarah.\n\nBest,\nBob",
        "attachments": [],
        "auto_classify_suggestion": "work"
    }
    emails.append(distractor2)

    # 4. Lottery Scam pretending to be Bob
    spam_email = {
        "id": "email_003",
        "thread_id": "thread_666",
        "folder": "spam",
        "sender_id": "cont_005",
        "subject": "Congratulations from Bob Vendor?",
        "timestamp": "2025-04-09T00:00:00Z",
        "importance": "low",
        "labels": ["spam"],
        "has_read": False,
        "body": "You have won a free trip! Reply to claim.",
        "attachments": [],
        "auto_classify_suggestion": "spam"
    }
    emails.append(spam_email)

    # 5. HR Department
    hr_email = {
        "id": "email_001",
        "thread_id": "thread_001",
        "folder": "inbox",
        "sender_id": "cont_003",
        "subject": "Insurance Plan Changes",
        "timestamp": "2025-04-08T10:30:00Z",
        "importance": "high",
        "labels": ["hr", "benefits"],
        "has_read": False,
        "body": "Please review the updated insurance plans for 2025. Deadline: April 20.",
        "attachments": [],
        "auto_classify_suggestion": "hr"
    }
    emails.append(hr_email)

    # 6. Tech Weekly Newsletter
    newsletter_email = {
        "id": "email_004",
        "thread_id": "thread_002",
        "folder": "inbox",
        "sender_id": "cont_007",
        "subject": "Tech Weekly Digest",
        "timestamp": "2025-04-07T06:00:00Z",
        "importance": "low",
        "labels": ["newsletter"],
        "has_read": True,
        "body": "Top stories: AI advances, new frameworks...",
        "attachments": [],
        "auto_classify_suggestion": "newsletter"
    }
    emails.append(newsletter_email)

    # 7-20. Random filler emails (inbox, spam, archive)
    filler_senders = ["cont_001", "cont_004", "cont_006", "cont_008"]
    filler_subjects = ["Code Review Request", "Lunch Invitation", "Quarterly Report", "Happy Birthday!", "Project Update"]
    for i in range(7, 21):
        eid = f"email_{i:03d}"
        sender = random.choice(filler_senders)
        subject = random.choice(filler_subjects)
        body = f"This is a test email number {i}."
        folder = random.choice(["inbox", "spam", "archive"])
        importance = random.choice(["normal", "low"])
        label = ["personal"] if sender == "cont_008" else ["work"]
        email = {
            "id": eid,
            "thread_id": f"thread_{random.randint(100,200)}",
            "folder": folder,
            "sender_id": sender,
            "subject": subject,
            "timestamp": "2025-04-01T12:00:00Z",
            "importance": importance,
            "labels": label,
            "has_read": False,
            "body": body,
            "attachments": [],
            "auto_classify_suggestion": "work"
        }
        emails.append(email)

    # Write all email files
    for email in emails:
        fname = f"data/emails/{email['id']}.json"
        with open(fname, "w") as f:
            json.dump(email, f, indent=2)

    # Additional empty dirs for distraction
    os.makedirs("raw_logs", exist_ok=True)
    os.makedirs("db_dumps", exist_ok=True)


if __name__ == "__main__":
    build_env()
