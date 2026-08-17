import os
import json

def build_env():
    # 确保cache目录存在
    os.makedirs("cache", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # accounts.json
    accounts = [
        {"account_id": "C001", "display_name": "LedgerFlow", "department": "Finance", "email": "ledgerflow@example.com", "permissions": ["admin"]},
        {"account_id": "C002", "display_name": "ShelfCloud", "department": "Retail", "email": "shelfcloud@example.com", "permissions": ["user"]},
        {"account_id": "C003", "display_name": "DataMine", "department": "Tech", "email": "datamine@example.com", "permissions": ["viewer"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # customers.json (用于干扰，但实际邮件需要从accounts拿邮箱)
    customers = [
        {"customer_id": "C001", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": ["finance"], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "ShelfCloud", "industry": "retail", "tier": "mid_market", "labels": ["retail"], "owner_name": "Bob"},
        {"customer_id": "C003", "customer_name": "DataMine", "industry": "tech", "tier": "startup", "labels": ["data"], "owner_name": "Charlie"}
    ]
    with open("data/customers/customers.json", "w") as f:
        os.makedirs("data/customers", exist_ok=True)
        json.dump({"customers": customers}, f, indent=2)

    # activity_logs.json (高风险客户C001，低风险C002，C003低风险但诱饵)
    activity_logs = [
        {"customer_id": "C001", "risk_level": "high", "last_active_days": 45, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "C002", "risk_level": "low", "last_active_days": 5, "usage_trend": "stable", "ticket_sentiment": "neutral"},
        {"customer_id": "C003", "risk_level": "high", "last_active_days": 60, "usage_trend": "down", "ticket_sentiment": "negative"}  # 高风险但行业不同（tech），且无对应新闻
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # news_samples.json (只有fintech/pain_point一条，其余为干扰)
    news_samples = [
        {"news_id": "N001", "industry": "fintech", "headline": "Fintech Regulations Tighten", "tone": "pain_point", "summary": "New fintech regulations may increase compliance costs."},
        {"news_id": "N002", "industry": "retail", "headline": "Retail Boom Expected", "tone": "opportunity", "summary": "Retail sales expected to rise 20% this quarter."},
        {"news_id": "N003", "industry": "fintech", "headline": "Blockchain Revolution", "tone": "opportunity", "summary": "Blockchain adoption accelerates in fintech."},
        {"news_id": "N004", "industry": "tech", "headline": "Tech Layoffs Continue", "tone": "pain_point", "summary": "Major tech firms announce further layoffs."}
    ]
    with open("data/news/news_samples.json", "w") as f:
        json.dump({"news_samples": news_samples}, f, indent=2)

    # 额外干扰文件
    with open("data/old_activity_logs_backup.json", "w") as f:
        f.write("{}")
    with open("data/news/unused_news.csv", "w") as f:
        f.write("id,headline\n")

if __name__ == "__main__":
    build_env()
