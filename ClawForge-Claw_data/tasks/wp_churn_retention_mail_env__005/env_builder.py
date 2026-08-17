import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 输出目标目录

    # 客户数据（两个客户，一个高风险一个低风险）
    customers = {
        "customers": [
            {
                "customer_id": "C001",
                "customer_name": "LedgerFlow",
                "industry": "fintech",
                "tier": "enterprise",
                "labels": ["strategic", "high_value"],
                "owner_name": "Alice"
            },
            {
                "customer_id": "C002",
                "customer_name": "ShelfCloud",
                "industry": "retail",
                "tier": "mid_market",
                "labels": ["growth"],
                "owner_name": "Bob"
            }
        ]
    }
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # 活动日志（C001 符合高风险条件，C002 不符合）
    activity_logs = {
        "activity_logs": [
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
                "last_active_days": 10,
                "usage_trend": "stable",
                "ticket_sentiment": "neutral"
            }
        ]
    }
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # 新闻样本（C001 行业 fintech 有 opportunity 新闻；C002 行业 retail 只有 pain_point）
    news_samples = {
        "news_samples": [
            {
                "news_id": "N001",
                "industry": "fintech",
                "headline": "New Fintech Opportunities Emerge",
                "tone": "opportunity",
                "summary": "New regulations open doors for innovative fintech solutions."
            },
            {
                "news_id": "N002",
                "industry": "retail",
                "headline": "Retail Struggles Amid Supply Chain",
                "tone": "pain_point",
                "summary": "Retail sector faces challenges."
            }
        ]
    }
    with open("data/news/news_samples.json", "w") as f:
        json.dump(news_samples, f, indent=2)

    # 干扰文件：过期的联系人备份
    with open("data/obsolete_contacts.json", "w") as f:
        json.dump({"contacts": []}, f, indent=2)
    # 干扰文件：活动日志旧版（格式不同，包含无用信息）
    with open("data/logs/activity_logs_backup.csv", "w") as f:
        f.write("customer_id,risk,days,trend,sentiment\n")
        f.write("C001,high,45,down,negative\n")
        f.write("C002,low,10,stable,neutral\n")

if __name__ == "__main__":
    build_env()
