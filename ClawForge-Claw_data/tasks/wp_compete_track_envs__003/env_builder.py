import os
import json

def build_env():
    # Create directory structure
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("data/competitors", exist_ok=True)
    os.makedirs("data/reports", exist_ok=True)

    # ── Policy files ──────────────────────────────────────────────
    # Target policy (the latest US AI Transparency Act)
    target_policy = {
        "policy_id": "US_AI_Transparency_Act_2025",
        "title": "US AI Transparency Act",
        "description": "Requires AI system transparency reporting for large providers.",
        "policy_type": "ai_regulation",
        "jurisdiction": "US",
        "status": "active",
        "impact_level": "high",
        "full_text": "Full text...",
        "summary": "Mandates disclosure of training data and model architecture.",
        "impact": {"affected_competitors": ["CloudMajor", "DataFlow AI"]},
        "changes": []
    }
    with open("data/policies/US_AI_Transparency_Act_2025.json", "w") as f:
        json.dump(target_policy, f)

    # Distractor: old version with different policy_id
    old_policy = {
        "policy_id": "US_AI_Transparency_Act_2023",
        "title": "US AI Transparency Act (Old)",
        "description": "Earlier proposal with softer requirements.",
        "policy_type": "ai_regulation",
        "jurisdiction": "US",
        "status": "proposed",
        "impact_level": "medium",
        "full_text": "Older full text...",
        "summary": "Weaker transparency rules.",
        "impact": {"affected_competitors": ["SmartSaaS"]},
        "changes": []
    }
    with open("data/policies/US_AI_Transparency_Act_2023.json", "w") as f:
        json.dump(old_policy, f)

    # Distractor: unrelated policy
    unrelated_policy = {
        "policy_id": "GDPR_2026",
        "title": "Global Data Privacy Framework",
        "description": "Updated global privacy standards.",
        "policy_type": "privacy",
        "jurisdiction": "Global",
        "status": "active",
        "impact_level": "medium",
        "full_text": "Full text...",
        "summary": "Privacy requirements for cross-border data.",
        "impact": {"affected_competitors": ["TechCorp"]},
        "changes": []
    }
    with open("data/policies/GDPR_2026.json", "w") as f:
        json.dump(unrelated_policy, f)

    # Distractor: policy missing impact field (invalid)
    invalid_policy = {
        "policy_id": "Invalid_Policy",
        "title": "Broken Policy",
        "description": "This file misses the impact field.",
        "policy_type": "antitrust",
        "jurisdiction": "EU",
        "status": "proposed",
        "impact_level": "low",
        "full_text": "...",
        "summary": "...",
        "changes": []
    }
    with open("data/policies/Broken_Policy.json", "w") as f:
        json.dump(invalid_policy, f)

    # ── Competitor files ─────────────────────────────────────────
    # Valid: CloudMajor
    cloudmajor = {
        "competitor_id": "CloudMajor",
        "name": "CloudMajor",
        "description": "Leading cloud provider with AI services.",
        "sector": "Cloud Computing",
        "market_cap": 800000,
        "market_share": 0.28,
        "revenue": 50000000,
        "user_count": 1200000,
        "growth_rate": 0.15,
        "financials": {},
        "products": ["CloudAI", "DataLake"],
        "news": []
    }
    with open("data/competitors/CloudMajor.json", "w") as f:
        json.dump(cloudmajor, f)

    # Valid: DataFlow AI
    dataflow = {
        "competitor_id": "DataFlow AI",
        "name": "DataFlow AI",
        "description": "AI-data pipeline startup.",
        "sector": "AI/ML",
        "market_cap": 1200000,
        "market_share": 0.05,
        "revenue": 8000000,
        "user_count": 350000,
        "growth_rate": 0.45,
        "financials": {},
        "products": ["FlowEngine", "ModelHub"],
        "news": []
    }
    with open("data/competitors/DataFlow AI.json", "w") as f:
        json.dump(dataflow, f)

    # Invalid: missing market_cap
    smartsaas = {
        "competitor_id": "SmartSaaS",
        "name": "SmartSaaS",
        "description": "SaaS platform for SMEs.",
        "sector": "Consumer SaaS",
        # missing market_cap
        "market_share": 0.12,
        "revenue": 12000000,
        "user_count": 800000,
        "growth_rate": 0.22,
        "financials": {},
        "products": ["SmartCRM"],
        "news": []
    }
    with open("data/competitors/SmartSaaS.json", "w") as f:
        json.dump(smartsaas, f)

    # Invalid: market_cap is a string (not numeric)
    techcorp = {
        "competitor_id": "TechCorp",
        "name": "TechCorp",
        "description": "Enterprise software giant.",
        "sector": "Enterprise Software",
        "market_cap": "N/A",
        "market_share": 0.35,
        "revenue": 90000000,
        "user_count": 2200000,
        "growth_rate": 0.08,
        "financials": {},
        "products": ["OfficeSuite", "CloudPlatform"],
        "news": []
    }
    with open("data/competitors/TechCorp.json", "w") as f:
        json.dump(techcorp, f)

    # Extra valid competitor (not affected by target policy, but valid)
    fakecorp = {
        "competitor_id": "FakeCorp",
        "name": "FakeCorp",
        "description": "Not in target impact list.",
        "sector": "AI/ML",
        "market_cap": 500000,
        "market_share": 0.02,
        "revenue": 2000000,
        "user_count": 50000,
        "growth_rate": 0.30,
        "financials": {},
        "products": ["FakeAI"],
        "news": []
    }
    with open("data/competitors/FakeCorp.json", "w") as f:
        json.dump(fakecorp, f)

if __name__ == "__main__":
    build_env()
