import os
import json
import random

def build_env():
    # Create directory structure
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("backup/temp", exist_ok=True)

    # === Customers ===
    customers = [
        {
            "customer_id": "C001",
            "customer_name": "LedgerFlow",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["priority", "finance"],
            "owner_name": "Alice"
        },
        {
            "customer_id": "C002",
            "customer_name": "ShelfCloud",
            "industry": "retail",
            "tier": "mid_market",
            "labels": ["logistics"],
            "owner_name": "Bob"
        },
        {
            "customer_id": "C003",
            "customer_name": "ClearBank",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["finance"],
            "owner_name": "Carol"
        },
        {
            "customer_id": "C004",
            "customer_name": "QuickCart",
            "industry": "retail",
            "tier": "mid_market",
            "labels": ["ecommerce"],
            "owner_name": "Dave"
        },
        {
            "customer_id": "C005",
            "customer_name": "DataVault",
            "industry": "fintech",
            "tier": "enterprise",
            "labels": ["security"],
            "owner_name": "Eve"
        }
    ]
    with open("data/customers/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # === Activity Logs ===
    activity_logs = [
        {"customer_id": "C001", "risk_level": "high", "last_active_days": 45, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "C002", "risk_level": "high", "last_active_days": 60, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "C003", "risk_level": "low", "last_active_days": 3, "usage_trend": "stable", "ticket_sentiment": "neutral"},
        {"customer_id": "C004", "risk_level": "low", "last_active_days": 10, "usage_trend": "stable", "ticket_sentiment": "neutral"},
        {"customer_id": "C005", "risk_level": "high", "last_active_days": 30, "usage_trend": "down", "ticket_sentiment": "negative"}
    ]
    # Add a distractor with high risk but stable usage (not qualifying because usage not down)
    activity_logs.append({"customer_id": "C003", "risk_level": "high", "last_active_days": 2, "usage_trend": "stable", "ticket_sentiment": "negative"})
    with open("data/logs/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # === News Samples ===
    news_samples = [
        {
            "news_id": "N001",
            "industry": "fintech",
            "headline": "Fintech Regulation Tightens: New Compliance Costs Loom",
            "tone": "pain_point",
            "summary": "New compliance rules expected to increase operational costs by 20% for small fintech firms."
        },
        {
            "news_id": "N002",
            "industry": "retail",
            "headline": "Retailers Embrace AI-Powered Inventory Management",
            "tone": "opportunity",
            "summary": "Major retailers report 30% reduction in waste using AI forecasting."
        },
        {
            "news_id": "N003",
            "industry": "retail",
            "headline": "Supply Chain Disruptions Still Hitting Small Retailers Hard",
            "tone": "pain_point",
            "summary": "Persistent logistics delays causing 15% revenue loss for mid-market retailers."
        },
        {
            "news_id": "N004",
            "industry": "fintech",
            "headline": "Digital Banking Adoption Surges Among Gen Z",
            "tone": "opportunity",
            "summary": "New fintech users under 25 grow by 40% year-over-year."
        },
        {
            "news_id": "N005",
            "industry": "fintech",
            "headline": "Fraud Detection: Legacy Systems Fall Short",
            "tone": "pain_point",
            "summary": "Traditional fraud detection misses up to 25% of sophisticated attacks."
        }
    ]
    with open("data/news/news_samples.json", "w") as f:
        json.dump({"news_samples": news_samples}, f, indent=2)

    # === Distractor files ===
    # Irrelevant backup copies
    if not os.path.exists("backup/customers_backup.json"):
        with open("backup/customers_backup.json", "w") as f:
            json.dump({"customers": []}, f)
    if not os.path.exists("backup/temp/activity_old.json"):
        with open("backup/temp/activity_old.json", "w") as f:
            json.dump({"activity_logs": []}, f)
    # A stale template file
    with open("ops/email_template.txt", "w") as f:
        f.write("Subject: We've got news for you!\nBody: Dear {{name}},\n{{message}}")
    # A previous cached file (should be overwritten)
    with open("ops/retention_cache.json", "w") as f:
        json.dump([{"customer_id": "stale"}], f)
    # Random log file
    with open("data/logs/old_format.txt", "w") as f:
        f.write("C001,low,5,stable,neutral\nC002,high,90,down,negative\n")

if __name__ == "__main__":
    build_env()
