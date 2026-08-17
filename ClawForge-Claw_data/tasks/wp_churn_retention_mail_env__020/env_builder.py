import json
import os

def build_env():
    # 创建目录结构
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("news", exist_ok=True)
    # 不创建 cache/ 目录，让 agent 创建

    # ---- 主客户数据 ----
    customers = [
        {"customer_id": "C001", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": ["financial", "high_value"], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "ShelfCloud", "industry": "retail", "tier": "mid_market", "labels": ["warehouse"], "owner_name": "Bob"},
        {"customer_id": "C003", "customer_name": "Finova", "industry": "fintech", "tier": "mid_market", "labels": ["startup"], "owner_name": "Charlie"},
        {"customer_id": "C004", "customer_name": "RetailMax", "industry": "retail", "tier": "enterprise", "labels": ["big_box"], "owner_name": "Diana"}
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # ---- 活动日志 ----
    activity_logs = [
        {"customer_id": "C001", "risk_level": "high", "last_active_days": 15, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 40, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 10, "usage_trend": "down", "ticket_sentiment": "neutral"},
        {"customer_id": "C004", "risk_level": "high", "last_active_days": 20, "usage_trend": "stable", "ticket_sentiment": "negative"}
    ]
    with open("logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # ---- 行业新闻 ----
    news_samples = [
        {"news_id": "N001", "industry": "fintech", "headline": "Open Banking Regulation Boosts Fintech Growth", "tone": "opportunity", "summary": "New regulations open doors for fintech innovation."},
        {"news_id": "N002", "industry": "fintech", "headline": "Rising Cybersecurity Threats in Finance", "tone": "pain_point", "summary": "Banks face increased cyber risks."},
        {"news_id": "N003", "industry": "retail", "headline": "Retail AI Adoption Accelerates", "tone": "opportunity", "summary": "AI helps retailers optimize supply chain."},
        {"news_id": "N004", "industry": "retail", "headline": "Supply Chain Disruptions Hit Retailers", "tone": "pain_point", "summary": "Global shipping delays affect retail inventory."}
    ]
    with open("news/news_samples.json", "w") as f:
        json.dump({"news_samples": news_samples}, f, indent=2)

    # ---- 干扰文件 ----
    # 过期客户
    old_customers = [
        {"customer_id": "C099", "customer_name": "OldBiz", "industry": "fintech", "tier": "mid_market", "labels": ["inactive"], "owner_name": "Ghost"}
    ]
    with open("data/old_customers.json", "w") as f:
        json.dump({"customers": old_customers}, f, indent=2)

    # 不完整日志（缺失字段，不可用）
    incomplete_logs = [
        {"customer_id": "C001", "risk_level": "high", "last_active_days": 15}  # 缺少 usage_trend 和 ticket_sentiment
    ]
    with open("logs/incomplete_logs.json", "w") as f:
        json.dump(incomplete_logs, f, indent=2)

    # 无关行业新闻（医疗）
    press_releases = [
        {"news_id": "N005", "industry": "healthcare", "headline": "Telemedicine Adoption Skyrockets", "tone": "opportunity", "summary": "Remote healthcare sees record growth."}
    ]
    with open("news/press_releases.json", "w") as f:
        json.dump(press_releases, f, indent=2)

if __name__ == "__main__":
    build_env()
