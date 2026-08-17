import os
import json

def build_env():
    # 清理并创建目录
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 客户数据 (3个客户，含干扰)
    customers = {
        "cust_001": {
            "customer_id": "cust_001",
            "customer_name": "LedgerFlow",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["key_account", "high_value"],
            "owner_name": "Alice"
        },
        "cust_002": {
            "customer_id": "cust_002",
            "customer_name": "ShelfCloud",
            "industry": "retail",
            "tier": "mid_market",
            "labels": ["growing"],
            "owner_name": "Bob"
        },
        "cust_003": {
            "customer_id": "cust_003",
            "customer_name": "DataPulse",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["tech_savvy"],
            "owner_name": "Charlie"
        }
    }

    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # 活动日志 (高风险条件：risk_level=high, usage_trend=down, ticket_sentiment=negative)
    # 只有 cust_001 满足，其余为干扰
    activity_logs = {
        "cust_001": {
            "customer_id": "cust_001",
            "risk_level": "high",
            "last_active_days": 45,
            "usage_trend": "down",
            "ticket_sentiment": "negative"
        },
        "cust_002": {
            "customer_id": "cust_002",
            "risk_level": "low",
            "last_active_days": 10,
            "usage_trend": "stable",
            "ticket_sentiment": "neutral"
        },
        "cust_003": {
            "customer_id": "cust_003",
            "risk_level": "high",
            "last_active_days": 30,
            "usage_trend": "stable",
            "ticket_sentiment": "neutral"
        }
    }

    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # 新闻样本 (行业匹配，tone=opportunity  -> fintech 只有一条)
    news_samples = {
        "news_001": {
            "news_id": "news_001",
            "industry": "fintech",
            "headline": "AI in Banking",
            "tone": "opportunity",
            "summary": "Banks are adopting AI to reduce churn."
        },
        "news_002": {
            "news_id": "news_002",
            "industry": "fintech",
            "headline": "Regulatory Pressure Rising",
            "tone": "pain_point",
            "summary": "New regulations may impact fintech margins."
        },
        "news_003": {
            "news_id": "news_003",
            "industry": "retail",
            "headline": "Supply Chain Innovation",
            "tone": "opportunity",
            "summary": "Retailers use AI to optimize supply chains."
        },
        "news_004": {
            "news_id": "news_004",
            "industry": "healthcare",
            "headline": "Telehealth Boom",
            "tone": "opportunity",
            "summary": "Telehealth adoption skyrockets."
        }
    }

    with open("data/news/news_samples.json", "w") as f:
        json.dump({"news_samples": news_samples}, f, indent=2)

    # 邮件模板
    template = """Dear {customer_name},

We've noticed your recent activity has declined. Here's a relevant industry news you might find interesting:

{headline}

Best regards,
Your Account Team"""

    with open("templates/retention_email_template.txt", "w") as f:
        f.write(template)

    # 创建一些无关的干扰文件
    os.makedirs("tmp", exist_ok=True)
    with open("tmp/old_export.csv", "w") as f:
        f.write("customer_id,churn_score\ncust_001,0.9")

if __name__ == "__main__":
    build_env()
