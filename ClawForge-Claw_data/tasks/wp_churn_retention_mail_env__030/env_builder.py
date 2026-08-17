import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)

    # 客户数据
    customers = {
        "customers": [
            {
                "customer_id": "cust_001",
                "customer_name": "LedgerFlow",
                "industry": "fintech",
                "tier": "enterprise",
                "labels": ["financial"],
                "owner_name": "Alice"
            },
            {
                "customer_id": "cust_002",
                "customer_name": "ShelfCloud",
                "industry": "retail",
                "tier": "mid_market",
                "labels": ["logistics"],
                "owner_name": "Bob"
            },
            {
                "customer_id": "cust_003",
                "customer_name": "FinTechy",
                "industry": "fintech",
                "tier": "mid_market",
                "labels": ["finance"],
                "owner_name": "Charlie"
            },
            # 干扰：重复ID但名字不同（脏数据）
            {
                "customer_id": "cust_001",
                "customer_name": "LedgerFlow2",
                "industry": "fintech",
                "tier": "enterprise",
                "labels": ["financial"],
                "owner_name": "Alice"
            }
        ]
    }
    # 移除重复项，保留第一个，但故意写两个来制造干扰，Agent需要处理重复ID
    # 但为了简化唯一性，我们在activity_logs中只与第一个cust_001匹配
    # 这里保留重复，但正确的客户是以activity_logs中的customer_id为准

    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # 活动日志数据
    activity_logs = {
        "activity_logs": [
            {
                "customer_id": "cust_001",
                "risk_level": "high",
                "last_active_days": 90,
                "usage_trend": "down",
                "ticket_sentiment": "negative"
            },
            {
                "customer_id": "cust_002",
                "risk_level": "low",
                "last_active_days": 30,
                "usage_trend": "down",
                "ticket_sentiment": "neutral"
            },
            {
                "customer_id": "cust_003",
                "risk_level": "high",
                "last_active_days": 60,
                "usage_trend": "stable",
                "ticket_sentiment": "negative"
            },
            # 干扰：缺少risk_level字段的脏数据
            {
                "customer_id": "cust_004",
                "last_active_days": 10,
                "usage_trend": "up",
                "ticket_sentiment": "positive"
            }
        ]
    }
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # 新闻样本数据
    news_samples = {
        "news_samples": [
            {
                "news_id": "news_001",
                "industry": "fintech",
                "headline": "Fintech startups face increased regulatory scrutiny",
                "tone": "pain_point",
                "summary": "Regulators are tightening controls on fintech firms."
            },
            {
                "news_id": "news_002",
                "industry": "fintech",
                "headline": "New fintech funding opportunities rise",
                "tone": "opportunity",
                "summary": "Venture capital is flowing into fintech."
            },
            {
                "news_id": "news_003",
                "industry": "retail",
                "headline": "Retail holiday sales forecast shows decline",
                "tone": "pain_point",
                "summary": "Consumer spending expected to drop."
            }
        ]
    }
    with open("data/news/news_samples.json", "w") as f:
        json.dump(news_samples, f, indent=2)

    # 创建其他无关文件作为干扰
    os.makedirs("data/accounts", exist_ok=True)
    accounts = {
        "accounts": [
            {"account_id": "acc_001", "display_name": "Alice", "department": "sales", "email": "alice@co.com", "permissions": ["read"]},
            {"account_id": "acc_002", "display_name": "Bob", "department": "support", "email": "bob@co.com", "permissions": ["write"]}
        ]
    }
    with open("data/accounts/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
