import os
import json
import shutil

def build_env():
    base = os.getcwd()  # should be 
    
    # ---- data/competitors/ ----
    comp_dir = os.path.join(base, "data", "competitors")
    os.makedirs(comp_dir, exist_ok=True)
    
    # SmartSaaS – latest version (version=2)
    smartsaas_latest = {
        "record_id": "comp-003",
        "competitor_id": "SmartSaaS",
        "name": "SmartSaaS",
        "description": "Leading SaaS platform for SMBs",
        "sector": "Consumer SaaS",
        "market_cap": 12000000000,
        "market_share": 12.5,
        "revenue": 5000000000,
        "user_count": 50000,
        "growth_rate": 0.28,
        "financials": {"last_quarter": 1.2e9, "yoy_growth": 0.35},
        "products": ["SmartCRM", "SmartAnalytics"],
        "news": ["Sep 2024: Raised Series D"],
        "version": 2
    }
    with open(os.path.join(comp_dir, "smartsaas.json"), "w") as f:
        json.dump(smartsaas_latest, f, indent=2)
    
    # SmartSaaS – older snapshot (version=1)
    smartsaas_old = {
        "record_id": "comp-003-old",
        "competitor_id": "SmartSaaS",
        "name": "SmartSaaS",
        "description": "SaaS platform for SMBs (legacy)",
        "sector": "Consumer SaaS",
        "market_cap": 8000000000,
        "market_share": 10.0,
        "revenue": 3500000000,
        "user_count": 30000,
        "growth_rate": 0.22,
        "financials": {"last_quarter": 0.9e9, "yoy_growth": 0.28},
        "products": ["SmartCRM"],
        "news": ["Jan 2024: Launched SmartCRM"],
        "version": 1
    }
    with open(os.path.join(comp_dir, "smartsaas_old.json"), "w") as f:
        json.dump(smartsaas_old, f, indent=2)
    
    # Other competitors (distractions)
    cloudmajor = {
        "record_id": "comp-001",
        "competitor_id": "CloudMajor",
        "name": "CloudMajor",
        "description": "Enterprise cloud infrastructure",
        "sector": "Cloud Computing",
        "market_cap": 200000000000,
        "market_share": 32.1,
        "revenue": 85000000000,
        "user_count": 5000000,
        "growth_rate": 0.15,
        "financials": {"last_quarter": 2.1e10, "yoy_growth": 0.18},
        "products": ["CloudCompute", "CloudStorage"],
        "news": ["Aug 2024: New data center in EU"]
    }
    with open(os.path.join(comp_dir, "cloudmajor.json"), "w") as f:
        json.dump(cloudmajor, f, indent=2)
    
    dataflow = {
        "record_id": "comp-002",
        "competitor_id": "DataFlow AI",
        "name": "DataFlow AI",
        "description": "AI/ML data pipeline platform",
        "sector": "AI/ML",
        "market_cap": 45000000000,
        "market_share": 8.7,
        "revenue": 12000000000,
        "user_count": 800000,
        "growth_rate": 0.42,
        "financials": {"last_quarter": 3.5e9, "yoy_growth": 0.55},
        "products": ["DataFlow Core", "DataFlow ML"],
        "news": ["Jun 2024: Partnered with NVIDIA"]
    }
    with open(os.path.join(comp_dir, "dataflow_ai.json"), "w") as f:
        json.dump(dataflow, f, indent=2)
    
    techcorp = {
        "record_id": "comp-004",
        "competitor_id": "TechCorp",
        "name": "TechCorp",
        "description": "Enterprise software suite",
        "sector": "Enterprise Software",
        "market_cap": 75000000000,
        "market_share": 22.3,
        "revenue": 28000000000,
        "user_count": 2000000,
        "growth_rate": 0.11,
        "financials": {"last_quarter": 6.8e9, "yoy_growth": 0.09},
        "products": ["TechSuite", "TechAnalytics"],
        "news": ["Mar 2024: Acquired Startup ABC"]
    }
    with open(os.path.join(comp_dir, "techcorp.json"), "w") as f:
        json.dump(techcorp, f, indent=2)
    
    # ---- data/users/ ----
    users_dir = os.path.join(base, "data", "users")
    os.makedirs(users_dir, exist_ok=True)
    
    users = [
        {"user_id": "u001", "name": "Alice Johnson", "email": "alice.j@enterprise.com", "competitor_id": "CloudMajor", "tier": "enterprise", "cohort": "cohort_q1_2025", "acquisition_source": "organic", "acquisition_campaign": "brand_awareness", "acquisition_date": "2025-01-15", "acquisition_cost": 120, "initial_channel": "blog", "lifetime_value": 5000},
        {"user_id": "u002", "name": "Bob Williams", "email": "bob.w@startup.io", "competitor_id": "SmartSaaS", "tier": "basic", "cohort": "cohort_q2_2025", "acquisition_source": "paid_ads", "acquisition_campaign": "spring_promo", "acquisition_date": "2025-04-10", "acquisition_cost": 100, "initial_channel": "google_ads", "lifetime_value": 1200, "archived": False},
        {"user_id": "u003", "name": "Carol Martinez", "email": "carol.m@cloudco.com", "competitor_id": "CloudMajor", "tier": "premium", "cohort": "cohort_q3_2024", "acquisition_source": "referral", "acquisition_campaign": "partner_program", "acquisition_date": "2024-08-20", "acquisition_cost": 50, "initial_channel": "partner", "lifetime_value": 8000},
        {"user_id": "u004", "name": "David Lee", "email": "david.lee@retail.net", "competitor_id": "DataFlow AI", "tier": "basic", "cohort": "cohort_q1_2026", "acquisition_source": "social", "acquisition_campaign": "linkedin_awareness", "acquisition_date": "2026-01-05", "acquisition_cost": 80, "initial_channel": "linkedin", "lifetime_value": 300},
        {"user_id": "u005", "name": "Emma Brown", "email": "emma.b@saas.co", "competitor_id": "SmartSaaS", "tier": "premium", "cohort": "cohort_q4_2025", "acquisition_source": "organic", "acquisition_campaign": "content_marketing", "acquisition_date": "2025-10-12", "acquisition_cost": 200, "initial_channel": "website", "lifetime_value": 3500, "archived": False},
        {"user_id": "u006", "name": "Frank Green", "email": "frank.g@techcorp.com", "competitor_id": "TechCorp", "tier": "enterprise", "cohort": "cohort_q1_2025", "acquisition_source": "paid_ads", "acquisition_campaign": "brand_awareness", "acquisition_date": "2025-02-28", "acquisition_cost": 150, "initial_channel": "google_ads", "lifetime_value": 7000},
        {"user_id": "u007", "name": "Grace Lee", "email": "grace.l@smartsaas.co", "competitor_id": "SmartSaaS", "tier": "basic", "cohort": "cohort_q2_2025", "acquisition_source": "referral", "acquisition_campaign": "partner_program", "acquisition_date": "2025-06-18", "acquisition_cost": 300, "initial_channel": "partner", "lifetime_value": 600, "archived": False},
        {"user_id": "u008", "name": "Henry Chen", "email": "henry.c@dataflow.com", "competitor_id": "DataFlow AI", "tier": "premium", "cohort": "cohort_q3_2024", "acquisition_source": "organic", "acquisition_campaign": "brand_awareness", "acquisition_date": "2024-09-01", "acquisition_cost": 90, "initial_channel": "blog", "lifetime_value": 4000},
        {"user_id": "u009", "name": "Ivy Wang", "email": "ivy.w@retail.net", "competitor_id": "SmartSaaS", "tier": "basic", "cohort": "cohort_q1_2025", "acquisition_source": "paid_ads", "acquisition_campaign": "spring_promo", "acquisition_date": "2025-03-15", "acquisition_cost": 150, "initial_channel": "google_ads", "lifetime_value": 800, "archived": True},
        {"user_id": "u010", "name": "Jack Smith", "email": "jack.s@startup.io", "competitor_id": "SmartSaaS", "tier": "enterprise", "cohort": "cohort_q4_2025", "acquisition_source": "social", "acquisition_campaign": "linkedin_awareness", "acquisition_date": "2025-11-20", "acquisition_cost": 250, "initial_channel": "linkedin", "lifetime_value": 5500, "archived": True},
    ]
    
    for u in users:
        fname = f"user_{u['user_id']}.json"
        with open(os.path.join(users_dir, fname), "w") as f:
            json.dump(u, f, indent=2)
    
    # ---- data/policies/ (distraction) ----
    policy_dir = os.path.join(base, "data", "policies")
    os.makedirs(policy_dir, exist_ok=True)
    policies = [
        {
            "policy_id": "pol-001",
            "title": "EU Digital Markets Act Compliance",
            "policy_type": "antitrust",
            "jurisdiction": "EU",
            "status": "active",
            "impact_level": "high",
            "full_text": "...",
            "summary": "Requires gatekeeper platforms to ensure interoperability...",
            "impact": {"competitors_affected": ["CloudMajor"]},
            "changes": ["Article 6 requirements"]
        },
        {
            "policy_id": "pol-002",
            "title": "US AI Transparency Act",
            "policy_type": "ai_regulation",
            "jurisdiction": "US",
            "status": "proposed",
            "impact_level": "medium",
            "full_text": "...",
            "summary": "Mandates disclosure of AI use in consumer-facing services...",
            "impact": {"competitors_affected": ["DataFlow AI", "SmartSaaS"]},
            "changes": ["Disclosure requirements"]
        }
    ]
    for p in policies:
        fname = f"{p['policy_id']}.json"
        with open(os.path.join(policy_dir, fname), "w") as f:
            json.dump(p, f, indent=2)
    
    # ---- other distraction files ----
    # data/accounts.json
    accounts = [
        {"account_id": "a001", "name": "Main Account", "display_name": "CompTrack", "role": "analyst", "email": "analyst@compete.io", "team": "Competitive Intelligence", "permissions": ["read", "write"]}
    ]
    with open(os.path.join(base, "data", "accounts.json"), "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)
    
    # data/contacts.json
    contacts = [
        {"contact_id": "c001", "name": "David Kim", "email": "dkim@regtech.com", "role": "Compliance Director", "team": "Legal", "social_handle": "@davidkim"},
        {"contact_id": "c002", "name": "Emily Zhang", "email": "emily.zhang@smartsaas.com", "role": "CEO", "team": "Executive", "social_handle": "@emilyzhang"}
    ]
    with open(os.path.join(base, "data", "contacts.json"), "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
