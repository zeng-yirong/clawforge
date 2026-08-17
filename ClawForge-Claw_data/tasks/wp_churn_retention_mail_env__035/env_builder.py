import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 客户数据（含干扰）
    customers = [
        {
            "customer_id": "C001",
            "customer_name": "LedgerFlow",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["churn_risk", "high_value"],
            "owner_name": "Alice"
        },
        {
            "customer_id": "C002",
            "customer_name": "ShelfCloud",
            "industry": "retail",
            "tier": "mid_market",
            "labels": ["auto_responder"],
            "owner_name": "Bob"
        },
        {
            "customer_id": "C003",
            "customer_name": "DataSync",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["vip"],
            "owner_name": "Charlie"
        },
        {
            "customer_id": "C004",
            "customer_name": "FinBridge",
            "industry": "fintech",
            "tier": "mid_market",
            "labels": [],
            "owner_name": "Diana"
        }
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # 活动日志（只有 C001 满足：high, >30, down, negative）
    activity_logs = [
        {
            "customer_id": "C001",
            "risk_level": "high",
            "last_active_days": 45,
            "usage_trend": "down",
            "ticket_sentiment": "negative"
        },
        {
            "customer_id": "C002",
            "risk_level": "high",
            "last_active_days": 15,
            "usage_trend": "down",
            "ticket_sentiment": "neutral"
        },
        {
            "customer_id": "C003",
            "risk_level": "low",
            "last_active_days": 60,
            "usage_trend": "stable",
            "ticket_sentiment": "negative"
        },
        {
            "customer_id": "C004",
            "risk_level": "high",
            "last_active_days": 25,
            "usage_trend": "down",
            "ticket_sentiment": "negative"
        }
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # 新闻样本（只有 N001 是 fintech + opportunity）
    news_samples = [
        {
            "news_id": "N001",
            "industry": "fintech",
            "headline": "Fintech Growth Surges: New Opportunities for 2025",
            "tone": "opportunity",
            "summary": "The fintech sector is expected to grow by 20% this year, driven by new regulations."
        },
        {
            "news_id": "N002",
            "industry": "retail",
            "headline": "Retail Rebound: Consumers Return to Stores",
            "tone": "opportunity",
            "summary": "Retail foot traffic increased 15% in Q2."
        },
        {
            "news_id": "N003",
            "industry": "fintech",
            "headline": "Fintech Faces Regulatory Headwinds",
            "tone": "pain_point",
            "summary": "New compliance requirements are straining fintech startups."
        }
    ]
    with open("data/news/news_samples.json", "w") as f:
        json.dump({"news_samples": news_samples}, f, indent=2)

    # 干扰文件
    # 备份日志（无 wrapper，格式不同）
    with open("data/logs/activity_logs_backup.json", "w") as f:
        json.dump(activity_logs, f, indent=2)
    # 过期客户 CSV
    with open("data/customers/deprecated_customers.csv", "w") as f:
        f.write("customer_id,customer_name,industry\nC099,OldClient,fintech\n")

if __name__ == "__main__":
    build_env()
