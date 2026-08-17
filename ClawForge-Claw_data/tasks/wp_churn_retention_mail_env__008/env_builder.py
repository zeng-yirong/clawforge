import os
import json

def build_env():
    # 创建 data 子目录
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("data/misc", exist_ok=True)   # 干扰目录
    os.makedirs("cache", exist_ok=True)       # 目标输出目录

    # --- customers ---
    customers = [
        {
            "customer_id": "C001",
            "customer_name": "LedgerFlow",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["premium"],
            "owner_name": "Alice"
        },
        {
            "customer_id": "C002",
            "customer_name": "ShelfCloud",
            "industry": "retail",
            "tier": "mid_market",
            "labels": ["standard"],
            "owner_name": "Bob"
        },
        {
            "customer_id": "C003",
            "customer_name": "DataVault",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["premium"],
            "owner_name": "Charlie"
        },
        {
            "customer_id": "C004",
            "customer_name": "FreshCart",
            "industry": "retail",
            "tier": "mid_market",
            "labels": ["new"],
            "owner_name": "Diana"
        }
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f)

    # --- activity logs ---
    # 只有 C001 和 C002 满足：risk_level=high, last_active_days>=30, usage_trend=down, ticket_sentiment=negative
    activity_logs = [
        {"customer_id": "C001", "risk_level": "high", "last_active_days": 45, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 60, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 10, "usage_trend": "stable", "ticket_sentiment": "neutral"},
        {"customer_id": "C004", "risk_level": "high", "last_active_days": 15, "usage_trend": "down", "ticket_sentiment": "negative"}  # last_active_days 不达标
    ]
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f)

    # --- news samples ---
    news_samples = [
        {"news_id": "N001", "industry": "fintech", "headline": "Fintech startups face funding winter", "tone": "pain_point", "summary": "Venture capital dries up for early-stage fintech firms."},
        {"news_id": "N002", "industry": "fintech", "headline": "New regulations boost fintech growth", "tone": "opportunity", "summary": "Regulatory sandbox opens doors for compliance-focused startups."},
        {"news_id": "N003", "industry": "retail", "headline": "Retail margins squeezed by inflation", "tone": "pain_point", "summary": "Rising costs force retailers to rethink pricing strategies."},
        {"news_id": "N004", "industry": "retail", "headline": "E-commerce expands into rural areas", "tone": "opportunity", "summary": "Online retail sees unexpected growth in underserved regions."},
        {"news_id": "N005", "industry": "healthcare", "headline": "Telehealth adoption surges", "tone": "opportunity", "summary": "Patients embrace virtual care post-pandemic."}  # 无关行业干扰
    ]
    with open("data/news/news_samples.json", "w") as f:
        json.dump({"news_samples": news_samples}, f)

    # --- 干扰文件（无关数据）---
    # 假 accounts 和 contacts
    accounts = [
        {"account_id": "A001", "display_name": "FinanceTeam", "department": "finance", "email": "fin@ledgerflow.com", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    contacts = [
        {"contact_id": "CT001", "name": "John Doe", "role": "CTO", "email": "john@ledgerflow.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

    # 一个空文件
    with open("data/misc/notes.txt", "w") as f:
        f.write("")

    # 一个无关的 Markdown
    with open("data/misc/old_churn_report.md", "w") as f:
        f.write("# Old report\nNot relevant.\n")

    # 预先存在的空 cache 文件（干扰）
    with open("cache/old_draft.json", "w") as f:
        f.write("{}")

if __name__ == "__main__":
    build_env()
