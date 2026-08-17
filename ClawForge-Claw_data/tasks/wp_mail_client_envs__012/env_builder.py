import os
import json
from datetime import datetime, timedelta

def build_env():
    # Create directories
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # Helper to create email json
    def make_email(eid, sender_id, subject, folder, has_read, body, importance="normal", labels=None, auto_classify_suggestion="work"):
        labels = labels or []
        return {
            "id": eid,
            "thread_id": eid,
            "folder": folder,
            "sender_id": sender_id,
            "subject": subject,
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
            "importance": importance,
            "labels": labels,
            "has_read": has_read,
            "body": body,
            "attachments": [],
            "auto_classify_suggestion": auto_classify_suggestion
        }

    # --- Target emails (must be processed) ---
    emails = []
    # Email from John Manager - unread, inbox
    emails.append(make_email(
        eid="msg_001",
        sender_id="john_manager",
        subject="Project Status Update",
        folder="inbox",
        has_read=False,
        body="Hi team,\n\nPlease confirm your availability for next week's project meeting. I'd like to schedule it on Monday or Wednesday.\nBest,\nJohn",
        auto_classify_suggestion="work"
    ))
    # Email from HR - unread, inbox
    emails.append(make_email(
        eid="msg_002",
        sender_id="hr_department",
        subject="New Insurance Plan",
        folder="inbox",
        has_read=False,
        body="Dear employee,\n\nWe have updated our insurance plans. Please review the attached documents and complete the enrollment form by the end of the month.\nHR Department",
        auto_classify_suggestion="hr"
    ))

    # --- Distractors ---
    # Already read from John
    emails.append(make_email(
        eid="msg_003",
        sender_id="john_manager",
        subject="Old Meeting Notes",
        folder="inbox",
        has_read=True,
        body="This is an old thread, no action needed.",
        auto_classify_suggestion="work"
    ))
    # Spam from lottery scam
    emails.append(make_email(
        eid="msg_004",
        sender_id="lottery_scam",
        subject="You won!",
        folder="inbox",
        has_read=False,
        body="Congratulations! You have won $1,000,000. Click here to claim.",
        importance="high",
        auto_classify_suggestion="spam"
    ))
    # Normal work email from Sarah
    emails.append(make_email(
        eid="msg_005",
        sender_id="sarah_developer",
        subject="Code Review Request",
        folder="inbox",
        has_read=False,
        body="Can you review my latest pull request? Thanks!",
        auto_classify_suggestion="work"
    ))
    # Already archived HR email
    emails.append(make_email(
        eid="msg_006",
        sender_id="hr_department",
        subject="Benefits Reminder",
        folder="archived",
        has_read=False,
        body="Just a reminder to check your benefits.",
        auto_classify_suggestion="hr"
    ))
    # Personal email from Tom
    emails.append(make_email(
        eid="msg_007",
        sender_id="tom_friend",
        subject="Dinner this weekend?",
        folder="inbox",
        has_read=False,
        body="Hey, want to grab dinner on Saturday?",
        auto_classify_suggestion="personal"
    ))
    # Newsletter
    emails.append(make_email(
        eid="msg_008",
        sender_id="tech_weekly",
        subject="Tech Weekly Digest",
        folder="inbox",
        has_read=False,
        body="Latest tech news...",
        auto_classify_suggestion="newsletter"
    ))
    # Finance email already processed (folder = finance)
    emails.append(make_email(
        eid="msg_009",
        sender_id="bob_vendor",
        subject="Invoice #123",
        folder="finance",
        has_read=True,
        body="Please pay invoice.",
        auto_classify_suggestion="finance"
    ))

    # Write all emails
    for email in emails:
        with open(f"data/emails/{email['id']}.json", "w") as f:
            json.dump(email, f, indent=2)

    # Create contacts.json
    contacts = {
        "contacts": [
            {"contact_id": "alice_client", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
            {"contact_id": "bob_vendor", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "normal"},
            {"contact_id": "hr_department", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "high"},
            {"contact_id": "john_manager", "name": "John Manager", "email": "john.manager@company.com", "role": "Manager", "team": "Leadership", "priority": "high"},
            {"contact_id": "lottery_scam", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
            {"contact_id": "sarah_developer", "name": "Sarah Developer", "email": "sarah.dev@company.com", "role": "Developer", "team": "Engineering", "priority": "normal"},
            {"contact_id": "tech_weekly", "name": "Tech Weekly", "email": "newsletter@techweekly.com", "role": "Newsletter", "team": "External", "priority": "low"},
            {"contact_id": "tom_friend", "name": "Tom Friend", "email": "tom.friend@gmail.com", "role": "Friend", "team": "Personal", "priority": "low"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # Create accounts.json (dummy)
    accounts = {
        "accounts": [
            {"account_id": "agent_account", "display_name": "AI Assistant", "email_address": "assistant@company.com",
             "default_signature": "Best,\nAI Assistant", "auto_classify_enabled": True, "reply_templates_enabled": True,
             "task_generation_enabled": True, "folders": ["inbox", "archived", "work", "personal", "spam", "newsletter", "finance", "hr"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

if __name__ == "__main__":
    build_env()
