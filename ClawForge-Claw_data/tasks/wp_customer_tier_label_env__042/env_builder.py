import os
import json
import random

def build_env():
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("rules", exist_ok=True)

    # customers
    customers = [
        {"customer_id": "C001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "enterprise", "labels": ["premium","vip"], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "mid_market", "labels": ["standard"], "owner_name": "Bob"},
        {"customer_id": "C003", "customer_name": "FinTechX", "industry": "fintech", "tier": "mid_market", "labels": ["new"], "owner_name": "Charlie"},
        {"customer_id": "C004", "customer_name": "HealthPlus", "industry": "healthcare", "tier": "enterprise", "labels": ["legacy"], "owner_name": "Diana"},
        {"customer_id": "C005", "customer_name": "DataCorp", "industry": "fintech", "tier": "mid_market", "labels": ["trial"], "owner_name": "Eve"}
    ]
    with open("data/customers/customers.json","w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # activity logs
    activity_logs = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 15, "usage_trend": "up"},
        {"customer_id": "C002", "risk_level": "low", "last_active_days": 45, "usage_trend": "up"},
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 90, "usage_trend": "down"},
        {"customer_id": "C004", "risk_level": "low", "last_active_days": 10, "usage_trend": "up"},
        {"customer_id": "C005", "risk_level": "high", "last_active_days": 120, "usage_trend": "down"}
    ]
    with open("data/logs/activity_logs.json","w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # consumption logs (C004 has dirty record)
    consumption_logs = [
        {"customer_id": "C001", "quarter_spend_usd": 25000},
        {"customer_id": "C002", "quarter_spend_usd": 12000},
        {"customer_id": "C003", "quarter_spend_usd": 8000},
        {"customer_id": "C004", "quarter_spend_usd": "N/A"},
        {"customer_id": "C005", "quarter_spend_usd": 5000}
    ]
    with open("data/logs/consumption_logs.json","w") as f:
        json.dump({"consumption_logs": consumption_logs}, f, indent=2)

    # segmentation rules (correct)
    rules = {
        "tiers": {
            "gold": {"min_spend": 20000, "max_inactive_days": 30},
            "silver": {"min_spend": 10000, "max_inactive_days": 60}
        },
        "fallback": "churn_risk",
        "churn_conditions": {"risk_level": "high", "usage_trend": "down"}
    }
    with open("rules/segmentation_rules.json","w") as f:
        json.dump(rules, f, indent=2)

    # old rules (interference)
    old_rules = {
        "tiers": {
            "gold": {"min_spend": 30000, "max_inactive_days": 20},
            "silver": {"min_spend": 15000, "max_inactive_days": 30}
        },
        "fallback": "churn_risk",
        "churn_conditions": {"risk_level": "high"}
    }
    with open("rules/old_rules.json","w") as f:
        json.dump(old_rules, f, indent=2)

    # legacy customer backup (interference)
    backup_customers = [
        {"customer_id": "C001", "customer_name": "CarePulse", "labels": ["gold"]},
        {"customer_id": "C006", "customer_name": "GhostCorp", "labels": ["unknown"]}
    ]
    with open("data/customers/customers_backup.json","w") as f:
        json.dump({"customers": backup_customers}, f, indent=2)

if __name__ == "__main__":
    build_env()
