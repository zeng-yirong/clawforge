import os
import json
import random

def build_env():
    # 创建目录结构
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("data/accounts", exist_ok=True)  # 干扰目录
    os.makedirs("data/contacts", exist_ok=True)  # 干扰目录

    # 客户数据 (customers.json)
    customers = {
        "customers": [
            {
                "customer_id": "C001",
                "customer_name": "LedgerFlow",
                "industry": "fintech",
                "tier": "enterprise",
                "labels": ["at_risk", "high_value"],
                "owner_name": "Alice"
            },
            {
                "customer_id": "C002",
                "customer_name": "ShelfCloud",
                "industry": "retail",
                "tier": "mid_market",
                "labels": ["active", "new"],
                "owner_name": "Bob"
            },
            {
                "customer_id": "C003",
                "customer_name": "FinTrax",
                "industry": "fintech",
                "tier": "enterprise",
                "labels": ["churned"],
                "owner_name": "Charlie"
            },
            {
                "customer_id": "C004",
                "customer_name": "RetailHub",
                "industry": "retail",
                "tier": "mid_market",
                "labels": ["dormant"],
                "owner_name": "Diana"
            },
            {
                "customer_id": "C005",
                "customer_name": "QuickBooks Clone",
                "industry": "fintech",
                "tier": "enterprise",
                "labels": ["active"],
                "owner_name": "Eve"
            }
        ]
    }
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # 干扰文件：accounts.json 和 contacts.json
    accounts = {
        "accounts": [
            {"account_id": "A001", "display_name": "LedgerFlow Admin", "department": "IT", "email": "admin@ledgerflow.io", "permissions": ["read", "write"]},
            {"account_id": "A002", "display_name": "ShelfCloud Billing", "department": "Finance", "email": "billing@shelfcloud.com", "permissions": ["read"]}
        ]
    }
    with open("data/accounts/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    contacts = {
        "contacts": [
            {"contact_id": "CT001", "name": "John Smith", "role": "CTO", "email": "john@ledgerflow.io"},
            {"contact_id": "CT002", "name": "Jane Doe", "role": "VP Eng", "email": "jane@shelfcloud.com"}
        ]
    }
    with open("data/contacts/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 活动日志 (activity_logs.json)
    activity_logs = {
        "activity_logs": [
            {
                "customer_id": "C001",
                "risk_level": "high",
                "last_active_days": 90,
                "usage_trend": "down",
                "ticket_sentiment": "negative"
            },
            {
                "customer_id": "C002",
                "risk_level": "high",
                "last_active_days": 45,
                "usage_trend": "down",
                "ticket_sentiment": "neutral"
            },
            {
                "customer_id": "C003",
                "risk_level": "low",
                "last_active_days": 120,
                "usage_trend": "stable",
                "ticket_sentiment": "neutral"
            },
            {
                "customer_id": "C004",
                "risk_level": "high",
                "last_active_days": 70,
                "usage_trend": "stable",
                "ticket_sentiment": "negative"
            },
            {
                "customer_id": "C005",
                "risk_level": "high",
                "last_active_days": 80,
                "usage_trend": "down",
                "ticket_sentiment": "neutral"
            }
        ]
    }
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # 新闻样本 (news_samples.json)
    news_samples = {
        "news_samples": [
            {
                "news_id": "N001",
                "industry": "fintech",
                "headline": "Regulatory Costs Squeeze Fintech Margins",
                "tone": "pain_point",
                "summary": "New compliance requirements are driving up operational costs for fintech companies, threatening profitability."
            },
            {
                "news_id": "N002",
                "industry": "fintech",
                "headline": "AI Lending Platforms See 300% Growth",
                "tone": "opportunity",
                "summary": "Fintech firms leveraging AI for credit scoring are capturing market share rapidly."
            },
            {
                "news_id": "N003",
                "industry": "retail",
                "headline": "Retailers Battle Inventory Glut Amid Demand Drop",
                "tone": "pain_point",
                "summary": "Consumer spending slowdown leaves retailers with excess stock and shrinking margins."
            },
            {
                "news_id": "N004",
                "industry": "retail",
                "headline": "Omnichannel Adoption Boosts Retail Revenue",
                "tone": "opportunity",
                "summary": "Retailers integrating online and offline channels report 20% higher customer retention."
            }
        ]
    }
    with open("data/news/news_samples.json", "w") as f:
        json.dump(news_samples, f, indent=2)

    # 额外干扰：过时版本的备份文件
    os.makedirs("backup", exist_ok=True)
    with open("backup/old_customers.json", "w") as f:
        json.dump({"customers": [{"customer_id": "C001", "customer_name": "LedgerFlow Legacy", "industry": "fintech"}]}, f)

    # 脏数据：日志中额外重复条目（但不会影响唯一答案，因为C001只有一条满足条件的）
    # 再写一个无关的 CSV 文件
    with open("data/logs/summary.csv", "w") as f:
        f.write("customer_id,risk_score\nC001,0.95\nC002,0.80\nC003,0.30\n")

if __name__ == "__main__":
    build_env()
