import os, json, random

def build_env():
    # 客户数据
    customers = [
        {"customer_id": "c001", "customer_name": "ShelfCloud", "industry": "retail", "tier": "mid_market", "labels": ["active"], "owner_name": "Bob"},
        {"customer_id": "c002", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": ["vip", "high_risk"], "owner_name": "Alice"},
        {"customer_id": "c003", "customer_name": "LoopPay", "industry": "fintech", "tier": "mid_market", "labels": ["new"], "owner_name": "Charlie"},
        {"customer_id": "c004", "customer_name": "FreshCart", "industry": "retail", "tier": "enterprise", "labels": ["churned"], "owner_name": "Diana"}
    ]
    os.makedirs("data/customers", exist_ok=True)
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # 活动日志 – 目标是 c003 (LoopPay)：高、35天、down、negative
    activity_logs = [
        {"customer_id": "c001", "risk_level": "low", "last_active_days": 5, "usage_trend": "stable", "ticket_sentiment": "neutral"},
        {"customer_id": "c002", "risk_level": "high", "last_active_days": 12, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "c003", "risk_level": "high", "last_active_days": 35, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "c004", "risk_level": "low", "last_active_days": 60, "usage_trend": "stable", "ticket_sentiment": "neutral"},
        {"customer_id": "c003", "risk_level": "high", "last_active_days": 35, "usage_trend": "down", "ticket_sentiment": "negative"}  # 重复诱饵
    ]
    os.makedirs("data/logs", exist_ok=True)
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # 新闻样本 – fintech 行业有一条 opportunity 新闻
    news_samples = [
        {"news_id": "n001", "industry": "fintech", "headline": "Asia Fintech Summit 2025 Kicks Off", "tone": "opportunity", "summary": "Hundreds of innovators gather."},
        {"news_id": "n002", "industry": "fintech", "headline": "RegTech Helps Banks Cut Compliance Costs by 30%", "tone": "opportunity", "summary": "New AML tools reduce burden."},
        {"news_id": "n003", "industry": "retail", "headline": "Retail Sales Slump Continues", "tone": "pain_point", "summary": "Consumer spending drops."},
        {"news_id": "n004", "industry": "retail", "headline": "Omnichannel Strategies Boost Revenue", "tone": "opportunity", "summary": "Case study on unified commerce."}
    ]
    os.makedirs("data/news", exist_ok=True)
    with open("data/news/news_samples.json", "w") as f:
        json.dump(news_samples, f, indent=2)

    # 干扰目录
    os.makedirs("tmp", exist_ok=True)
    with open("tmp/old_logs.csv", "w") as f:
        f.write("customer_id,risk,days\nc003,high,10\n")

    # 过期的缓存文件（诱饵）
    os.makedirs("ops", exist_ok=True)
    with open("ops/retention_cache.json", "w") as f:
        json.dump({"customer_id": "c002", "news_headline": "fake"}, f)  # 故意写错误数据

if __name__ == "__main__":
    build_env()
