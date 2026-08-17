import os
import json
import random

def build_env():
    # -------------------- 目录结构 --------------------
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # -------------------- 客户数据 (带干扰) --------------------
    customers = [
        {"customer_id": "C001", "customer_name": "ShelfCloud", "industry": "retail", "tier": "mid_market", "labels": ["logistics"], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": ["payment"], "owner_name": "Bob"},
        {"customer_id": "C003", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": ["payment"], "owner_name": "Carol"},
        {"customer_id": "C004", "customer_name": "QuickMart", "industry": "retail", "tier": "mid_market", "labels": ["grocery"], "owner_name": "Dave"},
        {"customer_id": "C005", "customer_name": "InfraGrid", "industry": "fintech", "tier": "enterprise", "labels": ["infrastructure"], "owner_name": "Eve"}
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # -------------------- 活动日志 (只有C003满足高风险) --------------------
    logs = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 2, "usage_trend": "stable", "ticket_sentiment": "neutral"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 10, "usage_trend": "down", "ticket_sentiment": "neutral"},  # trend down 但 sentiment neutral
        {"customer_id": "C003", "risk_level": "high", "last_active_days": 5, "usage_trend": "down", "ticket_sentiment": "negative"}, # 唯一全匹配
        {"customer_id": "C004", "risk_level": "high", "last_active_days": 7, "usage_trend": "stable", "ticket_sentiment": "negative"}, # trend stable
        {"customer_id": "C005", "risk_level": "low", "last_active_days": 1, "usage_trend": "up", "ticket_sentiment": "positive"}
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": logs}, f, indent=2)

    # -------------------- 新闻样本 (只有fintech + opportunity的一条) --------------------
    news = [
        {"news_id": "N001", "industry": "retail", "headline": "Retail Rebound: How AI is changing the shelf", "tone": "opportunity", "summary": "Retailers see new growth with AI-driven inventory."},
        {"news_id": "N002", "industry": "fintech", "headline": "Fintech Growth: New regulations open doors", "tone": "opportunity", "summary": "Fintech firms can leverage new policies to expand."},
        {"news_id": "N003", "industry": "fintech", "headline": "Market Downturn: Fintech startups struggle", "tone": "pain_point", "summary": "Many fintech firms face funding challenges."},
        {"news_id": "N004", "industry": "retail", "headline": "Retailers warn of supply chain risks", "tone": "pain_point", "summary": "Ongoing disruptions hurt bottom lines."},
        {"news_id": "N005", "industry": "fintech", "headline": "Fintech Security Breach Impacts thousands", "tone": "pain_point", "summary": "Customer data exposed in recent attack."}
    ]
    with open("data/news/news_samples.json", "w") as f:
        json.dump({"news_samples": news}, f, indent=2)

    # 额外干扰文件（可忽略）
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": []}, f)
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": []}, f)

if __name__ == "__main__":
    build_env()
