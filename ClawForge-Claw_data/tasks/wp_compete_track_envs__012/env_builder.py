import os
import json
import random

random.seed(42)

def build_env():
    # --- competitors ---
    comp_dir = "data/competitors"
    os.makedirs(comp_dir, exist_ok=True)
    competitors = [
        {
            "competitor_id": "c001",
            "name": "DataFlow AI",
            "description": "AI/ML data platform",
            "sector": "AI/ML",
            "market_cap": 12000000000,
            "market_share": 8.5,
            "revenue": 3500000000,
            "user_count": 45000,
            "growth_rate": 22.3,
            "financials": {"rnd_budget": 700000000, "profit_margin": 0.12},
            "products": ["DataFlow Core", "FlowAnalytics", "AIPipeline"],
            "news": ["Announced EU expansion Q1 2025"]
        },
        {
            "competitor_id": "c002",
            "name": "CloudMajor",
            "description": "Enterprise cloud provider",
            "sector": "Cloud Computing",
            "market_cap": 450000000000,
            "market_share": 32.0,
            "revenue": 180000000000,
            "user_count": 2000000,
            "growth_rate": 15.1,
            "financials": {"rnd_budget": 25000000000, "profit_margin": 0.25},
            "products": ["CloudSuite", "StoragePro", "ComputeMax"],
            "news": ["Acquired startup in Q4 2024"]
        },
        {
            "competitor_id": "c003",
            "name": "SmartSaaS",
            "description": "Consumer SaaS platform",
            "sector": "Consumer SaaS",
            "market_cap": 8000000000,
            "market_share": 5.2,
            "revenue": 1200000000,
            "user_count": 300000,
            "growth_rate": 35.0,
            "financials": {"rnd_budget": 300000000, "profit_margin": 0.05},
            "products": ["SmartApp", "SmartCRM", "SmartAnalytics"],
            "news": ["Launched freemium tier"]
        },
        {
            "competitor_id": "c004",
            "name": "TechCorp",
            "description": "Enterprise software vendor",
            "sector": "Enterprise Software",
            "market_cap": 22000000000,
            "market_share": 12.8,
            "revenue": 6500000000,
            "user_count": 850000,
            "growth_rate": 18.7,
            "financials": {"rnd_budget": 1200000000, "profit_margin": 0.20},
            "products": ["TechSuite", "SecurityGaurd", "DevOpsHub"],
            "news": ["Partnership with GlobalReg"]
        }
    ]
    for comp in competitors:
        path = os.path.join(comp_dir, f"{comp['competitor_id']}.json")
        with open(path, "w") as f:
            json.dump(comp, f, indent=2)

    # --- policies ---
    pol_dir = "data/policies"
    os.makedirs(pol_dir, exist_ok=True)
    policies = [
        {
            "policy_id": "p001",
            "title": "EU Digital Markets Act Compliance",
            "description": "Regulation for digital gatekeepers",
            "policy_type": "antitrust",
            "jurisdiction": "EU",
            "status": "active",
            "impact_level": "high",
            "full_text": "Full text ...",
            "summary": "Targets large platforms with unfair practices.",
            "impact": {
                "affected_criteria": {"tier": "enterprise", "acquisition_source": "referral"},
                "estimated_revenue_risk_per_user": 20000
            },
            "changes": ["Article 5 enforcement", "Data sharing requirements"]
        },
        {
            "policy_id": "p002",
            "title": "Global Data Privacy Framework",
            "description": "International data transfer rules",
            "policy_type": "privacy",
            "jurisdiction": "Global",
            "status": "active",
            "impact_level": "medium",
            "full_text": "Full text ...",
            "summary": "Governs cross-border data flows.",
            "impact": {"affected_criteria": {"tier": "basic"}},
            "changes": ["Standard contractual clauses v2024"]
        },
        {
            "policy_id": "p003",
            "title": "US AI Transparency Act",
            "description": "AI model disclosure requirements",
            "policy_type": "ai_regulation",
            "jurisdiction": "US",
            "status": "proposed",
            "impact_level": "medium",
            "full_text": "Full text ...",
            "summary": "Requires companies to disclose AI usage.",
            "impact": {"affected_criteria": {"sector": "AI/ML"}},
            "changes": ["Algorithmic bias audits"]
        }
    ]
    for pol in policies:
        path = os.path.join(pol_dir, f"{pol['policy_id']}.json")
        with open(path, "w") as f:
            json.dump(pol, f, indent=2)

    # --- users ---
    users_dir = "data/users"
    os.makedirs(users_dir, exist_ok=True)

    # Helper to generate a user
    def make_user(uid, name, email, comp_id, tier, cohort, source, campaign, date, cost, channel, ltv):
        return {
            "user_id": uid,
            "name": name,
            "email": email,
            "competitor_id": comp_id,
            "tier": tier,
            "cohort": cohort,
            "acquisition_source": source,
            "acquisition_campaign": campaign,
            "acquisition_date": date,
            "acquisition_cost": cost,
            "initial_channel": channel,
            "lifetime_value": ltv
        }

    # 20 users, carefully crafted
    users = [
        # DataFlow AI users – target 3 should be correctly matched
        make_user("u001","Alice Johnson","alice.j@enterprise.com","c001","enterprise","cohort_q1_2025","referral","partner_program","2025-02-10",1200,"partner",15000),
        make_user("u002","Bob Williams","bob.w@startup.io","c001","enterprise","cohort_q1_2026","referral","partner_program","2026-01-15",1500,"partner",20000),
        make_user("u003","Carol Martinez","carol.m@cloudco.com","c001","enterprise","cohort_q2_2025","referral","partner_program","2025-04-01",1800,"partner",25000),
        # DataFlow AI users – wrong tier (premium) and wrong source
        make_user("u004","David Lee","david.lee@retail.net","c001","premium","cohort_q3_2024","referral","partner_program","2024-08-15",800,"partner",12000),
        make_user("u005","Emma Brown","emma.b@saas.co","c001","enterprise","cohort_q4_2025","organic","brand_awareness","2025-10-01",500,"website",5000),
        # DataFlow AI user with typo in tier (should be excluded)
        make_user("u006","Frank Zhao","frank.z@test.com","c001","Enterprise","cohort_q1_2026","referral","partner_program","2026-03-01",1100,"partner",18000),
        # DataFlow AI user missing acquisition_source field (corrupt record)
        {"user_id":"u007","name":"Grace Kim","email":"grace.k@test.com","competitor_id":"c001","tier":"enterprise","cohort":"cohort_q2_2025","acquisition_campaign":"spring_promo","acquisition_date":"2025-05-01","acquisition_cost":600,"initial_channel":"blog","lifetime_value":9000},
        # Other competitor users (CloudMajor)
        make_user("u008","Hank Miller","hank.m@cloudmajor.io","c002","enterprise","cohort_q1_2025","referral","partner_program","2025-02-20",1300,"partner",22000),
        make_user("u009","Ivy Chen","ivy.c@cloudmajor.io","c002","enterprise","cohort_q1_2026","referral","partner_program","2026-01-10",1600,"partner",28000),
        make_user("u010","Jack Wilson","jack.w@cloudmajor.io","c002","premium","cohort_q3_2024","paid_ads","linkedin_awareness","2024-07-01",900,"linkedin",8000),
        # SmartSaaS users
        make_user("u011","Karen Brown","karen.b@smartsaas.com","c003","basic","cohort_q4_2025","organic","brand_awareness","2025-11-01",100,"website",3000),
        make_user("u012","Leo Davis","leo.d@smartsaas.com","c003","enterprise","cohort_q2_2025","referral","partner_program","2025-04-15",1400,"partner",19000),
        # TechCorp users
        make_user("u013","Maria Garcia","maria.g@techcorp.com","c004","enterprise","cohort_q1_2025","referral","partner_program","2025-03-01",1700,"partner",24000),
        make_user("u014","Nathan Brown","nathan.b@techcorp.com","c004","premium","cohort_q1_2026","paid_ads","spring_promo","2026-02-01",1100,"google_ads",7000),
        # DataFlow AI user with wrong source (social, not referral)
        make_user("u015","Olivia Lee","olivia.l@test.com","c001","enterprise","cohort_q4_2025","social","linkedin_awareness","2025-12-01",800,"linkedin",10000),
        # Another eligible DataFlow AI user (enterprise, referral) – but already 3? Actually we have u001,u002,u003 as correct. Let's add one more to make it 4? No, keep 3.
        # Add a duplicate of u002? No, better keep 3. So above 3 are correct.
        # Additional DataFlow AI user with tier "enterprise" but source missing? already u007.
        # Let's add one more with tier enterprise and referral but different campaign to ensure count.
        # Actually we have exactly 3 correct. Good.
        # Add a couple more noise users
        make_user("u016","Patricia White","pat.w@test.com","c004","basic","cohort_q3_2024","referral","partner_program","2024-09-01",400,"partner",2000),
        make_user("u017","Quinn Black","quinn.b@test.com","c002","enterprise","cohort_q2_2025","organic","content_marketing","2025-06-01",300,"blog",6000),
    ]

    # Add the corrupt record u007 manually (it's already inserted above as dict)
    users.append({
        "user_id": "u018",
        "name": "Rachel Green",
        "email": "rachel.g@test.com",
        "competitor_id": "c001",
        "tier": "enterprise",
        "cohort": "cohort_q1_2025",
        "acquisition_source": "referral",
        "acquisition_campaign": "partner_program",
        "acquisition_date": "2025-01-15",
        "acquisition_cost": 1100,
        "initial_channel": "partner",
        # lifetime_value missing (corrupt)
    })

    for usr in users:
        uid = usr.get("user_id", f"u{random.randint(100,999)}")
        path = os.path.join(users_dir, f"{uid}.json")
        with open(path, "w") as f:
            json.dump(usr, f, indent=2)

    # --- accounts.json (distraction) ---
    accounts = {
        "accounts": [
            {"account_id":"acct001","name":"alice.j","display_name":"Alice Johnson","role":"Admin","email":"alice.j@enterprise.com","team":"Executive","permissions":["read","write"]},
            {"account_id":"acct002","name":"bob.w","display_name":"Bob Williams","role":"Viewer","email":"bob.w@startup.io","team":"Marketing","permissions":["read"]}
        ]
    }
    with open("data/accounts.json","w") as f:
        json.dump(accounts, f, indent=2)

    # --- contacts.json (distraction) ---
    contacts = {
        "contacts": [
            {"contact_id":"cont001","name":"David Kim","email":"dkim@regtech.com","role":"Compliance Director","team":"Legal","social_handle":"@davidkim"},
            {"contact_id":"cont002","name":"Emily Zhang","email":"emily.zhang@smartsaas.com","role":"CTO","team":"Engineering","social_handle":"@emilyzhang"}
        ]
    }
    with open("data/contacts.json","w") as f:
        json.dump(contacts, f, indent=2)

    # --- ops directory (intentionally present? Agent should create file inside) ---
    # Do NOT create ops/ directory; Agent must create it as part of output.

if __name__ == "__main__":
    build_env()
