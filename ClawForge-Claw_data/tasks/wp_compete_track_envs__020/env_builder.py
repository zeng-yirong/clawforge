import os
import json
import random
from datetime import datetime, timedelta

def build_env():
    # ----- 竞品数据 -----
    competitors = [
        {"competitor_id": "cm001", "name": "CloudMajor",          "sector": "Cloud Computing", "market_cap": 450_000_000_000, "market_share": 0.32, "revenue": 90_000_000_000, "user_count": 12000, "growth_rate": 0.18, "financials": {"revenue_2024": 78e9}, "products": ["CloudCore","AI Suite"], "news": ["New data center in EU"]},
        {"competitor_id": "df002", "name": "DataFlow AI",         "sector": "AI/ML",           "market_cap": 120_000_000_000, "market_share": 0.08, "revenue": 25_000_000_000, "user_count": 8000,  "growth_rate": 0.35, "financials": {"revenue_2024": 18e9}, "products": ["DataLake","MLOps"], "news": ["Raised $500M"]},
        {"competitor_id": "ss003", "name": "SmartSaaS",           "sector": "Consumer SaaS",   "market_cap": 85_000_000_000,  "market_share": 0.05, "revenue": 12_000_000_000, "user_count": 5000,  "growth_rate": 0.10, "financials": {"revenue_2024": 10e9}, "products": ["SmartCRM","Analytics"], "news": []},
        {"competitor_id": "tc004", "name": "TechCorp",            "sector": "Enterprise Software", "market_cap":200_000_000_000,"market_share":0.15,"revenue":45_000_000_000,"user_count":15000,"growth_rate":0.22,"financials":{"revenue_2024":38e9},"products":["ERP","IoT"],"news":["Acquired startup"]},
        # 干扰项：名字拼写近似但不同
        {"competitor_id": "xx005", "name": "CloudMajorr",         "sector": "Cloud Computing", "market_cap": 1_000_000_000, "market_share": 0.01, "revenue": 200_000_000, "user_count": 300, "growth_rate": 0.02, "financials": {}, "products": [], "news": []},
    ]
    os.makedirs("data/competitors", exist_ok=True)
    for c in competitors:
        with open(f"data/competitors/{c['competitor_id']}.json", "w") as f:
            json.dump(c, f, indent=2)

    # ----- 用户数据 -----
    # 构造一批用户，其中属于CloudMajor (cm001) 且 2025年 referral 的有2个
    users = []
    user_counter = 0

    def make_user(comp_id, source, date_str, cost, tier="basic", cohort="cohort_q1_2025", campaign="partner_program", channel="partner", ltv=5000):
        nonlocal user_counter
        user_counter += 1
        uid = f"u{user_counter:03d}"
        return {
            "user_id": uid,
            "name": f"User {uid}",
            "email": f"{uid}@test.com",
            "competitor_id": comp_id,
            "tier": tier,
            "cohort": cohort,
            "acquisition_source": source,
            "acquisition_campaign": campaign,
            "acquisition_date": date_str,
            "acquisition_cost": cost,
            "initial_channel": channel,
            "lifetime_value": ltv
        }

    # CloudMajor 2025 referral 两个（答案）
    users.append(make_user("cm001", "referral", "2025-03-15", 500, campaign="partner_program", channel="partner"))
    users.append(make_user("cm001", "referral", "2025-07-22", 800, campaign="partner_program", channel="partner"))

    # CloudMajor 其他年份/渠道 干扰
    users.append(make_user("cm001", "organic",   "2025-01-10", 0,    campaign="brand_awareness", channel="website"))
    users.append(make_user("cm001", "paid_ads",  "2024-11-05", 1200, campaign="spring_promo",    channel="google_ads"))
    users.append(make_user("cm001", "referral",  "2024-12-01", 300,  campaign="partner_program", channel="partner"))
    users.append(make_user("cm001", "social",    "2026-02-14", 200,  campaign="linkedin_awareness", channel="linkedin"))

    # 其他竞品的用户
    for comp_id in ["df002", "ss003", "tc004", "xx005"]:
        users.append(make_user(comp_id, "referral", "2025-06-01", 400))
        users.append(make_user(comp_id, "organic",  "2025-03-20", 0))
        users.append(make_user(comp_id, "paid_ads", "2025-09-10", 900))

    # 添加一些脏数据：缺少acquisition_cost字段（另一个用户）
    dirty_user = {
        "user_id": "u099",
        "name": "Dirty User",
        "email": "dirty@test.com",
        "competitor_id": "cm001",
        "tier": "basic",
        "cohort": "cohort_q1_2025",
        "acquisition_source": "referral",
        "acquisition_campaign": "partner_program",
        "acquisition_date": "2025-04-01",
        # 缺少 acquisition_cost
        "initial_channel": "partner",
        "lifetime_value": 6000
    }
    users.append(dirty_user)

    # 添加一个日期格式异常的用户
    bad_date_user = make_user("cm001", "referral", "2025/01/01", 200, campaign="partner_program", channel="partner")
    bad_date_user["user_id"] = "u100"
    users.append(bad_date_user)

    os.makedirs("data/users", exist_ok=True)
    for u in users:
        with open(f"data/users/{u['user_id']}.json", "w") as f:
            json.dump(u, f, indent=2)

    # ----- 可选其他文件 (政策、账户等，作为干扰) -----
    policies = [
        {"policy_id":"p001","title":"EU Digital Markets Act Compliance","description":"...","policy_type":"antitrust","jurisdiction":"EU","status":"active","impact_level":"high","full_text":"...","summary":"...","impact":{"affected_competitors":["cm001","tc004"]},"changes":[]},
        {"policy_id":"p002","title":"Global Data Privacy Framework","description":"...","policy_type":"privacy","jurisdiction":"Global","status":"proposed","impact_level":"medium","full_text":"...","summary":"...","impact":{"affected_competitors":["df002","ss003"]},"changes":[]},
    ]
    os.makedirs("data/policies", exist_ok=True)
    for p in policies:
        with open(f"data/policies/{p['policy_id']}.json", "w") as f:
            json.dump(p, f, indent=2)

    accounts = {"accounts": [{"account_id":"a001","name":"Leo","display_name":"Leo","role":"Marketing","email":"leo@company.com","team":"Marketing","permissions":["read"]}]}
    with open("data/accounts.json","w") as f:
        json.dump(accounts, f, indent=2)

    contacts = {"contacts": [{"contact_id":"c001","name":"Sarah Chen","email":"sarah.chen@techcorp.com","role":"CEO","team":"Executive","social_handle":"@sarahchen"}]}
    with open("data/contacts.json","w") as f:
        json.dump(contacts, f, indent=2)

    # 额外干扰目录/文件
    os.makedirs("backup", exist_ok=True)
    with open("backup/temp.log","w") as f:
        f.write("irrelevant")
    with open("README.txt","w") as f:
        f.write("This is a test environment.")

if __name__ == "__main__":
    build_env()
