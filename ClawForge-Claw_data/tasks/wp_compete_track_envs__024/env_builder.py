import os
import json
import random

def build_env():
    # 用户数据目录
    os.makedirs("data/users", exist_ok=True)

    # 有效用户（每个渠道一个）
    users = [
        {
            "user_id": "user_001",
            "name": "Alice Johnson",
            "email": "alice.j@enterprise.com",
            "competitor_id": "comp_001",
            "tier": "basic",
            "cohort": "cohort_q1_2025",
            "acquisition_source": "organic",
            "acquisition_campaign": "brand_awareness",
            "acquisition_date": "2025-01-15",
            "acquisition_cost": 1000,
            "initial_channel": "website",
            "lifetime_value": 5000
        },
        {
            "user_id": "user_002",
            "name": "Bob Williams",
            "email": "bob.w@startup.io",
            "competitor_id": "comp_002",
            "tier": "premium",
            "cohort": "cohort_q2_2025",
            "acquisition_source": "paid_ads",
            "acquisition_campaign": "spring_promo",
            "acquisition_date": "2025-03-10",
            "acquisition_cost": 2000,
            "initial_channel": "google_ads",
            "lifetime_value": 3000
        },
        {
            "user_id": "user_003",
            "name": "Carol Martinez",
            "email": "carol.m@cloudco.com",
            "competitor_id": "comp_003",
            "tier": "enterprise",
            "cohort": "cohort_q3_2024",
            "acquisition_source": "referral",
            "acquisition_campaign": "partner_program",
            "acquisition_date": "2024-08-20",
            "acquisition_cost": 1500,
            "initial_channel": "partner",
            "lifetime_value": 1000
        },
        {
            "user_id": "user_004",
            "name": "David Lee",
            "email": "david.lee@retail.net",
            "competitor_id": "comp_004",
            "tier": "basic",
            "cohort": "cohort_q4_2025",
            "acquisition_source": "social",
            "acquisition_campaign": "linkedin_awareness",
            "acquisition_date": "2025-06-01",
            "acquisition_cost": 800,
            "initial_channel": "linkedin",
            "lifetime_value": 400
        }
    ]

    # 脏数据：acquisition_source 为空字符串（无效）
    dirty_user = {
        "user_id": "user_005",
        "name": "Emma Brown",
        "email": "emma.b@saas.co",
        "competitor_id": "comp_001",
        "tier": "premium",
        "cohort": "cohort_q1_2026",
        "acquisition_source": "",
        "acquisition_campaign": "content_marketing",
        "acquisition_date": "2026-01-10",
        "acquisition_cost": 500,
        "initial_channel": "blog",
        "lifetime_value": 200
    }
    users.append(dirty_user)

    # 写入每个用户
    for u in users:
        fname = f"data/users/{u['user_id']}.json"
        with open(fname, "w") as f:
            json.dump(u, f, indent=2)

    # 创建竞品和政策的干扰目录（空壳文件，不影响任务）
    os.makedirs("data/competitors", exist_ok=True)
    os.makedirs("data/policies", exist_ok=True)

    # 写一个简单的竞品文件
    comp_sample = {
        "competitor_id": "comp_001",
        "name": "CloudMajor",
        "sector": "Cloud Computing",
        "market_cap": 500000000000,
        "market_share": 0.35,
        "revenue": 150000000000,
        "user_count": 12000000,
        "growth_rate": 0.22,
        "financials": {"revenue_2024": 140000000000},
        "products": ["CloudSuite", "AI Platform"],
        "news": ["Expanded data center in EU"]
    }
    with open("data/competitors/comp_001.json", "w") as f:
        json.dump(comp_sample, f, indent=2)

    policy_sample = {
        "policy_id": "pol_001",
        "title": "EU Digital Markets Act Compliance",
        "policy_type": "antitrust",
        "jurisdiction": "EU",
        "status": "active",
        "impact_level": "high",
        "summary": "Regulation targeting large platform gatekeepers.",
        "impact": {"affected_sectors": ["Cloud Computing", "Consumer SaaS"]}
    }
    with open("data/policies/pol_001.json", "w") as f:
        json.dump(policy_sample, f, indent=2)

if __name__ == "__main__":
    build_env()
