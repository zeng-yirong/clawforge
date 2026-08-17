import os
import json
import random

def build_env():
    # 创建目录结构
    os.makedirs("data/competitors", exist_ok=True)
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("data/users", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---------- 竞品数据 ----------
    competitors = [
        {
            "competitor_id": "comp_001",
            "name": "CloudMajor",
            "description": "Leading cloud infrastructure provider",
            "sector": "Cloud Computing",
            "market_cap": 500000,
            "market_share": 0.25,
            "revenue": 200000,
            "user_count": 3000,
            "growth_rate": 0.12,
            "financials": {"gross_margin": 0.65, "r_d_spend": 50000},
            "products": ["CloudCompute", "CloudStorage"],
            "news": ["CloudMajor expands to APAC"]
        },
        {
            "competitor_id": "comp_002",
            "name": "DataFlow AI",
            "description": "AI/ML platform for enterprise",
            "sector": "AI/ML",
            "market_cap": 80000,
            "market_share": 0.08,
            "revenue": 30000,
            "user_count": 500,
            "growth_rate": 0.85,
            "financials": {"gross_margin": 0.55, "r_d_spend": 20000},
            "products": ["DataPipeline", "MLStudio"],
            "news": ["DataFlow AI raises Series B"]
        },
        {
            "competitor_id": "comp_003",
            "name": "SmartSaaS",
            "description": "Consumer SaaS productivity tools",
            "sector": "Consumer SaaS",
            "market_cap": 100000,
            "market_share": 0.15,
            "revenue": 80000,
            "user_count": 2000,
            "growth_rate": 0.25,
            "financials": {"gross_margin": 0.70, "r_d_spend": 12000},
            "products": ["SmartTask", "SmartNote"],
            "news": ["SmartSaaS acquires NoteFlow"]
        },
        {
            "competitor_id": "comp_004",
            "name": "TechCorp",
            "description": "Enterprise software conglomerate",
            "sector": "Enterprise Software",
            "market_cap": 300000,
            "market_share": 0.20,
            "revenue": 150000,
            "user_count": 4500,
            "growth_rate": 0.05,
            "financials": {"gross_margin": 0.60, "r_d_spend": 80000},
            "products": ["ERP", "CRM"],
            "news": ["TechCorp layoffs ongoing"]
        },
        # 诱饵：名字类似但不相干的竞品
        {
            "competitor_id": "comp_005",
            "name": "DataBricks Lite",
            "description": "Lightweight data analytics (unrelated to AI/ML)",
            "sector": "Data Analytics",
            "market_cap": 20000,
            "market_share": 0.02,
            "revenue": 5000,
            "user_count": 150,
            "growth_rate": -0.10,
            "financials": {"gross_margin": 0.30, "r_d_spend": 1000},
            "products": ["DB Light"],
            "news": ["DataBricks Lite pivoting"]
        }
    ]
    for comp in competitors:
        comp_id = comp["competitor_id"]
        with open(f"data/competitors/{comp_id}.json", "w") as f:
            json.dump(comp, f, indent=2)

    # ---------- 政策数据 ----------
    policies = [
        {
            "policy_id": "policy_001",
            "title": "EU Digital Markets Act Compliance",
            "description": "Regulation targeting large online platforms",
            "policy_type": "antitrust",
            "jurisdiction": "EU",
            "status": "active",
            "impact_level": "high",
            "full_text": "Full text here...",
            "summary": "EU DMA summary",
            "impact": {
                "affected_competitors": ["comp_002", "comp_005"],
                "compliance_cost": 100000
            },
            "changes": ["New data sharing requirements"]
        },
        # 干扰政策
        {
            "policy_id": "policy_002",
            "title": "US AI Transparency Act",
            "description": "US regulation on AI explainability",
            "policy_type": "ai_regulation",
            "jurisdiction": "US",
            "status": "proposed",
            "impact_level": "medium",
            "full_text": "Full text...",
            "summary": "US AI transparency summary",
            "impact": {
                "affected_competitors": ["comp_001"],
                "compliance_cost": 50000
            },
            "changes": ["Disclosure requirements"]
        }
    ]
    for pol in policies:
        pol_id = pol["policy_id"]
        with open(f"data/policies/{pol_id}.json", "w") as f:
            json.dump(pol, f, indent=2)

    # ---------- 用户数据 ----------
    # 构造用户列表，包含脏数据
    users = [
        {
            "user_id": "user_001",
            "name": "Alice Johnson",
            "email": "alice.j@enterprise.com",
            "competitor_id": "comp_002",
            "tier": "premium",
            "cohort": "cohort_q1_2025",
            "acquisition_source": "organic",
            "acquisition_campaign": "brand_awareness",
            "acquisition_date": "2025-01-15",
            "acquisition_cost": 120,
            "initial_channel": "website",
            "lifetime_value": 5000
        },
        {
            "user_id": "user_002",
            "name": "Bob Williams",
            "email": "bob.w@startup.io",
            "competitor_id": "comp_002",
            "tier": "basic",
            "cohort": "cohort_q2_2025",
            "acquisition_source": "paid_ads",
            "acquisition_campaign": "spring_promo",
            "acquisition_date": "2025-06-01",
            "acquisition_cost": 200,
            "initial_channel": "google_ads",
            "lifetime_value": 3000
        },
        {
            "user_id": "user_003",
            "name": "Carol Martinez",
            "email": "carol.m@cloudco.com",
            "competitor_id": "comp_002",
            "tier": "enterprise",
            "cohort": "cohort_q3_2024",
            "acquisition_source": "referral",
            "acquisition_campaign": "partner_program",
            "acquisition_date": "2024-08-20",
            "acquisition_cost": 280,
            "initial_channel": "partner",
            "lifetime_value": 8000
        },
        # comp_001 用户
        {
            "user_id": "user_004",
            "name": "David Lee",
            "email": "david.lee@retail.net",
            "competitor_id": "comp_001",
            "tier": "enterprise",
            "cohort": "cohort_q4_2025",
            "acquisition_source": "organic",
            "acquisition_campaign": "brand_awareness",
            "acquisition_date": "2025-11-01",
            "acquisition_cost": 150,
            "initial_channel": "website",
            "lifetime_value": 6000
        },
        {
            "user_id": "user_005",
            "name": "Emma Brown",
            "email": "emma.b@saas.co",
            "competitor_id": "comp_001",
            "tier": "premium",
            "cohort": "cohort_q1_2026",
            "acquisition_source": "paid_ads",
            "acquisition_campaign": "linkedin_awareness",
            "acquisition_date": "2026-02-10",
            "acquisition_cost": 250,
            "initial_channel": "linkedin",
            "lifetime_value": 7500
        },
        {
            "user_id": "user_006",
            "name": "Frank Green",
            "email": "frank.g@retail.net",
            "competitor_id": "comp_001",
            "tier": "basic",
            "cohort": "cohort_q3_2024",
            "acquisition_source": "referral",
            "acquisition_campaign": "partner_program",
            "acquisition_date": "2024-07-15",
            "acquisition_cost": 350,
            "initial_channel": "partner",
            "lifetime_value": 4000
        },
        # 脏数据：cost 缺失
        {
            "user_id": "user_007",
            "name": "Grace Hopper",
            "email": "grace.h@dataflow.ai",
            "competitor_id": "comp_002",
            "tier": "basic",
            "cohort": "cohort_q1_2025",
            "acquisition_source": "social",
            "acquisition_campaign": "content_marketing",
            "acquisition_date": "2025-03-01",
            # 故意缺失 acquisition_cost
            "initial_channel": "website",
            "lifetime_value": 2000
        },
        # 脏数据：cost 为非数字字符串
        {
            "user_id": "user_008",
            "name": "Henry Liu",
            "email": "henry.liu@dataflow.ai",
            "competitor_id": "comp_002",
            "tier": "premium",
            "cohort": "cohort_q2_2025",
            "acquisition_source": "paid_ads",
            "acquisition_campaign": "brand_awareness",
            "acquisition_date": "2025-04-20",
            "acquisition_cost": "N/A",
            "initial_channel": "google_ads",
            "lifetime_value": 3000
        },
        # 干扰用户（属于其他竞品）
        {
            "user_id": "user_009",
            "name": "Ivy Chen",
            "email": "ivy.c@smartsaas.com",
            "competitor_id": "comp_003",
            "tier": "basic",
            "cohort": "cohort_q1_2026",
            "acquisition_source": "organic",
            "acquisition_campaign": "content_marketing",
            "acquisition_date": "2026-01-01",
            "acquisition_cost": 90,
            "initial_channel": "blog",
            "lifetime_value": 1500
        }
    ]
    # 写入用户文件（每个用户单独一个文件）
    for u in users:
        uid = u["user_id"]
        with open(f"data/users/{uid}.json", "w") as f:
            json.dump(u, f, indent=2)

    # 可选：在ops下放一个占位文件，确保目录存在
    with open("ops/.gitkeep", "w") as f:
        pass

if __name__ == "__main__":
    build_env()
