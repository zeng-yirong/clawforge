import os
import json
import random

def build_env():
    # 确保父目录存在
    os.makedirs('data/customers', exist_ok=True)
    os.makedirs('data/logs', exist_ok=True)
    os.makedirs('data/news', exist_ok=True)
    os.makedirs('ops', exist_ok=True)
    os.makedirs('backup', exist_ok=True)  # 干扰目录

    # 客户数据
    customers = [
        {"customer_id": "cust001", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": ["premium"], "owner_name": "Alice"},
        {"customer_id": "cust002", "customer_name": "ShelfCloud", "industry": "retail", "tier": "mid_market", "labels": ["growth"], "owner_name": "Bob"},
        {"customer_id": "cust003", "customer_name": "DataVault", "industry": "fintech", "tier": "mid_market", "labels": ["startup"], "owner_name": "Carol"},
        {"customer_id": "cust004", "customer_name": "QuickMart", "industry": "retail", "tier": "enterprise", "labels": ["legacy"], "owner_name": "Dave"},
        {"customer_id": "cust005", "customer_name": "PayNest", "industry": "fintech", "tier": "enterprise", "labels": ["compliant"], "owner_name": "Eve"},
        {"customer_id": "cust006", "customer_name": "ShopWave", "industry": "retail", "tier": "mid_market", "labels": ["online"], "owner_name": "Frank"}
    ]
    with open('data/customers/customers.json', 'w') as f:
        json.dump(customers, f)

    # 活动日志（含干扰项）
    activity_logs = [
        # 真正的高风险（符合所有条件）
        {"customer_id": "cust001", "risk_level": "high", "last_active_days": 45, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "cust002", "risk_level": "high", "last_active_days": 60, "usage_trend": "down", "ticket_sentiment": "negative"},
        # 低风险干扰（last_active_days 低）
        {"customer_id": "cust003", "risk_level": "low", "last_active_days": 5, "usage_trend": "stable", "ticket_sentiment": "neutral"},
        {"customer_id": "cust004", "risk_level": "low", "last_active_days": 10, "usage_trend": "stable", "ticket_sentiment": "neutral"},
        # 高风险但 last_active_days 未超过30天
        {"customer_id": "cust005", "risk_level": "high", "last_active_days": 20, "usage_trend": "down", "ticket_sentiment": "negative"},
        # 高风险但 ticket_sentiment 不是 negative
        {"customer_id": "cust006", "risk_level": "high", "last_active_days": 50, "usage_trend": "down", "ticket_sentiment": "neutral"},
        # 额外干扰：不同标准但不应被选中
        {"customer_id": "cust001", "risk_level": "high", "last_active_days": 15, "usage_trend": "down", "ticket_sentiment": "negative"},  # 重复客户不同记录（混淆）
    ]
    with open('data/logs/activity_logs.json', 'w') as f:
        json.dump(activity_logs, f)

    # 新闻样本（含干扰）
    news_samples = [
        {"news_id": "n001", "industry": "fintech", "headline": "Fintech regulation tightens: compliance costs soar", "tone": "pain_point", "summary": "New rules squeeze profit margins for small players"},
        {"news_id": "n002", "industry": "fintech", "headline": "Blockchain boom opens new opportunities", "tone": "opportunity", "summary": "Innovation drives growth"},
        {"news_id": "n003", "industry": "retail", "headline": "Retail foot traffic hits record low", "tone": "pain_point", "summary": "Malls struggle to attract visitors"},
        {"news_id": "n004", "industry": "retail", "headline": "E-commerce surges, physical stores adapt", "tone": "opportunity", "summary": "Online sales offset decline"},
        {"news_id": "n005", "industry": "healthcare", "headline": "Health tech funding slows", "tone": "pain_point", "summary": "Irrelevant industry"},
    ]
    with open('data/news/news_samples.json', 'w') as f:
        json.dump(news_samples, f)

    # 干扰文件：过期备份
    with open('backup/old_activity_logs.json', 'w') as f:
        json.dump([{"customer_id": "cust001", "risk_level": "low"}], f)
    with open('backup/old_customers.json', 'w') as f:
        json.dump([], f)

if __name__ == '__main__':
    build_env()
