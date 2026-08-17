import json
import os

def build_env():
    # 创建目录
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 联系人
    contacts = [
        {"contact_id": "c001", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "c002", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "high"},
        {"contact_id": "c003", "name": "John Manager", "email": "john.manager@company.com", "role": "Manager", "team": "Leadership", "priority": "high"},
        {"contact_id": "c004", "name": "Tom Friend", "email": "tom.friend@gmail.com", "role": "Friend", "team": "Personal", "priority": "low"},
        {"contact_id": "c005", "name": "Tech Weekly", "email": "newsletter@techweekly.com", "role": "Newsletter", "team": "External", "priority": "low"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 账户
    account = {
        "account_id": "a001",
        "display_name": "John Manager",
        "email_address": "manager@company.com",
        "default_signature": "Best regards,\nJohn",
        "auto_classify_enabled": True,
        "reply_templates_enabled": True,
        "task_generation_enabled": True,
        "folders": ["inbox", "archive", "sent", "drafts"]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(account, f, indent=2)

    # 生成 10 封邮件，其中 3 封为 high + 未读（ID: email_002, email_005, email_008）
    emails = [
        {"id": "email_001", "thread_id": "t1", "folder": "inbox", "sender_id": "c004", "subject": "Hey, how are you?", "timestamp": "2025-03-01T10:00:00Z", "importance": "low", "labels": [], "has_read": True, "body": "Just checking in.", "attachments": [], "auto_classify_suggestion": "personal"},
        {"id": "email_002", "thread_id": "t2", "folder": "inbox", "sender_id": "c001", "subject": "Urgent: Payment pending", "timestamp": "2025-03-01T11:00:00Z", "importance": "high", "labels": ["urgent", "finance"], "has_read": False, "body": "Dear John, we still haven't received the payment for invoice #1234. Please address immediately or we may need to escalate. Best, Alice", "attachments": [], "auto_classify_suggestion": "finance"},
        {"id": "email_003", "thread_id": "t3", "folder": "inbox", "sender_id": "c005", "subject": "Tech Weekly Digest", "timestamp": "2025-03-01T12:00:00Z", "importance": "low", "labels": [], "has_read": False, "body": "Top stories this week...", "attachments": [], "auto_classify_suggestion": "newsletter"},
        {"id": "email_004", "thread_id": "t4", "folder": "inbox", "sender_id": "c002", "subject": "Service renewal", "timestamp": "2025-03-01T13:00:00Z", "importance": "normal", "labels": [], "has_read": True, "body": "Your subscription is about to expire.", "attachments": [], "auto_classify_suggestion": "work"},
        {"id": "email_005", "thread_id": "t5", "folder": "inbox", "sender_id": "c002", "subject": "Critical system failure", "timestamp": "2025-03-01T14:00:00Z", "importance": "high", "labels": ["urgent", "support"], "has_read": False, "body": "Critical: Our main server is down. Immediate action required. We need your approval for emergency maintenance. - Bob", "attachments": [], "auto_classify_suggestion": "work"},
        {"id": "email_006", "thread_id": "t6", "folder": "inbox", "sender_id": "c004", "subject": "Party invitation", "timestamp": "2025-03-01T15:00:00Z", "importance": "low", "labels": [], "has_read": True, "body": "You are invited to my birthday party!", "attachments": [], "auto_classify_suggestion": "personal"},
        {"id": "email_007", "thread_id": "t7", "folder": "inbox", "sender_id": "c001", "subject": "Follow-up on proposal", "timestamp": "2025-03-01T16:00:00Z", "importance": "normal", "labels": [], "has_read": False, "body": "Just a reminder about our proposal discussion.", "attachments": [], "auto_classify_suggestion": "work"},
        {"id": "email_008", "thread_id": "t8", "folder": "inbox", "sender_id": "c003", "subject": "Meeting schedule conflict", "timestamp": "2025-03-01T17:00:00Z", "importance": "high", "labels": ["urgent", "meeting"], "has_read": False, "body": "John, we have a conflict with the product review meeting on Friday. Please check your calendar and suggest alternatives. - John Manager", "attachments": [], "auto_classify_suggestion": "work"},
        {"id": "email_009", "thread_id": "t9", "folder": "inbox", "sender_id": "c004", "subject": "Lunch tomorrow?", "timestamp": "2025-03-01T18:00:00Z", "importance": "low", "labels": [], "has_read": False, "body": "Are you free for lunch tomorrow?", "attachments": [], "auto_classify_suggestion": "personal"},
        {"id": "email_010", "thread_id": "t10", "folder": "spam", "sender_id": "c004", "subject": "You won a lottery!", "timestamp": "2025-03-01T19:00:00Z", "importance": "low", "labels": [], "has_read": False, "body": "Congratulations, you have won $1,000,000!", "attachments": [], "auto_classify_suggestion": "spam"},
    ]
    for em in emails:
        with open(f"data/emails/{em['id']}.json", "w") as f:
            json.dump(em, f, indent=2)

if __name__ == "__main__":
    build_env()
