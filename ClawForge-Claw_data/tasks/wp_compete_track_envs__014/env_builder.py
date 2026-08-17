import os
import json
import shutil

def build_env():
    # 创建数据目录
    os.makedirs("data/competitors", exist_ok=True)
    os.makedirs("data/users", exist_ok=True)
    os.makedirs("data/backup", exist_ok=True)  # 干扰目录

    # ---------- 竞品数据 ----------
    competitors = [
        {
            "competitor_id": "CM01",
            "name": "CloudMajor",
            "description": "Leading cloud infrastructure provider",
            "sector": "Cloud Computing",
            "market_cap": 500000,
            "market_share": 0.25,
            "revenue": 200000,
            "user_count": 15000,
            "growth_rate": 0.15,
            "financials": {"revenue_2024": 180000, "profit_margin": 0.12},
            "products": ["ComputeEngine", "StorageSuite", "NetHub"],
            "news": [{"date": "2025-03-01", "title": "New data center in Asia"}]
        },
        {
            "competitor_id": "DF02",
            "name": "DataFlow AI",
            "description": "AI/ML platform for enterprises",
            "sector": "AI/ML",
            "market_cap": 80000,
            "market_share": 0.08,
            "revenue": 45000,
            "user_count": 8000,
            "growth_rate": 0.25,
            "financials": {"revenue_2024": 36000, "profit_margin": 0.05},
            "products": ["DataPipeline", "ModelHub", "AutoML"],
            "news": [{"date": "2025-02-15", "title": "Series C funding of $50M"}]
        },
        {
            "competitor_id": "SS03",
            "name": "SmartSaaS",
            "description": "SaaS solutions for small businesses",
            "sector": "Consumer SaaS",
            "market_cap": 120000,
            "market_share": 0.12,
            "revenue": 60000,
            "user_count": 12000,
            "growth_rate": 0.30,
            "financials": {"revenue_2024": 46000, "profit_margin": 0.10},
            "products": ["SmartCRM", "SmartBilling", "SmartAnalytics"],
            "news": [{"date": "2025-01-20", "title": "Acquired WidgetCorp"}]
        },
        {
            "competitor_id": "TC04",
            "name": "TechCorp",
            "description": "Enterprise software giant",
            "sector": "Enterprise Software",
            "market_cap": 900000,
            "market_share": 0.40,
            "revenue": 400000,
            "user_count": 50000,
            "growth_rate": 0.10,
            "financials": {"revenue_2024": 380000, "profit_margin": 0.22},
            "products": ["ERP", "HRMS", "CRM"],
            "news": [{"date": "2025-03-10", "title": "Quarterly earnings beat estimates"}]
        }
    ]
    for comp in competitors:
        fname = f"data/competitors/{comp['competitor_id']}.json"
        with open(fname, "w") as f:
            json.dump(comp, f, indent=2)

    # 干扰：备份目录中放一个旧版竞品，增长率符合但无用户关联
    backup_comp = {
        "competitor_id": "OT99",
        "name": "OtherAI",
        "sector": "AI/ML",
        "growth_rate": 0.35,
        # 其他字段省略以节省时间，但标准 JSON
        "description": "Old backup, ignore",
        "market_cap": 0,
        "market_share": 0.0,
        "revenue": 0,
        "user_count": 0,
        "financials": {},
        "products": [],
        "news": []
    }
    with open("data/backup/OT99.json", "w") as f:
        json.dump(backup_comp, f, indent=2)

    # ---------- 用户数据 ----------
    users = [
        {
            "user_id": "U001",
            "name": "Alice Johnson",
            "email": "alice.j@enterprise.com",
            "competitor_id": "CM01",
            "tier": "enterprise",
            "cohort": "cohort_q1_2025",
            "acquisition_source": "organic",
            "acquisition_campaign": "brand_awareness",
            "acquisition_date": "2025-01-15",
            "acquisition_cost": 50,
            "initial_channel": "blog",
            "lifetime_value": 1200
        },
        {
            "user_id": "U002",
            "name": "Bob Williams",
            "email": "bob.w@startup.io",
            "competitor_id": "DF02",
            "tier": "premium",
            "cohort": "cohort_q1_2026",
            "acquisition_source": "referral",
            "acquisition_campaign": "partner_program",
            "acquisition_date": "2026-01-20",
            "acquisition_cost": 30,
            "initial_channel": "partner",
            "lifetime_value": 2500
        },
        {
            "user_id": "U003",
            "name": "Carol Martinez",
            "email": "carol.m@cloudco.com",
            "competitor_id": "SS03",
            "tier": "premium",
            "cohort": "cohort_q2_2025",
            "acquisition_source": "referral",
            "acquisition_campaign": "partner_program",
            "acquisition_date": "2025-04-10",
            "acquisition_cost": 20,
            "initial_channel": "partner",
            "lifetime_value": 3200
        },
        {
            "user_id": "U004",
            "name": "David Lee",
            "email": "david.lee@retail.net",
            "competitor_id": "TC04",
            "tier": "basic",
            "cohort": "cohort_q3_2024",
            "acquisition_source": "paid_ads",
            "acquisition_campaign": "spring_promo",
            "acquisition_date": "2024-07-01",
            "acquisition_cost": 100,
            "initial_channel": "google_ads",
            "lifetime_value": 800
        },
        {
            "user_id": "U005",
            "name": "Emma Brown",
            "email": "emma.b@saas.co",
            "competitor_id": "DF02",
            "tier": "premium",
            "cohort": "cohort_q4_2025",
            "acquisition_source": "referral",
            "acquisition_campaign": "partner_program",
            "acquisition_date": "2025-10-05",
            "acquisition_cost": 25,
            "initial_channel": "partner",
            "lifetime_value": 2800
        },
        {
            "user_id": "U006",
            "name": "Frank Green",
            "email": "frank.g@new.com",
            "competitor_id": "SS03",
            "tier": "enterprise",
            "cohort": "cohort_q2_2025",
            "acquisition_source": "social",
            "acquisition_campaign": "linkedin_awareness",
            "acquisition_date": "2025-06-01",
            "acquisition_cost": 60,
            "initial_channel": "linkedin",
            "lifetime_value": 1500
        },
        {
            "user_id": "U007",
            "name": "Grace White",
            "email": "grace.w@new.com",
            "competitor_id": "CM01",
            "tier": "premium",
            "cohort": "cohort_q1_2025",
            "acquisition_source": "organic",
            "acquisition_campaign": "brand_awareness",
            "acquisition_date": "2025-02-10",
            "acquisition_cost": 40,
            "initial_channel": "blog",
            "lifetime_value": 1800
        },
        {
            "user_id": "U008",
            "name": "Henry Black",
            "email": "henry.b@new.com",
            "competitor_id": "TC04",
            "tier": "premium",
            "cohort": "cohort_q3_2024",
            "acquisition_source": "referral",
            "acquisition_campaign": "partner_program",
            "acquisition_date": "2024-08-15",
            "acquisition_cost": 35,
            "initial_channel": "partner",
            "lifetime_value": 2000
        }
    ]
    for usr in users:
        fname = f"data/users/{usr['user_id']}.json"
        with open(fname, "w") as f:
            json.dump(usr, f, indent=2)

    # 干扰：accounts.json 和 contacts.json（标准格式，但本任务无关）
    accounts = [
        {
            "account_id": "A001",
            "name": "Alpha Corp",
            "display_name": "Alpha Corp",
            "role": "admin",
            "email": "admin@alphacorp.com",
            "team": "Engineering",
            "permissions": ["read", "write"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    contacts = [
        {
            "contact_id": "C001",
            "name": "David Kim",
            "email": "dkim@regtech.com",
            "role": "CEO",
            "team": "Executive",
            "social_handle": "@davidkim"
        }
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

if __name__ == "__main__":
    build_env()
