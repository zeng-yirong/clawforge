import os
import json
import random

def build_env():
    # Create directory structure
    os.makedirs("logs", exist_ok=True)
    os.makedirs("customers", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("raw_logs", exist_ok=True)

    # Main customers list
    customers = {
        "customers": [
            {"customer_id": "C001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "mid_market", "labels": ["existing"], "owner_name": "Alice"},
            {"customer_id": "C002", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": [], "owner_name": "Bob"},
            {"customer_id": "C003", "customer_name": "AlphaMed", "industry": "healthcare", "tier": "mid_market", "labels": ["vip"], "owner_name": "Charlie"},
            {"customer_id": "C004", "customer_name": "BetaBank", "industry": "fintech", "tier": "enterprise", "labels": ["partner"], "owner_name": "Dave"},
            {"customer_id": "C005", "customer_name": "GammaHealth", "industry": "healthcare", "tier": "mid_market", "labels": [], "owner_name": "Eve"}
        ]
    }
    with open("customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # Activity logs (one per customer)
    activity_logs = {
        "activity_logs": [
            {"customer_id": "C001", "risk_level": "low", "last_active_days": 10, "usage_trend": "up"},
            {"customer_id": "C002", "risk_level": "low", "last_active_days": 50, "usage_trend": "down"},
            {"customer_id": "C003", "risk_level": "high", "last_active_days": 70, "usage_trend": "down"},
            {"customer_id": "C004", "risk_level": "high", "last_active_days": 200, "usage_trend": "down"},
            {"customer_id": "C005", "risk_level": "low", "last_active_days": 15, "usage_trend": "up"}
        ]
    }
    with open("logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # Consumption logs (one per customer)
    consumption_logs = {
        "consumption_logs": [
            {"customer_id": "C001", "quarter_spend_usd": 60000},
            {"customer_id": "C002", "quarter_spend_usd": 15000},
            {"customer_id": "C003", "quarter_spend_usd": 25000},
            {"customer_id": "C004", "quarter_spend_usd": 8000},
            {"customer_id": "C005", "quarter_spend_usd": 30000}
        ]
    }
    with open("logs/consumption_logs.json", "w") as f:
        json.dump(consumption_logs, f, indent=2)

    # Distractors
    # 1. An archived customer not in main roster
    archived = {
        "archived_customers": [
            {"customer_id": "C006", "customer_name": "OldClient", "tier": "bronze", "labels": []}
        ]
    }
    with open("customers/archived_customers.json", "w") as f:
        json.dump(archived, f, indent=2)

    # 2. A backup CSV with irrelevant raw activity data
    with open("raw_logs/activity_backup.csv", "w") as f:
        f.write("timestamp,user,action\n2024-09-01,alice,login\n2024-09-02,bob,logout\n")

    # 3. A stale consumption log with different values (should be ignored)
    stale_consumption = {
        "consumption_logs": [
            {"customer_id": "C001", "quarter_spend_usd": 40000},
            {"customer_id": "C002", "quarter_spend_usd": 20000}
        ]
    }
    with open("logs/stale_consumption_logs.json", "w") as f:
        json.dump(stale_consumption, f, indent=2)

    # 4. An extra customer record in a non-standard file
    extra = {
        "extra_customers": [
            {"customer_id": "C007", "customer_name": "FakeCorp", "tier": "gold", "labels": []}
        ]
    }
    with open("customers/extra_customers.json", "w") as f:
        json.dump(extra, f, indent=2)

    # 5. A note file
    with open("README.txt", "w") as f:
        f.write("This workspace contains customer data for tier label update.\n")

if __name__ == "__main__":
    build_env()
