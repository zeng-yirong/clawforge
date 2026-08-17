import json
import os
import random

def build_env():
    # 创建目录
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 客户数据（包含有效和无效客户）
    customers = [
        {"customer_id": "C001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "enterprise", "labels": [], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "mid_market", "labels": [], "owner_name": "Bob"},
        {"customer_id": "C003", "customer_name": "DataBridge", "industry": "fintech", "tier": "enterprise", "labels": [], "owner_name": "Charlie"},
        {"customer_id": "C004", "customer_name": "HealthSync", "industry": "healthcare", "tier": "mid_market", "labels": [], "owner_name": "Diana", "is_deleted": True},  # 已删除
        {"customer_id": "C005", "customer_name": "CloudNest", "industry": "fintech", "tier": "enterprise", "labels": [], "owner_name": "Eve"},
        {"customer_id": "C006", "customer_name": "MediCore", "industry": "healthcare", "tier": "mid_market", "labels": [], "owner_name": "Frank"},
        {"customer_id": "C007", "customer_name": "FinEdge", "industry": "fintech", "tier": "enterprise", "labels": [], "owner_name": "Grace"}
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # 活动日志（包含脏数据：负数 last_active_days）
    activity_logs = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 15, "usage_trend": "up"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 45, "usage_trend": "down"},
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 90, "usage_trend": "up"},
        {"customer_id": "C005", "risk_level": "low", "last_active_days": 5, "usage_trend": "up"},
        {"customer_id": "C006", "risk_level": "high", "last_active_days": -1, "usage_trend": "down"},  # 脏数据
        {"customer_id": "C007", "risk_level": "low", "last_active_days": 120, "usage_trend": "down"}
    ]
    # 注意 C004 已删除，C006 脏数据，C002 和 C003 正常
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # 消费日志（包含脏数据：负数 quarter_spend_usd）
    consumption_logs = [
        {"customer_id": "C001", "quarter_spend_usd": 15000},
        {"customer_id": "C002", "quarter_spend_usd": 8000},
        {"customer_id": "C003", "quarter_spend_usd": 4000},
        {"customer_id": "C005", "quarter_spend_usd": 12000},
        {"customer_id": "C006", "quarter_spend_usd": -500},  # 脏数据
        {"customer_id": "C007", "quarter_spend_usd": 6000}
    ]
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump(consumption_logs, f, indent=2)

    # 分段规则（从上到下匹配）
    rules = [
        {"min_spend": 10000, "max_inactive_days": 30, "label": "VIP"},
        {"min_spend": 5000, "max_inactive_days": 60, "label": "Premium"},
        {"label": "Standard"}
    ]
    with open("ops/segment_rules.json", "w") as f:
        json.dump(rules, f, indent=2)

    # 额外干扰文件（诱饵）
    os.makedirs("data/backup", exist_ok=True)
    with open("data/backup/customers_old.json", "w") as f:
        json.dump([{"customer_id": "C999", "customer_name": "Ghost", "labels": ["Legacy"]}], f)
    with open("data/old_segment_rules.json", "w") as f:
        json.dump([{"label": "Gold"}, {"label": "Silver"}], f)

if __name__ == "__main__":
    build_env()
