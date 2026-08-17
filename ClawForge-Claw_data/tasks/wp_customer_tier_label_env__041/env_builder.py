import json
import os

def build_env():
    # 创建目录结构
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)
    os.makedirs("result", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 干扰目录

    # 客户主数据（包含干扰客户 c003）
    customers = {
        "customers": [
            {
                "customer_id": "c001",
                "customer_name": "CarePulse",
                "industry": "healthcare",
                "tier": "enterprise",
                "labels": [],
                "owner_name": "Alice"
            },
            {
                "customer_id": "c002",
                "customer_name": "LedgerFlow",
                "industry": "fintech",
                "tier": "mid_market",
                "labels": [],
                "owner_name": "Bob"
            },
            {
                "customer_id": "c003",
                "customer_name": "DummyCorp",
                "industry": "retail",
                "tier": "small_business",
                "labels": ["existing_label"],
                "owner_name": "Eve"
            }
        ]
    }
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # 消费日志（c001、c002 有效，c004 是干扰客户（不在客户主数据中），还添加一条重复记录测试鲁棒性）
    consumption_logs = {
        "consumption_logs": [
            {"customer_id": "c001", "quarter_spend_usd": 15000},
            {"customer_id": "c002", "quarter_spend_usd": 5000},
            {"customer_id": "c004", "quarter_spend_usd": 20000},  # 干扰，客户不存在
            {"customer_id": "c001", "quarter_spend_usd": 15000}   # 重复记录（与第一条相同）
        ]
    }
    with open("data/logs/consumption_logs.json", "w") as f:
        json.dump(consumption_logs, f, indent=2)

    # 活动日志（c001、c002、c003 有记录，c005 是干扰客户）
    activity_logs = {
        "activity_logs": [
            {"customer_id": "c001", "risk_level": "low", "last_active_days": 15, "usage_trend": "up"},
            {"customer_id": "c002", "risk_level": "high", "last_active_days": 120, "usage_trend": "down"},
            {"customer_id": "c003", "risk_level": "low", "last_active_days": 100, "usage_trend": "down"},
            {"customer_id": "c005", "risk_level": "high", "last_active_days": 200, "usage_trend": "down"}
        ]
    }
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # 附件索引
    attachments = {
        "attachments": [
            {
                "path": "attachments/segmentation_rules.txt",
                "title": "Segmentation Rules",
                "kind": "text",
                "description": "Customer segmentation rules"
            }
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # 规则文件
    rules_content = """Segmentation Rules:
1. If quarter_spend_usd >= 10000 AND last_active_days <= 30 AND risk_level == 'low' AND usage_trend == 'up', then set label to "VIP".
2. If risk_level == 'high' AND last_active_days > 90, then set label to "churn_risk".
3. Otherwise, keep the existing labels unchanged.
Note: Only consider customers that have both consumption and activity logs.
"""
    with open("attachments/segmentation_rules.txt", "w") as f:
        f.write(rules_content)

if __name__ == "__main__":
    build_env()
