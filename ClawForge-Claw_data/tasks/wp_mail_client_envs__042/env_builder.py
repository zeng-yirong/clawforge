import json
import os

def build_env():
    # 创建目录
    os.makedirs("emails", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 干扰邮件（非 finance）
    work_mail = {
        "id": "w001",
        "thread_id": "t001",
        "folder": "inbox",
        "sender_id": "john.manager@company.com",
        "subject": "Q4 review",
        "timestamp": "2024-12-10T09:00:00Z",
        "importance": "high",
        "labels": ["work"],
        "has_read": False,
        "body": "Please prepare slides for Q4 meeting.",
        "attachments": [],
        "auto_classify_suggestion": "work"
    }
    personal_mail = {
        "id": "p001",
        "thread_id": "t002",
        "folder": "inbox",
        "sender_id": "tom.friend@gmail.com",
        "subject": "Dinner this weekend?",
        "timestamp": "2024-12-11T18:30:00Z",
        "importance": "low",
        "labels": ["personal"],
        "has_read": True,
        "body": "Hey, free for dinner on Saturday?",
        "attachments": [],
        "auto_classify_suggestion": "personal"
    }

    # 三个 finance 邮件
    finance1 = {
        "id": "f001",
        "thread_id": "t003",
        "folder": "inbox",
        "sender_id": "bob@vendor-services.com",
        "subject": "Invoice #12345 due",
        "timestamp": "2024-12-12T10:00:00Z",
        "importance": "high",
        "labels": ["finance", "urgent"],
        "has_read": False,
        "body": "Please process payment by end of month.\nDue:2024-12-20\nDue:2024-12-15",
        "attachments": [],
        "auto_classify_suggestion": "finance"
    }
    finance2 = {
        "id": "f002",
        "thread_id": "t004",
        "folder": "inbox",
        "sender_id": "alice@clientcorp.com",
        "subject": "Payment confirmation needed",
        "timestamp": "2024-12-13T14:00:00Z",
        "importance": "normal",
        "labels": ["finance"],
        "has_read": False,
        "body": "Could you confirm the wire transfer? Due:2024-12-18",
        "attachments": [],
        "auto_classify_suggestion": "finance"
    }
    finance3 = {
        "id": "f003",
        "thread_id": "t005",
        "folder": "inbox",
        "sender_id": "hr@company.com",
        "subject": "Expense report deadline",
        "timestamp": "2024-12-14T08:00:00Z",
        "importance": "normal",
        "labels": ["finance"],
        "has_read": True,
        "body": "Reminder: submit expense reports this Friday.",
        "attachments": [],
        "auto_classify_suggestion": "finance"
    }

    # 垃圾邮件 (Lottery Scam)
    scam_mail = {
        "id": "s001",
        "thread_id": "t006",
        "folder": "inbox",
        "sender_id": "winner@lottery-scam.com",
        "subject": "You won 1,000,000 USD!",
        "timestamp": "2024-12-11T06:00:00Z",
        "importance": "low",
        "labels": ["spam"],
        "has_read": False,
        "body": "Claim your prize now! Send us your bank details.",
        "attachments": [],
        "auto_classify_suggestion": "spam"
    }

    # 旧格式邮件 (缺少 auto_classify_suggestion 字段)
    old_mail = {
        "id": "old01",
        "thread_id": "t007",
        "folder": "inbox",
        "sender_id": "old_system@legacy.com",
        "subject": "Legacy report",
        "timestamp": "2024-11-01T12:00:00Z",
        "importance": "normal",
        "labels": ["legacy"],
        "has_read": False,
        "body": "Old data. Due:2024-11-01",
        "attachments": [],
        # 故意没有 auto_classify_suggestion
    }

    # 写入文件
    emails = [work_mail, personal_mail, finance1, finance2, finance3, scam_mail, old_mail]
    for mail in emails:
        fname = f"emails/email_{mail['id']}.json"
        with open(fname, "w") as f:
            json.dump(mail, f, indent=2)

if __name__ == "__main__":
    build_env()
