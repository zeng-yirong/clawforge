import os
import json
import shutil

def build_env():
    # 确保 cwd 已是 
    # 清理旧目录（如有）
    for d in ["data", "cache"]:
        if os.path.exists(d):
            shutil.rmtree(d)

    # 创建数据目录
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)

    # --- 活动日志 ---
    activity_logs = {
        "activity_logs": [
            {"customer_id": "C001", "risk_level": "high", "last_active_days": 45, "usage_trend": "down", "ticket_sentiment": "negative"},
            {"customer_id": "C002", "risk_level": "low", "last_active_days": 10, "usage_trend": "stable", "ticket_sentiment": "neutral"},
            {"customer_id": "C003", "risk_level": "high", "last_active_days": 60, "usage_trend": "down", "ticket_sentiment": "negative"},
            {"customer_id": "C004", "risk_level": "low", "last_active_days": 5, "usage_trend": "stable", "ticket_sentiment": "neutral"},
            # 干扰：重复记录（不同风险）
            {"customer_id": "C001", "risk_level": "low", "last_active_days": 100, "usage_trend": "stable", "ticket_sentiment": "neutral"}
        ]
    }
    with open("data/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # 干扰：旧格式日志（字段名不同）
    old_log = [{"id": "C001", "r": "high"}]
    with open("data/logs/old_activity_logs.json", "w") as f:
        json.dump(old_log, f)

    # --- 客户资料 ---
    customers = {
        "customers": [
            {"customer_id": "C001", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": ["high_value"], "owner_name": "Alice", "email": "contact@ledgerflow.com"},
            {"customer_id": "C003", "customer_name": "ShelfCloud", "industry": "retail", "tier": "mid_market", "labels": ["growing"], "owner_name": "Bob", "email": "info@shelfcloud.com"},
            {"customer_id": "C002", "customer_name": "DataPulse", "industry": "fintech", "tier": "mid_market", "labels": ["new"], "owner_name": "Charlie", "email": "hello@datapulse.com"},
            {"customer_id": "C004", "customer_name": "GreenLeaf", "industry": "retail", "tier": "enterprise", "labels": ["sustainable"], "owner_name": "Diana", "email": "support@greenleaf.com"}
        ]
    }
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # 干扰：csv 格式的客户（字段不全）
    with open("data/customers/backup_customers.csv", "w") as f:
        f.write("id,name\nC001,LedgerFlow\nC003,ShelfCloud\n")

    # --- 新闻样本 ---
    news_samples = {
        "news_samples": [
            {"news_id": "N001", "industry": "fintech", "headline": "Fintech Blockchain Adoption Surges", "tone": "opportunity", "summary": "More fintech companies are integrating blockchain for transparency."},
            {"news_id": "N002", "industry": "retail", "headline": "Retail Shifts to Omnichannel Experience", "tone": "opportunity", "summary": "Retailers are investing in unified commerce platforms."},
            # 干扰：不相关行业新闻
            {"news_id": "N003", "industry": "healthcare", "headline": "Healthcare AI Breakthrough", "tone": "pain_point", "summary": "Healthcare struggles with data silos."},
            # 干扰：另一条 fintech 新闻（但 tone 不同，agent 应匹配行业即可，这里给两条 fintech 新闻，其中一条是干扰？为了唯一性我们只给一条匹配的，但这里额外给一条 tone=pain_point 的 fintech 新闻，agent 可能会选错？为了保持唯一，我们把第二条 fintech 的 tone 设为 pain_point，但 agent 可能会选择任意一条，造成不唯一。所以去掉多余 fintech，只保留一条。但为了增加难度，可以保留，但要求 agent 必须选 tone=opportunity 的？但 prompt 没有指示，所以最好只保留一条。因此删除下面注释掉的。）
        ]
    }
    # 为了干净，不增加额外的 fintech 新闻
    with open("data/news/news_samples.json", "w") as f:
        json.dump(news_samples, f, indent=2)

    # 干扰：一个空目录
    os.makedirs("data/archived", exist_ok=True)

if __name__ == "__main__":
    build_env()
