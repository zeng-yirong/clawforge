import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("cache", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 客户数据
    customers = {
        "customers": [
            {
                "customer_id": "C001",
                "customer_name": "LedgerFlow",
                "industry": "fintech",
                "tier": "enterprise",
                "labels": ["churn_risk", "premium"],
                "owner_name": "Alice"
            },
            {
                "customer_id": "C002",
                "customer_name": "ShelfCloud",
                "industry": "retail",
                "tier": "mid_market",
                "labels": ["active"],
                "owner_name": "Bob"
            },
            {
                "customer_id": "C003",
                "customer_name": "LedgerFlow",
                "industry": "fintech",
                "tier": "enterprise",
                "labels": ["test"],
                "owner_name": "Charlie"
            },
            {
                "customer_id": "C004",
                "customer_name": "FinSync",
                "industry": "fintech",
                "tier": "mid_market",
                "labels": ["churn_risk"],
                "owner_name": "Diana"
            }
        ]
    }
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f)

    # 活动日志
    activity_logs = {
        "activity_logs": [
            {
                "customer_id": "C001",
                "risk_level": "high",
                "last_active_days": 120,
                "usage_trend": "down",
                "ticket_sentiment": "negative"
            },
            {
                "customer_id": "C002",
                "risk_level": "low",
                "last_active_days": 3,
                "usage_trend": "stable",
                "ticket_sentiment": "positive"
            },
            {
                "customer_id": "C003",
                "risk_level": "high",
                "last_active_days": 5,
                "usage_trend": "down",
                "ticket_sentiment": "negative"
            },
            {
                "customer_id": "C004",
                "risk_level": "high",
                "last_active_days": 90,
                "usage_trend": "stable",
                "ticket_sentiment": "neutral"
            },
            {
                "customer_id": "C005",
                "risk_level": "low",
                "last_active_days": 200,
                "usage_trend": "down",
                "ticket_sentiment": "negative"
            }
        ]
    }
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f)

    # 新闻样本
    news_samples = {
        "news_samples": [
            {
                "news_id": "N001",
                "industry": "fintech",
                "headline": "Fintech Startup Raises $100M",
                "tone": "opportunity",
                "summary": "A leading fintech startup secured $100M in Series C funding."
            },
            {
                "news_id": "N002",
                "industry": "retail",
                "headline": "Retail Sales Up 15% This Quarter",
                "tone": "opportunity",
                "summary": "Retail sector shows strong recovery."
            },
            {
                "news_id": "N003",
                "industry": "fintech",
                "headline": "Regulatory Changes Impact Fintech",
                "tone": "pain_point",
                "summary": "New regulations may slow fintech growth."
            }
        ]
    }
    with open("data/news/news_samples.json", "w") as f:
        json.dump(news_samples, f)

    # 干扰文件
    accounts = {
        "accounts": [
            {"account_id": "A001", "display_name": "LedgerFlow Admin", "department": "IT", "email": "admin@ledgerflow.com", "permissions": ["admin"]},
            {"account_id": "A002", "display_name": "ShelfCloud Manager", "department": "Ops", "email": "ops@shelfcloud.com", "permissions": ["read"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f)

    contacts = {
        "contacts": [
            {"contact_id": "CT001", "name": "Alice", "role": "CEO", "email": "alice@ledgerflow.com"},
            {"contact_id": "CT002", "name": "Bob", "role": "CTO", "email": "bob@shelfcloud.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f)

    # 旧缓存（干扰）
    old_cache = {"emails": [{"customer_id": "C001", "subject": "Old draft", "body": "outdated"}]}
    with open("cache/old_cache.json", "w") as f:
        json.dump(old_cache, f)

    # 一些无用文件
    with open("ops/README.txt", "w") as f:
        f.write("This is a placeholder for operations scripts.\n")
    with open("data/notes.txt", "w") as f:
        f.write("Random notes from data team.\n")

if __name__ == "__main__":
    build_env()
