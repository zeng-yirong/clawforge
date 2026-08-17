import os
import json

def build_env():
    # 确保目录存在
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs/live", exist_ok=True)
    os.makedirs("data/logs/archive", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 预先创建空目录，但验证时不要求文件存在

    # 客户档案（2个真实客户 + 2个干扰客户？但enum限制只能CarePulse和LedgerFlow，所以只创建这两个，但可以增加不同ID但同名？为了清晰，只创建两个）
    customers = [
        {
            "customer_id": "C001",
            "customer_name": "CarePulse",
            "industry": "healthcare",
            "tier": "enterprise",
            "labels": ["existing_label1"],
            "owner_name": "Alice"
        },
        {
            "customer_id": "C002",
            "customer_name": "LedgerFlow",
            "industry": "fintech",
            "tier": "mid_market",
            "labels": ["existing_label2"],
            "owner_name": "Bob"
        }
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # 真实活动日志 (live)
    live_activity = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 5, "usage_trend": "up"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 60, "usage_trend": "down"}
    ]
    with open("data/logs/live/activity_logs.json", "w") as f:
        json.dump({"activity_logs": live_activity}, f, indent=2)

    # 真实消费日志 (live)
    live_consumption = [
        {"customer_id": "C001", "quarter_spend_usd": 60000},
        {"customer_id": "C002", "quarter_spend_usd": 30000}
    ]
    with open("data/logs/live/consumption_logs.json", "w") as f:
        json.dump({"consumption_logs": live_consumption}, f, indent=2)

    # 存档（旧数据，干扰）
    archive_activity = [
        {"customer_id": "C001", "risk_level": "high", "last_active_days": 100, "usage_trend": "down"},
        {"customer_id": "C002", "risk_level": "low", "last_active_days": 3, "usage_trend": "up"}
    ]
    with open("data/logs/archive/activity_logs.json", "w") as f:
        json.dump({"activity_logs": archive_activity}, f, indent=2)

    archive_consumption = [
        {"customer_id": "C001", "quarter_spend_usd": 20000},
        {"customer_id": "C002", "quarter_spend_usd": 80000}
    ]
    with open("data/logs/archive/consumption_logs.json", "w") as f:
        json.dump({"consumption_logs": archive_consumption}, f, indent=2)

    # 根目录下的旧数据（另一层干扰）
    root_activity = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 90, "usage_trend": "down"},
        {"customer_id": "C002", "risk_level": "low", "last_active_days": 10, "usage_trend": "up"}
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": root_activity}, f, indent=2)

    root_consumption = [
        {"customer_id": "C001", "quarter_spend_usd": 10000},
        {"customer_id": "C002", "quarter_spend_usd": 90000}
    ]
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump({"consumption_logs": root_consumption}, f, indent=2)

    # 附加一个无关的附件文件，增加迷惑性
    os.makedirs("data", exist_ok=True)
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": []}, f, indent=2)

if __name__ == "__main__":
    build_env()
