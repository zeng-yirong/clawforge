import os
import json

def build_env():
    # 确保 data 子目录存在
    os.makedirs("data/competitors", exist_ok=True)
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("data/users", exist_ok=True)
    os.makedirs("reports", exist_ok=True)  # 空目录，留给 agent 写结果

    # ---------- 竞品数据 ----------
    competitors = [
        {
            "competitor_id": "comp_001",
            "name": "CloudMajor",
            "description": "Leading cloud infrastructure provider",
            "sector": "Cloud Computing",
            "market_cap": 450000000000,
            "market_share": 0.32,
            "revenue": 180000000000,
            "user_count": 50000000,
            "growth_rate": 0.15,
            "financials": {"revenue_2024": 170000000000, "net_income": 40000000000},
            "products": ["DataLake", "Analytics Suite"],
            "news": ["CloudMajor launches new AI platform"]
        },
        {
            "competitor_id": "comp_002",
            "name": "DataFlow AI",
            "description": "Enterprise AI and data platform",
            "sector": "AI/ML",
            "market_cap": 85000000000,
            "market_share": 0.11,
            "revenue": 32000000000,
            "user_count": 12000000,
            "growth_rate": 0.45,
            "financials": {"revenue_2024": 28000000000, "net_income": 5500000000},
            "products": ["CRM", "Marketing Automation"],
            "news": ["DataFlow AI acquires smaller competitor"]
        },
        {
            "competitor_id": "comp_003",
            "name": "SmartSaaS",
            "description": "Vertical SaaS for healthcare",
            "sector": "Consumer SaaS",
            "market_cap": 15000000000,
            "market_share": 0.04,
            "revenue": 6000000000,
            "user_count": 3000000,
            "growth_rate": 0.22,
            "financials": {"revenue_2024": 5500000000, "net_income": 800000000},
            "products": ["EHR System", "Patient Portal"],
            "news": ["SmartSaaS expands into Europe"]
        },
        {
            "competitor_id": "comp_004",
            "name": "TechCorp",
            "description": "Enterprise software suite provider",
            "sector": "Enterprise Software",
            "market_cap": 220000000000,
            "market_share": 0.18,
            "revenue": 95000000000,
            "user_count": 25000000,
            "growth_rate": 0.08,
            "financials": {"revenue_2024": 90000000000, "net_income": 18000000000},
            "products": ["ERP", "HR Suite", "Supply Chain"],
            "news": ["TechCorp partners with EU regulators"]
        }
    ]
    for comp in competitors:
        with open(f"data/competitors/{comp['competitor_id']}.json", "w") as f:
            json.dump(comp, f, indent=2)

    # ---------- 政策数据 ----------
    policies = [
        {
            "policy_id": "pol_001",
            "title": "EU Digital Markets Act Compliance",
            "description": "Regulation targeting large platforms with significant market power in the EU",
            "policy_type": "antitrust",
            "jurisdiction": "EU",
            "status": "active",
            "impact_level": "high",
            "full_text": "Full text of DMA...",
            "summary": "Imposes obligations on gatekeeper platforms",
            "impact": {
                "affected_competitors": ["comp_001", "comp_002"],
                "market_share_threshold": 0.15,
                "penalty_percent": 0.1
            },
            "changes": ["New compliance requirements for data sharing"]
        },
        {
            "policy_id": "pol_002",
            "title": "Global Data Privacy Framework",
            "description": "International data transfer mechanism",
            "policy_type": "privacy",
            "jurisdiction": "Global",
            "status": "active",
            "impact_level": "medium",
            "full_text": "Full text of GDPF...",
            "summary": "Governs cross-border data flows",
            "impact": {
                "affected_competitors": ["comp_003", "comp_004"],
                "compliance_cost": 5000000
            },
            "changes": ["Updated SCCs"]
        },
        {
            "policy_id": "pol_003",
            "title": "US AI Transparency Act",
            "description": "Requires disclosure of AI-generated content",
            "policy_type": "ai_regulation",
            "jurisdiction": "US",
            "status": "proposed",
            "impact_level": "high",
            "full_text": "Full text of AITA...",
            "summary": "Transparency labeling for AI outputs",
            "impact": {
                "affected_competitors": ["comp_002", "comp_004"],
                "effective_date": "2027-01-01"
            },
            "changes": ["Labeling requirements"]
        },
        {
            "policy_id": "pol_004",
            "title": "EU Digital Markets Act Compliance (Duplicate)",
            "description": "Duplicate entry with same title but different data (干扰项)",
            "policy_type": "antitrust",
            "jurisdiction": "EU",
            "status": "active",
            "impact_level": "low",
            "full_text": "Full text...",
            "summary": "Low impact version",
            "impact": {"affected_competitors": []},
            "changes": []
        }
    ]
    for pol in policies:
        with open(f"data/policies/{pol['policy_id']}.json", "w") as f:
            json.dump(pol, f, indent=2)

    # ---------- 用户数据 ----------
    # 为受影响竞品（comp_001, comp_002）构造用户，确保每个竞品 top acquisition_source 唯一
    users = []
    # comp_001 用户：referral 出现 3 次，organic 2次，paid_ads 1次 → top = referral
    for i in range(3):
        users.append({
            "user_id": f"user_{100+i}",
            "name": f"Alice {i}",
            "email": f"alice{i}@enterprise.com",
            "competitor_id": "comp_001",
            "tier": "enterprise",
            "cohort": "cohort_q1_2025",
            "acquisition_source": "referral",
            "acquisition_campaign": "partner_program",
            "acquisition_date": "2025-02-10",
            "acquisition_cost": 500,
            "initial_channel": "partner",
            "lifetime_value": 12000
        })
    for i in range(2):
        users.append({
            "user_id": f"user_{110+i}",
            "name": f"Bob {i}",
            "email": f"bob{i}@startup.io",
            "competitor_id": "comp_001",
            "tier": "premium",
            "cohort": "cohort_q2_2025",
            "acquisition_source": "organic",
            "acquisition_campaign": "content_marketing",
            "acquisition_date": "2025-03-15",
            "acquisition_cost": 0,
            "initial_channel": "blog",
            "lifetime_value": 8000
        })
    users.append({
        "user_id": "user_120",
        "name": "Carol M",
        "email": "carol.m@cloudco.com",
        "competitor_id": "comp_001",
        "tier": "basic",
        "cohort": "cohort_q3_2024",
        "acquisition_source": "paid_ads",
        "acquisition_campaign": "spring_promo",
        "acquisition_date": "2024-08-20",
        "acquisition_cost": 200,
        "initial_channel": "google_ads",
        "lifetime_value": 3000
    })
    # comp_002 用户：paid_ads 出现 4 次，organic 1 次 → top = paid_ads
    for i in range(4):
        users.append({
            "user_id": f"user_{200+i}",
            "name": f"David {i}",
            "email": f"david{i}@retail.net",
            "competitor_id": "comp_002",
            "tier": "premium",
            "cohort": "cohort_q4_2025",
            "acquisition_source": "paid_ads",
            "acquisition_campaign": "linkedin_awareness",
            "acquisition_date": "2025-11-05",
            "acquisition_cost": 300,
            "initial_channel": "linkedin",
            "lifetime_value": 15000
        })
    users.append({
        "user_id": "user_210",
        "name": "Emma B",
        "email": "emma.b@saas.co",
        "competitor_id": "comp_002",
        "tier": "basic",
        "cohort": "cohort_q1_2026",
        "acquisition_source": "organic",
        "acquisition_campaign": "brand_awareness",
        "acquisition_date": "2026-01-20",
        "acquisition_cost": 0,
        "initial_channel": "website",
        "lifetime_value": 5000
    })
    # 干扰用户：属于 comp_003 和 comp_004（这些竞品不在受影响列表中，不应出现在报告中）
    for i in range(2):
        users.append({
            "user_id": f"user_{300+i}",
            "name": f"Frank {i}",
            "email": f"frank{i}@test.com",
            "competitor_id": "comp_003",
            "tier": "enterprise",
            "cohort": "cohort_q1_2025",
            "acquisition_source": "social",
            "acquisition_campaign": "linkedin_awareness",
            "acquisition_date": "2025-02-01",
            "acquisition_cost": 100,
            "initial_channel": "linkedin",
            "lifetime_value": 6000
        })
    for i in range(2):
        users.append({
            "user_id": f"user_{400+i}",
            "name": f"Grace {i}",
            "email": f"grace{i}@test.com",
            "competitor_id": "comp_004",
            "tier": "premium",
            "cohort": "cohort_q2_2025",
            "acquisition_source": "referral",
            "acquisition_campaign": "partner_program",
            "acquisition_date": "2025-04-10",
            "acquisition_cost": 250,
            "initial_channel": "partner",
            "lifetime_value": 9000
        })
    for u in users:
        with open(f"data/users/{u['user_id']}.json", "w") as f:
            json.dump(u, f, indent=2)

    # 干扰文件：accounts.json 和 contacts.json（agent 不需要处理）
    accounts = [
        {"account_id": "acc_001", "name": "Sarah", "display_name": "Sarah Chen", "role": "Compliance Director", "email": "sarah.chen@techcorp.com", "team": "Legal", "permissions": ["read", "write"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)
    contacts = [
        {"contact_id": "cont_001", "name": "David Kim", "email": "dkim@regtech.com", "role": "CEO", "team": "Executive", "social_handle": "@davidkim"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
