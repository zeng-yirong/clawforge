import os
import json

def build_env():
    # Create directory structure
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # Helper to create email files
    def write_email(email_id, data):
        path = os.path.join("data/emails", f"{email_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # Email 1: Alice – 报价确认
    write_email("email_001", {
        "id": "email_001",
        "thread_id": "thread_001",
        "folder": "inbox",
        "sender_id": "alice@clientcorp.com",
        "subject": "报价确认",
        "timestamp": "2025-03-20T09:00:00Z",
        "importance": "normal",
        "labels": [],
        "has_read": False,
        "body": "你好，请确认一下报价。",
        "attachments": [],
        "auto_classify_suggestion": "work"
    })

    # Email 2: Bob – 付款提醒 (high)
    write_email("email_002", {
        "id": "email_002",
        "thread_id": "thread_002",
        "folder": "inbox",
        "sender_id": "bob@vendor-services.com",
        "subject": "付款提醒",
        "timestamp": "2025-03-20T10:00:00Z",
        "importance": "high",
        "labels": [],
        "has_read": False,
        "body": "请尽快支付发票 #123\n感谢您的合作。",
        "attachments": [],
        "auto_classify_suggestion": "finance"
    })

    # Email 3: HR – 年假申请
    write_email("email_003", {
        "id": "email_003",
        "thread_id": "thread_003",
        "folder": "inbox",
        "sender_id": "hr@company.com",
        "subject": "年假申请",
        "timestamp": "2025-03-20T11:00:00Z",
        "importance": "normal",
        "labels": [],
        "has_read": False,
        "body": "请提交年假申请审批。",
        "attachments": [],
        "auto_classify_suggestion": "hr"
    })

    # Email 4: John Manager – 项目进度
    write_email("email_004", {
        "id": "email_004",
        "thread_id": "thread_004",
        "folder": "inbox",
        "sender_id": "john.manager@company.com",
        "subject": "项目进度",
        "timestamp": "2025-03-20T12:00:00Z",
        "importance": "high",
        "labels": [],
        "has_read": False,
        "body": "请更新项目进度报告。",
        "attachments": [],
        "auto_classify_suggestion": "work"
    })

    # Email 5: Lottery Scam – 垃圾
    write_email("email_005", {
        "id": "email_005",
        "thread_id": "thread_005",
        "folder": "inbox",
        "sender_id": "winner@lottery-scam.com",
        "subject": "恭喜中奖",
        "timestamp": "2025-03-20T13:00:00Z",
        "importance": "low",
        "labels": [],
        "has_read": False,
        "body": "您中奖了！请点击链接。",
        "attachments": [],
        "auto_classify_suggestion": "spam"
    })

    # Email 6: Tech Weekly – 新闻简报
    write_email("email_006", {
        "id": "email_006",
        "thread_id": "thread_006",
        "folder": "inbox",
        "sender_id": "newsletter@techweekly.com",
        "subject": "本周技术动态",
        "timestamp": "2025-03-20T14:00:00Z",
        "importance": "low",
        "labels": [],
        "has_read": False,
        "body": "本周技术新闻汇总。",
        "attachments": [],
        "auto_classify_suggestion": "newsletter"
    })

    # Email 7: Sarah (已读, 干扰项)
    write_email("email_007", {
        "id": "email_007",
        "thread_id": "thread_007",
        "folder": "inbox",
        "sender_id": "sarah.dev@company.com",
        "subject": "代码审查请求",
        "timestamp": "2025-03-19T08:00:00Z",
        "importance": "normal",
        "labels": [],
        "has_read": True,
        "body": "请审查我的代码。",
        "attachments": [],
        "auto_classify_suggestion": "work"
    })

    # Optional: create contacts and accounts for realism (not used by verifier)
    contacts = [
        {"contact_id": "alice@clientcorp.com", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "bob@vendor-services.com", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "high"},
        {"contact_id": "hr@company.com", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "normal"},
        {"contact_id": "john.manager@company.com", "name": "John Manager", "email": "john.manager@company.com", "role": "Manager", "team": "Leadership", "priority": "high"},
        {"contact_id": "winner@lottery-scam.com", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
        {"contact_id": "newsletter@techweekly.com", "name": "Tech Weekly", "email": "newsletter@techweekly.com", "role": "Newsletter", "team": "External", "priority": "low"},
        {"contact_id": "sarah.dev@company.com", "name": "Sarah Developer", "email": "sarah.dev@company.com", "role": "Developer", "team": "Engineering", "priority": "normal"}
    ]
    with open("data/contacts.json", "w", encoding="utf-8") as f:
        json.dump({"contacts": contacts}, f, indent=2, ensure_ascii=False)

    account = {
        "account_id": "default",
        "display_name": "Boss",
        "email_address": "boss@company.com",
        "default_signature": "Thanks,\nBoss",
        "auto_classify_enabled": True,
        "reply_templates_enabled": True,
        "task_generation_enabled": True,
        "folders": ["inbox", "work", "finance", "hr", "personal", "spam", "newsletter", "archived"]
    }
    with open("data/accounts.json", "w", encoding="utf-8") as f:
        json.dump({"accounts": [account]}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    build_env()
