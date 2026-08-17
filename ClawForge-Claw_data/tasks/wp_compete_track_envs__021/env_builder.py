import os
import json
import random
random.seed(42)

def build_env():
    # 基础目录
    os.makedirs("data/competitors", exist_ok=True)
    os.makedirs("data/users", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 定义竞品数据 (只保留活跃的)
    competitors = {
        "cloud_major": {
            "competitor_id": "cloud_major",
            "name": "CloudMajor",
            "description": "Leading cloud infrastructure provider",
            "sector": "Cloud Computing",
            "market_cap": 5000,
            "market_share": 0.25,
            "revenue": 3000,
            "growth_rate": 0.15,
            "financials": {"net_income": 800, "r_d_spend": 400},
            "products": ["CloudCompute", "CloudStorage"],
            "news": ["Q1 earnings beat expectations"],
            "status": "active"
        },
        "dataflow_ai": {
            "competitor_id": "dataflow_ai",
            "name": "DataFlow AI",
            "description": "AI/ML platform for enterprise",
            "sector": "AI/ML",
            "market_cap": 3200,
            "market_share": 0.18,
            "revenue": 2100,
            "growth_rate": 0.22,
            "financials": {"net_income": 450, "r_d_spend": 600},
            "products": ["DataFlow Engine", "AI Studio"],
            "news": ["New partnership announced"],
            "status": "active"
        },
        "smartsaas": {
            "competitor_id": "smartsaas",
            "name": "SmartSaaS",
            "description": "Consumer SaaS tools",
            "sector": "Consumer SaaS",
            "market_cap": 1800,
            "market_share": 0.10,
            "revenue": 1200,
            "growth_rate": 0.08,
            "financials": {"net_income": 200, "r_d_spend": 150},
            "products": ["SmartCRM", "SmartAnalytics"],
            "news": ["User growth slowing"],
            "status": "active"
        },
        "techcorp": {
            "competitor_id": "techcorp",
            "name": "TechCorp",
            "description": "Enterprise software giant",
            "sector": "Enterprise Software",
            "market_cap": 7000,
            "market_share": 0.32,
            "revenue": 5200,
            "growth_rate": 0.18,
            "financials": {"net_income": 1200, "r_d_spend": 900},
            "products": ["TechERP", "TechCRM"],
            "news": ["Acquired mid-size competitor"],
            "status": "active"
        }
    }

    # 写竞品文件
    for cid, cdata in competitors.items():
        with open(f"data/competitors/{cid}.json", "w") as f:
            json.dump(cdata, f, indent=2)

    # 干扰文件：旧备份（status deprecated）
    backup = competitors["cloud_major"].copy()
    backup["status"] = "deprecated"
    backup["market_cap"] = 9999  # 与活跃版本不同
    with open("data/competitors/backup_cloud_major.json", "w") as f:
        json.dump(backup, f, indent=2)

    # 干扰文件：README
    with open("data/competitors/README.md", "w") as f:
        f.write("# Competitors data dump\nThis directory contains competitor snapshots.\n")

    # 用户定义：为每个活跃竞品分配若干用户
    user_templates = [
        ("Alice Johnson", "alice.j@enterprise.com", "enterprise", "cohort_q1_2025", "organic", "brand_awareness", "2025-01-15", 0, "website", 1200),
        ("Bob Williams", "bob.w@startup.io", "basic", "cohort_q1_2026", "paid_ads", "spring_promo", "2026-02-20", 50, "google_ads", 800),
        ("Carol Martinez", "carol.m@cloudco.com", "premium", "cohort_q2_2025", "referral", "partner_program", "2025-04-10", 0, "partner", 2000),
        ("David Lee", "david.lee@retail.net", "enterprise", "cohort_q3_2024", "social", "linkedin_awareness", "2024-08-05", 30, "linkedin", 1500),
        ("Emma Brown", "emma.b@saas.co", "basic", "cohort_q4_2025", "organic", "content_marketing", "2025-11-12", 0, "blog", 600),
        ("Frank Green", "frank.g@cloudmajor.io", "premium", "cohort_q1_2025", "paid_ads", "brand_awareness", "2025-02-01", 40, "google_ads", 1800),
        ("Grace Lee", "grace.lee@dataflow.ai", "enterprise", "cohort_q2_2025", "referral", "partner_program", "2025-05-15", 0, "partner", 2200),
        ("Henry Wang", "henry.w@smartsaas.com", "basic", "cohort_q3_2024", "social", "linkedin_awareness", "2024-09-20", 25, "linkedin", 700),
        ("Ivy Chen", "ivy.c@techcorp.com", "enterprise", "cohort_q4_2025", "organic", "content_marketing", "2025-12-01", 0, "blog", 1900),
        ("Jack Davis", "jack.d@startup.io", "premium", "cohort_q1_2026", "paid_ads", "spring_promo", "2026-03-10", 60, "google_ads", 2100),
        ("Karen Wilson", "karen.w@cloudco.com", "basic", "cohort_q2_2025", "referral", "partner_program", "2025-06-25", 0, "partner", 950),
        ("Leo Martinez", "leo.m@retail.net", "enterprise", "cohort_q3_2024", "social", "brand_awareness", "2024-10-05", 35, "linkedin", 1600),
        ("Mia Zhang", "mia.z@saas.co", "premium", "cohort_q4_2025", "organic", "content_marketing", "2025-11-30", 0, "blog", 1300),
        ("Noah Kim", "noah.k@cloudmajor.io", "basic", "cohort_q1_2025", "paid_ads", "brand_awareness", "2025-01-20", 45, "google_ads", 550),
        ("Olivia Brown", "olivia.b@dataflow.ai", "enterprise", "cohort_q2_2025", "referral", "partner_program", "2025-07-01", 0, "partner", 2500),
        ("Peter Jones", "peter.j@smartsaas.com", "basic", "cohort_q3_2024", "social", "linkedin_awareness", "2024-11-15", 20, "linkedin", 400),
        ("Quinn Smith", "quinn.s@techcorp.com", "premium", "cohort_q4_2025", "organic", "content_marketing", "2025-12-15", 0, "blog", 1700),
        ("Rachel Adams", "rachel.a@techcorp.com", "enterprise", "cohort_q1_2025", "paid_ads", "spring_promo", "2025-03-01", 55, "google_ads", 2000),
        ("Sam Taylor", "sam.t@cloudmajor.io", "basic", "cohort_q2_2025", "referral", "partner_program", "2025-08-20", 0, "partner", 500),
        ("Tina Chen", "tina.c@dataflow.ai", "premium", "cohort_q3_2024", "social", "brand_awareness", "2024-12-10", 30, "linkedin", 1800),
        ("Uma Patel", "uma.p@techcorp.com", "enterprise", "cohort_q4_2025", "organic", "content_marketing", "2025-09-05", 0, "blog", 1400),
        ("Victor Lee", "victor.l@techcorp.com", "basic", "cohort_q1_2026", "paid_ads", "spring_promo", "2026-01-05", 70, "google_ads", 650)
    ]

    # 分配用户到竞品 (竞争关系: cloud_major, dataflow_ai, smartsaas, techcorp)
    # 手动分配确保最终计数: cloud_major 5, dataflow_ai 4, smartsaas 3, techcorp 6
    assignments = {
        "cloud_major": [0, 4, 9, 13, 18],   # 索引
        "dataflow_ai": [1, 6, 14, 19],
        "smartsaas": [2, 7, 15],
        "techcorp": [3, 8, 11, 16, 17, 20]   # 注意：索引21会被忽略作为干扰
    }

    # 干扰用户 - 不关联任何活跃竞品
    extra_user = {
        "user_id": "user_extra",
        "name": "Zara White",
        "email": "zara.w@ghost.com",
        "competitor_id": "non_existent",
        "tier": "basic",
        "cohort": "cohort_q1_2025",
        "acquisition_source": "organic",
        "acquisition_campaign": "brand_awareness",
        "acquisition_date": "2025-01-01",
        "acquisition_cost": 10,
        "initial_channel": "blog",
        "lifetime_value": 100
    }
    with open(f"data/users/user_extra.json", "w") as f:
        json.dump(extra_user, f, indent=2)

    user_idx = 0
    for comp_id, indices in assignments.items():
        for idx in indices:
            t = user_templates[idx]
            user = {
                "user_id": f"user_{user_idx:03d}",
                "name": t[0],
                "email": t[1],
                "competitor_id": comp_id,
                "tier": t[2],
                "cohort": t[3],
                "acquisition_source": t[4],
                "acquisition_campaign": t[5],
                "acquisition_date": t[6],
                "acquisition_cost": t[7],
                "initial_channel": t[8],
                "lifetime_value": t[9]
            }
            with open(f"data/users/user_{user_idx:03d}.json", "w") as f:
                json.dump(user, f, indent=2)
            user_idx += 1

    print("Environment built: data/competitors (4 active + 1 deprecated + 1 readme), data/users (18 valid + 1 extra), ops/ ready.")

if __name__ == "__main__":
    build_env()
