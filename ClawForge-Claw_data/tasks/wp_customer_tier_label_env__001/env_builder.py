import os
import json
import random
random.seed(42)

def build_env():
    # 确保目录结构
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/labels", exist_ok=True)  # 空目录，留给agent写
    os.makedirs("ops", exist_ok=True)  # 干扰目录

    # 1. customers.json (5个客户)
    customers = [
        {
            "customer_id": "C001",
            "customer_name": "CarePulse",
            "industry": "healthcare",
            "tier": "mid_market",
            "labels": [],
            "owner_name": "Alice"
        },
        {
            "customer_id": "C002",
            "customer_name": "LedgerFlow",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": [],
            "owner_name": "Bob"
        },
        {
            "customer_id": "C003",
            "customer_name": "HealthPlus",
            "industry": "healthcare",
            "tier": "mid_market",
            "labels": [],
            "owner_name": "Carol"
        },
        {
            "customer_id": "C004",
            "customer_name": "FinTechX",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": [],
            "owner_name": "Dave"
        },
        {
            "customer_id": "C005",
            "customer_name": "OldData",
            "industry": "healthcare",
            "tier": "mid_market",
            "labels": ["legacy"],
            "owner_name": "Eve"
        }
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # 2. consumption_logs.json (除C005外都有，C005缺失)
    consumption_logs = [
        {"customer_id": "C001", "quarter_spend_usd": 8000},
        {"customer_id": "C002", "quarter_spend_usd": 15000},
        {"customer_id": "C003", "quarter_spend_usd": 50000},
        {"customer_id": "C004", "quarter_spend_usd": 25000}
        # C005 故意缺失
    ]
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump(consumption_logs, f, indent=2)

    # 3. activity_logs.json (所有5个客户都有)
    activity_logs = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 5, "usage_trend": "up"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 100, "usage_trend": "down"},
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 10, "usage_trend": "up"},
        {"customer_id": "C004", "risk_level": "mid", "last_active_days": 60, "usage_trend": "up"},
        {"customer_id": "C005", "risk_level": "high", "last_active_days": 200, "usage_trend": "down"}
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # 4. 干扰文件
    # 旧的activity日志，数据不同
    old_activity = [
        {"customer_id": "C001", "risk_level": "high", "last_active_days": 60, "usage_trend": "up"},
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 45, "usage_trend": "down"}
    ]
    with open("data/logs/old_activity_logs.json", "w") as f:
        json.dump(old_activity, f, indent=2)

    # 备份customers（过时）
    backup_customers = [
        {
            "customer_id": "C001",
            "customer_name": "CarePulse",
            "industry": "healthcare",
            "tier": "enterprise",
            "labels": ["vip"],
            "owner_name": "Alice"
        }
    ]
    with open("data/customers/backup_customers.json", "w") as f:
        json.dump(backup_customers, f, indent=2)

    # 无关的ops文件夹中的文件
    with open("ops/notes.txt", "w") as f:
        f.write("Don't use this file.")

    # 5. 额外干扰：在consumption_logs中加入一个不存在的客户（Ghost）
    # 但注意，按规则这个客户不在customers中，Agent应该忽略
    with open("data/logs/consumption_logs.json", "r") as f:
        existing = json.load(f)
    existing.append({"customer_id": "GHOST", "quarter_spend_usd": 99999})
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump(existing, f, indent=2)

    # 6. 额外干扰：activity_logs中也加一个Ghost
    with open("data/logs/activity_logs.json", "r") as f:
        existing_act = json.load(f)
    existing_act.append({"customer_id": "GHOST", "risk_level": "low", "last_active_days": 1, "usage_trend": "up"})
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(existing_act, f, indent=2)

if __name__ == "__main__":
    build_env()
