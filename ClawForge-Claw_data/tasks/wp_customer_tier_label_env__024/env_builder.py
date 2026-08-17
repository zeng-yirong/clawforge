import os
import json
import random

def build_env():
    # 确保基础目录存在
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 客户主数据（5个客户，每个都有初始等级）
    customers = [
        {"customer_id": "C001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "enterprise", "labels": [], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "mid_market", "labels": [], "owner_name": "Bob"},
        {"customer_id": "C003", "customer_name": "DataStream", "industry": "fintech", "tier": "enterprise", "labels": [], "owner_name": "Charlie"},
        {"customer_id": "C004", "customer_name": "CloudSync", "industry": "healthcare", "tier": "mid_market", "labels": [], "owner_name": "Diana"},
        {"customer_id": "C005", "customer_name": "MockCorp", "industry": "fintech", "tier": "mid_market", "labels": [], "owner_name": "Eve"}
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # 备份文件（干扰项，内容故意旧一点）
    backup_customers = [
        {"customer_id": "C001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "mid_market", "labels": [], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": [], "owner_name": "Bob"}
    ]
    with open("data/customers/customers_backup.json", "w") as f:
        json.dump({"customers": backup_customers}, f, indent=2)

    # 季度消费日志（5个客户各一条 + 一条诱饵记录C006）
    consumption_logs = [
        {"customer_id": "C001", "quarter_spend_usd": 12000},
        {"customer_id": "C002", "quarter_spend_usd": 8000},
        {"customer_id": "C003", "quarter_spend_usd": 4000},
        {"customer_id": "C004", "quarter_spend_usd": 15000},
        {"customer_id": "C005", "quarter_spend_usd": 2000},
        {"customer_id": "C006", "quarter_spend_usd": 9999}  # 诱饵，客户不存在
    ]
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump({"consumption_logs": consumption_logs}, f, indent=2)

    # 草稿版本消费日志（干扰项，格式错误，内容不一致）
    draft_logs = [
        {"customer_id": "C001", "quarter_spend_usd": 11000},
        {"customer_id": "C003", "quarter_spend_usd": "五千"}  # 非数字
    ]
    with open("data/logs/consumption_logs_draft.csv", "w") as f:
        f.write("customer_id,spend\n")
        f.write("C001,11000\n")
        f.write("C003,5000\n")

    # 活动日志（5个客户 + 一条诱饵C007）
    activity_logs = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 25, "usage_trend": "up"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 40, "usage_trend": "down"},
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 70, "usage_trend": "down"},
        {"customer_id": "C004", "risk_level": "low", "last_active_days": 10, "usage_trend": "up"},
        {"customer_id": "C005", "risk_level": "high", "last_active_days": 90, "usage_trend": "down"},
        {"customer_id": "C007", "risk_level": "low", "last_active_days": 15, "usage_trend": "up"}  # 诱饵
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # 无关文件
    with open("notes/readme.txt", "w") as f:
        f.write("This is a note file, ignore me.")
    with open("ops/.gitkeep", "w") as f:
        f.write("")

if __name__ == "__main__":
    build_env()
