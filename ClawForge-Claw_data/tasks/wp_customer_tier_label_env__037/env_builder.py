import json
import os

def build_env():
    # --- 客户主数据 ---
    customers = [
        {
            "customer_id": "C001",
            "customer_name": "CarePulse",
            "industry": "healthcare",
            "tier": "enterprise",
            "labels": ["existing_label"],
            "owner_name": "Alice"
        },
        {
            "customer_id": "C002",
            "customer_name": "LedgerFlow",
            "industry": "fintech",
            "tier": "mid_market",
            "labels": [],
            "owner_name": "Bob"
        },
        {
            "customer_id": "C003",
            "customer_name": "WellCare",
            "industry": "healthcare",
            "tier": "mid_market",
            "labels": ["old"],
            "owner_name": "Charlie"
        },
        {
            "customer_id": "C004",
            "customer_name": "FinTechCo",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": [],
            "owner_name": "Diana"
        },
        # 干扰：客户在消费记录里是无效字符串
        {
            "customer_id": "C005",
            "customer_name": "PulsePlus",
            "industry": "healthcare",
            "tier": "mid_market",
            "labels": [],
            "owner_name": "Eve"
        },
        # 干扰：客户没有任何消费和活动日志
        {
            "customer_id": "C006",
            "customer_name": "GhostCorp",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["legacy"],
            "owner_name": "Frank"
        }
    ]

    # --- 消费日志 ---
    consumption_logs = [
        {"customer_id": "C001", "quarter_spend_usd": 15000},
        {"customer_id": "C002", "quarter_spend_usd": 3000},
        {"customer_id": "C003", "quarter_spend_usd": 8000},
        {"customer_id": "C004", "quarter_spend_usd": 12000},
        # 干扰：消费金额为无效字符串
        {"customer_id": "C005", "quarter_spend_usd": "N/A"}
    ]

    # --- 活动日志 ---
    activity_logs = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 25, "usage_trend": "up"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 120, "usage_trend": "down"},
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 60, "usage_trend": "stable"},
        {"customer_id": "C004", "risk_level": "low", "last_active_days": 45, "usage_trend": "up"},
        # 干扰：C005 有活动记录，但消费无效，最终应被跳过
        {"customer_id": "C005", "risk_level": "low", "last_active_days": 10, "usage_trend": "up"}
    ]

    # --- 写出文件 ---
    os.makedirs("data/customers", exist_ok=True)
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    os.makedirs("data/logs", exist_ok=True)
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump({"consumption_logs": consumption_logs}, f, indent=2)

    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # 额外创建 ops 目录（空），便于 agent 写入结果
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
