import os
import json
import random

def build_env():
    # 确保工作目录干净
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("data/competitors", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 用于存放输出

    # ========== 生成政策文件 (干扰 + 目标) ==========
    # 目标政策：US AI Transparency Act (active, high impact)
    target_policy = {
        "policy_id": "pol_us_ai_transparency",
        "title": "US AI Transparency Act",
        "description": "Mandates disclosure of AI models used in consumer products.",
        "policy_type": "ai_regulation",
        "jurisdiction": "US",
        "status": "active",
        "impact_level": "high",
        "full_text": "...",
        "summary": "Requires transparency in AI systems.",
        "impact": {
            "affected_competitors": ["comp_cloudmajor"],
            "affected_sectors": ["AI/ML", "Enterprise Software"],
            "estimated_fine": 50000000
        },
        "changes": ["New reporting requirements for AI models"]
    }
    with open("data/policies/pol_us_ai_transparency.json", "w") as f:
        json.dump(target_policy, f, indent=2)

    # 干扰政策1：欧盟数字市场法案 (active, medium impact) - 不影响 US 竞品
    inter_policy1 = {
        "policy_id": "pol_eu_dma",
        "title": "EU Digital Markets Act Compliance",
        "description": "Regulates large online platforms.",
        "policy_type": "antitrust",
        "jurisdiction": "EU",
        "status": "active",
        "impact_level": "medium",
        "full_text": "...",
        "summary": "Gatekeeper obligations for big tech.",
        "impact": {
            "affected_competitors": ["comp_eu_gatekeeper"],
            "affected_sectors": ["Cloud Computing"],
            "estimated_fine": 20000000
        },
        "changes": []
    }
    with open("data/policies/pol_eu_dma.json", "w") as f:
        json.dump(inter_policy1, f, indent=2)

    # 干扰政策2：全球数据隐私框架 (proposed, low influence)
    inter_policy2 = {
        "policy_id": "pol_global_privacy",
        "title": "Global Data Privacy Framework",
        "description": "International data transfer standards.",
        "policy_type": "privacy",
        "jurisdiction": "Global",
        "status": "proposed",
        "impact_level": "medium",
        "full_text": "...",
        "summary": "Framework for cross-border data flows.",
        "impact": {
            "affected_competitors": [],
            "affected_sectors": ["All"],
            "estimated_fine": 10000000
        },
        "changes": []
    }
    with open("data/policies/pol_global_privacy.json", "w") as f:
        json.dump(inter_policy2, f, indent=2)

    # 干扰文件：一个过期的 .bak 文件，假装是旧政策
    with open("data/policies/pol_obsolete.bak", "w") as f:
        f.write("This is an obsolete backup, not a real policy.")

    # ========== 生成竞品文件 (干扰 + 目标) ==========
    # 目标竞品：CloudMajor (AI/ML sector, revenue 80M)
    target_competitor = {
        "competitor_id": "comp_cloudmajor",
        "name": "CloudMajor",
        "description": "Leading cloud and AI infrastructure provider.",
        "sector": "AI/ML",
        "market_cap": 120000000000,
        "market_share": 0.25,
        "revenue": 80000000,
        "user_count": 5000000,
        "growth_rate": 0.18,
        "financials": {"last_quarter_revenue": 20000000},
        "products": ["AI-Platform", "CloudCompute"],
        "news": ["Launched new AI model in Q1"]
    }
    with open("data/competitors/comp_cloudmajor.json", "w") as f:
        json.dump(target_competitor, f, indent=2)

    # 干扰竞品1：DataFlow AI (Cloud Computing sector, revenue 120M, 但sector不匹配，且未在目标政策影响列表中)
    dist_comp1 = {
        "competitor_id": "comp_dataflow",
        "name": "DataFlow AI",
        "description": "Data pipeline and analytics company.",
        "sector": "Cloud Computing",
        "market_cap": 8000000000,
        "market_share": 0.15,
        "revenue": 120000000,
        "user_count": 200000,
        "growth_rate": 0.35,
        "financials": {"last_quarter_revenue": 30000000},
        "products": ["DataPipeline", "Analytics"],
        "news": ["Acquired by BigCo"]
    }
    with open("data/competitors/comp_dataflow.json", "w") as f:
        json.dump(dist_comp1, f, indent=2)

    # 干扰竞品2：SmartSaaS (AI/ML sector, 但 revenue 30M < 50M, 且未被目标政策影响列表包含)
    dist_comp2 = {
        "competitor_id": "comp_smartsaas",
        "name": "SmartSaaS",
        "description": "Small SaaS company with AI features.",
        "sector": "AI/ML",
        "market_cap": 300000000,
        "market_share": 0.03,
        "revenue": 30000000,
        "user_count": 10000,
        "growth_rate": 0.50,
        "financials": {"last_quarter_revenue": 8000000},
        "products": ["SmartCRM"],
        "news": []
    }
    with open("data/competitors/comp_smartsaas.json", "w") as f:
        json.dump(dist_comp2, f, indent=2)

    # 干扰竞品3：TechCorp (Enterprise Software sector, revenue 60M, 但未被目标政策影响列表包含)
    dist_comp3 = {
        "competitor_id": "comp_techcorp",
        "name": "TechCorp",
        "description": "Enterprise software giant.",
        "sector": "Enterprise Software",
        "market_cap": 50000000000,
        "market_share": 0.10,
        "revenue": 60000000,
        "user_count": 2000000,
        "growth_rate": 0.05,
        "financials": {"last_quarter_revenue": 15000000},
        "products": ["OfficeSuite", "CloudERP"],
        "news": ["Completed migration to cloud"]
    }
    with open("data/competitors/comp_techcorp.json", "w") as f:
        json.dump(dist_comp3, f, indent=2)

    # 额外干扰：一个非 JSON 文件
    with open("data/competitors/readme.txt", "w") as f:
        f.write("Competitor data last updated 2025-03-01\n")

    # ========== 生成 accounts.json 和 contacts.json (可选的干扰) ==========
    accounts = [
        {"account_id": "acc001", "name": "Alice", "role": "analyst", "email": "alice@example.com"},
        {"account_id": "acc002", "name": "Bob", "role": "manager", "email": "bob@example.com"}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    contacts = [
        {"contact_id": "ct001", "name": "David Kim", "email": "dkim@regtech.com", "role": "Compliance Director"},
        {"contact_id": "ct002", "name": "Emily Zhang", "email": "emily.zhang@smartsaas.com", "role": "CEO"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

if __name__ == "__main__":
    build_env()
