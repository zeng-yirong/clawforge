import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("raw_logs", exist_ok=True)
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 预创建，agent可直接写入

    # 活动日志（每个客户一条，没有歧义）
    activity_logs = [
        {"customer_id": "CarePulse", "risk_level": "low", "last_active_days": 20, "usage_trend": "up"},
        {"customer_id": "LedgerFlow", "risk_level": "high", "last_active_days": 90, "usage_trend": "down"}
    ]
    with open("raw_logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f)

    # 消费日志
    consumption_logs = [
        {"customer_id": "CarePulse", "quarter_spend_usd": 6000},
        {"customer_id": "LedgerFlow", "quarter_spend_usd": 1500}
    ]
    with open("raw_logs/consumption_logs.json", "w") as f:
        json.dump(consumption_logs, f)

    # 客户清单（含原始 tier 和 labels，干扰项）
    customers = {
        "customers": [
            {"customer_id": "CarePulse", "customer_name": "CarePulse", "industry": "healthcare", "tier": "enterprise", "labels": ["old_manual"], "owner_name": "Alice"},
            {"customer_id": "LedgerFlow", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "mid_market", "labels": ["vip"], "owner_name": "Bob"}
        ]
    }
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f)

    # 额外干扰文件：旧标签备份，诱饵
    with open("raw_logs/old_labels_backup.json", "w") as f:
        json.dump({"CarePulse": "enterprise", "LedgerFlow": "mid_market"}, f)

if __name__ == "__main__":
    build_env()
