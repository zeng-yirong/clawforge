import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/competitors/archive", exist_ok=True)
    os.makedirs("data/policies/draft", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("backups", exist_ok=True)

    # ---------- 竞品数据 ----------
    # 1. CloudMajor – 不是 AI/ML  sector
    write_json("data/competitors/cloudmajor.json", {
        "competitor_id": "cm001",
        "name": "CloudMajor",
        "sector": "Cloud Computing",
        "market_cap": 5000000,
        "growth_rate": 0.12,
        "user_count": 1000000,
        "revenue": 1200000,
        "financials": {"profit": 300000},
        "products": ["CloudSuite"],
        "news": ["New data center in Europe"]
    })

    # 2. DataFlow AI – 符合条件，growth 0.35
    write_json("data/competitors/dataflow_ai.json", {
        "competitor_id": "df001",
        "name": "DataFlow AI",
        "sector": "AI/ML",
        "market_cap": 2000000,
        "growth_rate": 0.35,
        "user_count": 500000,
        "revenue": 800000,
        "financials": {"profit": 120000},
        "products": ["DataFlow Platform", "AI Pipelines"],
        "news": ["New funding round of $50M"]
    })

    # 3. SmartSaaS – 不是 AI/ML
    write_json("data/competitors/smartsaas.json", {
        "competitor_id": "ss002",
        "name": "SmartSaaS",
        "sector": "Consumer SaaS",
        "market_cap": 1500000,
        "growth_rate": 0.18,
        "user_count": 300000,
        "revenue": 400000,
        "financials": {"profit": 50000},
        "products": ["SmartCRM"],
        "news": ["Product launch"]
    })

    # 4. TechCorp – 不是 AI/ML
    write_json("data/competitors/techcorp.json", {
        "competitor_id": "tc003",
        "name": "TechCorp",
        "sector": "Enterprise Software",
        "market_cap": 3000000,
        "growth_rate": 0.25,
        "user_count": 800000,
        "revenue": 2000000,
        "financials": {"profit": 600000},
        "products": ["EnterpriseHub"],
        "news": ["Acquisition of small startup"]
    })

    # 5. NeuralNet – 符合条件，growth 0.28
    write_json("data/competitors/neuralnet.json", {
        "competitor_id": "nn004",
        "name": "NeuralNet",
        "sector": "AI/ML",
        "market_cap": 500000,
        "growth_rate": 0.28,
        "user_count": 100000,
        "revenue": 150000,
        "financials": {"profit": 20000},
        "products": ["NeuralStudio", "ModelHub"],
        "news": ["Partnership with university"]
    })

    # 6. OldAI – 脏数据：market_cap 是字符串，无法用于计算
    write_json("data/competitors/oldai.json", {
        "competitor_id": "oa005",
        "name": "OldAI",
        "sector": "AI/ML",
        "market_cap": "invalid",   # <-- 故意脏数据
        "growth_rate": 0.22,
        "user_count": 50000,
        "revenue": 20000,
        "financials": {"profit": -1000},
        "products": ["LegacyAI"],
        "news": ["Shutting down"]
    })

    # 7. 重复（但不同 ID）的 DataFlow 变体 – 名字类似，growth 低，不满足条件
    write_json("data/competitors/dataflow_v2.json", {
        "competitor_id": "df006",
        "name": "DataFlow AI Lite",
        "sector": "AI/ML",
        "market_cap": 800000,
        "growth_rate": 0.15,
        "user_count": 150000,
        "revenue": 200000,
        "financials": {"profit": 30000},
        "products": ["Lite Platform"],
        "news": []
    })

    # 8. 存档文件夹中的旧竞品 – 虽为 AI/ML 但 growth 很低
    write_json("data/competitors/archive/cloudmajor_old.json", {
        "competitor_id": "cm_old",
        "name": "CloudMajor (Old)",
        "sector": "AI/ML",
        "market_cap": 1000000,
        "growth_rate": 0.10,
        "user_count": 400000,
        "revenue": 600000,
        "financials": {"profit": -50000},
        "products": ["OldCloud"],
        "news": ["No recent news"]
    })

    # ---------- 政策数据 ----------
    # 活跃的 AI 法规
    write_json("data/policies/us_ai_transparency_act.json", {
        "policy_id": "pol_001",
        "title": "US AI Transparency Act",
        "policy_type": "ai_regulation",
        "jurisdiction": "US",
        "status": "active",
        "impact_level": "high",
        "full_text": "...",
        "summary": "Requires AI providers to disclose training data and algorithm decisions.",
        "impact": {"sectors": ["AI/ML"], "market_effect": "increased compliance cost"},
        "changes": [{"date": "2025-01-01", "description": "Effective in US"}]
    })
    # 干扰政策
    write_json("data/policies/eu_dma.json", {
        "policy_id": "pol_002",
        "title": "EU Digital Markets Act Compliance",
        "policy_type": "antitrust",
        "jurisdiction": "EU",
        "status": "active",
        "impact_level": "medium",
        "full_text": "...",
        "summary": "Obligations for gatekeeper platforms",
        "impact": {"sectors": ["Cloud Computing"], "market_effect": "revenue loss"},
        "changes": []
    })
    write_json("data/policies/global_privacy.json", {
        "policy_id": "pol_003",
        "title": "Global Data Privacy Framework",
        "policy_type": "privacy",
        "jurisdiction": "Global",
        "status": "proposed",
        "impact_level": "medium",
        "full_text": "...",
        "summary": "Future privacy regulation",
        "impact": {"sectors": ["all"], "market_effect": "compliance cost"},
        "changes": [{"date": "2026-06-01", "description": "Expected to enter force"}]
    })
    # 草稿
    write_json("data/policies/draft/upcoming_ai_act.json", {
        "policy_id": "pol_draft",
        "title": "US AI Liability Act (draft)",
        "policy_type": "ai_regulation",
        "jurisdiction": "US",
        "status": "proposed",
        "impact_level": "high",
        "full_text": "...",
        "summary": "Not yet finalized",
        "impact": {},
        "changes": []
    })

    # ---------- 其他干扰 ----------
    write_json("backups/competitors_2024.json", {
        "competitors": [{"competitor_id": "old_cm", "name": "CloudMajor", "sector": "AI/ML"}]
    })

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    build_env()
