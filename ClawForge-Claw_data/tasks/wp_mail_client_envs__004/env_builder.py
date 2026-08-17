import json
import os
import random
from datetime import datetime, timedelta

def build_env():
    # 创建目录结构
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # 账户数据（干扰性账户信息）
    accounts = [
        {
            "account_id": "a001",
            "display_name": "Zhou Yong",
            "email_address": "zhou@company.com",
            "default_signature": "Regards, Zhou",
            "auto_classify_enabled": True,
            "reply_templates_enabled": True,
            "task_generation_enabled": True,
            "folders": ["inbox", "sent", "archive", "spam"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    # 联系人数据（包含正常联系人和垃圾发送者）
    contacts = [
        {"contact_id": "c01", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "c02", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "normal"},
        {"contact_id": "c03", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "normal"},
        {"contact_id": "c04", "name": "John Manager", "email": "john.manager@company.com", "role": "Manager", "team": "Leadership", "priority": "high"},
        {"contact_id": "c05", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
        {"contact_id": "c06", "name": "Sarah Developer", "email": "sarah.dev@company.com", "role": "Developer", "team": "Engineering", "priority": "normal"},
        {"contact_id": "c07", "name": "Tech Weekly", "email": "newsletter@techweekly.com", "role": "Newsletter", "team": "External", "priority": "low"},
        {"contact_id": "c08", "name": "Tom Friend", "email": "tom.friend@gmail.com", "role": "Friend", "team": "Personal", "priority": "normal"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

    # 邮件生成辅助
    base_time = datetime(2025, 4, 1, 8, 0, 0)
    emails = []

    # 有效紧急邮件（未回复，高优先级，非垃圾/新闻稿）
    valid_high_unreplied = [
        {"id": "em001", "thread_id": "t001", "sender_id": "c01", "subject": "Urgent: Payment deadline extension needed", "importance": "high", "labels": ["work", "finance"], "has_reply": False, "timestamp": (base_time + timedelta(hours=1)).isoformat()},
        {"id": "em002", "thread_id": "t002", "sender_id": "c04", "subject": "Audit preparation: missing documents", "importance": "high", "labels": ["work"], "has_reply": False, "timestamp": (base_time + timedelta(hours=2)).isoformat()},
        {"id": "em003", "thread_id": "t003", "sender_id": "c06", "subject": "Critical production bug report", "importance": "high", "labels": ["work", "engineering"], "has_reply": False, "timestamp": (base_time + timedelta(hours=3)).isoformat()},
    ]

    # 已回复的紧急邮件（需要被排除）
    replied_high = [
        {"id": "em004", "thread_id": "t004", "sender_id": "c04", "subject": "Quarterly review schedule", "importance": "high", "labels": ["work"], "has_reply": True, "timestamp": (base_time + timedelta(hours=0.5)).isoformat()},
        {"id": "em005", "thread_id": "t005", "sender_id": "c01", "subject": "Contract renewal urgent", "importance": "high", "labels": ["work", "finance"], "has_reply": True, "timestamp": (base_time + timedelta(hours=4)).isoformat()},
    ]

    # 垃圾/新闻邮件（需要被排除）
    spam_newsletter = [
        {"id": "em006", "thread_id": "t006", "sender_id": "c05", "subject": "You won 10 million dollars!", "importance": "low", "labels": ["spam"], "has_reply": False, "timestamp": (base_time + timedelta(hours=5)).isoformat()},
        {"id": "em007", "thread_id": "t007", "sender_id": "c07", "subject": "Tech Weekly: Top 10 AI frameworks", "importance": "low", "labels": ["newsletter"], "has_reply": False, "timestamp": (base_time + timedelta(hours=6)).isoformat()},
        {"id": "em008", "thread_id": "t008", "sender_id": "c05", "subject": "Special lottery offer", "importance": "normal", "labels": ["spam"], "has_reply": False, "timestamp": (base_time + timedelta(hours=7)).isoformat()},
    ]

    # 其他干扰邮件（低优先级/正常但未回复）
    other_low_normal_unreplied = [
        {"id": "em009", "thread_id": "t009", "sender_id": "c02", "subject": "Monthly report update", "importance": "normal", "labels": ["work"], "has_reply": False, "timestamp": (base_time + timedelta(hours=8)).isoformat()},
        {"id": "em010", "thread_id": "t010", "sender_id": "c03", "subject": "New employee onboarding form", "importance": "low", "labels": ["hr"], "has_reply": False, "timestamp": (base_time + timedelta(hours=9)).isoformat()},
        {"id": "em011", "thread_id": "t011", "sender_id": "c08", "subject": "Dinner party invitation", "importance": "low", "labels": ["personal"], "has_reply": False, "timestamp": (base_time + timedelta(hours=10)).isoformat()},
    ]

    # 合成所有邮件并写入
    all_emails = valid_high_unreplied + replied_high + spam_newsletter + other_low_normal_unreplied
    random.shuffle(all_emails)  # 增加干扰顺序

    for mail in all_emails:
        mail.setdefault("folder", "inbox")
        mail.setdefault("has_read", False)
        mail.setdefault("attachments", [])
        mail.setdefault("auto_classify_suggestion", "work")
        mail.setdefault("body", "This is a placeholder body for email " + mail["id"])
        with open(f"data/emails/{mail['id']}.json", "w") as f:
            json.dump(mail, f)

    # 额外创建两个非标准文件作为诱饵
    os.makedirs("db_dumps", exist_ok=True)
    with open("db_dumps/backup.log", "w") as f:
        f.write("some irrelevant log")
    with open("ops/note.txt", "w") as f:
        f.write("This directory will be used later")

if __name__ == "__main__":
    build_env()
