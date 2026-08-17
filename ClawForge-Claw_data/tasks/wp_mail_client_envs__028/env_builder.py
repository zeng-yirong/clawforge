import os
import json
import shutil
from datetime import datetime, timezone

def build_env():
    # 清空并重建工作区
    base = os.getcwd()
    for item in os.listdir(base):
        path = os.path.join(base, item)
        try:
            if os.path.isfile(path) or os.path.islink(path):
                os.unlink(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
        except Exception:
            pass

    # 创建必要目录
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("todo", exist_ok=True)  # 供 agent 输出，但 builder 留空

    # ========== 联系人 ==========
    contacts = [
        {"contact_id": "sarah", "name": "Sarah Developer", "email": "sarah.dev@company.com",
         "role": "Developer", "team": "Engineering", "priority": "high"},
        {"contact_id": "alice", "name": "Alice Client", "email": "alice@clientcorp.com",
         "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "hr", "name": "HR Department", "email": "hr@company.com",
         "role": "HR", "team": "Human Resources", "priority": "normal"},
        {"contact_id": "tom", "name": "Tom Friend", "email": "tom.friend@gmail.com",
         "role": "Friend", "team": "Personal", "priority": "low"},
        {"contact_id": "lottery", "name": "Lottery Scam", "email": "winner@lottery-scam.com",
         "role": "Spammer", "team": "External", "priority": "low"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

    # ========== 账户 ==========
    accounts = [
        {"account_id": "me", "display_name": "User", "email_address": "user@company.com",
         "default_signature": "Best, User", "auto_classify_enabled": True,
         "reply_templates_enabled": True, "task_generation_enabled": True,
         "folders": ["inbox", "sent", "drafts", "archive", "spam", "work", "personal", "hr"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    # ========== 邮件（关键条件）==========
    # 符合条件：labels 包含 "todo"，has_read=false，subject/body 含 "Phoenix"
    # 干扰邮件：不含 todo / 已读 / 不含 Phoenix / 其他 sender
    emails_data = [
        # --- 符合条件（2封）---
        {
            "id": "e001",
            "thread_id": "t01",
            "folder": "inbox",
            "sender_id": "sarah",
            "subject": "Project Phoenix update",
            "timestamp": "2025-03-18T10:00:00Z",
            "importance": "high",
            "labels": ["todo", "work"],
            "has_read": False,
            "body": "Please review the design mockups. TODO: finalize wireframes. Due: 2025-03-20\nAlso check the latest specs.",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        {
            "id": "e002",
            "thread_id": "t02",
            "folder": "inbox",
            "sender_id": "sarah",
            "subject": "Phoenix deployment checklist",
            "timestamp": "2025-03-19T09:00:00Z",
            "importance": "normal",
            "labels": ["todo", "work"],
            "has_read": False,
            "body": "Due: 2025-03-22\nMake sure all services are updated.",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        # --- 干扰：有 todo 标签但已读 ---
        {
            "id": "e003",
            "thread_id": "t03",
            "folder": "inbox",
            "sender_id": "sarah",
            "subject": "Phoenix Q1 review notes",
            "timestamp": "2025-03-16T07:00:00Z",
            "importance": "normal",
            "labels": ["todo", "work"],
            "has_read": True,
            "body": "Due: 2025-03-18 (already done).",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        # --- 干扰：有 todo 标签，未读，但不含 Phoenix ---
        {
            "id": "e004",
            "thread_id": "t04",
            "folder": "inbox",
            "sender_id": "hr",
            "subject": "HR policy update",
            "timestamp": "2025-03-17T08:00:00Z",
            "importance": "normal",
            "labels": ["todo"],
            "has_read": False,
            "body": "Please sign the new policy by Due: 2025-03-31.",
            "attachments": [],
            "auto_classify_suggestion": "hr"
        },
        # --- 干扰：无 todo 标签，未读，含 Phoenix ---
        {
            "id": "e005",
            "thread_id": "t05",
            "folder": "inbox",
            "sender_id": "alice",
            "subject": "Phoenix integration proposal",
            "timestamp": "2025-03-20T11:00:00Z",
            "importance": "high",
            "labels": ["work"],
            "has_read": False,
            "body": "This is a new proposal for Phoenix. Due: 2025-04-01",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        # --- 干扰：垃圾邮件 ---
        {
            "id": "e006",
            "thread_id": "t06",
            "folder": "inbox",
            "sender_id": "lottery",
            "subject": "You won a prize!",
            "timestamp": "2025-03-15T06:00:00Z",
            "importance": "low",
            "labels": ["spam"],
            "has_read": False,
            "body": "Click here to claim your lottery. No due date.",
            "attachments": [],
            "auto_classify_suggestion": "spam"
        },
        # --- 干扰：个人邮件 ---
        {
            "id": "e007",
            "thread_id": "t07",
            "folder": "inbox",
            "sender_id": "tom",
            "subject": "Dinner this weekend?",
            "timestamp": "2025-03-14T18:30:00Z",
            "importance": "normal",
            "labels": ["personal"],
            "has_read": False,
            "body": "Let's meet Saturday. Due: ???",
            "attachments": [],
            "auto_classify_suggestion": "personal"
        }
    ]

    for mail in emails_data:
        path = os.path.join("data/emails", f"{mail['id']}.json")
        with open(path, "w") as f:
            json.dump(mail, f)

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
