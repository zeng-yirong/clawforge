import json
import os

def build_env():
    # customers
    customers = [
        {
            "customer_id": "C001",
            "customer_name": "CarePulse",
            "industry": "healthcare",
            "tier": "mid_market",
            "labels": ["standard"],
            "owner_name": "Alice"
        },
        {
            "customer_id": "C002",
            "customer_name": "LedgerFlow",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["premium"],
            "owner_name": "Bob"
        },
        {
            "customer_id": "C003",
            "customer_name": "HealthSync",
            "industry": "healthcare",
            "tier": "enterprise",
            "labels": ["premium", "high_value"],
            "owner_name": "Carol"
        },
        {
            "customer_id": "C004",
            "customer_name": "FinCore",
            "industry": "fintech",
            "tier": "mid_market",
            "labels": ["standard"],
            "owner_name": "Dave"
        },
        {
            "customer_id": "C005",
            "customer_name": "MediTrack",
            "industry": "healthcare",
            "tier": "mid_market",
            "labels": ["standard"],
            "owner_name": "Eve"
        },
        {
            "customer_id": "C006",
            "customer_name": "PayNest",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["premium", "high_value"],
            "owner_name": "Frank"
        }
    ]
    os.makedirs("data/customers", exist_ok=True)
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # consumption logs (quarter_spend_usd)
    consumption = [
        {"customer_id": "C001", "quarter_spend_usd": 150000},
        {"customer_id": "C002", "quarter_spend_usd": 75000},
        {"customer_id": "C003", "quarter_spend_usd": 200000},
        {"customer_id": "C004", "quarter_spend_usd": 30000},
        {"customer_id": "C005", "quarter_spend_usd": 120000},
        # C006 missing consumption log (intentionally)
    ]
    os.makedirs("data/logs", exist_ok=True)
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump({"consumption_logs": consumption}, f, indent=2)

    # activity logs
    activity = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 5, "usage_trend": "up"},
        {"customer_id": "C002", "risk_level": "low", "last_active_days": 20, "usage_trend": "up"},
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 10, "usage_trend": "up"},
        {"customer_id": "C004", "risk_level": "high", "last_active_days": 60, "usage_trend": "down"},
        # C005 missing activity log
        {"customer_id": "C006", "risk_level": "low", "last_active_days": 1, "usage_trend": "up"}
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity}, f, indent=2)

    # distraction: old label_updates.json (empty)
    os.makedirs("ops", exist_ok=True)
    with open("ops/label_updates.json", "w") as f:
        json.dump([], f)

    # distraction: raw_logs with an irrelevant CSV
    os.makedirs("raw_logs", exist_ok=True)
    with open("raw_logs/session_dump.csv", "w") as f:
        f.write("session,time,status\ns001,2025-01-01,closed\n")

    # distraction: extra customer not in logs
    extra_customers = [
        {"customer_id": "C007", "customer_name": "DataBridge", "industry": "fintech",
         "tier": "mid_market", "labels": ["standard"], "owner_name": "Grace"}
    ]
    with open("data/customers/customers.json", "r") as f:
        current = json.load(f)
    current["customers"].extend(extra_customers)
    with open("data/customers/customers.json", "w") as f:
        json.dump(current, f, indent=2)

if __name__ == "__main__":
    build_env()
