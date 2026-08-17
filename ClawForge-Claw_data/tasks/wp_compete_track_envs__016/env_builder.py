import os
import json

def build_env():
    # ----- 竞品数据 -----
    competitors = [
        {
            "competitor_id": "CloudMajor",
            "name": "CloudMajor",
            "sector": "Cloud Computing",
            "market_cap": 450000000000,
            "market_share": 32.5,
            "revenue": 180000000000,
            "user_count": 5000000,
            "growth_rate": 12.3,
            "financials": {"fiscal_year": 2025, "net_income": 40000000000, "r&d": 15000000000},
            "products": ["CloudInfra", "AIPlatform"],
            "news": ["expanding eu data centers"]
        },
        {
            "competitor_id": "DataFlow AI",
            "name": "DataFlow AI",
            "sector": "AI/ML",
            "market_cap": 120000000000,
            "market_share": 18.7,
            "revenue": 45000000000,
            "user_count": 1200000,
            "growth_rate": 25.1,
            "financials": {"fiscal_year": 2025, "net_income": 8000000000, "r&d": 6000000000},
            "products": ["DataPipeline", "MLStudio"],
            "news": ["new nlp model launch"]
        },
        {
            "competitor_id": "SmartSaaS",
            "name": "SmartSaaS",
            "sector": "Consumer SaaS",
            "market_cap": 25000000000,
            "market_share": 5.2,
            "revenue": 8000000000,
            "user_count": 3000000,
            "growth_rate": 8.7,
            "financials": {"fiscal_year": 2025, "net_income": 1200000000, "r&d": 900000000},
            "products": ["SmartCRM", "AnalyticsHub"],
            "news": ["acquired startup"]
        },
        {
            "competitor_id": "TechCorp",
            "name": "TechCorp",
            "sector": "Enterprise Software",
            "market_cap": 90000000000,
            "market_share": 14.3,
            "revenue": 35000000000,
            "user_count": 4000000,
            "growth_rate": 6.2,
            "financials": {"fiscal_year": 2025, "net_income": 5000000000, "r&d": 4000000000},
            "products": ["ERP Suite", "SecurityX"],
            "news": ["new partnership"]
        }
    ]
    os.makedirs("data/competitors", exist_ok=True)
    for c in competitors:
        with open(f"data/competitors/{c['competitor_id']}.json", "w") as f:
            json.dump(c, f)

    # ----- 政策数据 -----
    policies = [
        {
            "policy_id": "EU_DMA_001",
            "title": "EU Digital Markets Act Compliance",
            "description": "Regulation for digital gatekeepers",
            "policy_type": "antitrust",
            "jurisdiction": "EU",
            "status": "active",
            "impact_level": "high",
            "full_text": "Full text placeholder",
            "summary": "Compliance requirements for large platforms",
            "impact": {"affected_competitors": ["CloudMajor", "DataFlow AI"]},
            "changes": ["data sharing requirements"]
        },
        {
            "policy_id": "US_AI_001",
            "title": "US AI Transparency Act",
            "description": "Disclosure requirements for AI systems",
            "policy_type": "ai_regulation",
            "jurisdiction": "US",
            "status": "active",
            "impact_level": "medium",
            "full_text": "Full text placeholder",
            "summary": "Transparency obligations",
            "impact": {"affected_competitors": ["TechCorp"]},
            "changes": ["model card requirements"]
        },
        {
            "policy_id": "GLOBAL_PRIV_001",
            "title": "Global Data Privacy Framework",
            "description": "International data transfer standards",
            "policy_type": "privacy",
            "jurisdiction": "Global",
            "status": "proposed",
            "impact_level": "high",
            "full_text": "Full text placeholder",
            "summary": "Cross-border data rules",
            "impact": {"affected_competitors": ["SmartSaaS"]},
            "changes": ["consent requirements"]
        },
        # 干扰：已过期 (status 无效) 但 copilot 故意写错
        {
            "policy_id": "OBSOLETE",
            "title": "Old Policy",
            "description": "Outdated",
            "policy_type": "privacy",
            "jurisdiction": "Global",
            "status": "expired",
            "impact_level": "high",
            "full_text": "irrelevant",
            "summary": "not active",
            "impact": {"affected_competitors": ["CloudMajor"]},
            "changes": []
        }
    ]
    os.makedirs("data/policies", exist_ok=True)
    for p in policies:
        with open(f"data/policies/{p['policy_id']}.json", "w") as f:
            json.dump(p, f)

    # ----- 用户数据 -----
    users = [
        {"user_id": "U001", "name": "Alice Johnson", "email": "alice.j@enterprise.com", "competitor_id": "CloudMajor", "tier": "enterprise", "cohort": "cohort_q1_2025", "acquisition_source": "organic", "acquisition_campaign": "brand_awareness", "acquisition_date": "2025-01-15", "acquisition_cost": 50, "initial_channel": "blog", "lifetime_value": 12000},
        {"user_id": "U002", "name": "Bob Williams", "email": "bob.w@startup.io", "competitor_id": "CloudMajor", "tier": "basic", "cohort": "cohort_q2_2025", "acquisition_source": "paid_ads", "acquisition_campaign": "spring_promo", "acquisition_date": "2025-04-10", "acquisition_cost": 200, "initial_channel": "google_ads", "lifetime_value": 3000},
        {"user_id": "U003", "name": "Carol Martinez", "email": "carol.m@cloudco.com", "competitor_id": "CloudMajor", "tier": "premium", "cohort": "cohort_q3_2024", "acquisition_source": "organic", "acquisition_campaign": "content_marketing", "acquisition_date": "2024-09-01", "acquisition_cost": 0, "initial_channel": "website", "lifetime_value": 25000},
        {"user_id": "U004", "name": "David Lee", "email": "david.lee@retail.net", "competitor_id": "DataFlow AI", "tier": "enterprise", "cohort": "cohort_q4_2025", "acquisition_source": "referral", "acquisition_campaign": "partner_program", "acquisition_date": "2025-11-20", "acquisition_cost": 30, "initial_channel": "partner", "lifetime_value": 8000},
        {"user_id": "U005", "name": "Emma Brown", "email": "emma.b@saas.co", "competitor_id": "DataFlow AI", "tier": "basic", "cohort": "cohort_q1_2026", "acquisition_source": "referral", "acquisition_campaign": "partner_program", "acquisition_date": "2026-01-05", "acquisition_cost": 25, "initial_channel": "partner", "lifetime_value": 2000},
        # 脏数据：空 acquisition_source
        {"user_id": "U006", "name": "Fake User", "email": "fake@test.com", "competitor_id": "SmartSaaS", "tier": "basic", "cohort": "cohort_q1_2025", "acquisition_source": "", "acquisition_campaign": "none", "acquisition_date": "2025-06-01", "acquisition_cost": 10, "initial_channel": "unknown", "lifetime_value": 100},
        # 脏数据：competitor_id 不存在
        {"user_id": "U007", "name": "Ghost", "email": "ghost@void.com", "competitor_id": "NonExistent", "tier": "premium", "cohort": "cohort_q2_2025", "acquisition_source": "social", "acquisition_campaign": "linkedin_awareness", "acquisition_date": "2025-07-15", "acquisition_cost": 150, "initial_channel": "linkedin", "lifetime_value": 500},
        # 脏数据：重复 user_id（实际应该忽略）
        {"user_id": "U001", "name": "Alice Johnson duplicate", "email": "alice2@enterprise.com", "competitor_id": "CloudMajor", "tier": "enterprise", "cohort": "cohort_q1_2025", "acquisition_source": "organic", "acquisition_campaign": "brand_awareness", "acquisition_date": "2025-01-15", "acquisition_cost": 50, "initial_channel": "blog", "lifetime_value": 12000}
    ]
    os.makedirs("data/users", exist_ok=True)
    # 避免重复 ID 覆盖：我们写不同文件名
    written_ids = set()
    for u in users:
        uid = u["user_id"]
        if uid in written_ids:
            # 重复的写不同文件名，但内容保留
            filename = f"data/users/{uid}_dup.json"
        else:
            filename = f"data/users/{uid}.json"
            written_ids.add(uid)
        with open(filename, "w") as f:
            json.dump(u, f)

    # ----- 干扰目录 -----
    os.makedirs("archive/policies", exist_ok=True)
    with open("archive/policies/old_policy.json", "w") as f:
        json.dump({"policy_id": "OLD", "status": "active", "impact_level": "high", "impact": {"affected_competitors": ["CloudMajor"]}}, f)

    os.makedirs("backup", exist_ok=True)
    with open("backup/competitors_2024.json", "w") as f:
        json.dump({"competitor_id": "CloudMajor", "market_cap": 400000000000}, f)

    # ----- accounts / contacts 干扰 -----
    accounts = [
        {"account_id": "A001", "name": "Admin", "display_name": "Admin", "role": "admin", "email": "admin@compete.io", "team": "operations", "permissions": ["read", "write"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)
    contacts = [
        {"contact_id": "C001", "name": "David Kim", "email": "dkim@regtech.com", "role": "Compliance Director", "team": "Legal", "social_handle": "@davidkim"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

if __name__ == "__main__":
    build_env()
