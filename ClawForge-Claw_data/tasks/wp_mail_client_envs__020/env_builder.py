import os
import json

def build_env():
    # 创建目录
    os.makedirs('data/emails', exist_ok=True)
    os.makedirs('ops', exist_ok=True)  # 留给 agent 放产物

    # 联系人文件
    contacts = [
        {"contact_id": "tom_friend", "name": "Tom Friend", "email": "tom.friend@gmail.com", "role": "Friend", "team": "Personal", "priority": "high"},
        {"contact_id": "alice_client", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "lottery_scam", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
    ]
    with open('data/contacts.json', 'w') as f:
        json.dump(contacts, f, indent=2)

    # 邮件数据（含干扰项）
    emails = [
        {"id": "e001", "sender_id": "tom_friend", "subject": "Project deadline tomorrow", "importance": "high", "has_read": False, "body": "We need to finalize the report...", "folder": "inbox", "timestamp": "2025-04-10T10:00:00", "labels": [], "attachments": [], "thread_id": "t1", "auto_classify_suggestion": "work"},
        {"id": "e002", "sender_id": "tom_friend", "subject": "Weekly sync", "importance": "high", "has_read": True, "body": "Let's catch up...", "folder": "inbox", "timestamp": "2025-04-09T10:00:00", "labels": [], "attachments": [], "thread_id": "t2", "auto_classify_suggestion": "work"},
        {"id": "e003", "sender_id": "alice_client", "subject": "Invoice needed", "importance": "high", "has_read": False, "body": "Please send the invoice...", "folder": "inbox", "timestamp": "2025-04-08T10:00:00", "labels": [], "attachments": [], "thread_id": "t3", "auto_classify_suggestion": "finance"},
        {"id": "e004", "sender_id": "tom_friend", "subject": "Lunch tomorrow", "importance": "low", "has_read": False, "body": "Want to grab lunch?", "folder": "inbox", "timestamp": "2025-04-10T12:00:00", "labels": [], "attachments": [], "thread_id": "t4", "auto_classify_suggestion": "personal"},
        {"id": "e005", "sender_id": "lottery_scam", "subject": "You won a prize!", "importance": "high", "has_read": False, "body": "Click here to claim...", "folder": "inbox", "timestamp": "2025-04-11T08:00:00", "labels": [], "attachments": [], "thread_id": "t5", "auto_classify_suggestion": "spam"},
        {"id": "e006", "sender_id": "tom_friend", "subject": "Urgent: server down", "importance": "high", "has_read": False, "body": "Production server is down!", "folder": "inbox", "timestamp": "2025-04-11T09:00:00", "labels": [], "attachments": [], "thread_id": "t6", "auto_classify_suggestion": "work"},
    ]
    for email in emails:
        with open(f'data/emails/{email["id"]}.json', 'w') as f:
            json.dump(email, f, indent=2)

if __name__ == '__main__':
    build_env()
