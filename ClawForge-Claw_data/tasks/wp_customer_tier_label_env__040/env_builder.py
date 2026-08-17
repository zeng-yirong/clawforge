import os
import json

def build_env():
    # Create required directories
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("temp", exist_ok=True)

    # Main customer data
    customers = {
        "customers": [
            {"customer_id": "CP001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "mid_market", "labels": [], "owner_name": "Alice"},
            {"customer_id": "LF001", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": [], "owner_name": "Bob"},
            {"customer_id": "NT001", "customer_name": "NovaTech", "industry": "fintech", "tier": "mid_market", "labels": [], "owner_name": "Charlie"}
        ]
    }
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # Outdated backup (distraction)
    backup_customers = {
        "customers": [
            {"customer_id": "CP001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "enterprise", "labels": ["vip"], "owner_name": "Alice"},
            {"customer_id": "LF001", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "mid_market", "labels": [], "owner_name": "Bob"}
        ]
    }
    with open("data/customers/backup_customers.json", "w") as f:
        json.dump(backup_customers, f, indent=2)

    # Activity logs
    activity_logs = {
        "activity_logs": [
            {"customer_id": "CP001", "risk_level": "low", "last_active_days": 10, "usage_trend": "up"},
            {"customer_id": "LF001", "risk_level": "high", "last_active_days": 50, "usage_trend": "down"},
            {"customer_id": "NT001", "risk_level": "low", "last_active_days": 120, "usage_trend": "down"}
        ]
    }
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # Consumption logs
    consumption_logs = {
        "consumption_logs": [
            {"customer_id": "CP001", "quarter_spend_usd": 6000},
            {"customer_id": "LF001", "quarter_spend_usd": 2000},
            {"customer_id": "NT001", "quarter_spend_usd": 0}
        ]
    }
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump(consumption_logs, f, indent=2)

    # Old consumption data (distraction)
    old_consumption = {
        "consumption_logs": [
            {"customer_id": "CP001", "quarter_spend_usd": 4000},
            {"customer_id": "LF001", "quarter_spend_usd": 5000}
        ]
    }
    with open("data/logs/old_consumption_logs.json", "w") as f:
        json.dump(old_consumption, f, indent=2)

    # Tier rules (JSON for machine readability)
    tier_rules = [
        {"label": "premium", "conditions": {"quarter_spend_usd_ge": 5000, "last_active_days_le": 30}},
        {"label": "dormant", "conditions": {"quarter_spend_usd_lt": 1000, "last_active_days_gt": 90}},
        {"label": "at_risk", "conditions": {"risk_level": "high"}},
        {"label": "standard", "default": True}
    ]
    with open("ops/tier_rules.json", "w") as f:
        json.dump(tier_rules, f, indent=2)

    # Irrelevant attachment listing
    attachments = {
        "attachments": [
            {"path": "data/logs/old_consumption_logs.json", "title": "Old Q1 consumption", "kind": "json", "description": "Previous quarter data"}
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # Empty placeholder
    open("temp/placeholder.txt", "a").close()

if __name__ == "__main__":
    build_env()
