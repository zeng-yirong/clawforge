import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/customers", exist_ok=True)

    # 客户主数据 (干扰项之一)
    customers = {
        "customers": [
            {"customer_id": "C001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "enterprise", "labels": ["old_vip"], "owner_name": "Alice"},
            {"customer_id": "C002", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "mid_market", "labels": ["old_high"], "owner_name": "Bob"},
            {"customer_id": "C003", "customer_name": "HealthFirst", "industry": "healthcare", "tier": "mid_market", "labels": ["old_standard"], "owner_name": "Charlie"},
            {"customer_id": "C004", "customer_name": "FinTechX", "industry": "fintech", "tier": "enterprise", "labels": ["old_high"], "owner_name": "Diana"},
            {"customer_id": "C005", "customer_name": "OldCorp", "industry": "fintech", "tier": "standard", "labels": ["old_standard"], "owner_name": "Eve"}
        ]
    }
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # 正确的活动日志
    activity_logs = {
        "activity_logs": [
            {"customer_id": "C001", "risk_level": "low", "last_active_days": 20, "usage_trend": "up"},
            {"customer_id": "C002", "risk_level": "low", "last_active_days": 45, "usage_trend": "up"},
            {"customer_id": "C003", "risk_level": "high", "last_active_days": 80, "usage_trend": "down"},
            {"customer_id": "C004", "risk_level": "low", "last_active_days": 25, "usage_trend": "up"},
            {"customer_id": "C005", "risk_level": "high", "last_active_days": 400, "usage_trend": "down"}
        ]
    }
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # 正确的消费日志
    consumption_logs = {
        "consumption_logs": [
            {"customer_id": "C001", "quarter_spend_usd": 85000},
            {"customer_id": "C002", "quarter_spend_usd": 35000},
            {"customer_id": "C003", "quarter_spend_usd": 15000},
            {"customer_id": "C004", "quarter_spend_usd": 50000},
            {"customer_id": "C005", "quarter_spend_usd": 20000}
        ]
    }
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump(consumption_logs, f, indent=2)

    # 干扰：旧版消费日志（误导agent）
    old_consumption = {
        "consumption_logs": [
            {"customer_id": "C001", "quarter_spend_usd": 60000},
            {"customer_id": "C002", "quarter_spend_usd": 30000},
            {"customer_id": "C003", "quarter_spend_usd": 12000}
        ]
    }
    with open("data/logs/consumption_logs_old.json", "w") as f:
        json.dump(old_consumption, f, indent=2)

    # 干扰：备份活动日志（误导agent）
    backup_activity = {
        "activity_logs": [
            {"customer_id": "C001", "risk_level": "low", "last_active_days": 100, "usage_trend": "down"},
            {"customer_id": "C002", "risk_level": "low", "last_active_days": 60, "usage_trend": "up"}
        ]
    }
    with open("data/logs/activity_logs_backup.json", "w") as f:
        json.dump(backup_activity, f, indent=2)

    # 其他干扰文件（账户、联系人、附件等）
    accounts = {
        "accounts": [
            {"account_id": "A001", "display_name": "Alice", "department": "CS", "email": "alice@company.com", "permissions": ["admin"]},
            {"account_id": "A002", "display_name": "Bob", "department": "CS", "email": "bob@company.com", "permissions": ["view"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    contacts = {
        "contacts": [
            {"contact_id": "CT001", "name": "Dr. Smith", "role": "CTO", "email": "smith@carepulse.com"},
            {"contact_id": "CT002", "name": "Jane Doe", "role": "CFO", "email": "jane@ledgerflow.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    attachments = {
        "attachments": [
            {"path": "data/logs/report.pdf", "title": "Q1 Report", "kind": "pdf", "description": "Quarterly summary"},
            {"path": "data/logs/old_notes.txt", "title": "Old Notes", "kind": "text", "description": "Deprecated"}
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

if __name__ == "__main__":
    build_env()
