import json, os, random, string

def random_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

def build_env():
    # 确保目录存在
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # agent 需要创建结果文件

    # 联系人
    contacts = [
        {"contact_id": "c_alice", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "c_bob",   "name": "Bob Vendor",   "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "normal"},
        {"contact_id": "c_hr",    "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "low"},
        {"contact_id": "c_john",  "name": "John Manager",  "email": "john.manager@company.com", "role": "Manager", "team": "Leadership", "priority": "high"},
        {"contact_id": "c_lottery","name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 邮件模板
    base_emails = [
        # 正确答案：Alice Client 的 2 封紧急未读邮件
        (random_id(), "c_alice", "Urgent: Payment overdue", "high", False, "Dear support, please process payment immediately."),
        (random_id(), "c_alice", "New contract deadline", "high", False, "We need to finalize the contract by tomorrow."),
        # 干扰：已读或低重要性或非客户
        (random_id(), "c_alice", "Old invoice", "low", True, "This was already paid, please ignore."),
        (random_id(), "c_bob",   "Vendor update", "high", False, "Our new product line is ready."),
        (random_id(), "c_hr",    "Meeting reminder", "normal", False, "Don't forget the all-hands meeting."),
        (random_id(), "c_john",  "Project status", "high", True, "The milestone is on track."),
        (random_id(), "c_lottery","You won!", "low", False, "Click here to claim your prize."),
        (random_id(), "c_alice", "Friendly hello", "normal", False, "Just checking in."),
    ]

    for eid, sender_id, subject, importance, has_read, body in base_emails:
        email = {
            "id": eid,
            "thread_id": eid,  # 简化
            "folder": "inbox",
            "sender_id": sender_id,
            "subject": subject,
            "timestamp": "2025-03-15T10:00:00Z",
            "importance": importance,
            "labels": [],
            "has_read": has_read,
            "body": body,
            "attachments": [],
            "auto_classify_suggestion": "work"  # 可忽略
        }
        with open(f"data/emails/{eid}.json", "w") as f:
            json.dump(email, f, indent=2)

if __name__ == "__main__":
    build_env()
