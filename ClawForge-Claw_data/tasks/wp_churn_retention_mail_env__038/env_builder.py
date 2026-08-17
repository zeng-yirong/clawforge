import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- customers.json ---
    customers = [
        {"customer_id": "C001", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": ["finance", "saas"], "owner_name": "Amanda"},
        {"customer_id": "C002", "customer_name": "ShelfCloud", "industry": "retail", "tier": "mid_market", "labels": ["ecommerce", "cloud"], "owner_name": "Bob"},
        {"customer_id": "C003", "customer_name": "PayNest", "industry": "fintech", "tier": "mid_market", "labels": ["payments"], "owner_name": "Amanda"},
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # --- activity_logs.json ---
    activity_logs = [
        {"customer_id": "C001", "risk_level": "high", "last_active_days": 45, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 10, "usage_trend": "stable", "ticket_sentiment": "neutral"},
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 60, "usage_trend": "down", "ticket_sentiment": "negative"},
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # --- news_samples.json ---
    news_samples = [
        {"news_id": "N001", "industry": "fintech", "headline": "Open Banking Regulation Boosts Fintech Innovation", "tone": "opportunity", "summary": "New regulatory framework opens doors for agile fintechs."},
        {"news_id": "N002", "industry": "fintech", "headline": "Rising Fraud Concerns in Digital Payments", "tone": "pain_point", "summary": "Financial institutions struggle with increasing fraud attempts."},
        {"news_id": "N003", "industry": "retail", "headline": "Retailers Embrace AI for Supply Chain Optimization", "tone": "opportunity", "summary": "AI-driven demand forecasting reduces waste by 20%."},
        {"news_id": "N004", "industry": "retail", "headline": "High Return Rates Eat into Retail Margins", "tone": "pain_point", "summary": "E-commerce returns hit record highs, squeezing profits."},
    ]
    with open("data/news/news_samples.json", "w") as f:
        json.dump(news_samples, f, indent=2)

    # 额外干扰文件（无用但存在）
    os.makedirs("data/accounts", exist_ok=True)
    accounts = [
        {"account_id": "A001", "display_name": "Amanda Smith", "department": "Success", "email": "amanda@company.com", "permissions": ["read", "write"]},
    ]
    with open("data/accounts/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 留一个空目录作为诱饵
    os.makedirs("tmp", exist_ok=True)

if __name__ == "__main__":
    build_env()
