import os
import json
import random

def build_env():
    # 确保工作目录是 .
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("ops", exist_ok=True)          # 用于存放 agent 的产出
    os.makedirs("data/archived", exist_ok=True) # 干扰目录

    # 客户列表 (wrapper=customers)
    customers = [
        {"customer_id": "c001", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": ["finance", "blockchain"], "owner_name": "Alice"},
        {"customer_id": "c002", "customer_name": "ShelfCloud", "industry": "retail", "tier": "mid_market", "labels": ["ecommerce", "cloud"], "owner_name": "Bob"},
        {"customer_id": "c003", "customer_name": "DataWave", "industry": "fintech", "tier": "mid_market", "labels": ["analytics", "AI"], "owner_name": "Charlie"},
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # 活动日志 (wrapper=activity_logs)
    # 干扰项：c002 风险低且活跃，c001 风险高且不活跃，c003 风险高且不活跃
    # 再加一条干扰：c003 的另一条记录（风险低但活跃）—— 让 agent 必须按规则过滤
    activity_logs = [
        {"customer_id": "c001", "risk_level": "high", "last_active_days": 45, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "c002", "risk_level": "low", "last_active_days": 10, "usage_trend": "stable", "ticket_sentiment": "neutral"},
        {"customer_id": "c003", "risk_level": "high", "last_active_days": 90, "usage_trend": "down", "ticket_sentiment": "negative"},
        # 干扰重复记录（不同风险等级，但 agent 应忽略，因为我们只取 risk=high 且 days>30）
        {"customer_id": "c003", "risk_level": "low", "last_active_days": 15, "usage_trend": "stable", "ticket_sentiment": "positive"},
        # 添加一条无关客户（id 不存在于 customers 中，应被忽略）
        {"customer_id": "c999", "risk_level": "high", "last_active_days": 60, "usage_trend": "down", "ticket_sentiment": "negative"},
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # 新闻样本 (wrapper=news_samples)
    news_samples = [
        {"news_id": "n001", "industry": "fintech", "headline": "Fintech 2.0: Embedded Finance Is Reshaping Lending", "tone": "opportunity", "summary": "Embedded finance is creating new revenue streams for traditional lenders."},
        {"news_id": "n002", "industry": "fintech", "headline": "Regulatory Crackdown Slows Fintech Innovation", "tone": "pain_point", "summary": "New compliance rules are increasing operational costs for fintech firms."},
        {"news_id": "n003", "industry": "retail", "headline": "Retailers Embrace AI-Driven Inventory Management", "tone": "opportunity", "summary": "AI tools help retailers reduce waste and improve stock turnover."},
        {"news_id": "n004", "industry": "healthcare", "headline": "Telehealth Reimbursement Uncertainty Hurts Providers", "tone": "pain_point", "summary": "Providers face financial risk due to unclear telehealth billing policies."},
    ]
    with open("data/news/news_samples.json", "w") as f:
        json.dump({"news_samples": news_samples}, f, indent=2)

    # 干扰文件：多余的 csv 日志
    with open("data/archived/old_logs.csv", "w") as f:
        f.write("customer_id,risk,days\nc001,low,120\nc002,high,5\n")

if __name__ == "__main__":
    build_env()
