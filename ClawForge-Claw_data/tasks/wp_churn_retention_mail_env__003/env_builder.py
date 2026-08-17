import os
import json
import random

def build_env():
    # ----- 客户数据 -----
    customers = [
        {"customer_id": "C001", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise",
         "labels": ["key_account"], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "ShelfCloud", "industry": "retail", "tier": "mid_market",
         "labels": ["upsell_potential"], "owner_name": "Bob"},
        {"customer_id": "C003", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise",
         "labels": ["vip"], "owner_name": "Charlie"},
        {"customer_id": "C004", "customer_name": "ShelfCloud", "industry": "retail", "tier": "mid_market",
         "labels": ["new"], "owner_name": "Diana"},
        {"customer_id": "C005", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "mid_market",
         "labels": ["risk"], "owner_name": "Eve"},
    ]
    os.makedirs("data/customers", exist_ok=True)
    with open("data/customers/customers.json", "w") as f:
        json.dump(customers, f, indent=2)

    # ----- 活动日志（包含干扰：高风险但活跃天数少、趋势平稳的低风险等）-----
    activity_logs = [
        {"customer_id": "C001", "risk_level": "high", "last_active_days": 45, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 10, "usage_trend": "down", "ticket_sentiment": "negative"},   # 活跃天数不足
        {"customer_id": "C003", "risk_level": "low",  "last_active_days": 60, "usage_trend": "down", "ticket_sentiment": "negative"},   # 风险等级低
        {"customer_id": "C004", "risk_level": "high", "last_active_days": 35, "usage_trend": "stable", "ticket_sentiment": "neutral"}, # 趋势平稳
        {"customer_id": "C005", "risk_level": "high", "last_active_days": 50, "usage_trend": "down", "ticket_sentiment": "negative"},   # 真正高危
    ]
    os.makedirs("data/logs", exist_ok=True)
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump(activity_logs, f, indent=2)

    # ----- 行业新闻样本（包含机会型与痛点型，干扰行业）-----
    news_samples = [
        {"news_id": "N001", "industry": "fintech", "headline": "新支付技术让 LedgerFlow 用户交易量翻倍",
         "tone": "opportunity", "summary": "某 fintech 公司采用新结算系统后月度交易量增长120%"},
        {"news_id": "N002", "industry": "fintech", "headline": "监管收紧，多家 fintech 面临合规困境",
         "tone": "pain_point", "summary": "新法规要求 stronger KYC，中小 fintech 成本上升"},
        {"news_id": "N003", "industry": "retail",   "headline": "ShelfCloud 推出的 AI 库存方案帮助零售商减少30%滞销",
         "tone": "opportunity", "summary": "零售业借助 ShelfCloud 方案实现智能补货"},
        {"news_id": "N004", "industry": "retail",   "headline": "线下客流萎缩，零售商急需线上转型",
         "tone": "pain_point", "summary": "消费者习惯改变，传统门店销售额持续下滑"},
        {"news_id": "N005", "industry": "fintech", "headline": "区块链跨境支付兴起，风险与机遇并存",
         "tone": "opportunity", "summary": "多个 fintech 开始试点去中心化支付，效率提升但监管未知"},
    ]
    os.makedirs("data/news", exist_ok=True)
    with open("data/news/news_samples.json", "w") as f:
        json.dump(news_samples, f, indent=2)

    # ----- 干扰文件：旧缓存（无关）-----
    os.makedirs("cache", exist_ok=True)
    # 放置一个过时的缓存文件（干扰项，agent 应替换或忽略）
    old_cache = [
        {"customer_id": "C003", "subject": "旧的挽留邮件", "body": "此邮件已过期"}
    ]
    with open("cache/old_retention_emails.json", "w") as f:
        json.dump(old_cache, f, indent=2)

    # 额外干扰：其他格式文件
    with open("data/accounts.json", "w") as f:
        json.dump([], f)
    with open("data/contacts.json", "w") as f:
        json.dump([], f)

    # 打印环境摘要（调试用，不影响）
    print("环境构建完成，数据已就绪。")

if __name__ == "__main__":
    build_env()
