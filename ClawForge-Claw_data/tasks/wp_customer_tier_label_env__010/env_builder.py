import json, os

def build_env():
    # 确保目录存在
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 客户基本信息 (5个客户)
    customers = [
        {
            "customer_id": "C001",
            "customer_name": "Alpha Corp",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": [],
            "owner_name": "Alice"
        },
        {
            "customer_id": "C002",
            "customer_name": "Beta Inc",
            "industry": "healthcare",
            "tier": "mid_market",
            "labels": [],
            "owner_name": "Bob"
        },
        {
            "customer_id": "C003",
            "customer_name": "Gamma Ltd",
            "industry": "fintech",
            "tier": "mid_market",
            "labels": [],
            "owner_name": "Carol"
        },
        {
            "customer_id": "C004",
            "customer_name": "Delta Co",
            "industry": "healthcare",
            "tier": "enterprise",
            "labels": [],
            "owner_name": "Dave"
        },
        {
            "customer_id": "C005",
            "customer_name": "Epsilon LLC",
            "industry": "fintech",
            "tier": "mid_market",
            "labels": [],
            "owner_name": "Eve"
        }
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # 消费数据 (对应5个客户)
    consumption_logs = [
        {"customer_id": "C001", "quarter_spend_usd": 75000},
        {"customer_id": "C002", "quarter_spend_usd": 30000},
        {"customer_id": "C003", "quarter_spend_usd": 10000},
        {"customer_id": "C004", "quarter_spend_usd": 60000},
        {"customer_id": "C005", "quarter_spend_usd": 25000}
    ]
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump(consumption_logs, f, indent=2)

    # 活跃数据 (对应5个客户)
    activity_logs = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 15, "usage_trend": "up"},
        {"customer_id": "C002", "risk_level": "low", "last_active_days": 45, "usage_trend": "up"},
        {"customer_id": "C003", "risk_level": "high", "last_active_days": 90, "usage_trend": "down"},
        {"customer_id": "C004", "risk_level": "low", "last_active_days": 10, "usage_trend": "up"},
        {"customer_id": "C005", "risk_level": "high", "last_active_days": 20, "usage_trend": "up"}
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # 干扰文件：旧季度消费数据
    old_consumption = [
        {"customer_id": "C001", "quarter_spend_usd": 45000},
        {"customer_id": "C002", "quarter_spend_usd": 20000}
    ]
    with open("data/logs/consumption_logs_2024Q2.json", "w") as f:
        json.dump(old_consumption, f, indent=2)

    # 干扰文件：无关的附件/账户数据
    attachments = [{"path": "/tmp/report.pdf", "title": "Q3 Summary", "kind": "pdf", "description": "unrelated"}]
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    accounts = [{"account_id": "ACC001", "display_name": "Admin", "department": "IT", "email": "admin@co.com", "permissions": ["read"]}]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

if __name__ == "__main__":
    build_env()
