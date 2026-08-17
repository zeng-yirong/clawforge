import os
import json

def build_env():
    # 创建目录
    os.makedirs("ops", exist_ok=True)
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/old_reports", exist_ok=True)

    # 规则文件
    rules_text = """Segmentation Rules:
- High Value (premium): quarter_spend_usd >= 80000 AND risk_level == "low" AND last_active_days <= 7
- Attention (attention): quarter_spend_usd >= 80000 AND risk_level == "high"
- Standard (standard): quarter_spend_usd >= 50000 AND quarter_spend_usd < 80000 AND risk_level == "low" AND last_active_days <= 30
- Others: keep existing labels (no update needed)
"""
    with open("ops/segmentation_rules.txt", "w") as f:
        f.write(rules_text)

    # 客户档案
    customers = [
        {"customer_id": "C001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "enterprise", "labels": ["active"], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "mid_market", "labels": ["active"], "owner_name": "Bob"},
        {"customer_id": "C003", "customer_name": "MedTech", "industry": "healthcare", "tier": "enterprise", "labels": ["active"], "owner_name": "Charlie"},
        {"customer_id": "C004", "customer_name": "FinServe", "industry": "fintech", "tier": "mid_market", "labels": ["vip"], "owner_name": "Diana"},
        {"customer_id": "C005", "customer_name": "DataCorp", "industry": "healthcare", "tier": "enterprise", "labels": ["inactive"], "owner_name": "Eve"}
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # 消费日志（最新）
    consumption_logs = [
        {"customer_id": "C001", "quarter_spend_usd": 95000},
        {"customer_id": "C002", "quarter_spend_usd": 45000},
        {"customer_id": "C003", "quarter_spend_usd": 72000},
        {"customer_id": "C004", "quarter_spend_usd": 82000},
        {"customer_id": "C005", "quarter_spend_usd": 30000}
    ]
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump(consumption_logs, f, indent=2)

    # 活动日志（最新）
    activity_logs = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 5, "usage_trend": "up"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 12, "usage_trend": "down"},
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 20, "usage_trend": "up"},
        {"customer_id": "C004", "risk_level": "high", "last_active_days": 3, "usage_trend": "up"},
        {"customer_id": "C005", "risk_level": "low", "last_active_days": 60, "usage_trend": "down"}
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # 干扰项1：旧消费日志
    old_consumption = [
        {"customer_id": "C001", "quarter_spend_usd": 60000},
        {"customer_id": "C003", "quarter_spend_usd": 40000}
    ]
    with open("data/logs/consumption_logs_2023.json", "w") as f:
        json.dump(old_consumption, f, indent=2)

    # 干扰项2：备份活动日志（含错误数据）
    backup_activity = [
        {"customer_id": "C001", "risk_level": "high", "last_active_days": 2, "usage_trend": "down"},
        {"customer_id": "C004", "risk_level": "low", "last_active_days": 30, "usage_trend": "up"}
    ]
    with open("data/logs/activity_logs_backup.json", "w") as f:
        json.dump(backup_activity, f, indent=2)

    # 干扰项3：已归档客户（不应处理）
    archived = [
        {"customer_id": "C006", "customer_name": "OldCo", "industry": "fintech", "tier": "mid_market", "labels": ["archived"], "owner_name": "Frank"}
    ]
    with open("data/customers/archived_customers.json", "w") as f:
        json.dump(archived, f, indent=2)

    # 干扰项4：无关目录
    with open("data/old_reports/note.txt", "w") as f:
        f.write("This is an old report, ignore it.\n")

if __name__ == "__main__":
    build_env()
