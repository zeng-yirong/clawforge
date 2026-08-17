import os
import json

def build_env():
    # Create directory structure
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # customers.json
    customers = [
        {"customer_id": "C001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "enterprise", "labels": ["existing"], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "mid_market", "labels": ["existing"], "owner_name": "Bob"},
        {"customer_id": "C003", "customer_name": "HealthSync", "industry": "healthcare", "tier": "mid_market", "labels": ["existing"], "owner_name": "Charlie"}
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # consumption_logs.json (latest)
    consumption_logs = [
        {"customer_id": "C001", "quarter_spend_usd": 62000},
        {"customer_id": "C002", "quarter_spend_usd": 18000}
    ]
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump(consumption_logs, f, indent=2)

    # activity_logs.json (latest)
    activity_logs = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 15, "usage_trend": "up"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 70, "usage_trend": "down"}
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # old_activity_logs.json (干扰)
    old_activity = [
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 30, "usage_trend": "up"},
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 200, "usage_trend": "down"}
    ]
    with open("data/logs/old_activity_logs.json", "w") as f:
        json.dump(old_activity, f, indent=2)

    # old_consumption_logs.json (干扰)
    old_consumption = [
        {"customer_id": "C003", "quarter_spend_usd": 40000}
    ]
    with open("data/logs/old_consumption_logs.json", "w") as f:
        json.dump(old_consumption, f, indent=2)

    # 其他无关文件，增加干扰
    os.makedirs("data/accounts", exist_ok=True)
    accounts = [
        {"account_id": "A001", "display_name": "Alice", "department": "Sales", "email": "alice@example.com", "permissions": ["read", "write"]},
        {"account_id": "A002", "display_name": "Bob", "department": "Engineering", "email": "bob@example.com", "permissions": ["read"]}
    ]
    with open("data/accounts/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 在ops目录下留一个占位文件，确保目录存在但无干扰（已经创建了目录）

if __name__ == "__main__":
    build_env()
