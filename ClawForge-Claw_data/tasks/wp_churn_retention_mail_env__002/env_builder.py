import os
import json
import random

def build_env():
    random.seed(42)

    # 1. accounts (干扰，不直接使用)
    accounts = [
        {"account_id": "acc_001", "display_name": "Tom", "department": "sales", "email": "tom@company.com", "permissions": ["read", "write"]},
        {"account_id": "acc_002", "display_name": "Jerry", "department": "ops", "email": "jerry@company.com", "permissions": ["read"]},
    ]
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    # 2. contacts (干扰)
    contacts = [
        {"contact_id": "con_001", "name": "Alice", "role": "admin", "email": "alice@ledgerflow.com"},
        {"contact_id": "con_002", "name": "Bob", "role": "manager", "email": "bob@shelfcloud.com"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

    # 3. customers (真实)
    customers = [
        {
            "customer_id": "cust_ledgerflow",
            "customer_name": "LedgerFlow",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["premium", "integration"],
            "owner_name": "Alice"
        },
        {
            "customer_id": "cust_shelfcloud",
            "customer_name": "ShelfCloud",
            "industry": "retail",
            "tier": "mid_market",
            "labels": ["ecommerce", "growth"],
            "owner_name": "Bob"
        },
    ]
    os.makedirs("data/customers", exist_ok=True)
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f)

    # 4. activity_logs (高风险+低活跃+负情绪只有一个)
    activity_logs = [
        {
            "customer_id": "cust_ledgerflow",
            "risk_level": "high",
            "last_active_days": 45,
            "usage_trend": "down",
            "ticket_sentiment": "negative"
        },
        {
            "customer_id": "cust_shelfcloud",
            "risk_level": "high",
            "last_active_days": 60,
            "usage_trend": "down",
            "ticket_sentiment": "neutral"   # 干扰：情绪不为负
        },
        # 额外干扰：另一个客户（customer不存在）但日志有，应忽略
        {
            "customer_id": "cust_ghost",
            "risk_level": "high",
            "last_active_days": 10,
            "usage_trend": "stable",
            "ticket_sentiment": "negative"
        },
    ]
    os.makedirs("data/logs", exist_ok=True)
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f)

    # 5. news_samples (只有一条 fintech 机遇)
    news_samples = [
        {
            "news_id": "news_fintech_opp",
            "industry": "fintech",
            "headline": "Digital Payment Trends 2025: Why Early Adopters Win",
            "tone": "opportunity",
            "summary": "Companies adopting digital payments ahead of competition see 30% higher retention."
        },
        {
            "news_id": "news_retail_pain",
            "industry": "retail",
            "headline": "Rising Logistics Costs Squeeze Retail Margins",
            "tone": "pain_point",
            "summary": "Retailers are struggling with increasing shipping costs."
        },
    ]
    os.makedirs("data/news", exist_ok=True)
    with open("data/news/news_samples.json", "w") as f:
        json.dump({"news_samples": news_samples}, f)

    # 额外干扰：一个空目录
    os.makedirs("raw_logs", exist_ok=True)
    # 额外干扰：一个无关的txt
    with open("README.txt", "w") as f:
        f.write("This is not the file you are looking for.\n")

    # 6. 创建cache目录，确保后续Agent可以写
    os.makedirs("cache", exist_ok=True)

if __name__ == "__main__":
    build_env()
