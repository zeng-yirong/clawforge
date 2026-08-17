import os
import json
import random

def build_env():
    # ========== 1. 客户数据 ==========
    customers = [
        {"customer_id": "C001", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": ["premium"], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "ShelfCloud", "industry": "retail", "tier": "mid_market", "labels": ["vip"], "owner_name": "Bob"},
        {"customer_id": "C003", "customer_name": "PayBridge", "industry": "fintech", "tier": "enterprise", "labels": ["new"], "owner_name": "Charlie"},
        {"customer_id": "C004", "customer_name": "RetailSync", "industry": "retail", "tier": "mid_market", "labels": ["legacy"], "owner_name": "Diana"},
        {"customer_id": "C005", "customer_name": "DataCore", "industry": "fintech", "tier": "small_business", "labels": ["trial"], "owner_name": "Eve"},
    ]
    os.makedirs("data/customers", exist_ok=True)
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # ========== 2. 活动日志（带干扰：重复记录、不完整记录） ==========
    activity_logs = [
        {"customer_id": "C001", "risk_level": "high", "last_active_days": 45, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "C002", "risk_level": "low", "last_active_days": 5, "usage_trend": "stable", "ticket_sentiment": "neutral"},
        {"customer_id": "C003", "risk_level": "high", "last_active_days": 60, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "C004", "risk_level": "high", "last_active_days": 32, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "C005", "risk_level": "low", "last_active_days": 2, "usage_trend": "stable", "ticket_sentiment": "positive"},
        # 干扰：重复的C001日志（但risk_level不同，应忽略）
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 2, "usage_trend": "stable", "ticket_sentiment": "positive"},
        # 干扰：缺失字段记录
        {"customer_id": "C006", "risk_level": "high", "last_active_days": 90},  # 无ticket_sentiment
    ]
    os.makedirs("data/logs", exist_ok=True)
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # ========== 3. 新闻样本 ==========
    news_samples = [
        {"news_id": "N001", "industry": "fintech", "headline": "央行发布数字人民币新规", "tone": "opportunity", "summary": "新政策利好合规支付平台"},
        {"news_id": "N002", "industry": "retail", "headline": "线下零售回暖，智慧仓储需求激增", "tone": "opportunity", "summary": "零售客户应加速数字化转型"},
        {"news_id": "N003", "industry": "fintech", "headline": "某头部平台因风控漏洞被罚", "tone": "pain_point", "summary": "行业监管趋严，合规成本上升"},
        {"news_id": "N004", "industry": "healthcare", "headline": "医疗AI获FDA批准", "tone": "opportunity", "summary": "远程医疗市场扩大"},  # 干扰：行业不匹配
        {"news_id": "N005", "industry": "retail", "headline": "电商退货率创新高", "tone": "pain_point", "summary": "供应链压力增加"},
    ]
    os.makedirs("data/news", exist_ok=True)
    with open("data/news/news_samples.json", "w") as f:
        json.dump({"news_samples": news_samples}, f, indent=2)

    # ========== 4. 缓存目录（开始时为空） ==========
    os.makedirs("cache", exist_ok=True)

if __name__ == "__main__":
    build_env()
