import os
import json
import random

random.seed(42)

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def build_env():
    # --- customers ---
    customers = [
        {"customer_id": "C001", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": ["premium"], "owner_name": "Alice"},
        {"customer_id": "C002", "customer_name": "ShelfCloud", "industry": "retail", "tier": "mid_market", "labels": ["standard"], "owner_name": "Bob"},
        {"customer_id": "C003", "customer_name": "Finwise", "industry": "fintech", "tier": "mid_market", "labels": ["new"], "owner_name": "Carol"},
        {"customer_id": "C004", "customer_name": "ShopNest", "industry": "retail", "tier": "enterprise", "labels": ["premium"], "owner_name": "Dave"},
        {"customer_id": "C005", "customer_name": "DataPulse", "industry": "fintech", "tier": "enterprise", "labels": ["premium"], "owner_name": "Eve"},
    ]
    write_json("data/customers/customers.json", customers)

    # --- accounts ---
    accounts = [
        {"account_id": "A001", "display_name": "LedgerFlow Admin", "department": "Engineering", "email": "admin@ledgerflow.com", "permissions": ["read", "write"]},
        {"account_id": "A002", "display_name": "ShelfCloud Ops", "department": "Operations", "email": "ops@shelfcloud.com", "permissions": ["read"]},
    ]
    write_json("data/accounts.json", accounts)

    # --- contacts ---
    contacts = [
        {"contact_id": "CT001", "name": "Wang Li", "role": "CTO", "email": "wang@ledgerflow.com"},
        {"contact_id": "CT002", "name": "Zhang Wei", "role": "VP Engineering", "email": "zhang@shelfcloud.com"},
    ]
    write_json("data/contacts.json", contacts)

    # --- activity_logs ---
    activity_logs = [
        {"customer_id": "C001", "risk_level": "high", "last_active_days": 45, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 60, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "C003", "risk_level": "high", "last_active_days": 10, "usage_trend": "stable", "ticket_sentiment": "neutral"},
        {"customer_id": "C004", "risk_level": "low", "last_active_days": 5, "usage_trend": "stable", "ticket_sentiment": "positive"},
        {"customer_id": "C005", "risk_level": "high", "last_active_days": 90, "usage_trend": "down", "ticket_sentiment": "negative"},
    ]
    write_json("data/logs/activity_logs.json", activity_logs)

    # --- news_samples ---
    news_samples = [
        {"news_id": "N001", "industry": "fintech", "headline": "Digital payments surge 40% in emerging markets", "tone": "opportunity", "summary": "New report shows strong growth in fintech adoption."},
        {"news_id": "N002", "industry": "retail", "headline": "Retail AI assistants boost conversion by 25%", "tone": "opportunity", "summary": "Case study reveals major ROI for retailers using AI."},
        {"news_id": "N003", "industry": "fintech", "headline": "Regulatory changes threaten fintech margins", "tone": "pain_point", "summary": "New compliance costs may squeeze profits."},
        {"news_id": "N004", "industry": "retail", "headline": "Supply chain disruptions continue to hurt inventory", "tone": "pain_point", "summary": "Retailers face ongoing challenges in sourcing."},
        {"news_id": "N005", "industry": "fintech", "headline": "Fintech unicorns raise record funding in Q3", "tone": "opportunity", "summary": "Investors bullish on fintech innovation."},
    ]
    write_json("data/news/news_samples.json", news_samples)

    # --- interference files ---
    # old activity logs (outdated)
    old_logs = [
        {"customer_id": "C001", "risk_level": "low", "last_active_days": 2, "usage_trend": "stable", "ticket_sentiment": "positive"},
    ]
    write_json("data/archive/old_activity_logs.json", old_logs)

    # irrelevant news (no industry match)
    irrelevant_news = [
        {"news_id": "N010", "industry": "healthcare", "headline": "Telemedicine adoption doubles", "tone": "opportunity", "summary": "Healthcare sector digital transformation."},
    ]
    write_json("data/news/irrelevant_news.json", irrelevant_news)

    # another file to distract
    write_json("data/misc/random.json", {"note": "not needed"})

    # ops directory for output (agent to create)
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
