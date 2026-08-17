import os
import json

def build_env():
    # Ensure base directories
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---- Main customer list ----
    customers = [
        {"customer_id": "C001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "silver", "labels": ["active"], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "gold", "labels": ["premium"], "owner_name": "Bob"},
        {"customer_id": "C003", "customer_name": "CarePulse", "industry": "healthcare", "tier": "silver", "labels": ["active"], "owner_name": "Carol"},
        {"customer_id": "C004", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "bronze", "labels": ["new"], "owner_name": "David"}
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # ---- Consumption logs ----
    consumption_logs = [
        {"customer_id": "C001", "quarter_spend_usd": 12000},
        {"customer_id": "C002", "quarter_spend_usd": 9000},
        {"customer_id": "C003", "quarter_spend_usd": 2500},
        {"customer_id": "C004", "quarter_spend_usd": 6000},
        # Interloper: C005 not in customers list
        {"customer_id": "C005", "quarter_spend_usd": 15000}
    ]
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump(consumption_logs, f, indent=2)

    # ---- Activity logs ----
    activity_logs = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 15, "usage_trend": "up"},
        {"customer_id": "C002", "risk_level": "low", "last_active_days": 55, "usage_trend": "down"},
        {"customer_id": "C003", "risk_level": "high", "last_active_days": 200, "usage_trend": "down"},
        {"customer_id": "C004", "risk_level": "low", "last_active_days": 30, "usage_trend": "up"},
        # same interloper
        {"customer_id": "C005", "risk_level": "low", "last_active_days": 10, "usage_trend": "up"}
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # ---- Distractors ----
    # Old activity logs (duplicate with outdated data)
    old_activity = [
        {"customer_id": "C001", "risk_level": "high", "last_active_days": 120, "usage_trend": "down"}
    ]
    with open("data/logs/old_activity_logs.json", "w") as f:
        json.dump(old_activity, f, indent=2)

    # Unrelated accounts.json
    accounts = [
        {"account_id": "ACC01", "display_name": "Admin", "department": "IT", "email": "admin@corp.com", "permissions": ["read", "write"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # Unrelated attachments
    attachments = [
        {"path": "data/logs/old_activity_logs.json", "title": "Old Activity Backup", "kind": "log", "description": "Backup from Q1"}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # Backup customer list with different tiers (misleading)
    backup_customers = [
        {"customer_id": "C001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "bronze", "labels": ["inactive"], "owner_name": "Alice"}
    ]
    with open("data/customers/backup_customers.json", "w") as f:
        json.dump(backup_customers, f, indent=2)

if __name__ == "__main__":
    build_env()
