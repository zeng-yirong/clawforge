import os
import json

def build_env():
    # 创建必要的目录
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("rules", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("data/backup", exist_ok=True)

    # 干扰项：旧版客户文件
    backup_customers = [
        {"customer_id": "C001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "enterprise", "labels": ["VIP"]},
        {"customer_id": "C002", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "mid_market", "labels": []}
    ]
    with open("data/backup/customers_old.json", "w") as f:
        json.dump({"customers": backup_customers}, f)

    # 真实的客户基础信息（作为参考，但agent不需要更新它）
    customers = [
        {"customer_id": "C001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "enterprise", "labels": [], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "mid_market", "labels": [], "owner_name": "Bob"}
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f)

    # 消费日志（唯一记录，无重复）
    consumption = [
        {"customer_id": "C001", "quarter_spend_usd": 8500},
        {"customer_id": "C002", "quarter_spend_usd": 1800}
    ]
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump({"consumption_logs": consumption}, f)

    # 活动日志（唯一记录）
    activity = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 20, "usage_trend": "up"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 90, "usage_trend": "down"}
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity}, f)

    # 规则文件
    rules = {
        "tiers": [
            {
                "name": "Gold",
                "min_spend": 5000,
                "max_inactive_days": 30,
                "allowed_risk": ["low"]
            },
            {
                "name": "Silver",
                "min_spend": 2000,
                "max_inactive_days": 60,
                "allowed_risk": ["low", "medium"]
            },
            {
                "name": "Bronze",
                "min_spend": 0,
                "max_inactive_days": 90,
                "allowed_risk": ["low", "medium", "high"]
            },
            {
                "name": "At Risk",
                "min_spend": 0,
                "max_inactive_days": 120,
                "allowed_risk": ["low", "medium", "high"]
            }
        ]
    }
    with open("rules/segmentation_rules.json", "w") as f:
        json.dump(rules, f)

    # 干扰规则备份（agent不应该使用）
    old_rules = {"tiers": [{"name": "Premium", "min_spend": 10000}]}
    with open("rules/segmentation_rules_backup.json", "w") as f:
        json.dump(old_rules, f)

    # 干扰日志目录（过期数据）
    os.makedirs("data/old_logs", exist_ok=True)
    old_consumption = [{"customer_id": "C001", "quarter_spend_usd": 3000}]
    with open("data/old_logs/consumption_logs.json", "w") as f:
        json.dump({"consumption_logs": old_consumption}, f)

    # 干扰README
    with open("README.txt", "w") as f:
        f.write("This workspace contains customer data for tier labeling.")

if __name__ == "__main__":
    build_env()
