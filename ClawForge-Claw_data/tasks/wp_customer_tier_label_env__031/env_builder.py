import os
import json

def build_env():
    # 创建目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    # 客户主数据（含干扰字段）
    customers = {
        "customers": [
            {
                "customer_id": "cust_001",
                "customer_name": "CarePulse",
                "industry": "healthcare",
                "tier": "enterprise",
                "labels": ["old_label"],
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
                "customer_name": "HealthWell",
                "industry": "healthcare",
                "tier": "enterprise",
                "labels": ["gold"],
                "owner_name": "Carol"
            }
        ]
    }
    with open("data/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # 消费日志（主文件）
    consumption = {
        "consumption_logs": [
            {"customer_id": "cust_001", "quarter_spend_usd": 12000},
            {"customer_id": "cust_002", "quarter_spend_usd": 8000},
            {"customer_id": "cust_003", "quarter_spend_usd": 15000}
        ]
    }
    with open("logs/consumption_logs.json", "w") as f:
        json.dump(consumption, f, indent=2)

    # 活动日志（主文件）
    activity = {
        "activity_logs": [
            {"customer_id": "cust_001", "risk_level": "low", "last_active_days": 25, "usage_trend": "up"},
            {"customer_id": "cust_002", "risk_level": "low", "last_active_days": 10, "usage_trend": "down"},
            {"customer_id": "cust_003", "risk_level": "high", "last_active_days": 45, "usage_trend": "up"}
        ]
    }
    with open("logs/activity_logs.json", "w") as f:
        json.dump(activity, f, indent=2)

    # 干扰文件：过期活动日志
    old_activity = {
        "activity_logs": [
            {"customer_id": "cust_001", "risk_level": "low", "last_active_days": 60, "usage_trend": "up"},
            {"customer_id": "cust_002", "risk_level": "low", "last_active_days": 90, "usage_trend": "down"}
        ]
    }
    with open("logs/activity_logs_old.json", "w") as f:
        json.dump(old_activity, f, indent=2)

    # 干扰文件：重复消费记录（数值不同）
    dup_consumption = {
        "consumption_logs": [
            {"customer_id": "cust_001", "quarter_spend_usd": 9999},
            {"customer_id": "cust_003", "quarter_spend_usd": 14999}
        ]
    }
    with open("logs/consumption_logs_duplicate.json", "w") as f:
        json.dump(dup_consumption, f, indent=2)

    # 干扰文件：无关联系人
    contacts = {
        "contacts": [
            {"contact_id": "c1", "name": "Alice", "role": "admin", "email": "alice@example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

if __name__ == "__main__":
    build_env()
