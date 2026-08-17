import json, os, random

def build_env():
    # 客户基础数据
    customers = [
        {"customer_id": "C001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "enterprise", "labels": ["existing_label_A"], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "mid_market", "labels": ["existing_label_B", "existing_label_C"], "owner_name": "Bob"},
        {"customer_id": "C003", "customer_name": "NovaHealth", "industry": "healthcare", "tier": "enterprise", "labels": [], "owner_name": "Charlie"},
        {"customer_id": "C004", "customer_name": "FinWave", "industry": "fintech", "tier": "mid_market", "labels": ["old_label"], "owner_name": "Diana"},
        {"customer_id": "C005", "customer_name": "MedCore", "industry": "healthcare", "tier": "enterprise", "labels": ["vip"], "owner_name": "Eve"}
    ]
    os.makedirs("data/customers", exist_ok=True)
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # 活动日志
    activity_logs = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 15, "usage_trend": "up"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 45, "usage_trend": "down"},
        {"customer_id": "C003", "risk_level": "high", "last_active_days": 120, "usage_trend": "down"},
        {"customer_id": "C004", "risk_level": "low", "last_active_days": 80, "usage_trend": "up"},
        {"customer_id": "C005", "risk_level": "high", "last_active_days": 5, "usage_trend": "up"}
    ]
    os.makedirs("data/logs", exist_ok=True)
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # 消费日志 (最新)
    consumption_logs = [
        {"customer_id": "C001", "quarter_spend_usd": 75000},
        {"customer_id": "C002", "quarter_spend_usd": 32000},
        {"customer_id": "C003", "quarter_spend_usd": 18000},
        {"customer_id": "C004", "quarter_spend_usd": 22000},
        {"customer_id": "C005", "quarter_spend_usd": 60000}
    ]
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump(consumption_logs, f, indent=2)

    # 干扰：旧版本的消费日志（日期较早，应忽略）
    os.makedirs("data_backup", exist_ok=True)
    old_consumption = [
        {"customer_id": "C001", "quarter_spend_usd": 30000, "period": "Q1"},
        {"customer_id": "C002", "quarter_spend_usd": 15000, "period": "Q1"},
        {"customer_id": "C003", "quarter_spend_usd": 8000, "period": "Q1"},
        {"customer_id": "C004", "quarter_spend_usd": 10000, "period": "Q1"},
        {"customer_id": "C005", "quarter_spend_usd": 20000, "period": "Q1"}
    ]
    with open("data_backup/consumption_logs_old.json", "w") as f:
        json.dump(old_consumption, f, indent=2)

    # 干扰：一个无关的CSV文件
    os.makedirs("raw_data", exist_ok=True)
    with open("raw_data/spend_summary.csv", "w") as f:
        f.write("customer,amount\nC001,1234\n")

    # 创建空ops目录
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
