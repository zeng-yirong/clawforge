import os
import json

def build_env():
    # 创建 data 目录
    os.makedirs("data", exist_ok=True)
    # 创建 output 目录（空目录，用于存放 agent 产物）
    os.makedirs("output", exist_ok=True)

    # 客户数据（唯一答案：高风险客户 LedgerFlow 和 ShelfCloud，注意干扰项）
    customers = [
        {"customer_id": "cust_001", "customer_name": "LedgerFlow", "industry": "fintech", "tier": "enterprise", "labels": ["active", "premium"], "owner_name": "Maggie"},
        {"customer_id": "cust_002", "customer_name": "ShelfCloud", "industry": "retail", "tier": "mid_market", "labels": ["new"], "owner_name": "Tom"},
        {"customer_id": "cust_003", "customer_name": "DataStream", "industry": "fintech", "tier": "enterprise", "labels": ["vip"], "owner_name": "Maggie"},  # 低风险干扰
        {"customer_id": "cust_004", "customer_name": "GreenLeaf", "industry": "healthcare", "tier": "small_business", "labels": [], "owner_name": "Jane"}  # 无关行业干扰
    ]
    with open("data/customers.json", "w") as f:
        json.dump({"customers": customers}, f, indent=2)

    # 活动日志（注意：高风险且满足条件的只有 cust_001 和 cust_002）
    activity_logs = [
        {"customer_id": "cust_001", "risk_level": "high", "last_active_days": 45, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "cust_002", "risk_level": "high", "last_active_days": 60, "usage_trend": "down", "ticket_sentiment": "negative"},
        {"customer_id": "cust_003", "risk_level": "low", "last_active_days": 5, "usage_trend": "stable", "ticket_sentiment": "neutral"},  # 低风险，不应被选中
        {"customer_id": "cust_004", "risk_level": "high", "last_active_days": 10, "usage_trend": "stable", "ticket_sentiment": "negative"}  # 活跃天数不足30，不应被选中
    ]
    with open("data/activity_logs.json", "w") as f:
        json.dump({"activity_logs": activity_logs}, f, indent=2)

    # 新闻样本（为每个行业提供机会型和痛点型，使得唯一答案明确）
    news_samples = [
        {"news_id": "news_001", "industry": "fintech", "headline": "New Open Banking Regulations Boost Demand for LedgerFlow Solutions", "tone": "opportunity", "summary": "Open banking mandates create huge upsell for LedgerFlow's ledger tools."},
        {"news_id": "news_002", "industry": "fintech", "headline": "Fintech Layoffs Surge, Startups Struggle to Retain Talent", "tone": "pain_point", "summary": "Many fintech companies are cutting costs."},
        {"news_id": "news_003", "industry": "retail", "headline": "Retail AI Adoption: ShelfCloud's Predictive Inventory Now 30% More Accurate", "tone": "opportunity", "summary": "ShelfCloud's AI models just achieved 30% accuracy improvement."},
        {"news_id": "news_004", "industry": "retail", "headline": "Rising Shelf Space Costs Squeeze Retail Margins", "tone": "pain_point", "summary": "Retailers face increasing shelf space expenses."},
        {"news_id": "news_005", "industry": "healthcare", "headline": "Healthcare IT Investment Hits Record High", "tone": "opportunity", "summary": "Hospitals increase spending on digital health tools."},  # 不匹配的行业干扰
        {"news_id": "news_006", "industry": "fintech", "headline": "Old Fintech News (duplicate tone)", "tone": "opportunity", "summary": "This is a duplicate opportunity news for fintech, but not the best."}  # 干扰：同一行业多条机会新闻，但应选第一个合理？
    ]
    with open("data/news_samples.json", "w") as f:
        json.dump({"news_samples": news_samples}, f, indent=2)

    # 额外干扰文件：无关的 accounts 和 contacts（让环境更有迷惑性）
    accounts = [
        {"account_id": "acc_001", "display_name": "Maggie", "department": "CS", "email": "maggie@example.com", "permissions": ["admin"]},
        {"account_id": "acc_002", "display_name": "Tom", "department": "Sales", "email": "tom@example.com", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "con_001", "name": "Alice", "role": "CEO", "email": "alice@ledgerflow.com"},
        {"contact_id": "con_002", "name": "Bob", "role": "CTO", "email": "bob@shelfcloud.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
