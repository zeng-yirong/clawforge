import os
import json

def build_env():
    # 创建目录结构
    dirs = ["data/emails", "ops"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 联系人数据（供参考）
    contacts = {
        "contacts": [
            {"contact_id": "alice_client", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
            {"contact_id": "bob_vendor", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "high"},
            {"contact_id": "hr_dept", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "normal"},
            {"contact_id": "lottery_scam", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 账户数据
    accounts = {
        "accounts": [
            {"account_id": "main", "display_name": "Main User", "email_address": "user@company.com", "default_signature": "Best,\nUser", "auto_classify_enabled": True, "reply_templates_enabled": True, "task_generation_enabled": True, "folders": ["inbox", "archive", "spam", "work", "personal"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 生成 10 封邮件
    emails = [
        # msg001 – alice high（干扰）
        {"id": "msg001", "thread_id": "t1", "folder": "inbox", "sender_id": "alice@clientcorp.com", "subject": "Proposal review", "timestamp": "2025-03-20T09:00:00Z", "importance": "high", "labels": ["work"], "has_read": False, "body": "Please review the attached proposal.", "attachments": [], "auto_classify_suggestion": "work"},
        # msg002 – bob high（目标）
        {"id": "msg002", "thread_id": "t2", "folder": "inbox", "sender_id": "bob@vendor-services.com", "subject": "URGENT: Payment overdue", "timestamp": "2025-03-20T10:15:00Z", "importance": "high", "labels": ["work", "urgent"], "has_read": False, "body": "Payment is overdue by 30 days.", "attachments": [], "auto_classify_suggestion": "finance"},
        # msg003 – bob normal（干扰）
        {"id": "msg003", "thread_id": "t2", "folder": "inbox", "sender_id": "bob@vendor-services.com", "subject": "Weekly status", "timestamp": "2025-03-19T14:00:00Z", "importance": "normal", "labels": ["work"], "has_read": True, "body": "All good this week.", "attachments": [], "auto_classify_suggestion": "work"},
        # msg004 – 垃圾邮件（干扰）
        {"id": "msg004", "thread_id": "t3", "folder": "inbox", "sender_id": "winner@lottery-scam.com", "subject": "You won a prize!", "timestamp": "2025-03-20T08:00:00Z", "importance": "low", "labels": ["spam"], "has_read": False, "body": "Click here to claim.", "attachments": [], "auto_classify_suggestion": "spam"},
        # msg005 – bob high（目标）
        {"id": "msg005", "thread_id": "t4", "folder": "inbox", "sender_id": "bob@vendor-services.com", "subject": "Critical: Server down", "timestamp": "2025-03-20T11:30:00Z", "importance": "high", "labels": ["work", "urgent"], "has_read": False, "body": "Our server is down. Please respond ASAP.", "attachments": [], "auto_classify_suggestion": "work"},
        # msg006 – alice normal（干扰）
        {"id": "msg006", "thread_id": "t5", "folder": "inbox", "sender_id": "alice@clientcorp.com", "subject": "Meeting reminder", "timestamp": "2025-03-20T07:45:00Z", "importance": "normal", "labels": ["work"], "has_read": True, "body": "Don't forget the 11am meeting.", "attachments": [], "auto_classify_suggestion": "work"},
        # msg007 – bob high（目标）
        {"id": "msg007", "thread_id": "t6", "folder": "inbox", "sender_id": "bob@vendor-services.com", "subject": "Invoice #1234 dispute", "timestamp": "2025-03-20T12:00:00Z", "importance": "high", "labels": ["finance", "urgent"], "has_read": False, "body": "Dispute on invoice #1234.", "attachments": [], "auto_classify_suggestion": "finance"},
        # msg008 – 内部 HR 邮件（干扰）
        {"id": "msg008", "thread_id": "t7", "folder": "inbox", "sender_id": "hr@company.com", "subject": "Policy update", "timestamp": "2025-03-19T16:00:00Z", "importance": "normal", "labels": ["hr"], "has_read": True, "body": "New policy effective next month.", "attachments": [], "auto_classify_suggestion": "hr"},
        # msg009 – bob low（干扰）
        {"id": "msg009", "thread_id": "t8", "folder": "inbox", "sender_id": "bob@vendor-services.com", "subject": "Quick question", "timestamp": "2025-03-18T09:30:00Z", "importance": "low", "labels": ["work"], "has_read": True, "body": "Just a quick question.", "attachments": [], "auto_classify_suggestion": "work"},
        # msg010 – spam 另一封（干扰）
        {"id": "msg010", "thread_id": "t9", "folder": "inbox", "sender_id": "winner@lottery-scam.com", "subject": "Final notice", "timestamp": "2025-03-20T06:00:00Z", "importance": "low", "labels": ["spam"], "has_read": False, "body": "Urgent claim required.", "attachments": [], "auto_classify_suggestion": "spam"}
    ]

    for email in emails:
        filepath = f"data/emails/{email['id']}.json"
        with open(filepath, "w") as f:
            json.dump(email, f, indent=2)

if __name__ == "__main__":
    build_env()
