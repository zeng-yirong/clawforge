import os
import json

def build_env():
    # Create directory structure
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("archive", exist_ok=True)

    # Customer data (5 records, one with industry "education" as distraction)
    customers = [
        {"customer_id": "C001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "enterprise", "labels": ["active"]},
        {"customer_id": "C002", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "mid_market", "labels": ["vip"]},
        {"customer_id": "C003", "customer_name": "CarePulse", "industry": "healthcare", "tier": "enterprise", "labels": ["new"]},
        {"customer_id": "C004", "customer_name": "DataStream", "industry": "fintech", "tier": "mid_market", "labels": ["inactive"]},
        {"customer_id": "C005", "customer_name": "EduLearn", "industry": "education", "tier": "mid_market", "labels": ["startup"]}
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # Real activity logs
    activity_logs = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 10, "usage_trend": "up"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 150, "usage_trend": "down"},
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 45, "usage_trend": "up"},
        {"customer_id": "C004", "risk_level": "high", "last_active_days": 200, "usage_trend": "down"},
        {"customer_id": "C005", "risk_level": "low", "last_active_days": 30, "usage_trend": "up"}
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # Real consumption logs
    consumption_logs = [
        {"customer_id": "C001", "quarter_spend_usd": 12000},
        {"customer_id": "C002", "quarter_spend_usd": 500},
        {"customer_id": "C003", "quarter_spend_usd": 9000},
        {"customer_id": "C004", "quarter_spend_usd": 1500},
        {"customer_id": "C005", "quarter_spend_usd": 3000}
    ]
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump(consumption_logs, f, indent=2)

    # Distractor: old activity logs with different values (would lead to wrong labels)
    old_logs = [
        {"customer_id": "C001", "risk_level": "high", "last_active_days": 90, "usage_trend": "down"},
        {"customer_id": "C002", "risk_level": "low", "last_active_days": 20, "usage_trend": "up"},
        {"customer_id": "C003", "risk_level": "high", "last_active_days": 200, "usage_trend": "down"},
        {"customer_id": "C004", "risk_level": "low", "last_active_days": 15, "usage_trend": "up"},
        {"customer_id": "C005", "risk_level": "high", "last_active_days": 180, "usage_trend": "down"}
    ]
    with open("data/logs/activity_logs_old.json", "w") as f:
        json.dump(old_logs, f, indent=2)

    # Distractor: an extra customer file in archive
    archive_customer = [{"customer_id": "C099", "customer_name": "Ghost", "industry": "fintech", "tier": "enterprise", "labels": ["legacy"]}]
    with open("archive/customers_backup.json", "w") as f:
        json.dump(archive_customer, f, indent=2)

if __name__ == "__main__":
    build_env()
