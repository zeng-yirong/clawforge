import os
import json

def build_env():
    # Create directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("backup", exist_ok=True)
    os.makedirs("old", exist_ok=True)

    # ---- customers ----
    customers = [
        {
            "customer_id": "cust_001",
            "customer_name": "LedgerFlow",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["key_account", "high_revenue"],
            "owner_name": "Alice Wang"
        },
        {
            "customer_id": "cust_002",
            "customer_name": "ShelfCloud",
            "industry": "retail",
            "tier": "mid_market",
            "labels": ["growing"],
            "owner_name": "Bob Li"
        },
        {
            "customer_id": "cust_003",
            "customer_name": "DataStream",
            "industry": "fintech",
            "tier": "mid_market",
            "labels": ["startup"],
            "owner_name": "Carol Zhang"
        },
        {
            "customer_id": "cust_004",
            "customer_name": "QuickCart",
            "industry": "retail",
            "tier": "enterprise",
            "labels": ["key_account"],
            "owner_name": "David Chen"
        },
        # 干扰客户（tier 不同，但不会影响筛选）
        {
            "customer_id": "cust_005",
            "customer_name": "AlphaAI",
            "industry": "fintech",
            "tier": "small_business",
            "labels": [],
            "owner_name": "Eve Zhao"
        }
    ]
    with open("data/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # ---- activity logs ----
    activities = [
        {
            "customer_id": "cust_001",
            "risk_level": "high",
            "last_active_days": 45,
            "usage_trend": "down",
            "ticket_sentiment": "negative"
        },
        {
            "customer_id": "cust_002",
            "risk_level": "high",
            "last_active_days": 30,
            "usage_trend": "down",
            "ticket_sentiment": "neutral"
        },
        {
            "customer_id": "cust_003",
            "risk_level": "low",
            "last_active_days": 15,
            "usage_trend": "stable",
            "ticket_sentiment": "positive"
        },
        {
            "customer_id": "cust_004",
            "risk_level": "high",
            "last_active_days": 60,
            "usage_trend": "stable",
            "ticket_sentiment": "negative"
        },
        # 干扰条目：不同 customer_id 但 low risk，不会入选
        {
            "customer_id": "cust_005",
            "risk_level": "low",
            "last_active_days": 10,
            "usage_trend": "stable",
            "ticket_sentiment": "positive"
        }
    ]
    with open("data/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activities}, f, indent=2)

    # ---- news samples ----
    news_samples = [
        {
            "news_id": "news_001",
            "industry": "fintech",
            "headline": "Fintech Regulations Tighten: What It Means for Your Business",
            "tone": "pain_point",
            "summary": "New compliance requirements could slow down operations."
        },
        {
            "news_id": "news_002",
            "industry": "fintech",
            "headline": "AI-Driven Fraud Detection Solutions See Surge in Demand",
            "tone": "opportunity",
            "summary": "Adopt AI to stay ahead of threats."
        },
        {
            "news_id": "news_003",
            "industry": "retail",
            "headline": "Retail Apocalypse? Not Yet – How Smart Brands Adapt",
            "tone": "pain_point",
            "summary": "Traditional retailers face fierce online competition."
        },
        {
            "news_id": "news_004",
            "industry": "retail",
            "headline": "E-commerce Growth Strategies for 2025",
            "tone": "opportunity",
            "summary": "Omnichannel approach drives revenue."
        },
        # 干扰新闻（同 industry、tone 不同，不影响唯一答案）
        {
            "news_id": "news_005",
            "industry": "fintech",
            "headline": "Market Volatility Creates Uncertainty for Fintech Startups",
            "tone": "pain_point",
            "summary": "Investors are pulling back."
        },
        {
            "news_id": "news_006",
            "industry": "retail",
            "headline": "Supply Chain Woes Continue to Haunt Retailers",
            "tone": "pain_point",
            "summary": "Logistics remain a major challenge."
        }
    ]
    with open("data/news_samples.json", "w") as f:
        json.dump({"news_samples": news_samples}, f, indent=2)

    # ---- 干扰文件：旧版本、备份等 ----
    with open("backup/customers_old.json", "w") as f:
        json.dump({"customers": []}, f)
    with open("old/activity_logs_2024.json", "w") as f:
        json.dump({"activity_logs": []}, f)

if __name__ == "__main__":
    build_env()
