import os
import json
import random

def build_env():
    # Create directories
    os.makedirs("data/competitors", exist_ok=True)
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # Agent will produce output here; we can pre-create empty dir

    # ---- Competitors ----
    competitors = [
        {
            "competitor_id": "comp_001",
            "name": "CloudMajor",
            "sector": "Cloud Computing",
            "market_cap": 850000000000,
            "market_share": 32.4,
            "revenue": 180000000000,
            "user_count": 250000000,
            "growth_rate": 12.5,
            "financials": {"fiscal_year": 2025, "currency": "USD"},
            "products": ["CloudCompute", "ServerlessDB", "AIMLPlatform"],
            "news": ["Expanded EU data centers", "Lobbying against DMA"]
        },
        {
            "competitor_id": "comp_002",
            "name": "DataFlow AI",
            "sector": "AI/ML",
            "market_cap": 120000000000,
            "market_share": 8.1,
            "revenue": 22000000000,
            "user_count": 45000000,
            "growth_rate": 35.2,
            "financials": {"fiscal_year": 2025, "currency": "USD"},
            "products": ["DataFlowEngine", "AutoML Studio"],
            "news": ["Series F closed", "Hiring in Berlin"]
        },
        {
            "competitor_id": "comp_003",
            "name": "SmartSaaS",
            "sector": "Consumer SaaS",
            "market_cap": 45000000000,
            "market_share": 5.6,
            "revenue": 9000000000,
            "user_count": 120000000,
            "growth_rate": 18.0,
            "financials": {"fiscal_year": 2024, "currency": "USD"},
            "products": ["SmartCRM", "SmartERP"],
            "news": ["New pricing model", "Partnership with EU banks"]
        }
    ]
    for comp in competitors:
        with open(f"data/competitors/{comp['competitor_id']}.json", "w") as f:
            json.dump(comp, f, indent=2)

    # ---- Policies (with targeted answer) ----
    # Answer: two EU high-impact active policies
    policies = [
        {
            "policy_id": "EU-DMA-2025",
            "title": "EU Digital Markets Act Compliance",
            "description": "Gatekeeper obligations for large platforms",
            "policy_type": "antitrust",
            "jurisdiction": "EU",
            "status": "active",
            "impact_level": "high",
            "full_text": "...",
            "summary": "Applies to companies with market cap >75B EUR in EU",
            "impact": {"affected_services": ["cloud", "advertising"]},
            "changes": [{"date": "2025-01-01", "description": "Full enforcement begins"}]
        },
        {
            "policy_id": "EU-GDPR-2026",
            "title": "Global Data Privacy Framework",
            "description": "Updated data transfer rules for non-EU entities",
            "policy_type": "privacy",
            "jurisdiction": "EU",
            "status": "active",
            "impact_level": "high",
            "full_text": "...",
            "summary": "Requires Data Protection Impact Assessments for cloud providers",
            "impact": {"affected_services": ["data_transfer", "storage"]},
            "changes": [{"date": "2026-06-01", "description": "New fines up to 10% global turnover"}]
        },
        # Distractor: EU but medium impact (should be excluded)
        {
            "policy_id": "EU-E-Waste-2024",
            "title": "EU Electronic Waste Directive",
            "description": "Hardware recycling requirements",
            "policy_type": "environment",
            "jurisdiction": "EU",
            "status": "active",
            "impact_level": "medium",
            "full_text": "...",
            "summary": "Applies to data center hardware disposal",
            "impact": {"affected_services": ["hardware"]},
            "changes": [{"date": "2024-12-01", "description": "Compliance deadline"}]
        },
        # Distractor: US high impact active (wrong jurisdiction)
        {
            "policy_id": "US-AI-2025",
            "title": "US AI Transparency Act",
            "description": "Disclosure requirements for AI systems",
            "policy_type": "ai_regulation",
            "jurisdiction": "US",
            "status": "active",
            "impact_level": "high",
            "full_text": "...",
            "summary": "Applies to any AI deployed in US market",
            "impact": {"affected_services": ["AI_models"]},
            "changes": [{"date": "2025-07-01", "description": "Effective date"}]
        },
        # Distractor: EU high impact but proposed (should be excluded)
        {
            "policy_id": "EU-CSA-2027",
            "title": "EU Cloud Sovereignty Act",
            "description": "Proposed regulation for cloud data residency",
            "policy_type": "privacy",
            "jurisdiction": "EU",
            "status": "proposed",
            "impact_level": "high",
            "full_text": "...",
            "summary": "Would require 100% in-EU data storage",
            "impact": {"affected_services": ["all_cloud"]},
            "changes": [{"date": "2027-01-01", "description": "Proposed enforcement"}]
        },
        # Malformed entry (missing 'status' field) - should be ignored or cause agent to skip safely
        {
            "policy_id": "BROKEN-DATA",
            "title": "Corrupted Entry",
            "description": "This file has missing required fields",
            "policy_type": "unknown",
            "jurisdiction": "EU",
            "impact_level": "high",
            "full_text": "garbage",
            "summary": "should not be processed",
            "impact": {},
            "changes": []
            # deliberately no 'status' key
        }
    ]
    for pol in policies:
        with open(f"data/policies/{pol['policy_id']}.json", "w") as f:
            json.dump(pol, f, indent=2)

    # Also create a small accounts.json to simulate clutter but not needed for task
    accounts = [
        {"account_id": "acc_001", "name": "CloudMajor", "display_name": "CloudMajor Inc.", "role": "competitor", "email": "info@cloudmajor.io", "team": "exec", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

if __name__ == "__main__":
    build_env()
