import os
import json

def build_env():
    # ===== 客户主数据 =====
    customers = [
        {"customer_id": "C001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "enterprise", "labels": ["vip"], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "mid_market", "labels": ["high_potential"], "owner_name": "Bob"},
        {"customer_id": "C003", "customer_name": "HealthFirst", "industry": "healthcare", "tier": "mid_market", "labels": [], "owner_name": "Charlie"},
        {"customer_id": "C004", "customer_name": "FinServe", "industry": "fintech", "tier": "enterprise", "labels": ["active"], "owner_name": "Diana"},
        {"customer_id": "C005", "customer_name": "MediCore", "industry": "healthcare", "tier": "mid_market", "labels": ["old_label"], "owner_name": "Eve"},
        {"customer_id": "C006", "customer_name": "QuickPay", "industry": "fintech", "tier": "enterprise", "labels": ["star"], "owner_name": "Frank"},
    ]
    os.makedirs("data/customers", exist_ok=True)
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # ===== 活动日志 (有干扰：C005 缺少消费，C006 缺少活动) =====
    activity_logs = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 20, "usage_trend": "up"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 60, "usage_trend": "down"},
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 5, "usage_trend": "up"},
        {"customer_id": "C004", "risk_level": "high", "last_active_days": 45, "usage_trend": "down"},
        {"customer_id": "C005", "risk_level": "low", "last_active_days": 28, "usage_trend": "up"},
        # C006 没有活动记录 → 视为缺失
        # 干扰项：不存在的客户
        {"customer_id": "C007", "risk_level": "low", "last_active_days": 10, "usage_trend": "up"},
    ]
    os.makedirs("data/logs", exist_ok=True)
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # ===== 消费日志 =====
    consumption_logs = [
        {"customer_id": "C001", "quarter_spend_usd": 15000},
        {"customer_id": "C002", "quarter_spend_usd": 12000},
        {"customer_id": "C003", "quarter_spend_usd": 8000},
        {"customer_id": "C004", "quarter_spend_usd": 5000},
        # C005 没有消费记录 → 视为缺失
        {"customer_id": "C006", "quarter_spend_usd": 25000},
        # 干扰项：不存在的客户
        {"customer_id": "C008", "quarter_spend_usd": 3000},
    ]
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump({"consumption_logs": consumption_logs}, f, indent=2)

    # ===== 干扰文件 =====
    # data/attachments.json
    attachments = [
        {"path": "reports/q1_summary.pdf", "title": "Q1 Summary", "kind": "pdf", "description": "Quarterly report"},
        {"path": "presentations/strategy.pptx", "title": "Strategy Deck", "kind": "pptx", "description": "Annual planning"}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # data/accounts.json
    accounts = [
        {"account_id": "ACC001", "display_name": "Admin", "department": "IT", "email": "admin@co.com", "permissions": ["read", "write"]},
        {"account_id": "ACC002", "display_name": "Ops", "department": "Operations", "email": "ops@co.com", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # data/contacts.json
    contacts = [
        {"contact_id": "CT001", "name": "John", "role": "Manager", "email": "john@co.com"},
        {"contact_id": "CT002", "name": "Jane", "role": "Engineer", "email": "jane@co.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 创建 ops 目录（留给 agent 写入）
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
