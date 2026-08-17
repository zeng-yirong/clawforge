import os
import json
import random

def build_env():
    # 确保目录存在
    os.makedirs("data/competitors", exist_ok=True)
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("data/users", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---------- 竞品数据 ----------
    competitors = [
        {
            "competitor_id": "cloudmajor",
            "name": "CloudMajor",
            "sector": "Cloud Computing",
            "market_share": 0.35,
            "revenue": 3500000000,
            "growth_rate": 0.12
        },
        {
            "competitor_id": "dataflow_ai",
            "name": "DataFlow AI",
            "sector": "AI/ML",
            "market_share": 0.12,
            "revenue": 850000000,
            "growth_rate": 0.35
        },
        {
            "competitor_id": "smartsaas",
            "name": "SmartSaaS",
            "sector": "AI/ML",
            "market_share": 0.08,
            "revenue": 420000000,
            "growth_rate": 0.28
        },
        {
            "competitor_id": "techcorp",
            "name": "TechCorp",
            "sector": "Enterprise Software",
            "market_share": 0.15,
            "revenue": 1800000000,
            "growth_rate": 0.05
        },
        {
            "competitor_id": "aistartup",
            "name": "AIStartup",
            "sector": "AI/ML",
            "market_share": 0.05,
            "revenue": 150000000,
            "growth_rate": 0.45
        }
    ]
    for c in competitors:
        with open(f"data/competitors/{c['competitor_id']}.json", "w") as f:
            json.dump(c, f)

    # 干扰项：一个字段缺失的竞品 (market_share 缺失)
    corrupt_comp = {
        "competitor_id": "old_ai_co",
        "name": "OldAICo",
        "sector": "AI/ML",
        "revenue": 50000000,
        "growth_rate": 0.1
    }
    with open("data/competitors/old_ai_co.json", "w") as f:
        json.dump(corrupt_comp, f)

    # 干扰项：一个 JSON 格式错误的文件（无法解析）
    with open("data/competitors/bad_format.json", "w") as f:
        f.write("this is not json")

    # ---------- 政策数据 ----------
    policies = [
        {
            "policy_id": "eu_dma",
            "title": "EU Digital Markets Act Compliance",
            "impact_level": "high",
            "jurisdiction": "EU",
            "status": "active"
        },
        {
            "policy_id": "global_privacy",
            "title": "Global Data Privacy Framework",
            "impact_level": "medium",
            "jurisdiction": "Global",
            "status": "active"
        },
        {
            "policy_id": "us_ai_act",
            "title": "US AI Transparency Act",
            "impact_level": "high",
            "jurisdiction": "US",
            "status": "proposed"
        },
        {
            "policy_id": "eu_proposed",
            "title": "EU Proposed AI Regulation",
            "impact_level": "high",
            "jurisdiction": "EU",
            "status": "proposed"   # 未生效，不应计入
        },
        {
            "policy_id": "draft_policy",
            "title": "Draft Consumer Law",
            "impact_level": "medium",
            "jurisdiction": "EU",
            "status": "active"
        }
    ]
    for p in policies:
        with open(f"data/policies/{p['policy_id']}.json", "w") as f:
            json.dump(p, f)

    # ---------- 用户数据 ----------
    users = [
        {"user_id": "alice", "name": "Alice Johnson", "acquisition_source": "referral", "tier": "enterprise"},
        {"user_id": "bob", "name": "Bob Williams", "acquisition_source": "referral", "tier": "premium"},
        {"user_id": "carol", "name": "Carol Martinez", "acquisition_source": "paid_ads", "tier": "basic"},
        {"user_id": "david", "name": "David Lee", "acquisition_source": "referral", "tier": "basic"},
        {"user_id": "emma", "name": "Emma Brown", "acquisition_source": "organic", "tier": "enterprise"},
        # 干扰项：源字段带空格
        {"user_id": "frank", "name": "Frank Green", "acquisition_source": "referral ", "tier": "basic"},
        # 干扰项：源字段拼写错误
        {"user_id": "grace", "name": "Grace White", "acquisition_source": "refrral", "tier": "premium"},
        # 干扰项：源字段缺失
        {"user_id": "henry", "name": "Henry Black", "tier": "enterprise"}
    ]
    for u in users:
        with open(f"data/users/{u['user_id']}.json", "w") as f:
            json.dump(u, f)

    # 无关文件放在 ops 中迷惑 agent
    with open("ops/draft_notes.txt", "w") as f:
        f.write("Some draft notes, ignore.")
    os.makedirs("archived", exist_ok=True)
    with open("archived/old_competitors.json", "w") as f:
        f.write("[]")

    # 创建一个可选的字段说明文件（但prompt未要求）
    with open("data/fields_enum.json", "w") as f:
        json.dump({
            "competitor_sector": ["AI/ML", "Cloud Computing", "Consumer SaaS", "Enterprise Software"],
            "policy_status": ["active", "proposed"],
            "acquisition_source": ["organic", "paid_ads", "referral", "social"]
        }, f)
