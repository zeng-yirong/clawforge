import os
import json
import random

def build_env():
    # 创建目录结构
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("cache", exist_ok=True)

    # 客户数据（包含干扰客户）
    customers = [
        {"customer_id": "C001", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": ["finance"], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "ShelfCloud", "industry": "retail", "tier": "mid_market", "labels": ["logistics"], "owner_name": "Bob"},
        {"customer_id": "C003", "customer_name": "DataPulse", "industry": "fintech", "tier": "enterprise", "labels": ["analytics"], "owner_name": "Charlie"},
        {"customer_id": "C004", "customer_name": "GreenCart", "industry": "retail", "tier": "mid_market", "labels": ["grocery"], "owner_name": "Diana"},
        {"customer_id": "C005", "customer_name": "BlueOcean", "industry": "fintech", "tier": "mid_market", "labels": ["payments"], "owner_name": "Eve"}
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # 活动日志（对应客户，注入干扰条件）
    activity_logs = [
        {"customer_id": "C001", "risk_level": "high", "last_active_days": 45, "usage_trend": "down", "ticket_sentiment": "negative"},  # 高危
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 60, "usage_trend": "down", "ticket_sentiment": "negative"},  # 高危
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 90, "usage_trend": "stable", "ticket_sentiment": "neutral"},  # 低风险
        {"customer_id": "C004", "risk_level": "high", "last_active_days": 10, "usage_trend": "down", "ticket_sentiment": "negative"},   # 活跃天数不足
        {"customer_id": "C005", "risk_level": "high", "last_active_days": 35, "usage_trend": "down", "ticket_sentiment": "neutral"}    # 情绪中性
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # 新闻样本（各行业包含干扰项）
    news_samples = [
        {"news_id": "N001", "industry": "fintech", "headline": "Fintech Regulatory Crackdown Looms", "tone": "pain_point", "summary": "New regulations threaten fintech margins."},
        {"news_id": "N002", "industry": "fintech", "headline": "Digital Payments Surge in 2024", "tone": "opportunity", "summary": "Adoption of digital payments grows."},
        {"news_id": "N003", "industry": "retail", "headline": "Retail Supply Chain Disruptions", "tone": "pain_point", "summary": "Supply chain delays impact retailers."},
        {"news_id": "N004", "industry": "retail", "headline": "E-commerce Growth Opportunities", "tone": "opportunity", "summary": "Online retail expands."},
        {"news_id": "N005", "industry": "healthcare", "headline": "Health Data Breach", "tone": "pain_point", "summary": "Healthcare data breach affects millions."}
    ]
    with open("data/news/news_samples.json", "w") as f:
        json.dump({"news_samples": news_samples}, f, indent=2)

    # 留下一个空 cache 目录
    open("cache/.gitkeep", "w").close()

if __name__ == "__main__":
    build_env()
