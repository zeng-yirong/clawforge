import os
import json

def build_env():
    # 确保 cwd 已为 ，直接使用相对路径
    # 创建目录结构
    os.makedirs("data/competitors", exist_ok=True)
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("data/users", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 空目录，agent 需要写入文件

    # --- 竞品数据 (4 个，其中 3 个受影响，1 个干扰) ---
    competitors = [
        {
            "competitor_id": "comp-001",
            "name": "CloudMajor",
            "description": "Leading cloud infrastructure provider",
            "sector": "Cloud Computing",
            "market_cap": 850000,
            "market_share": 15.5,
            "revenue": 420000,
            "user_count": 15000,
            "growth_rate": 8.2,
            "financials": {"revenue_2024": 420000, "net_income": 82000},
            "products": ["CloudStorage", "ComputeEngine", "AIPlatform"],
            "news": ["Expanded EU data centers in 2025"]
        },
        {
            "competitor_id": "comp-002",
            "name": "DataFlow AI",
            "description": "AI/ML platform for enterprise",
            "sector": "AI/ML",
            "market_cap": 320000,
            "market_share": 10.2,
            "revenue": 185000,
            "user_count": 8200,
            "growth_rate": 22.1,
            "financials": {"revenue_2024": 185000, "net_income": 34000},
            "products": ["DataFlowStudio", "MLPipeline", "AutoModel"],
            "news": ["Received Series C funding"]
        },
        {
            "competitor_id": "comp-003",
            "name": "SmartSaaS",
            "description": "Consumer SaaS for productivity",
            "sector": "Consumer SaaS",
            "market_cap": 210000,
            "market_share": 8.7,
            "revenue": 95000,
            "user_count": 5100,
            "growth_rate": 15.4,
            "financials": {"revenue_2024": 95000, "net_income": 12000},
            "products": ["SmartTask", "SmartCalendar", "SmartNotes"],
            "news": ["Launched in EU market last year"]
        },
        {
            "competitor_id": "comp-004",
            "name": "TechCorp",
            "description": "Enterprise software suite",
            "sector": "Enterprise Software",
            "market_cap": 680000,
            "market_share": 12.0,
            "revenue": 310000,
            "user_count": 12000,
            "growth_rate": 6.8,
            "financials": {"revenue_2024": 310000, "net_income": 55000},
            "products": ["TechSuite", "AnalyticsPro", "CRMEnterprise"],
            "news": ["Announced layoffs in Q1"]
        }
    ]
    for comp in competitors:
        filepath = f"data/competitors/{comp['competitor_id']}.json"
        with open(filepath, "w") as f:
            json.dump(comp, f, indent=2)

    # --- 政策数据 (4 个，2 个满足条件，2 个干扰) ---
    policies = [
        {
            "policy_id": "pol-001",
            "title": "EU Digital Markets Act Compliance",
            "description": "Obligations for gatekeeper platforms",
            "policy_type": "antitrust",
            "jurisdiction": "EU",
            "status": "active",
            "impact_level": "high",
            "full_text": "...",
            "summary": "Regulates large online platforms",
            "impact": {"affected_competitors": ["comp-001", "comp-002"], "revenue_impact": "15%"},
            "changes": ["New data sharing requirements"]
        },
        {
            "policy_id": "pol-002",
            "title": "Global Data Privacy Framework",
            "description": "International data transfer rules",
            "policy_type": "privacy",
            "jurisdiction": "Global",
            "status": "active",
            "impact_level": "medium",
            "full_text": "...",
            "summary": "Framework for cross-border data flows",
            "impact": {"affected_competitors": ["comp-001", "comp-003"]},
            "changes": ["Updated standard contractual clauses"]
        },
        {
            "policy_id": "pol-003",
            "title": "US AI Transparency Act",
            "description": "Disclosure requirements for AI systems",
            "policy_type": "ai_regulation",
            "jurisdiction": "US",
            "status": "proposed",
            "impact_level": "high",
            "full_text": "...",
            "summary": "Requires AI model documentation",
            "impact": {"affected_competitors": ["comp-002", "comp-004"]},
            "changes": ["Mandatory bias audits"]
        },
        {
            "policy_id": "pol-004",
            "title": "EU AI Liability Directive",
            "description": "Liability rules for AI products",
            "policy_type": "ai_regulation",
            "jurisdiction": "EU",
            "status": "active",
            "impact_level": "high",
            "full_text": "...",
            "summary": "Shifts burden of proof to AI providers",
            "impact": {"affected_competitors": ["comp-003"], "penalty_max": "4% of revenue"},
            "changes": ["Strict liability for high-risk AI"]
        }
    ]
    for pol in policies:
        filepath = f"data/policies/{pol['policy_id']}.json"
        with open(filepath, "w") as f:
            json.dump(pol, f, indent=2)

    # --- 用户数据 (为 3 个受影响竞品提供用户，加入脏数据) ---
    users = []
    # CloudMajor (comp-001) 用户
    users.extend([
        {"user_id": "u001", "name": "Alice Johnson", "email": "alice.j@enterprise.com", "competitor_id": "comp-001", "tier": "enterprise", "cohort": "cohort_q1_2025", "acquisition_source": "paid_ads", "acquisition_campaign": "brand_awareness", "acquisition_date": "2025-01-15", "acquisition_cost": 250, "initial_channel": "google_ads", "lifetime_value": 3000},
        {"user_id": "u002", "name": "Bob Williams", "email": "bob.w@startup.io", "competitor_id": "comp-001", "tier": "premium", "cohort": "cohort_q1_2026", "acquisition_source": "organic", "acquisition_campaign": "content_marketing", "acquisition_date": "2026-01-20", "acquisition_cost": 0, "initial_channel": "blog", "lifetime_value": 1500},  # 正常，成本0
        {"user_id": "u003", "name": "Carol Martinez", "email": "carol.m@cloudco.com", "competitor_id": "comp-001", "tier": "basic", "cohort": "cohort_q2_2025", "acquisition_source": "referral", "acquisition_campaign": "partner_program", "acquisition_date": "2025-04-10", "acquisition_cost": 175, "initial_channel": "partner", "lifetime_value": 800},
        {"user_id": "u004", "name": "David Lee", "email": "david.lee@retail.net", "competitor_id": "comp-001", "tier": "enterprise", "cohort": "cohort_q4_2025", "acquisition_source": "paid_ads", "acquisition_campaign": "spring_promo", "acquisition_date": "2025-10-01", "acquisition_cost": 320, "initial_channel": "google_ads", "lifetime_value": 4000},
        {"user_id": "u005", "name": "Emma Brown", "email": "emma.b@saas.co", "competitor_id": "comp-001", "tier": "premium", "cohort": "cohort_q3_2024", "acquisition_source": "social", "acquisition_campaign": "linkedin_awareness", "acquisition_date": "2024-07-22", "acquisition_cost": -50, "initial_channel": "linkedin", "lifetime_value": 2200}  # 脏数据：负数
    ])
    # DataFlow AI (comp-002) 用户
    users.extend([
        {"user_id": "u006", "name": "Frank Green", "email": "frank.g@data.ai", "competitor_id": "comp-002", "tier": "enterprise", "cohort": "cohort_q1_2025", "acquisition_source": "organic", "acquisition_campaign": "brand_awareness", "acquisition_date": "2025-02-11", "acquisition_cost": 500, "initial_channel": "website", "lifetime_value": 6000},
        {"user_id": "u007", "name": "Grace Lee", "email": "grace.l@ai.com", "competitor_id": "comp-002", "tier": "premium", "cohort": "cohort_q2_2025", "acquisition_source": "paid_ads", "acquisition_campaign": "spring_promo", "acquisition_date": "2025-05-30", "acquisition_cost": 15000, "initial_channel": "google_ads", "lifetime_value": 8000},  # 脏数据：大于10000
        {"user_id": "u008", "name": "Henry Kim", "email": "henry.k@ml.io", "competitor_id": "comp-002", "tier": "basic", "cohort": "cohort_q3_2024", "acquisition_source": "referral", "acquisition_campaign": "partner_program", "acquisition_date": "2024-09-15", "acquisition_cost": 480, "initial_channel": "partner", "lifetime_value": 1200},
        {"user_id": "u009", "name": "Ivy Wang", "email": "ivy.w@saas.io", "competitor_id": "comp-002", "tier": "enterprise", "cohort": "cohort_q1_2026", "acquisition_source": "social", "acquisition_campaign": "linkedin_awareness", "acquisition_date": "2026-03-01", "acquisition_cost": 620, "initial_channel": "linkedin", "lifetime_value": 5100}
    ])
    # SmartSaaS (comp-003) 用户
    users.extend([
        {"user_id": "u010", "name": "Jack Davis", "email": "jack.d@smart.com", "competitor_id": "comp-003", "tier": "basic", "cohort": "cohort_q3_2024", "acquisition_source": "organic", "acquisition_campaign": "content_marketing", "acquisition_date": "2024-08-20", "acquisition_cost": 30, "initial_channel": "blog", "lifetime_value": 400},
        {"user_id": "u011", "name": "Karen Wilson", "email": "karen.w@saas.co", "competitor_id": "comp-003", "tier": "premium", "cohort": "cohort_q4_2025", "acquisition_source": "paid_ads", "acquisition_campaign": "brand_awareness", "acquisition_date": "2025-11-05", "acquisition_cost": 210, "initial_channel": "google_ads", "lifetime_value": 2500},
        {"user_id": "u012", "name": "Leo Zhang", "email": "leo.z@cloud.com", "competitor_id": "comp-003", "tier": "enterprise", "cohort": "cohort_q1_2026", "acquisition_source": "referral", "acquisition_campaign": "partner_program", "acquisition_date": "2026-02-14", "acquisition_cost": 180, "initial_channel": "partner", "lifetime_value": 3200},
        {"user_id": "u013", "name": "Mia Johnson", "email": "mia.j@co.io", "competitor_id": "comp-003", "tier": "basic", "cohort": "cohort_q2_2025", "acquisition_source": "social", "acquisition_campaign": "linkedin_awareness", "acquisition_date": "2025-06-18", "acquisition_cost": 60000, "initial_channel": "linkedin", "lifetime_value": 900}  # 脏数据：大于10000
    ])
    # 再加入一个干扰用户（属于无关竞品 comp-004）
    users.append({
        "user_id": "u014", "name": "Noah Brown", "email": "noah.b@techcorp.com", "competitor_id": "comp-004", "tier": "enterprise", "cohort": "cohort_q1_2025", "acquisition_source": "paid_ads", "acquisition_campaign": "brand_awareness", "acquisition_date": "2025-01-10", "acquisition_cost": 400, "initial_channel": "google_ads", "lifetime_value": 4500
    })
    for u in users:
        filepath = f"data/users/{u['user_id']}.json"
        with open(filepath, "w") as f:
            json.dump(u, f, indent=2)

if __name__ == "__main__":
    build_env()
    print("Environment built successfully.")
