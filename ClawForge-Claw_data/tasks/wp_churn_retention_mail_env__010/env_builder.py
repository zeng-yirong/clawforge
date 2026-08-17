import os
import json

def build_env():
    # 创建必要目录（包括缓存目标目录）
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("ops/cache", exist_ok=True)
    os.makedirs("data/contacts", exist_ok=True)  # 干扰目录

    # ---------- 真实客户数据 ----------
    customers = [
        {
            "customer_id": "cust_001",
            "customer_name": "LedgerFlow",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["premium"],
            "owner_name": "Alice Wang",
            "email": "alice@ledgerflow.com"
        },
        {
            "customer_id": "cust_002",
            "customer_name": "ShelfCloud",
            "industry": "retail",
            "tier": "mid_market",
            "labels": ["startup"],
            "owner_name": "Bob Li",
            "email": "bob@shelfcloud.com"
        },
        {
            "customer_id": "cust_003",
            "customer_name": "HealthMate",
            "industry": "healthcare",
            "tier": "enterprise",
            "labels": ["regulated"],
            "owner_name": "Carol Chen",
            "email": "carol@healthmate.com"
        }
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f)

    # ---------- 活动日志（含干扰项） ----------
    activity_logs = [
        {"customer_id": "cust_001", "risk_level": "high", "last_active_days": 35, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "cust_002", "risk_level": "low", "last_active_days": 5, "usage_trend": "stable", "ticket_sentiment": "neutral"},
        {"customer_id": "cust_003", "risk_level": "high", "last_active_days": 50, "usage_trend": "down", "ticket_sentiment": "negative"}  # 高风险但行业无对应新闻
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f)

    # ---------- 新闻样本（仅 fintech 有匹配） ----------
    news_samples = [
        {
            "news_id": "news_001",
            "industry": "fintech",
            "tone": "pain_point",
            "headline": "New regulations increase compliance costs for fintech firms",
            "summary": "Fintech companies face higher operational expenses due to stricter rules."
        }
    ]
    with open("data/news/news_samples.json", "w") as f:
        json.dump({"news_samples": news_samples}, f)

    # ---------- 干扰文件 ----------
    # CSV 格式的备份日志（字段重复且数值有微小差异）
    with open("data/logs/activity_logs_backup.csv", "w") as f:
        f.write("customer_id,risk_level,last_active_days,usage_trend,ticket_sentiment\n")
        f.write("cust_001,high,30,down,negative\n")
        f.write("cust_002,low,10,stable,neutral\n")
        f.write("cust_003,high,45,down,negative\n")

    # 无用的文本文件
    with open("data/news/global_news.txt", "w") as f:
        f.write("No relevant news today.\n")

    # 联系人干扰（Agent 不应使用）
    contacts = [
        {"contact_id": "ct_001", "name": "Alice Wang", "role": "CEO", "email": "alice@ledgerflow.com"},
        {"contact_id": "ct_002", "name": "Bob Li", "role": "CTO", "email": "bob@shelfcloud.com"}
    ]
    with open("data/contacts/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

if __name__ == "__main__":
    build_env()
