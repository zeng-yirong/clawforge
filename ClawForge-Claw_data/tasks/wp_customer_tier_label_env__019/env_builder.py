import os
import json
import shutil

def build_env():
    # 创建目录结构
    os.makedirs("rules", exist_ok=True)
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/backup", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 规则文件
    rules = {
        "tiers": [
            {
                "name": "Gold",
                "min_spend": 50000,
                "max_active_days": 30,
                "allowed_risk": ["low"]
            },
            {
                "name": "Silver",
                "min_spend": 20000,
                "max_active_days": 90,
                "allowed_risk": ["low"]
            },
            {
                "name": "Bronze",
                "default": True
            }
        ]
    }
    with open("rules/tier_rules.json", "w") as f:
        json.dump(rules, f, indent=2)

    # 客户档案
    customers = [
        {"customer_id": "C001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "standard", "labels": [], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "standard", "labels": [], "owner_name": "Bob"},
        {"customer_id": "C003", "customer_name": "HealthFirst", "industry": "healthcare", "tier": "standard", "labels": [], "owner_name": "Carol"},
        {"customer_id": "C004", "customer_name": "FinTechX", "industry": "fintech", "tier": "standard", "labels": [], "owner_name": "Dave"},
        {"customer_id": "C005", "customer_name": "DataSync", "industry": "fintech", "tier": "standard", "labels": [], "owner_name": "Eve"}
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # 消费日志（含干扰项）
    consumption_logs = [
        # 有效记录
        {"customer_id": "C001", "quarter_spend_usd": 60000},
        {"customer_id": "C002", "quarter_spend_usd": 30000},
        {"customer_id": "C003", "quarter_spend_usd": 10000},
        {"customer_id": "C004", "quarter_spend_usd": 70000},
        {"customer_id": "C005", "quarter_spend_usd": 45000},
        # 干扰：负数金额
        {"customer_id": "C001", "quarter_spend_usd": -500},
        # 干扰：不存在的客户
        {"customer_id": "C006", "quarter_spend_usd": 50000},
        # 干扰：重复记录（数值相同，不影响）
        {"customer_id": "C002", "quarter_spend_usd": 30000}
    ]
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump({"consumption_logs": consumption_logs}, f, indent=2)

    # 活动日志（含干扰项）
    activity_logs = [
        # 有效记录
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 15, "usage_trend": "up"},
        {"customer_id": "C002", "risk_level": "low", "last_active_days": 60, "usage_trend": "up"},
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 200, "usage_trend": "down"},
        {"customer_id": "C004", "risk_level": "high", "last_active_days": 5, "usage_trend": "up"},
        {"customer_id": "C005", "risk_level": "low", "last_active_days": 120, "usage_trend": "down"},
        # 干扰：负活跃天数
        {"customer_id": "C003", "risk_level": "low", "last_active_days": -5, "usage_trend": "down"},
        # 干扰：空风险等级
        {"customer_id": "C005", "risk_level": "", "last_active_days": 100, "usage_trend": "up"},
        # 干扰：不存在的客户
        {"customer_id": "C007", "risk_level": "low", "last_active_days": 10, "usage_trend": "up"}
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # 额外干扰文件
    # 旧标签文件
    old_labels = [{"customer_id": "C001", "old_tier": "Bronze"}]
    with open("data/backup/labels_old.json", "w") as f:
        json.dump(old_labels, f, indent=2)
    # 无关CSV
    with open("data/logs/old_consumption.csv", "w") as f:
        f.write("customer,spend\nC001,20000\n")

if __name__ == "__main__":
    build_env()
