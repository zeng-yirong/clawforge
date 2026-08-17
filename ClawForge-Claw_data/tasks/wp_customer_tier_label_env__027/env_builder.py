import os
import json

def build_env():
    # Create directory structure
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("customers", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # -------------------- Customers master --------------------
    customers = {
        "customers": [
            {
                "customer_id": "cust_carepulse",
                "customer_name": "CarePulse",
                "industry": "healthcare",
                "tier": "enterprise",
                "labels": ["enterprise", "priority:high"],
                "owner_name": "Alice"
            },
            {
                "customer_id": "cust_ledgerflow",
                "customer_name": "LedgerFlow",
                "industry": "fintech",
                "tier": "mid_market",
                "labels": ["mid_market", "risk:low"],
                "owner_name": "Bob"
            },
            {
                "customer_id": "cust_healthplus",
                "customer_name": "HealthPlus",
                "industry": "healthcare",
                "tier": "startup",
                "labels": ["startup"],
                "owner_name": "Carol"
            },
            {
                "customer_id": "cust_dummy",
                "customer_name": "DummyCorp",
                "industry": "retail",
                "tier": "basic",
                "labels": ["basic"],
                "owner_name": "Eve"
            }
        ]
    }
    with open("customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # -------------------- Consumption logs --------------------
    consumption_logs = {
        "consumption_logs": [
            {"customer_id": "cust_carepulse", "quarter_spend_usd": 60000},
            {"customer_id": "cust_ledgerflow", "quarter_spend_usd": 30000},
            {"customer_id": "cust_healthplus", "quarter_spend_usd": 8000},
            # invalid record (negative spend) – should be ignored
            {"customer_id": "cust_dummy", "quarter_spend_usd": -500}
        ]
    }
    with open("raw_data/consumption_logs.json", "w") as f:
        json.dump(consumption_logs, f, indent=2)

    # -------------------- Activity logs --------------------
    activity_logs = {
        "activity_logs": [
            {"customer_id": "cust_carepulse", "risk_level": "low", "last_active_days": 5, "usage_trend": "up"},
            {"customer_id": "cust_ledgerflow", "risk_level": "low", "last_active_days": 20, "usage_trend": "down"},
            {"customer_id": "cust_healthplus", "risk_level": "high", "last_active_days": 60, "usage_trend": "down"}
            # cust_dummy has no activity log – must be skipped
        ]
    }
    with open("raw_data/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # -------------------- Interference files (old backups) --------------------
    old_activity = {
        "activity_logs": [
            {"customer_id": "cust_dummy", "risk_level": "low", "last_active_days": 2, "usage_trend": "up"}
        ]
    }
    with open("raw_data/old_activity_logs_backup.json", "w") as f:
        json.dump(old_activity, f, indent=2)

    old_customers = {
        "customers": [
            {"customer_id": "cust_old", "customer_name": "OldCo", "industry": "fintech", "tier": "legacy", "labels": ["legacy"], "owner_name": "None"}
        ]
    }
    with open("raw_data/backup_customers.json", "w") as f:
        json.dump(old_customers, f, indent=2)

    # Empty ops dummy (to ensure dir exists)
    with open("ops/.gitkeep", "w") as f:
        f.write("")

if __name__ == "__main__":
    build_env()
