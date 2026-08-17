import os
import json

def build_env():
    # 创建目录结构
    for d in ["data/customers", "data/logs", "data/news", "ops"]:
        os.makedirs(d, exist_ok=True)

    # 客户数据（共4个客户，2个高风险2个低风险）
    customers = [
        {
            "customer_id": "C001",
            "customer_name": "LedgerFlow",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["premium", "long-term"],
            "owner_name": "Alice"
        },
        {
            "customer_id": "C002",
            "customer_name": "ShelfCloud",
            "industry": "retail",
            "tier": "mid_market",
            "labels": ["new", "growth"],
            "owner_name": "Bob"
        },
        {
            "customer_id": "C003",
            "customer_name": "QuantBridge",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["premium", "key-account"],
            "owner_name": "Carol"
        },
        {
            "customer_id": "C004",
            "customer_name": "FreshCart",
            "industry": "retail",
            "tier": "mid_market",
            "labels": ["seasonal"],
            "owner_name": "Dave"
        }
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # 活动日志（C001和C003为高风险，其余为低风险）
    activity_logs = [
        {
            "customer_id": "C001",
            "risk_level": "high",
            "last_active_days": 45,
            "usage_trend": "down",
            "ticket_sentiment": "negative"
        },
        {
            "customer_id": "C002",
            "risk_level": "low",
            "last_active_days": 7,
            "usage_trend": "stable",
            "ticket_sentiment": "neutral"
        },
        {
            "customer_id": "C003",
            "risk_level": "high",
            "last_active_days": 60,
            "usage_trend": "down",
            "ticket_sentiment": "negative"
        },
        {
            "customer_id": "C004",
            "risk_level": "low",
            "last_active_days": 3,
            "usage_trend": "stable",
            "ticket_sentiment": "neutral"
        }
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # 新闻样本（fintech有一条opportunity、一条pain_point；retail有一条opportunity）
    news_samples = [
        {
            "news_id": "N001",
            "industry": "fintech",
            "headline": "全球Fintech融资回暖，区块链支付获50亿注资",
            "tone": "opportunity",
            "summary": "多家机构看好金融科技前景，新一轮增长周期开启"
        },
        {
            "news_id": "N002",
            "industry": "fintech",
            "headline": "监管趋严：多家中小银行收紧API接口",
            "tone": "pain_point",
            "summary": "行业合规成本上升，小型Fintech公司面临挑战"
        },
        {
            "news_id": "N003",
            "industry": "retail",
            "headline": "零售业数字化转型加速，AI库存管理成新宠",
            "tone": "opportunity",
            "summary": "智能零售解决方案大幅降低损耗，头部企业已试点"
        }
    ]
    with open("data/news/news_samples.json", "w") as f:
        json.dump({"news_samples": news_samples}, f, indent=2)

if __name__ == "__main__":
    build_env()
