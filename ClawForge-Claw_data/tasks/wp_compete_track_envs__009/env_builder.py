import os
import json

def build_env():
    # Create directories
    os.makedirs("competitors", exist_ok=True)
    os.makedirs("users", exist_ok=True)
    os.makedirs("policies", exist_ok=True)

    # Competitors
    competitors = [
        {
            "competitor_id": "cloudmajor",
            "name": "CloudMajor",
            "sector": "Cloud Computing",
            "market_cap": 50000000000,
            "market_share": 0.28,
            "revenue": 12000000000,
            "user_count": 500000,
            "growth_rate": 0.15,
            "financials": {"fiscal_year": 2025, "net_income": 2500000000},
            "products": ["Cloud Storage", "Compute Engine", "AI Platform"],
            "news": ["New data center in EU announced"]
        },
        {
            "competitor_id": "dataflow_ai",
            "name": "DataFlow AI",
            "sector": "Cloud Computing",
            "market_cap": 15000000000,
            "market_share": 0.12,
            "revenue": 3000000000,
            "user_count": 120000,
            "growth_rate": 0.35,
            "financials": {"fiscal_year": 2025, "net_income": 450000000},
            "products": ["ML Pipeline", "Data Lake", "AutoML"],
            "news": ["Series C funding of $500M"]
        },
        {
            "competitor_id": "smartsaas",
            "name": "SmartSaaS",
            "sector": "Consumer SaaS",
            "market_cap": 8000000000,
            "market_share": 0.05,
            "revenue": 2000000000,
            "user_count": 80000,
            "growth_rate": 0.08,
            "financials": {"fiscal_year": 2025, "net_income": 300000000},
            "products": ["CRM Lite", "Invoice Pro"],
            "news": ["New mobile app launched"]
        },
        {
            "competitor_id": "techcorp",
            "name": "TechCorp",
            "sector": "Enterprise Software",
            "market_cap": 60000000000,
            "market_share": 0.40,
            "revenue": 25000000000,
            "user_count": 1000000,
            "growth_rate": 0.05,
            "financials": {"fiscal_year": 2025, "net_income": 5000000000},
            "products": ["ERP Suite", "HR Platform"],
            "news": ["Acquired startup for $2B"]
        }
    ]
    for comp in competitors:
        fname = f"competitors/{comp['competitor_id']}.json"
        with open(fname, "w") as f:
            json.dump(comp, f, indent=2)

    # Users – CloudMajor (3 clean, 3 dirty), DataFlow (3 clean), SmartSaaS (2 clean), TechCorp (2 clean)
    users = [
        # CloudMajor clean
        {"user_id": "cm_001", "name": "Alice Johnson", "email": "alice.j@cloudmajor.io", "competitor_id": "cloudmajor", "tier": "enterprise", "cohort": "cohort_q1_2025", "acquisition_source": "organic", "acquisition_campaign": "brand_awareness", "acquisition_date": "2025-01-15", "acquisition_cost": 2000, "initial_channel": "blog", "lifetime_value": 15000},
        {"user_id": "cm_002", "name": "Bob Williams", "email": "bob.w@cloudmajor.io", "competitor_id": "cloudmajor", "tier": "basic", "cohort": "cohort_q2_2025", "acquisition_source": "paid_ads", "acquisition_campaign": "spring_promo", "acquisition_date": "2025-04-10", "acquisition_cost": 5000, "initial_channel": "google_ads", "lifetime_value": 30000},
        {"user_id": "cm_003", "name": "Carol Martinez", "email": "carol.m@cloudmajor.io", "competitor_id": "cloudmajor", "tier": "premium", "cohort": "cohort_q3_2024", "acquisition_source": "organic", "acquisition_campaign": "content_marketing", "acquisition_date": "2024-09-01", "acquisition_cost": 2500, "initial_channel": "blog", "lifetime_value": 18000},
        # CloudMajor dirty - cost string
        {"user_id": "cm_dirty_1", "name": "Dirty User", "email": "dirty@cloudmajor.io", "competitor_id": "cloudmajor", "tier": "basic", "cohort": "cohort_q1_2025", "acquisition_source": "referral", "acquisition_campaign": "partner_program", "acquisition_date": "2025-02-20", "acquisition_cost": "NaN", "initial_channel": "partner", "lifetime_value": 5000},
        # CloudMajor dirty - negative cost
        {"user_id": "cm_dirty_2", "name": "Bad Cost", "email": "bad@cloudmajor.io", "competitor_id": "cloudmajor", "tier": "basic", "cohort": "cohort_q1_2025", "acquisition_source": "social", "acquisition_campaign": "linkedin_awareness", "acquisition_date": "2025-03-01", "acquisition_cost": -500, "initial_channel": "linkedin", "lifetime_value": 7000},
        # CloudMajor dirty - empty source
        {"user_id": "cm_dirty_3", "name": "No Source", "email": "nosrc@cloudmajor.io", "competitor_id": "cloudmajor", "tier": "basic", "cohort": "cohort_q1_2025", "acquisition_source": "", "acquisition_campaign": "brand_awareness", "acquisition_date": "2025-03-15", "acquisition_cost": 1000, "initial_channel": "blog", "lifetime_value": 8000},
        # DataFlow AI clean
        {"user_id": "df_001", "name": "David Lee", "email": "david.lee@dataflow.ai", "competitor_id": "dataflow_ai", "tier": "enterprise", "cohort": "cohort_q4_2025", "acquisition_source": "referral", "acquisition_campaign": "partner_program", "acquisition_date": "2025-10-05", "acquisition_cost": 1000, "initial_channel": "partner", "lifetime_value": 12000},
        {"user_id": "df_002", "name": "Emma Brown", "email": "emma.b@dataflow.ai", "competitor_id": "dataflow_ai", "tier": "premium", "cohort": "cohort_q1_2026", "acquisition_source": "social", "acquisition_campaign": "linkedin_awareness", "acquisition_date": "2026-01-20", "acquisition_cost": 3000, "initial_channel": "linkedin", "lifetime_value": 22000},
        {"user_id": "df_003", "name": "Frank Green", "email": "frank.g@dataflow.ai", "competitor_id": "dataflow_ai", "tier": "basic", "cohort": "cohort_q2_2025", "acquisition_source": "organic", "acquisition_campaign": "brand_awareness", "acquisition_date": "2025-05-12", "acquisition_cost": 1800, "initial_channel": "blog", "lifetime_value": 14000},
        # SmartSaaS (should be excluded)
        {"user_id": "ss_001", "name": "Grace Kim", "email": "grace.k@smartsaas.com", "competitor_id": "smartsaas", "tier": "basic", "cohort": "cohort_q1_2025", "acquisition_source": "organic", "acquisition_campaign": "brand_awareness", "acquisition_date": "2025-01-01", "acquisition_cost": 500, "initial_channel": "blog", "lifetime_value": 3000},
        {"user_id": "ss_002", "name": "Henry Lee", "email": "henry.l@smartsaas.com", "competitor_id": "smartsaas", "tier": "premium", "cohort": "cohort_q3_2024", "acquisition_source": "paid_ads", "acquisition_campaign": "spring_promo", "acquisition_date": "2024-08-15", "acquisition_cost": 2000, "initial_channel": "google_ads", "lifetime_value": 10000},
        # TechCorp (should be excluded)
        {"user_id": "tc_001", "name": "Irene Wu", "email": "irene.w@techcorp.com", "competitor_id": "techcorp", "tier": "enterprise", "cohort": "cohort_q1_2025", "acquisition_source": "referral", "acquisition_campaign": "partner_program", "acquisition_date": "2025-02-10", "acquisition_cost": 3000, "initial_channel": "partner", "lifetime_value": 25000},
        {"user_id": "tc_002", "name": "Jack Brown", "email": "jack.b@techcorp.com", "competitor_id": "techcorp", "tier": "basic", "cohort": "cohort_q2_2025", "acquisition_source": "social", "acquisition_campaign": "linkedin_awareness", "acquisition_date": "2025-05-20", "acquisition_cost": 1500, "initial_channel": "linkedin", "lifetime_value": 9000},
    ]
    for u in users:
        fname = f"users/{u['user_id']}.json"
        with open(fname, "w") as f:
            json.dump(u, f, indent=2)

    # Policy (distractor)
    policy = {
        "policy_id": "eu_dma",
        "title": "EU Digital Markets Act Compliance",
        "description": "New DMA rules for large platforms",
        "policy_type": "antitrust",
        "jurisdiction": "EU",
        "status": "active",
        "impact_level": "high",
        "full_text": "...",
        "summary": "Affects cloud providers with >10% market share.",
        "impact": {"affected_competitors": ["cloudmajor", "dataflow_ai", "techcorp"]},
        "changes": ["New interoperability requirements"]
    }
    with open("policies/eu_dma.json", "w") as f:
        json.dump(policy, f, indent=2)

    # accounts.json (distractor)
    accounts = [
        {"account_id": "acc_1", "name": "Alice Johnson", "display_name": "Alice J.", "role": "Analyst", "email": "alice.j@enterprise.com", "team": "Marketing", "permissions": ["read", "write"]}
    ]
    with open("accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # contacts.json (distractor)
    contacts = [
        {"contact_id": "ct_1", "name": "David Kim", "email": "dkim@regtech.com", "role": "CEO", "team": "Executive", "social_handle": "@davidkim"}
    ]
    with open("contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # Extra distractor file
    with open("README.md", "w") as f:
        f.write("# CompeteTrack workspace\n")

if __name__ == "__main__":
    build_env()
