import os
import json

def build_env():
    # 创建必要目录
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("ops", exist_ok=True)           # 用于存放agent产物
    os.makedirs("data/backups", exist_ok=True)  # 干扰目录

    # ---------- 客户数据 ----------
    customers = [
        {"customer_id": "C001", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": ["high_value"], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "ShelfCloud", "industry": "retail", "tier": "mid_market", "labels": ["growing"], "owner_name": "Bob"},
        {"customer_id": "C003", "customer_name": "DataSphere", "industry": "fintech", "tier": "enterprise", "labels": ["stable"], "owner_name": "Charlie"}
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f)

    # ---------- 活动日志 ----------
    logs = [
        {"customer_id": "C001", "risk_level": "high", "last_active_days": 45, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 60, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 5, "usage_trend": "stable", "ticket_sentiment": "neutral"}
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": logs}, f)

    # ---------- 新闻样本 ----------
    news = [
        {"news_id": "N001", "industry": "fintech", "headline": "Fintech Market Opportunity", "tone": "opportunity", "summary": "Growing demand for digital payments."},
        {"news_id": "N002", "industry": "retail", "headline": "Retail Recovery Trends", "tone": "opportunity", "summary": "Retail sector sees rebound."},
        {"news_id": "N003", "industry": "fintech", "headline": "Regulatory Challenges", "tone": "pain_point", "summary": "New regulations pose hurdles."},
        {"news_id": "N004", "industry": "retail", "headline": "Supply Chain Issues", "tone": "pain_point", "summary": "Logistics disruptions continue."}
    ]
    with open("data/news/news_samples.json", "w") as f:
        json.dump({"news_samples": news}, f)

    # ---------- 干扰文件 ----------
    with open("data/logs/old_logs.json", "w") as f:
        f.write("invalid json content")
    with open("data/news/unrelated_news.csv", "w") as f:
        f.write("headline,source\nSome news,ABC")
    with open("data/backups/readme.txt", "w") as f:
        f.write("This is a backup folder.")

if __name__ == "__main__":
    build_env()
