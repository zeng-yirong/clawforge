import json
import os
import random

def build_env():
    # 创建目录
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 正式客户 (5个)
    customers = [
        {"customer_id": "C001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "enterprise", "labels": [], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "mid_market", "labels": [], "owner_name": "Bob"},
        {"customer_id": "C003", "customer_name": "DataBridge", "industry": "tech", "tier": "mid_market", "labels": [], "owner_name": "Charlie"},
        {"customer_id": "C004", "customer_name": "CloudSync", "industry": "tech", "tier": "enterprise", "labels": [], "owner_name": "Diana"},
        {"customer_id": "C005", "customer_name": "SecurePath", "industry": "fintech", "tier": "mid_market", "labels": [], "owner_name": "Eve"},
    ]
    # 测试客户 (干扰)
    test_customers = [
        {"customer_id": "test_001", "customer_name": "TestAlpha", "industry": "test", "tier": "none", "labels": [], "owner_name": "dev"},
        {"customer_id": "test_002", "customer_name": "TestBeta", "industry": "test", "tier": "none", "labels": [], "owner_name": "dev"},
    ]
    all_customers = customers + test_customers
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": all_customers}, f, indent=2)

    # 消费日志 (每个客户都有)
    # 按规则设计消费: C001消费60000, C002消费8000, C003消费25000, C004消费12000, C005消费40000
    # 测试客户也有数据，但应被忽略
    consumption_logs = [
        {"customer_id": "C001", "quarter_spend_usd": 60000},
        {"customer_id": "C002", "quarter_spend_usd": 8000},
        {"customer_id": "C003", "quarter_spend_usd": 25000},
        {"customer_id": "C004", "quarter_spend_usd": 12000},
        {"customer_id": "C005", "quarter_spend_usd": 40000},
        {"customer_id": "test_001", "quarter_spend_usd": 30000},
        {"customer_id": "test_002", "quarter_spend_usd": 5000},
    ]
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump({"consumption_logs": consumption_logs}, f, indent=2)

    # 活动日志 (last_active_days 和 usage_trend)
    # C001: 消费>50000且活跃>30 -> Churn Risk (假设40天)
    # C002: 消费<10000 -> Low Spender
    # C003: 消费25000 (1万~5万) 趋势 up -> Growth
    # C004: 消费12000 (1万~5万) 趋势 down -> Steady
    # C005: 消费40000 (1万~5万) 趋势 up -> Growth
    activity_logs = [
        {"customer_id": "C001", "risk_level": "high", "last_active_days": 40, "usage_trend": "down"},
        {"customer_id": "C002", "risk_level": "low", "last_active_days": 5, "usage_trend": "up"},
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 15, "usage_trend": "up"},
        {"customer_id": "C004", "risk_level": "low", "last_active_days": 20, "usage_trend": "down"},
        {"customer_id": "C005", "risk_level": "low", "last_active_days": 25, "usage_trend": "up"},
        {"customer_id": "test_001", "risk_level": "high", "last_active_days": 60, "usage_trend": "down"},
        {"customer_id": "test_002", "risk_level": "low", "last_active_days": 2, "usage_trend": "up"},
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # 额外干扰：一个无关的文件夹和文件
    os.makedirs("data/customers/archive", exist_ok=True)
    with open("data/customers/archive/old_backup.json", "w") as f:
        json.dump({"note": "this is just junk"}, f)

if __name__ == "__main__":
    build_env()
