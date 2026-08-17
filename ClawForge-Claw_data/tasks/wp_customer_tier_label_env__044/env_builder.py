import json
import os

def build_env():
    # 数据目录
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)

    # 客户档案 (干扰项：已经有一个客户 LedgerFlow，标签为空)
    customers = {
        "customers": [
            {
                "customer_id": "CarePulse",
                "customer_name": "CarePulse",
                "industry": "healthcare",
                "tier": "enterprise",
                "labels": [],
                "owner_name": "Alice"
            },
            {
                "customer_id": "LedgerFlow",
                "customer_name": "LedgerFlow",
                "industry": "fintech",
                "tier": "mid_market",
                "labels": [],
                "owner_name": "Bob"
            }
        ]
    }
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # 消费日志 (最新数据)
    consumption_logs = {
        "consumption_logs": [
            {
                "customer_id": "CarePulse",
                "quarter_spend_usd": 15000
            },
            {
                "customer_id": "LedgerFlow",
                "quarter_spend_usd": 2000
            }
        ]
    }
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump(consumption_logs, f, indent=2)

    # 错误干扰：一份过期的消费日志 (CarePulse 消费 8000，会误导为 Active)
    old_consumption = {
        "consumption_logs": [
            {
                "customer_id": "CarePulse",
                "quarter_spend_usd": 8000
            }
        ]
    }
    with open("data/logs/consumption_logs_2023.json", "w") as f:
        json.dump(old_consumption, f, indent=2)

    # 活动日志
    activity_logs = {
        "activity_logs": [
            {
                "customer_id": "CarePulse",
                "risk_level": "low",
                "last_active_days": 5,
                "usage_trend": "up"
            },
            {
                "customer_id": "LedgerFlow",
                "risk_level": "high",
                "last_active_days": 90,
                "usage_trend": "down"
            }
        ]
    }
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # 附件：分段规则
    rules_text = """# Segment Rules
- VIP: quarter_spend_usd >= 10000 and last_active_days <= 30
- Active: quarter_spend_usd >= 5000 and last_active_days <= 60
- Standard: otherwise
"""
    with open("data/attachments/segment_rules.txt", "w") as f:
        f.write(rules_text)

    # 额外诱饵文件（无实际影响）
    with open("data/logs/activity_logs_backup.json", "w") as f:
        json.dump({"activity_logs": []}, f)
    with open("data/customers/customers_backup.json", "w") as f:
        json.dump({"customers": []}, f)

if __name__ == "__main__":
    build_env()
