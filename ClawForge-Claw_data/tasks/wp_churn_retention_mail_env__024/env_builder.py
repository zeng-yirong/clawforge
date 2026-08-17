import os
import json

def build_env():
    # 确保目录结构
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 放一个干扰文件

    # 1. 客户数据
    customers = {
        "customers": [
            {
                "customer_id": "C001",
                "customer_name": "LedgerFlow",
                "industry": "fintech",
                "tier": "enterprise",
                "labels": ["finance"],
                "owner_name": "Alice"
            },
            {
                "customer_id": "C002",
                "customer_name": "ShelfCloud",
                "industry": "retail",
                "tier": "mid_market",
                "labels": ["warehouse"],
                "owner_name": "Bob"
            },
            {
                "customer_id": "C003",
                "customer_name": "DataVault",
                "industry": "fintech",
                "tier": "enterprise",
                "labels": ["data"],
                "owner_name": "Charlie"
            }
        ]
    }
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # 2. 活动日志（包含干扰重复记录）
    activity_logs = {
        "activity_logs": [
            # C001 高风险，超过30天（正确）
            {"customer_id": "C001", "risk_level": "high", "last_active_days": 45, "usage_trend": "down", "ticket_sentiment": "negative"},
            # C001 低风险，短活跃（干扰）
            {"customer_id": "C001", "risk_level": "low", "last_active_days": 10, "usage_trend": "stable", "ticket_sentiment": "positive"},
            # C002 高风险，超过30天（正确）
            {"customer_id": "C002", "risk_level": "high", "last_active_days": 60, "usage_trend": "stable", "ticket_sentiment": "neutral"},
            # C003 低风险（不符合）
            {"customer_id": "C003", "risk_level": "low", "last_active_days": 10, "usage_trend": "stable", "ticket_sentiment": "positive"}
        ]
    }
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # 3. 新闻样本
    news_samples = {
        "news_samples": [
            {"news_id": "N001", "industry": "fintech", "headline": "Fintech Boom Continues", "tone": "opportunity", "summary": "Investors pouring into fintech."},
            {"news_id": "N002", "industry": "fintech", "headline": "Regulatory Challenges Ahead", "tone": "pain_point", "summary": "New regulations may slow growth."},
            {"news_id": "N003", "industry": "retail", "headline": "Retail Resurgence", "tone": "opportunity", "summary": "Retail sector sees uptick."},
            {"news_id": "N004", "industry": "retail", "headline": "Supply Chain Woes", "tone": "pain_point", "summary": "Supply chain issues persist."}
        ]
    }
    with open("data/news/news_samples.json", "w") as f:
        json.dump(news_samples, f, indent=2)

    # 4. 干扰文件：一个空的 txt 和 ops 下的无关文件
    with open("ops/old_draft.txt", "w") as f:
        f.write("This is a temp file, ignore.\n")
    with open("data/logs/backup.csv", "w") as f:
        f.write("something,else\n")

if __name__ == "__main__":
    build_env()
