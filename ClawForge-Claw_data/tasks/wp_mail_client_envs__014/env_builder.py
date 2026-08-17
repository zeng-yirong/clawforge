import os
import json

def build_env():
    # 创建目录
    os.makedirs("inbox", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # 联系人数据
    contacts = [
        {"contact_id": "alice_client", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "bob_vendor", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "normal"},
        {"contact_id": "john_manager", "name": "John Manager", "email": "john.manager@company.com", "role": "Manager", "team": "Leadership", "priority": "high"},
        {"contact_id": "sarah_developer", "name": "Sarah Developer", "email": "sarah.dev@company.com", "role": "Developer", "team": "Engineering", "priority": "normal"},
        {"contact_id": "tom_friend", "name": "Tom Friend", "email": "tom.friend@gmail.com", "role": "Friend", "team": "Personal", "priority": "low"},
        {"contact_id": "hr_department", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "normal"},
        {"contact_id": "lottery_scam", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
        {"contact_id": "tech_weekly", "name": "Tech Weekly", "email": "newsletter@techweekly.com", "role": "Newsletter", "team": "External", "priority": "low"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

    # 账户数据（简单）
    account = {
        "account_id": "admin",
        "display_name": "Admin",
        "email_address": "admin@company.com",
        "default_signature": "Best, Admin",
        "auto_classify_enabled": True,
        "reply_templates_enabled": True,
        "task_generation_enabled": True,
        "folders": ["Inbox", "Sent", "Archive", "Drafts"]
    }
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": [account]}, f)

    # 邮件列表
    emails = [
        {
            "id": "email_001",
            "thread_id": "thread_001",
            "folder": "Inbox",
            "sender_id": "alice_client",
            "subject": "Meeting Confirmation",
            "timestamp": "2025-03-10T09:00:00Z",
            "importance": "high",
            "labels": [],
            "has_read": False,
            "body": "Hi, we need to finalize the meeting time. Action: Send invite to all participants.",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        {
            "id": "email_002",
            "thread_id": "thread_002",
            "folder": "Inbox",
            "sender_id": "lottery_scam",
            "subject": "You won!",
            "timestamp": "2025-03-10T09:01:00Z",
            "importance": "high",
            "labels": [],
            "has_read": False,
            "body": "You won $1,000,000! Click here to claim.",
            "attachments": [],
            "auto_classify_suggestion": "spam"
        },
        {
            "id": "email_003",
            "thread_id": "thread_003",
            "folder": "Inbox",
            "sender_id": "hr_department",
            "subject": "Annual Leave Policy",
            "timestamp": "2025-03-10T09:02:00Z",
            "importance": "normal",
            "labels": ["hr"],
            "has_read": False,
            "body": "Please find attached the updated policy. No action needed.",
            "attachments": [],
            "auto_classify_suggestion": "hr"
        },
        {
            "id": "email_004",
            "thread_id": "thread_004",
            "folder": "Inbox",
            "sender_id": "tom_friend",
            "subject": "Weekend Plans",
            "timestamp": "2025-03-10T09:03:00Z",
            "importance": "low",
            "labels": ["personal"],
            "has_read": False,
            "body": "Hey, want to grab a coffee this weekend?",
            "attachments": [],
            "auto_classify_suggestion": "personal"
        },
        {
            "id": "email_005",
            "thread_id": "thread_005",
            "folder": "Inbox",
            "sender_id": "john_manager",
            "subject": "Project Report Review",
            "timestamp": "2025-03-10T09:04:00Z",
            "importance": "high",
            "labels": ["work"],
            "has_read": False,
            "body": "John here. Please review the project report and provide feedback. TODO: Review report by Friday.",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        {
            "id": "email_006",
            "thread_id": "thread_006",
            "folder": "Inbox",
            "sender_id": "tech_weekly",
            "subject": "Tech Weekly Digest",
            "timestamp": "2025-03-10T09:05:00Z",
            "importance": "low",
            "labels": ["newsletter"],
            "has_read": False,
            "body": "Latest tech news... no action required.",
            "attachments": [],
            "auto_classify_suggestion": "newsletter"
        },
        {
            "id": "email_007",
            "thread_id": "thread_007",
            "folder": "Inbox",
            "sender_id": "sarah_developer",
            "subject": "Code Review Request",
            "timestamp": "2025-03-10T09:06:00Z",
            "importance": "high",
            "labels": ["work"],
            "has_read": False,
            "body": "Can you take a look at the code? Action: Review PR #123.",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        {
            "id": "email_008",
            "thread_id": "thread_008",
            "folder": "Inbox",
            "sender_id": "bob_vendor",
            "subject": "Invoice Attached",
            "timestamp": "2025-03-10T09:07:00Z",
            "importance": "high",
            "labels": ["finance"],
            "has_read": False,
            "body": "Please process the attached invoice. Payment due in 30 days.",
            "attachments": [{"name": "invoice.pdf", "type": "application/pdf"}],
            "auto_classify_suggestion": "finance"
        },
        {
            "id": "email_009",
            "thread_id": "thread_009",
            "folder": "Inbox",
            "sender_id": "lottery_scam",
            "subject": "Special Offer",
            "timestamp": "2025-03-10T09:08:00Z",
            "importance": "low",
            "labels": [],
            "has_read": False,
            "body": "Click here to claim your prize.",
            "attachments": [],
            "auto_classify_suggestion": "spam"
        },
        {
            "id": "email_010",
            "thread_id": "thread_010",
            "folder": "Inbox",
            "sender_id": "alice_client",
            "subject": "Thanks",
            "timestamp": "2025-03-10T09:09:00Z",
            "importance": "normal",
            "labels": [],
            "has_read": False,
            "body": "Thanks for your help! Much appreciated.",
            "attachments": [],
            "auto_classify_suggestion": "work"
        }
    ]

    for email in emails:
        with open(f"inbox/{email['id']}.json", "w") as f:
            json.dump(email, f)

    # 干扰文件
    with open("inbox/readme.txt", "w") as f:
        f.write("This is a text file, not a JSON email.")

    # 无效JSON（缺少字段）
    with open("inbox/invalid.json", "w") as f:
        f.write('{"id": "x"')   # 不完整的JSON

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
