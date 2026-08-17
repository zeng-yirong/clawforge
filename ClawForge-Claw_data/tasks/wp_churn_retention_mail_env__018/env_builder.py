import json
import os
import random

def build_env():
    # 创建目录结构
    dirs = ["data/customers", "data/logs", "data/news", "ops"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # ===== 客户数据 =====
    customers = [
        {
            "customer_id": "CUST-001",
            "customer_name": "LedgerFlow",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["finance", "blockchain"],
            "owner_name": "Alice",
            "email": "ledgerflow@example.com"
        },
        {
            "customer_id": "CUST-002",
            "customer_name": "ShelfCloud",
            "industry": "retail",
            "tier": "mid_market",
            "labels": ["ecommerce", "cloud"],
            "owner_name": "Bob",
            "email": "shelfcloud@example.com"
        },
        {
            "customer_id": "CUST-003",
            "customer_name": "DataSpan",
            "industry": "fintech",
            "tier": "mid_market",
            "labels": ["analytics", "bigdata"],
            "owner_name": "Carol",
            "email": "dataspan@example.com"
        }
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # ===== 活动日志 =====
    # 只有一个客户真正高危：CUST-001 (risk=high, last_active_days>90, trend=down, sentiment=negative)
    activity_logs = [
        {
            "customer_id": "CUST-001",
            "risk_level": "high",
            "last_active_days": 120,
            "usage_trend": "down",
            "ticket_sentiment": "negative"
        },
        {
            "customer_id": "CUST-002",
            "risk_level": "high",
            "last_active_days": 10,
            "usage_trend": "stable",
            "ticket_sentiment": "neutral"
        },
        {
            "customer_id": "CUST-003",
            "risk_level": "low",
            "last_active_days": 30,
            "usage_trend": "up",
            "ticket_sentiment": "positive"
        }
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # ===== 新闻样本（包含干扰项） =====
    news_samples = [
        {
            "news_id": "NEWS-001",
            "industry": "fintech",
            "headline": "Fintech Boom in Asia",
            "tone": "opportunity",
            "summary": "Asia's fintech market is expected to grow 25% this year."
        },
        {
            "news_id": "NEWS-002",
            "industry": "retail",
            "headline": "Supply Chain Crisis Hits Retailers",
            "tone": "pain_point",
            "summary": "Retailers worldwide struggle with logistics delays."
        },
        {
            "news_id": "NEWS-003",
            "industry": "fintech",
            "headline": "Regulatory Crackdown on Crypto Lending",
            "tone": "pain_point",
            "summary": "New regulations threaten fintech lending platforms."
        },
        {
            "news_id": "NEWS-004",
            "industry": "healthcare",
            "headline": "Telemedicine Adoption Skyrockets",
            "tone": "opportunity",
            "summary": "Telehealth platforms see record usage."
        }
    ]
    with open("data/news/news_samples.json", "w") as f:
        json.dump({"news_samples": news_samples}, f, indent=2)

    # 额外干扰文件（增加难度）
    # accounts.json – 与任务无关但存在
    accounts = [
        {"account_id": "ACC-001", "display_name": "Ledger Admin", "department": "IT", "email": "admin@ledgerflow.com", "permissions": ["read", "write"]},
        {"account_id": "ACC-002", "display_name": "Shelf Ops", "department": "Operations", "email": "ops@shelfcloud.com", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # contacts.json – 无关联系人
    contacts = [
        {"contact_id": "CONT-001", "name": "Alice Johnson", "role": "VP Engineering", "email": "alice@ledgerflow.com"},
        {"contact_id": "CONT-002", "name": "Bob Lee", "role": "CTO", "email": "bob@shelfcloud.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
