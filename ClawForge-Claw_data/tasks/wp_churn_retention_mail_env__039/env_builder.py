import os
import json
import random

def build_env():
    # 确保工作目录是 .
    cwd = os.getcwd()
    # 创建必要目录
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)

    # -------------------- 客户数据（包含干扰项） --------------------
    customers = [
        {
            "customer_id": "C001",
            "customer_name": "LedgerFlow",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["premium", "high_value"],
            "owner_name": "Alice"
        },
        {
            "customer_id": "C002",
            "customer_name": "ShelfCloud",
            "industry": "retail",
            "tier": "mid_market",
            "labels": ["standard"],
            "owner_name": "Bob"
        },
        {
            "customer_id": "C003",
            "customer_name": "FinCore",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["high_value"],
            "owner_name": "Charlie"
        },
        {
            "customer_id": "C004",
            "customer_name": "RetailMart",
            "industry": "retail",
            "tier": "mid_market",
            "labels": ["new"],
            "owner_name": "Diana"
        },
        {
            "customer_id": "C005",
            "customer_name": "DataPipe",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["vip"],
            "owner_name": "Eve"
        }
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # -------------------- 活动日志（包含满足条件的客户和干扰项） --------------------
    activity_logs = [
        # 高风险客户：C001 (fintech) -> last_active_days=45 >=30, trend=down, sentiment=negative, risk_level=high
        {"customer_id": "C001", "risk_level": "high", "last_active_days": 45, "usage_trend": "down", "ticket_sentiment": "negative"},
        # C002 (retail) -> risk=high, days=60, trend=down, sentiment=negative 符合
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 60, "usage_trend": "down", "ticket_sentiment": "negative"},
        # C003 (fintech) -> risk=high, days=10 (小于30), trend=stable, sentiment=neutral -> 不符
        {"customer_id": "C003", "risk_level": "high", "last_active_days": 10, "usage_trend": "stable", "ticket_sentiment": "neutral"},
        # C004 (retail) -> risk=low, days=90, trend=down, sentiment=negative -> risk=low 排除
        {"customer_id": "C004", "risk_level": "low", "last_active_days": 90, "usage_trend": "down", "ticket_sentiment": "negative"},
        # C005 (fintech) -> risk=high, days=120, trend=down, sentiment=negative -> 符合
        {"customer_id": "C005", "risk_level": "high", "last_active_days": 120, "usage_trend": "down", "ticket_sentiment": "negative"},
        # 额外干扰：重复记录（C001不同状态）但不在客户表中？ 不需要
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # -------------------- 新闻样本（包含每个行业至少一条opportunity，以及pain_point干扰） --------------------
    news_samples = [
        # fintech opportunity
        {"news_id": "N001", "industry": "fintech", "headline": "Fintech Innovation Index 2024: Top Growth Markets", "tone": "opportunity", "summary": "A report highlights new fintech opportunities in Southeast Asia, with projected 25% growth."},
        # fintech pain_point 干扰
        {"news_id": "N002", "industry": "fintech", "headline": "Regulatory Crackdown on Crypto Lending", "tone": "pain_point", "summary": "New regulations may limit certain fintech products."},
        # retail opportunity
        {"news_id": "N003", "industry": "retail", "headline": "Retail AI Adoption Surges 40% in Q2", "tone": "opportunity", "summary": "Retailers using AI see 20% increase in customer retention."},
        # retail pain_point 干扰
        {"news_id": "N004", "industry": "retail", "headline": "Supply Chain Disruptions Hit Small Retailers", "tone": "pain_point", "summary": "Delays in shipping are affecting inventory."},
        # 多余机会新闻（同一行业第二条）
        {"news_id": "N005", "industry": "fintech", "headline": "Blockchain-based Payments Gain Traction", "tone": "opportunity", "summary": "More merchants adopting blockchain payments, reducing fees."},
    ]
    with open("data/news/news_samples.json", "w") as f:
        json.dump({"news_samples": news_samples}, f, indent=2)

    # 注意：不创建任何其他文件，保证干净

build_env()
