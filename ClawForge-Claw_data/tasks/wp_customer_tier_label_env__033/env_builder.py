import json
import os

def build_env():
    # Create directory structure
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Customers (3 valid + 1 incomplete as decoy? Actually we'll keep all complete for simplicity, but add decoy logs)
    customers = [
        {
            "customer_id": "cust_001",
            "customer_name": "CarePulse",
            "industry": "healthcare",
            "tier": "enterprise",
            "labels": ["existing"],
            "owner_name": "Alice"
        },
        {
            "customer_id": "cust_002",
            "customer_name": "LedgerFlow",
            "industry": "fintech",
            "tier": "mid_market",
            "labels": [],
            "owner_name": "Bob"
        },
        {
            "customer_id": "cust_003",
            "customer_name": "CarePulse",
            "industry": "healthcare",
            "tier": "mid_market",
            "labels": ["vip"],
            "owner_name": "Charlie"
        }
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # Activity logs (3 valid + 1 decoy for non-existent customer)
    activity_logs = [
        {"customer_id": "cust_001", "risk_level": "low", "last_active_days": 25, "usage_trend": "up"},
        {"customer_id": "cust_002", "risk_level": "high", "last_active_days": 120, "usage_trend": "down"},
        {"customer_id": "cust_003", "risk_level": "low", "last_active_days": 5, "usage_trend": "up"},
        {"customer_id": "cust_999", "risk_level": "high", "last_active_days": 200, "usage_trend": "down"}  # decoy
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # Consumption logs (3 valid + 1 decoy)
    consumption_logs = [
        {"customer_id": "cust_001", "quarter_spend_usd": 12000},
        {"customer_id": "cust_002", "quarter_spend_usd": 3000},
        {"customer_id": "cust_003", "quarter_spend_usd": 8000},
        {"customer_id": "cust_999", "quarter_spend_usd": 9999}  # decoy
    ]
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump({"consumption_logs": consumption_logs}, f, indent=2)

if __name__ == "__main__":
    build_env()
