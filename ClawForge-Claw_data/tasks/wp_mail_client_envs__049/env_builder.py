import json
import os
import random
from datetime import datetime, timedelta

def build_env():
    # 确保数据目录存在
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # 联系人信息（包含内部和外部）
    contacts = [
        {"contact_id": "c001", "name": "张三", "email": "zhangsan@company.com", "role": "Developer", "team": "Engineering", "priority": "normal"},
        {"contact_id": "c002", "name": "李四", "email": "lisi@company.com", "role": "HR", "team": "Human Resources", "priority": "high"},
        {"contact_id": "c003", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "c004", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "normal"},
        {"contact_id": "c005", "name": "Phishing Attacker", "email": "support@secure-update.net", "role": "Spammer", "team": "External", "priority": "low"},
        {"contact_id": "c006", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "normal"},
        {"contact_id": "c007", "name": "Tom Friend", "email": "tom.friend@gmail.com", "role": "Friend", "team": "Personal", "priority": "low"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": {c["contact_id"]: c for c in contacts}}, f, indent=2, ensure_ascii=False)

    # 创建一些邮件（包含干扰项和正确答案）
    now = datetime.now()
    emails = []

    # 正确答案：3封来自外部域，未读，非spam，主题含“紧急”或“重要”
    # 1: 外部钓鱼，未读，主题含“紧急”
    emails.append({
        "id": "e001",
        "thread_id": "t001",
        "folder": "inbox",
        "sender_id": "c005",
        "subject": "[紧急] 您的账户存在风险，请立即验证",
        "timestamp": (now - timedelta(hours=2)).isoformat(),
        "importance": "high",
        "labels": ["security"],
        "has_read": False,
        "body": "请点击链接验证您的账户……",
        "attachments": [],
        "auto_classify_suggestion": "spam"
    })
    # 2: 外部客户，未读，主题含“重要”
    emails.append({
        "id": "e002",
        "thread_id": "t002",
        "folder": "inbox",
        "sender_id": "c003",
        "subject": "重要会议邀请 – 项目进度同步",
        "timestamp": (now - timedelta(hours=5)).isoformat(),
        "importance": "high",
        "labels": ["meeting"],
        "has_read": False,
        "body": "Alice 邀请您参加下周一的会议。",
        "attachments": [],
        "auto_classify_suggestion": "work"
    })
    # 3: 外部供应商，未读，主题含“紧急”
    emails.append({
        "id": "e003",
        "thread_id": "t003",
        "folder": "inbox",
        "sender_id": "c004",
        "subject": "紧急: 发票需今日确认",
        "timestamp": (now - timedelta(hours=1)).isoformat(),
        "importance": "high",
        "labels": ["finance"],
        "has_read": False,
        "body": "请尽快确认发票附件。",
        "attachments": ["invoice.pdf"],
        "auto_classify_suggestion": "finance"
    })

    # 干扰项
    # 4: 内部域名，未读，主题含“紧急”（不符合外部域）
    emails.append({
        "id": "e004",
        "thread_id": "t004",
        "folder": "inbox",
        "sender_id": "c006",
        "subject": "紧急通知：办公室搬迁计划",
        "timestamp": (now - timedelta(days=1)).isoformat(),
        "importance": "high",
        "labels": ["hr"],
        "has_read": False,
        "body": "请查看附件中的搬迁方案。",
        "attachments": ["relocation.pdf"],
        "auto_classify_suggestion": "hr"
    })
    # 5: 外部域名，已读，主题含“重要”（不符合未读）
    emails.append({
        "id": "e005",
        "thread_id": "t005",
        "folder": "inbox",
        "sender_id": "c007",
        "subject": "重要：周末聚会地点变更",
        "timestamp": (now - timedelta(days=2)).isoformat(),
        "importance": "low",
        "labels": ["personal"],
        "has_read": True,
        "body": "改到三里屯了。",
        "attachments": [],
        "auto_classify_suggestion": "personal"
    })
    # 6: 外部域名，未读，但folder=spam（不符合非spam）
    emails.append({
        "id": "e006",
        "thread_id": "t006",
        "folder": "spam",
        "sender_id": "c005",
        "subject": "重要: 您中奖了！",
        "timestamp": (now - timedelta(hours=3)).isoformat(),
        "importance": "low",
        "labels": [],
        "has_read": False,
        "body": "恭喜您获得百万大奖……",
        "attachments": [],
        "auto_classify_suggestion": "spam"
    })
    # 7: 内部域名，未读，主题不含“紧急”或“重要”（正常邮件）
    emails.append({
        "id": "e007",
        "thread_id": "t007",
        "folder": "inbox",
        "sender_id": "c001",
        "subject": "代码审查请求",
        "timestamp": (now - timedelta(minutes=30)).isoformat(),
        "importance": "normal",
        "labels": ["code"],
        "has_read": False,
        "body": "请审查PR #123。",
        "attachments": [],
        "auto_classify_suggestion": "work"
    })
    # 8: 外部域名，未读，主题含“紧急”，但folder=spam（再增加一个干扰）
    emails.append({
        "id": "e008",
        "thread_id": "t008",
        "folder": "spam",
        "sender_id": "c005",
        "subject": "紧急: 最后通知",
        "timestamp": (now - timedelta(hours=4)).isoformat(),
        "importance": "low",
        "labels": [],
        "has_read": False,
        "body": "再给一次机会……",
        "attachments": [],
        "auto_classify_suggestion": "spam"
    })
    # 9: 外部域名，未读，主题不含关键词
    emails.append({
        "id": "e009",
        "thread_id": "t009",
        "folder": "inbox",
        "sender_id": "c003",
        "subject": "下季度合作方案",
        "timestamp": (now - timedelta(days=3)).isoformat(),
        "importance": "normal",
        "labels": ["client"],
        "has_read": False,
        "body": "请查看附件。",
        "attachments": ["proposal.pdf"],
        "auto_classify_suggestion": "work"
    })
    # 10: 外部域名，已读，主题含“紧急”，folder非spam（已读不满足）
    emails.append({
        "id": "e010",
        "thread_id": "t010",
        "folder": "inbox",
        "sender_id": "c004",
        "subject": "紧急: 合同到期提醒",
        "timestamp": (now - timedelta(hours=6)).isoformat(),
        "importance": "high",
        "labels": [],
        "has_read": True,
        "body": "请续签合同。",
        "attachments": [],
        "auto_classify_suggestion": "work"
    })

    for e in emails:
        with open(f"data/emails/{e['id']}.json", "w") as f:
            json.dump(e, f, indent=2, ensure_ascii=False)

    # 可选：创建 accounts.json（仅作目录完整性）
    accounts = {
        "account_id": "acc_main",
        "display_name": "AI Mail Admin",
        "email_address": "admin@company.com",
        "default_signature": "Best regards",
        "auto_classify_enabled": True,
        "reply_templates_enabled": True,
        "task_generation_enabled": True,
        "folders": ["inbox", "sent", "drafts", "spam", "trash", "work", "personal", "newsletter", "finance", "hr"]
    }
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": {"acc_main": accounts}}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    build_env()
