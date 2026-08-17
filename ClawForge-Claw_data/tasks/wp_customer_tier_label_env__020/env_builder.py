import os
import json
import csv
import random

def build_env():
    # 创建目录结构
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("archive", exist_ok=True)
    os.makedirs("temp", exist_ok=True)

    # 客户数据（含干扰项：重复、过期标记、缺失字段）
    customers = [
        {"customer_id": "C001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "mid_market", "labels": ["old"], "owner_name": "Alice", "status": "active"},
        {"customer_id": "C002", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": ["vip"], "owner_name": "Bob", "status": "active"},
        # 重复记录（完全一致，去重后不影响）
        {"customer_id": "C001", "customer_name": "CarePulse", "industry": "healthcare", "tier": "mid_market", "labels": ["old"], "owner_name": "Alice", "status": "active"},
        # 过期客户（status = inactive，业务要求忽略）
        {"customer_id": "C003", "customer_name": "HealthFirst", "industry": "healthcare", "tier": "basic", "labels": [], "owner_name": "Charlie", "status": "inactive"},
        # 字段缺失（缺少 industry，视为脏数据，应排除）
        {"customer_id": "C004", "customer_name": "DataDynamo", "industry": None, "tier": "mid_market", "labels": [], "owner_name": "Diana", "status": "active"},
    ]
    # 写入 CSV（使用标准格式）
    with open("raw_data/customers.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["customer_id","customer_name","industry","tier","labels","owner_name","status"])
        writer.writeheader()
        writer.writerows(customers)

    # 活动日志（含干扰：负的活跃天数、重复行、缺失字段）
    activity_logs = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 15, "usage_trend": "up"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 45, "usage_trend": "down"},
        # 重复行（完全相同）
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 15, "usage_trend": "up"},
        # 异常数据：活跃天数为负数（应视为脏数据）
        {"customer_id": "C005", "risk_level": "low", "last_active_days": -5, "usage_trend": "up"},
        # 缺失 risk_level
        {"customer_id": "C006", "risk_level": None, "last_active_days": 10, "usage_trend": "down"},
    ]
    with open("raw_data/activity_logs.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["customer_id","risk_level","last_active_days","usage_trend"])
        writer.writeheader()
        writer.writerows(activity_logs)

    # 消费日志（含干扰：负消费、重复、缺失字段）
    consumption_logs = [
        {"customer_id": "C001", "quarter_spend_usd": 12000},
        {"customer_id": "C002", "quarter_spend_usd": 6000},
        # 重复
        {"customer_id": "C001", "quarter_spend_usd": 12000},
        # 负消费（脏数据）
        {"customer_id": "C005", "quarter_spend_usd": -100},
        # 缺失 customer_id
        {"customer_id": None, "quarter_spend_usd": 5000},
    ]
    with open("raw_data/consumption_logs.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["customer_id","quarter_spend_usd"])
        writer.writeheader()
        writer.writerows(consumption_logs)

    # 规则文档（唯一客观规则）
    rules = [
        {"tier": "premium", "min_spend": 10000, "max_spend": 9999999, "min_active_days": 0, "max_active_days": 30, "risk_level": "low"},
        {"tier": "standard", "min_spend": 5000, "max_spend": 9999, "min_active_days": 0, "max_active_days": 60, "risk_level": "any"},
        {"tier": "basic", "min_spend": 0, "max_spend": 4999, "min_active_days": 0, "max_active_days": 9999, "risk_level": "any"},
    ]
    with open("raw_data/segmentation_rules.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["tier","min_spend","max_spend","min_active_days","max_active_days","risk_level"])
        writer.writeheader()
        writer.writerows(rules)

    # 干扰文件：旧标签归档
    old_labels = [
        {"customer_id": "C001", "label": "silver", "date": "2024-01-01"},
        {"customer_id": "C002", "label": "gold", "date": "2024-01-01"},
    ]
    with open("archive/old_tier_labels.json", "w") as f:
        json.dump(old_labels, f)

    # 临时无关文件
    with open("temp/unprocessed_data.csv", "w") as f:
        f.write("a,b,c\n1,2,3")

    # 空文件制造干扰
    with open("raw_data/.DS_Store", "w") as f:
        f.write("")

if __name__ == "__main__":
    build_env()
