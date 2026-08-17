import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/competitors", exist_ok=True)
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("data/users", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ========== 竞品数据 ==========
    competitors = [
        {
            "competitor_id": "comp_001",
            "name": "CloudMajor",
            "description": "Leading cloud infrastructure and AI services provider",
            "sector": "AI/ML",
            "market_cap": 850000000,
            "market_share": 34.2,
            "revenue": 320000000,
            "user_count": 1500000,
            "growth_rate": 18.5,
            "financials": {"fiscal_year": 2025, "net_income": 89000000},
            "products": ["CloudCompute", "AIForge", "AutoML Suite"],
            "news": [{"date": "2025-03-10", "title": "CloudMajor launches AutoML Suite, aims at enterprise AI"}]
        },
        {
            "competitor_id": "comp_002",
            "name": "DataFlow AI",
            "description": "Data engineering and analytics platform",
            "sector": "AI/ML",
            "market_cap": 420000000,
            "market_share": 22.8,
            "revenue": 180000000,
            "user_count": 900000,
            "growth_rate": 25.3,
            "financials": {"fiscal_year": 2025, "net_income": 45000000},
            "products": ["DataPipeline", "MLStudio"],
            "news": [{"date": "2025-02-28", "title": "DataFlow AI partners with Snowflake"}]
        },
        {
            "competitor_id": "comp_003",
            "name": "SmartSaaS",
            "description": "Vertical SaaS for marketing analytics",
            "sector": "Consumer SaaS",
            "market_cap": 180000000,
            "market_share": 12.5,
            "revenue": 95000000,
            "user_count": 600000,
            "growth_rate": 8.2,
            "financials": {"fiscal_year": 2025, "net_income": 15000000},
            "products": ["SmartAnalytics", "CampaignOptimizer"],
            "news": [{"date": "2025-03-05", "title": "SmartSaaS acquires AdTech startup"}]
        }
    ]
    for c in competitors:
        with open(f"data/competitors/{c['competitor_id']}.json", "w") as f:
            json.dump(c, f, indent=2)

    # ========== 政策数据（包含干扰和诱饵） ==========
    policies = [
        {
            "policy_id": "pol_001",
            "title": "EU Digital Markets Act Compliance",
            "description": "Regulation to ensure fair competition in EU digital markets",
            "policy_type": "antitrust",
            "jurisdiction": "EU",
            "status": "proposed",
            "impact_level": "high",
            "full_text": "Full text of DMA...",
            "summary": "Proposed regulation targeting big tech platforms",
            "impact": {"competitors": ["CloudMajor", "TechCorp"], "severity": "high"},
            "changes": [{"effective_date": "2026-01-01", "description": "Gatekeeper obligations"}]
        },
        {
            "policy_id": "pol_002",
            "title": "Global Data Privacy Framework",
            "description": "International standards for data protection",
            "policy_type": "privacy",
            "jurisdiction": "Global",
            "status": "active",
            "impact_level": "medium",
            "full_text": "Full text of GDPF...",
            "summary": "Framework harmonizing privacy laws across regions",
            "impact": {"competitors": ["DataFlow AI", "SmartSaaS"], "severity": "moderate"},
            "changes": [{"effective_date": "2025-06-01", "description": "Consent requirements updated"}]
        },
        {
            "policy_id": "pol_003",
            "title": "US AI Transparency Act",
            "description": "Mandates transparency and explainability for AI systems",
            "policy_type": "ai_regulation",
            "jurisdiction": "US",
            "status": "active",
            "impact_level": "high",
            "full_text": "Full text of US AI Transparency Act...",
            "summary": "Requires companies to disclose AI training data and decision logic",
            "impact": {"competitors": ["CloudMajor", "DataFlow AI"], "severity": "high"},
            "changes": [{"effective_date": "2025-08-01", "description": "AI model registration requirement"}]
        },
        {
            "policy_id": "pol_004",
            "title": "EU AI Liability Directive",
            "description": "Liability framework for AI-caused harm",
            "policy_type": "ai_regulation",
            "jurisdiction": "EU",
            "status": "proposed",
            "impact_level": "medium",
            "full_text": "Full text of EU AI Liability...",
            "summary": "Proposed directive shifting burden of proof",
            "impact": {"competitors": ["SmartSaaS", "TechCorp"], "severity": "moderate"},
            "changes": [{"effective_date": "2027-01-01", "description": "Strict liability for high-risk AI"}]
        }
    ]
    for p in policies:
        with open(f"data/policies/{p['policy_id']}.json", "w") as f:
            json.dump(p, f, indent=2)

    # ========== 用户数据（干扰 + 关联CloudMajor） ==========
    users = [
        {"user_id": "usr_001", "name": "Alice Johnson", "email": "alice.j@enterprise.com",
         "competitor_id": "comp_001", "tier": "enterprise", "cohort": "cohort_q4_2025",
         "acquisition_source": "paid_ads", "acquisition_campaign": "brand_awareness",
         "acquisition_date": "2025-01-15", "acquisition_cost": 1200, "initial_channel": "google_ads",
         "lifetime_value": 48000},
        {"user_id": "usr_002", "name": "Bob Williams", "email": "bob.w@startup.io",
         "competitor_id": "comp_001", "tier": "basic", "cohort": "cohort_q1_2026",
         "acquisition_source": "referral", "acquisition_campaign": "partner_program",
         "acquisition_date": "2025-02-10", "acquisition_cost": 300, "initial_channel": "partner",
         "lifetime_value": 12000},
        {"user_id": "usr_003", "name": "Carol Martinez", "email": "carol.m@cloudco.com",
         "competitor_id": "comp_002", "tier": "premium", "cohort": "cohort_q2_2025",
         "acquisition_source": "organic", "acquisition_campaign": "content_marketing",
         "acquisition_date": "2025-03-20", "acquisition_cost": 0, "initial_channel": "blog",
         "lifetime_value": 72000}
    ]
    for u in users:
        with open(f"data/users/{u['user_id']}.json", "w") as f:
            json.dump(u, f, indent=2)

    # ========== 账户和联系人（纯粹干扰） ==========
    accounts = {"accounts": [
        {"account_id": "acct_01", "name": "default", "display_name": "Default Account",
         "role": "admin", "email": "admin@compete.ai", "team": "Engineering",
         "permissions": ["read", "write"]}
    ]}
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    contacts = {"contacts": [
        {"contact_id": "c_001", "name": "David Kim", "email": "dkim@regtech.com",
         "role": "Compliance Director", "team": "Legal", "social_handle": "@davidkim"},
        {"contact_id": "c_002", "name": "Emily Zhang", "email": "emily.zhang@smartsaas.com",
         "role": "CEO", "team": "Executive", "social_handle": "@emilyzhang"}
    ]}
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 空占位文件（增加干扰）
    with open("data/policies/old_policy.json", "w") as f:
        json.dump({"title": "Obsolete Privacy Act", "status": "deprecated", "impact_level": "low"}, f)
    with open("data/competitors/outdated_comp.json", "w") as f:
        json.dump({"competitor_id": "comp_old", "name": "ObsoleteCorp", "sector": "Legacy"}, f)

if __name__ == "__main__":
    build_env()
