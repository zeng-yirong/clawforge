import os
import json
import random

def build_env():
    # 创建目录结构
    dirs = ["data/competitors", "data/policies", "data/users", "reports"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 竞品数据 (四个竞品，两个受 US AI Transparency Act 高影响)
    competitors = {
        "cloudmajor": {
            "competitor_id": "cm1",
            "name": "CloudMajor",
            "description": "Leading cloud provider",
            "sector": "Cloud Computing",
            "market_cap": 500000,
            "market_share": 0.25,
            "revenue": 120000,
            "user_count": 2000000,
            "growth_rate": 12.5,
            "financials": {"revenue_2024": 110000},
            "products": ["cloud_storage", "compute", "ai_platform"],
            "news": ["new region launched"]
        },
        "dataflow_ai": {
            "competitor_id": "da1",
            "name": "DataFlow AI",
            "description": "AI/ML platform",
            "sector": "AI/ML",
            "market_cap": 30000,
            "market_share": 0.18,
            "revenue": 45000,
            "user_count": 800000,
            "growth_rate": 28.3,
            "financials": {"revenue_2024": 38000},
            "products": ["data_pipeline", "model_training", "inference_api"],
            "news": ["series D funding"]
        },
        "smartsaas": {
            "competitor_id": "sm1",
            "name": "SmartSaaS",
            "description": "Enterprise SaaS",
            "sector": "Enterprise Software",
            "market_cap": 20000,
            "market_share": 0.12,
            "revenue": 32000,
            "user_count": 500000,
            "growth_rate": 15.2,
            "financials": {"revenue_2024": 28000},
            "products": ["crm", "analytics"],
            "news": ["new partnership"]
        },
        "techcorp": {
            "competitor_id": "tc1",
            "name": "TechCorp",
            "description": "Consumer SaaS",
            "sector": "Consumer SaaS",
            "market_cap": 10000,
            "market_share": 0.08,
            "revenue": 15000,
            "user_count": 300000,
            "growth_rate": 5.1,
            "financials": {"revenue_2024": 14000},
            "products": ["productivity_app"],
            "news": ["layoff announcement"]
        }
    }

    # 写入竞品文件 (每个竞品一个文件)
    for key, data in competitors.items():
        fpath = f"data/competitors/{key}.json"
        with open(fpath, "w") as f:
            json.dump(data, f, indent=2)

    # 创建干扰文件：一个旧版本备份，一个格式错误的文件
    old_data = competitors["cloudmajor"].copy()
    old_data["market_share"] = 0.20  # 旧值
    with open("data/competitors/cloudmajor_backup.json", "w") as f:
        json.dump(old_data, f, indent=2)

    # 格式错误文件 (非 JSON)
    with open("data/competitors/corrupt.txt", "w") as f:
        f.write("this is not json")

    # 政策数据
    policies = {
        "eu_dma": {
            "policy_id": "p1",
            "title": "EU Digital Markets Act Compliance",
            "description": "Regulation for digital gatekeepers",
            "policy_type": "antitrust",
            "jurisdiction": "EU",
            "status": "active",
            "impact_level": "high",
            "full_text": "...",
            "summary": "Obligations for large platforms",
            "impact": {
                "affected_competitors": ["cm1", "sm1"],
                "market_restrictions": "gatekeeper rules"
            },
            "changes": ["data sharing requirements"]
        },
        "us_ai_transparency": {
            "policy_id": "p2",
            "title": "US AI Transparency Act",
            "description": "Requires disclosure of AI usage",
            "policy_type": "ai_regulation",
            "jurisdiction": "US",
            "status": "active",
            "impact_level": "high",
            "full_text": "...",
            "summary": "AI disclosure requirements",
            "impact": {
                "affected_competitors": ["da1", "tc1"],
                "key_requirement": "public AI model registry"
            },
            "changes": ["training data disclosure"]
        },
        "global_privacy": {
            "policy_id": "p3",
            "title": "Global Data Privacy Framework",
            "description": "International data transfer rules",
            "policy_type": "privacy",
            "jurisdiction": "Global",
            "status": "proposed",
            "impact_level": "medium",
            "full_text": "...",
            "summary": "Cross-border data rules",
            "impact": {
                "affected_competitors": [],
                "scope": "all companies"
            },
            "changes": ["standard contractual clauses"]
        }
    }

    # 写入政策文件
    for key, data in policies.items():
        fpath = f"data/policies/{key}.json"
        with open(fpath, "w") as f:
            json.dump(data, f, indent=2)

    # 添加干扰政策：一个过期的政策（同名但旧版本）
    old_policy = policies["us_ai_transparency"].copy()
    old_policy["status"] = "repealed"
    old_policy["impact"]["affected_competitors"] = ["cm1"]  # 旧版本影响不同
    with open("data/policies/us_ai_transparency_old.json", "w") as f:
        json.dump(old_policy, f, indent=2)

    # 用户数据 (简单几组, 作为背景)
    users = [
        {"user_id": "u1", "name": "Alice Johnson", "email": "alice.j@enterprise.com", "competitor_id": "cm1", "tier": "enterprise", "cohort": "cohort_q1_2025", "acquisition_source": "organic", "acquisition_cost": 0, "lifetime_value": 5000},
        {"user_id": "u2", "name": "Bob Williams", "email": "bob.w@startup.io", "competitor_id": "da1", "tier": "premium", "cohort": "cohort_q2_2025", "acquisition_source": "paid_ads", "acquisition_cost": 100, "lifetime_value": 800},
        {"user_id": "u3", "name": "Carol Martinez", "email": "carol.m@cloudco.com", "competitor_id": "sm1", "tier": "basic", "cohort": "cohort_q3_2024", "acquisition_source": "referral", "acquisition_cost": 20, "lifetime_value": 200}
    ]
    with open("data/users/users.json", "w") as f:
        json.dump({"users": users}, f, indent=2)

    # 额外干扰：空目录、隐藏文件
    os.makedirs("data/backup", exist_ok=True)
    with open("data/backup/.hidden", "w") as f:
        f.write("secret")

if __name__ == "__main__":
    build_env()
