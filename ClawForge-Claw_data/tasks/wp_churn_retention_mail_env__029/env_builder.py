import os
import json
import shutil

def build_env():
    # 确保工作目录下干净（cwd = .）
    if os.path.exists("ops"):
        shutil.rmtree("ops")
    if os.path.exists("data"):
        shutil.rmtree("data")

    # ---------- 创建目录 ----------
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---------- 客户数据（含测试账号） ----------
    customers = [
        {
            "customer_id": "cust_001",
            "customer_name": "LedgerFlow",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["finance", "payments"],
            "owner_name": "Alice"
        },
        {
            "customer_id": "cust_002",
            "customer_name": "ShelfCloud",
            "industry": "retail",
            "tier": "mid_market",
            "labels": ["ecommerce", "inventory"],
            "owner_name": "Bob"
        },
        {
            "customer_id": "cust_003",
            "customer_name": "DataPulse",
            "industry": "fintech",
            "tier": "mid_market",
            "labels": ["analytics"],
            "owner_name": "Charlie"
        },
        {
            "customer_id": "test_acc_01",
            "customer_name": "TestAccount",
            "industry": "retail",
            "tier": "mid_market",
            "labels": [],
            "owner_name": "Test"
        }
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # ---------- 活动日志（含一个高风险的现有客户、一个低风险、一个不存在的客户ID） ----------
    activity_logs = [
        {
            "customer_id": "cust_001",
            "risk_level": "low",
            "last_active_days": 10,
            "usage_trend": "stable",
            "ticket_sentiment": "neutral"
        },
        {
            "customer_id": "cust_002",
            "risk_level": "high",
            "last_active_days": 60,
            "usage_trend": "down",
            "ticket_sentiment": "negative"
        },
        {
            "customer_id": "cust_003",
            "risk_level": "low",
            "last_active_days": 20,
            "usage_trend": "up",
            "ticket_sentiment": "positive"
        },
        {
            "customer_id": "ghost_customer",
            "risk_level": "high",
            "last_active_days": 90,
            "usage_trend": "down",
            "ticket_sentiment": "negative"
        }
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # ---------- 新闻样本（每个行业一条积极消息，外加负面干扰） ----------
    news_samples = [
        {
            "news_id": "news_001",
            "industry": "fintech",
            "headline": "Fintech Boom: New Regulations Boost Innovation",
            "tone": "opportunity",
            "summary": "Regulatory changes open doors for fintechs."
        },
        {
            "news_id": "news_002",
            "industry": "retail",
            "headline": "Retailers Embrace AI for Personalized Shopping",
            "tone": "opportunity",
            "summary": "AI adoption in retail surges."
        },
        {
            "news_id": "news_003",
            "industry": "fintech",
            "headline": "Major Fintech Data Breach Shakes Confidence",
            "tone": "pain_point",
            "summary": "Data breach incidents worry investors."
        },
        {
            "news_id": "news_004",
            "industry": "retail",
            "headline": "Supply Chain Disruptions Hit Retail Hard",
            "tone": "pain_point",
            "summary": "Retailers face ongoing supply chain issues."
        },
        {
            "news_id": "news_005",
            "industry": "healthcare",
            "headline": "Healthcare Tech Advances in 2025",
            "tone": "opportunity",
            "summary": "New technologies improve patient outcomes."
        }
    ]
    with open("data/news/news_samples.json", "w") as f:
        json.dump({"news_samples": news_samples}, f, indent=2)

    # ---------- 旧的缓存文件（干扰项） ----------
    old_cache = [
        {
            "customer_id": "cust_001",
            "customer_name": "LedgerFlow",
            "industry": "fintech",
            "news_headline": "Some old headline",
            "email_body": "This is an obsolete email."
        }
    ]
    with open("ops/email_cache.json", "w") as f:
        json.dump(old_cache, f, indent=2)

if __name__ == "__main__":
    build_env()
