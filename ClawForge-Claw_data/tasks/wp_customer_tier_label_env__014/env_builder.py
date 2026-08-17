import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 客户数据 (6个客户, labels初始为空)
    customers = [
        {"customer_id": "C001", "customer_name": "Acme Corp", "industry": "fintech", "tier": "mid_market", "labels": []},
        {"customer_id": "C002", "customer_name": "Beta Inc", "industry": "healthcare", "tier": "enterprise", "labels": []},
        {"customer_id": "C003", "customer_name": "Gamma Ltd", "industry": "fintech", "tier": "mid_market", "labels": []},
        {"customer_id": "C004", "customer_name": "Delta LLC", "industry": "healthcare", "tier": "enterprise", "labels": []},
        {"customer_id": "C005", "customer_name": "Epsilon Co", "industry": "fintech", "tier": "mid_market", "labels": []},
        {"customer_id": "C006", "customer_name": "Zeta Group", "industry": "healthcare", "tier": "enterprise", "labels": []}
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # 消费日志 (包含负值和干扰客户C007)
    consumption_logs = [
        {"customer_id": "C001", "quarter_spend_usd": 1000},
        {"customer_id": "C001", "quarter_spend_usd": 800},
        {"customer_id": "C001", "quarter_spend_usd": -200},   # 负数干扰
        {"customer_id": "C002", "quarter_spend_usd": 900},
        {"customer_id": "C003", "quarter_spend_usd": 400},
        {"customer_id": "C004", "quarter_spend_usd": 1200},
        {"customer_id": "C005", "quarter_spend_usd": 600},
        {"customer_id": "C007", "quarter_spend_usd": 1000}    # 不在customer列表的干扰
    ]
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump({"consumption_logs": consumption_logs}, f, indent=2)

    # 活动日志 (C006缺失)
    activity_logs = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 20, "usage_trend": "up"},
        {"customer_id": "C002", "risk_level": "low", "last_active_days": 40, "usage_trend": "down"},
        {"customer_id": "C003", "risk_level": "high", "last_active_days": 10, "usage_trend": "up"},
        {"customer_id": "C004", "risk_level": "low", "last_active_days": 10, "usage_trend": "up"},
        {"customer_id": "C005", "risk_level": "high", "last_active_days": 90, "usage_trend": "down"},
        {"customer_id": "C007", "risk_level": "low", "last_active_days": 5, "usage_trend": "up"}  # 干扰
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # 规则文件 (JSON格式)
    rules = {
        "rules": [
            {"tier": "gold", "condition": "spend > 1500 && inactive_days <= 30"},
            {"tier": "silver", "condition": "spend > 800 && spend <= 1500 && inactive_days <= 60"},
            {"tier": "bronze", "condition": "default"}
        ]
    }
    with open("ops/tier_rules.json", "w") as f:
        json.dump(rules, f, indent=2)

    # 干扰文件: 旧规则 (CSV格式)
    with open("ops/old_tier_rules.csv", "w") as f:
        f.write("tier,min_spend\nsilver,1000\ngold,2000\n")

if __name__ == "__main__":
    build_env()
