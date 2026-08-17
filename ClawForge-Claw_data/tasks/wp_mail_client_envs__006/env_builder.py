import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    # 干扰文件
    with open("ops/old_report.json", "w") as f:
        json.dump({"irrelevant": True}, f)

    # 联系人
    contacts = [
        {"contact_id": "c001", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "c002", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "normal"},
        {"contact_id": "c003", "name": "John Manager", "email": "john.manager@company.com", "role": "Manager", "team": "Leadership", "priority": "high"},
        {"contact_id": "c004", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 账号
    accounts = [
        {"account_id": "acct001", "display_name": "John Manager", "email_address": "john.manager@company.com", "default_signature": "Best, John", "auto_classify_enabled": True, "reply_templates_enabled": True, "task_generation_enabled": True, "folders": ["inbox", "sent", "drafts", "archive", "work", "personal", "spam"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # 邮件
    emails = [
        {
            "id": "mail_001",
            "thread_id": "th001",
            "folder": "inbox",
            "sender_id": "alice@clientcorp.com",
            "subject": "Contract Renewal",
            "timestamp": "2025-03-20T09:15:00Z",
            "importance": "high",
            "labels": ["important"],
            "has_read": False,
            "has_archived": False,
            "body": "Dear John,\n\nWe need to finalize the contract renewal. Please send me the updated proposal. Also, I'd like to schedule a video call next Tuesday at 2 PM to discuss details.\n\nTask: Prepare quarterly review document by Friday.\n\nBest,\nAlice",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        {
            "id": "mail_002",
            "thread_id": "th001",
            "folder": "archive",
            "sender_id": "alice@clientcorp.com",
            "subject": "Follow-up on meeting",
            "timestamp": "2025-03-19T14:30:00Z",
            "importance": "normal",
            "labels": [],
            "has_read": False,
            "has_archived": True,
            "body": "Hi John, just a note about yesterday's meeting. Thanks!",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        {
            "id": "mail_003",
            "thread_id": "th002",
            "folder": "inbox",
            "sender_id": "alice@clientcorp.com",
            "subject": "Budget proposal",
            "timestamp": "2025-03-18T10:00:00Z",
            "importance": "normal",
            "labels": ["finance"],
            "has_read": True,
            "has_archived": False,
            "body": "John, attached is the budget proposal for Q2. Please review.",
            "attachments": [],
            "auto_classify_suggestion": "finance"
        },
        {
            "id": "mail_004",
            "thread_id": "th003",
            "folder": "inbox",
            "sender_id": "bob@vendor-services.com",
            "subject": "Invoice for March",
            "timestamp": "2025-03-21T08:00:00Z",
            "importance": "low",
            "labels": [],
            "has_read": False,
            "has_archived": False,
            "body": "Dear Sir, please find attached the invoice for March services. Kindly process payment.",
            "attachments": [],
            "auto_classify_suggestion": "finance"
        },
        {
            "id": "mail_005",
            "thread_id": "th004",
            "folder": "spam",
            "sender_id": "winner@lottery-scam.com",
            "subject": "You are a winner!",
            "timestamp": "2025-03-22T12:00:00Z",
            "importance": "low",
            "labels": [],
            "has_read": False,
            "has_archived": False,
            "body": "Congratulations! You have won $1,000,000. Click here to claim.",
            "attachments": [],
            "auto_classify_suggestion": "spam"
        }
    ]
    for email in emails:
        with open(f"data/emails/{email['id']}.json", "w") as f:
            json.dump(email, f, indent=2)

if __name__ == "__main__":
    build_env()
