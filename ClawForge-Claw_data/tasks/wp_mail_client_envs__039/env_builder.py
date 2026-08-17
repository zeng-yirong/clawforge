import os
import json
from datetime import datetime, timedelta

def build_env():
    # Create directories
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # Helper to create email file
    def write_email(record_id, thread_id, folder, sender_id, subject, timestamp,
                    importance, labels, has_read, body, attachments, auto_classify_suggestion):
        email = {
            "id": record_id,
            "thread_id": thread_id,
            "folder": folder,
            "sender_id": sender_id,
            "subject": subject,
            "timestamp": timestamp,
            "importance": importance,
            "labels": labels,
            "has_read": has_read,
            "body": body,
            "attachments": attachments,
            "auto_classify_suggestion": auto_classify_suggestion
        }
        with open(f"data/emails/{record_id}.json", "w") as f:
            json.dump(email, f, indent=2)

    base_time = datetime.now() - timedelta(days=7)

    # Genuine newsletter, unread
    write_email(
        record_id="email_01",
        thread_id="thread_news_001",
        folder="inbox",
        sender_id="newsletter@techweekly.com",
        subject="Weekly Tech Digest: AI Breakthroughs",
        timestamp=(base_time + timedelta(hours=2)).isoformat(),
        importance="low",
        labels=["newsletter", "tech"],
        has_read=False,
        body="This week's top stories...",
        attachments=[],
        auto_classify_suggestion="newsletter"
    )

    # Newsletter, but already read
    write_email(
        record_id="email_02",
        thread_id="thread_news_002",
        folder="inbox",
        sender_id="newsletter@techweekly.com",
        subject="Tech Weekly – Weekend Special",
        timestamp=(base_time + timedelta(hours=5)).isoformat(),
        importance="low",
        labels=["newsletter", "tech"],
        has_read=True,
        body="Check out these deals...",
        attachments=[],
        auto_classify_suggestion="newsletter"
    )

    # Spam, unread (should not be included)
    write_email(
        record_id="email_03",
        thread_id="thread_spam_001",
        folder="inbox",
        sender_id="winner@lottery-scam.com",
        subject="YOU WON $1,000,000!!!",
        timestamp=(base_time + timedelta(hours=1)).isoformat(),
        importance="high",
        labels=["spam"],
        has_read=False,
        body="Click here to claim your prize...",
        attachments=[],
        auto_classify_suggestion="spam"
    )

    # HR, unread (no newsletter label)
    write_email(
        record_id="email_04",
        thread_id="thread_hr_001",
        folder="inbox",
        sender_id="hr@company.com",
        subject="Updated Company Policy",
        timestamp=(base_time + timedelta(days=1)).isoformat(),
        importance="normal",
        labels=["hr", "policy"],
        has_read=False,
        body="Please review the updated policy document...",
        attachments=[],
        auto_classify_suggestion="hr"
    )

    # Newsletter, unread, but already in archive folder – still unread, should be counted
    write_email(
        record_id="email_05",
        thread_id="thread_news_003",
        folder="archive",
        sender_id="newsletter@techweekly.com",
        subject="Tech Weekly: Cloud Trends",
        timestamp=(base_time + timedelta(days=2)).isoformat(),
        importance="low",
        labels=["newsletter"],
        has_read=False,
        body="Cloud is the future...",
        attachments=[],
        auto_classify_suggestion="newsletter"
    )

    # Another newsletter, unread
    write_email(
        record_id="email_06",
        thread_id="thread_news_004",
        folder="inbox",
        sender_id="newsletter@techweekly.com",
        subject="Tech Weekly: Cybersecurity Essentials",
        timestamp=(base_time + timedelta(days=3)).isoformat(),
        importance="low",
        labels=["newsletter", "security"],
        has_read=False,
        body="Stay safe online...",
        attachments=[],
        auto_classify_suggestion="newsletter"
    )

    # Newsletter, unread but auto_classify_suggestion is wrong (still label includes newsletter)
    write_email(
        record_id="email_07",
        thread_id="thread_news_005",
        folder="inbox",
        sender_id="alice@clientcorp.com",
        subject="Re: Project Update – Newsletter marketing",
        timestamp=(base_time + timedelta(hours=8)).isoformat(),
        importance="high",
        labels=["newsletter", "work"],
        has_read=False,
        body="Let's discuss the newsletter campaign...",
        attachments=[],
        auto_classify_suggestion="work"
    )

    # A work email (no newsletter label)
    write_email(
        record_id="email_08",
        thread_id="thread_work_001",
        folder="inbox",
        sender_id="john.manager@company.com",
        subject="Q3 Budget Review",
        timestamp=(base_time + timedelta(days=4)).isoformat(),
        importance="high",
        labels=["work", "finance"],
        has_read=False,
        body="Please prepare the Q3 budget report...",
        attachments=[],
        auto_classify_suggestion="work"
    )

    # Create dummy accounts.json and contacts.json (not used by task, but for realism)
    accounts = [
        {
            "account_id": "acc_001",
            "display_name": "Main Account",
            "email_address": "me@company.com",
            "default_signature": "Best regards\nJohn",
            "auto_classify_enabled": True,
            "reply_templates_enabled": True,
            "task_generation_enabled": True,
            "folders": ["inbox", "archive", "work", "personal", "spam", "newsletter", "finance", "hr"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "c001", "name": "Tech Weekly", "email": "newsletter@techweekly.com", "role": "Newsletter", "team": "External", "priority": "low"},
        {"contact_id": "c002", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "normal"},
        {"contact_id": "c003", "name": "John Manager", "email": "john.manager@company.com", "role": "Manager", "team": "Leadership", "priority": "high"},
        {"contact_id": "c004", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "normal"},
        {"contact_id": "c005", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "high"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
