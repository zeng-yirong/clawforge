import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("data/old", exist_ok=True)

    # ---- 核心客户数据 ----
    customers = [
        {"customer_id": "cust-001", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": ["financial", "core"], "owner_name": "Alice"},
        {"customer_id": "cust-002", "customer_name": "ShelfCloud", "industry": "retail", "tier": "mid_market", "labels": ["warehouse"], "owner_name": "Bob"},
        {"customer_id": "cust-003", "customer_name": "PaperTrail", "industry": "fintech", "tier": "enterprise", "labels": ["accounting"], "owner_name": "Charlie"},
        {"customer_id": "cust-004", "customer_name": "RetailHub", "industry": "retail", "tier": "mid_market", "labels": [], "owner_name": "Diana"}
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # ---- 活动日志（含干扰项） ----
    activity_logs = [
        # 真正的高风险客户（满足所有流失条件）
        {"customer_id": "cust-001", "risk_level": "high", "last_active_days": 90, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "cust-002", "risk_level": "high", "last_active_days": 75, "usage_trend": "down", "ticket_sentiment": "negative"},
        # 干扰：risk_level 高但最近活动天数少（不满足“没动静”）
        {"customer_id": "cust-003", "risk_level": "high", "last_active_days": 10, "usage_trend": "stable", "ticket_sentiment": "neutral"},
        # 干扰：risk_level 低但有大量不活跃天数
        {"customer_id": "cust-004", "risk_level": "low", "last_active_days": 80, "usage_trend": "down", "ticket_sentiment": "negative"},
        # 干扰：不存在的客户
        {"customer_id": "cust-999", "risk_level": "high", "last_active_days": 60, "usage_trend": "down", "ticket_sentiment": "negative"}
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # ---- 过期备份日志（干扰文件） ----
    backup = [
        {"customer_id": "cust-001", "risk_level": "low", "last_active_days": 5, "usage_trend": "up", "ticket_sentiment": "positive"}
    ]
    with open("data/logs/activity_logs_backup.json", "w") as f:
        json.dump({"activity_logs": backup}, f, indent=2)

    # ---- 行业新闻样本 ----
    news_samples = [
        {"news_id": "news-001", "industry": "fintech", "headline": "Fintech struggles with regulatory compliance", "tone": "pain_point", "summary": "Many fintechs face increased scrutiny from regulators, making it harder to launch new products."},
        {"news_id": "news-002", "industry": "fintech", "headline": "New blockchain opportunities attract investors", "tone": "opportunity", "summary": "Blockchain adoption in fintech opens new revenue streams."},
        {"news_id": "news-003", "industry": "retail", "headline": "Retailers face supply chain disruptions", "tone": "pain_point", "summary": "Global logistics delays continue to impact retail inventory levels."},
        {"news_id": "news-004", "industry": "retail", "headline": "Retail growth in emerging markets expected", "tone": "opportunity", "summary": "E-commerce expansion in Southeast Asia offers new opportunities."},
        {"news_id": "news-005", "industry": "healthcare", "headline": "Healthcare data breach concerns rise", "tone": "pain_point", "summary": "Patient data security remains a top concern for healthcare providers."}
    ]
    with open("data/news/news_samples.json", "w") as f:
        json.dump({"news_samples": news_samples}, f, indent=2)

    # ---- 旧版本客户归档（干扰文件） ----
    old_customers = [
        {"customer_id": "cust-001", "customer_name": "LedgerFlow (old)", "industry": "fintech"}
    ]
    with open("data/old/customers_archive.json", "w") as f:
        json.dump({"archive": old_customers}, f, indent=2)

    # ---- 非标准格式文件（干扰） ----
    with open("data/old/unused.csv", "w") as f:
        f.write("id,value\n1,abc\n2,xyz\n")

if __name__ == "__main__":
    build_env()
