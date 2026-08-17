import os
import json

def build_env():
    # 创建必要的目录
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 活动日志（包含干扰）
    activity_logs = [
        {
            "customer_id": "cust_001",
            "risk_level": "high",
            "last_active_days": 45,
            "usage_trend": "down",
            "ticket_sentiment": "negative"
        },
        {
            "customer_id": "cust_002",
            "risk_level": "high",
            "last_active_days": 60,
            "usage_trend": "down",
            "ticket_sentiment": "negative"
        },
        # 干扰：last_active_days 太小，不符合条件
        {
            "customer_id": "cust_003",
            "risk_level": "high",
            "last_active_days": 10,
            "usage_trend": "down",
            "ticket_sentiment": "negative"
        },
        # 干扰：risk_level 为 low
        {
            "customer_id": "cust_004",
            "risk_level": "low",
            "last_active_days": 50,
            "usage_trend": "down",
            "ticket_sentiment": "negative"
        },
        # 干扰：usage_trend 为 stable
        {
            "customer_id": "cust_005",
            "risk_level": "high",
            "last_active_days": 35,
            "usage_trend": "stable",
            "ticket_sentiment": "negative"
        }
    ]

    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # 新闻样本（每个行业一条 opportunity，一条 pain_point）
    news_samples = [
        {
            "news_id": "news_001",
            "industry": "fintech",
            "headline": "Fintech startup breaks even after 5 years",
            "tone": "opportunity",
            "summary": "A major fintech player just announced profitability, signaling market recovery."
        },
        {
            "news_id": "news_002",
            "industry": "fintech",
            "headline": "New regulations crush small lenders",
            "tone": "pain_point",
            "summary": "Strict new rules are forcing fintechs to restructure."
        },
        {
            "news_id": "news_003",
            "industry": "retail",
            "headline": "Retail giant launches AI-powered supply chain",
            "tone": "opportunity",
            "summary": "With AI, retailers can cut costs by 20% and improve delivery times."
        },
        {
            "news_id": "news_004",
            "industry": "retail",
            "headline": "Consumer spending drops sharply",
            "tone": "pain_point",
            "summary": "Rising inflation is squeezing retail margins."
        }
    ]

    with open("data/news/news_samples.json", "w") as f:
        json.dump({"news_samples": news_samples}, f, indent=2)

    # 额外干扰数据（仅供场景丰富）
    os.makedirs("data/accounts", exist_ok=True)
    with open("data/accounts/accounts.json", "w") as f:
        json.dump({"accounts": [
            {"account_id": "acc_001", "display_name": "Alice", "department": "Engineering", "email": "alice@example.com", "permissions": ["read", "write"]},
            {"account_id": "acc_002", "display_name": "Bob", "department": "Sales", "email": "bob@example.com", "permissions": ["read"]}
        ]}, f, indent=2)

    os.makedirs("data/contacts", exist_ok=True)
    with open("data/contacts/contacts.json", "w") as f:
        json.dump({"contacts": [
            {"contact_id": "con_001", "name": "Charlie", "role": "CEO", "email": "charlie@example.com"},
            {"contact_id": "con_002", "name": "Diana", "role": "CTO", "email": "diana@example.com"}
        ]}, f, indent=2)

    os.makedirs("data/customers", exist_ok=True)
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": [
            {"customer_id": "cust_001", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": ["active"], "owner_name": "Alice"},
            {"customer_id": "cust_002", "customer_name": "ShelfCloud", "industry": "retail", "tier": "mid_market", "labels": ["vip"], "owner_name": "Bob"}
        ]}, f, indent=2)

if __name__ == "__main__":
    build_env()
