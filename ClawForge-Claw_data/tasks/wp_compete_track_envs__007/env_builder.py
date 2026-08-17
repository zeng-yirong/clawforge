import os
import json
import random
random.seed(42)

def build_env():
    # 创建目录结构
    os.makedirs("data/competitors", exist_ok=True)
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ===== 竞品数据 =====
    competitors = {
        "cc_001": {
            "competitor_id": "cc_001",
            "name": "CloudMajor",
            "description": "Leading cloud infrastructure provider",
            "sector": "Cloud Computing",
            "market_cap": 320000000000,
            "market_share": 0.34,
            "revenue": 98000000000,
            "user_count": 450000,
            "growth_rate": 0.12,
            "financials": {"fiscal_year": 2025, "profit_margin": 0.22},
            "products": ["ComputeEngine", "StorageX", "AI Suite"],
            "news": ["CloudMajor launches new AI chip"]
        },
        "cc_002": {
            "competitor_id": "cc_002",
            "name": "DataFlow AI",
            "description": "AI/ML platform for enterprises",
            "sector": "AI/ML",
            "market_cap": 85000000000,
            "market_share": 0.12,
            "revenue": 12000000000,
            "user_count": 180000,
            "growth_rate": 0.28,
            "financials": {"fiscal_year": 2025, "profit_margin": 0.15},
            "products": ["DataFlow Core", "AutoML Suite", "ModelHub"],
            "news": ["DataFlow AI secures $200M funding"]
        },
        "cc_003": {
            "competitor_id": "cc_003",
            "name": "SmartSaaS",
            "description": "Consumer SaaS productivity tools",
            "sector": "Consumer SaaS",
            "market_cap": 23000000000,
            "market_share": 0.08,
            "revenue": 4800000000,
            "user_count": 1200000,
            "growth_rate": 0.05,
            "financials": {"fiscal_year": 2024, "profit_margin": 0.08},
            "products": ["SmartSheets", "TaskFlow", "Connect"],
            "news": ["SmartSaaS expands to Asia market"]
        },
        "cc_004": {
            "competitor_id": "cc_004",
            "name": "TechCorp",
            "description": "Enterprise software and analytics",
            "sector": "Enterprise Software",
            "market_cap": 180000000000,
            "market_share": 0.22,
            "revenue": 65000000000,
            "user_count": 800000,
            "growth_rate": 0.09,
            "financials": {"fiscal_year": 2025, "profit_margin": 0.18},
            "products": ["AnalyticsPro", "ERP Next", "IoT Platform"],
            "news": ["TechCorp acquires analytics startup"]
        },
        "cc_005": {
            "competitor_id": "cc_005",
            "name": "CloudNova",
            "description": "Emerging cloud services challenger",
            "sector": "Cloud Computing",
            "market_cap": 12000000000,
            "market_share": 0.05,
            "revenue": 2100000000,
            "user_count": 95000,
            "growth_rate": 0.45,
            "financials": {"fiscal_year": 2025, "profit_margin": 0.03},
            "products": ["NovaCompute", "LightStorage"],
            "news": ["CloudNova enters European market"]
        }
    }
    for cid, cdata in competitors.items():
        with open(f"data/competitors/{cid}.json", "w") as f:
            json.dump(cdata, f, indent=2)

    # ===== 政策数据 =====
    policies = {
        "pol_001": {
            "policy_id": "pol_001",
            "title": "US AI Transparency Act",
            "description": "Requires AI companies to disclose model training data and biases",
            "policy_type": "ai_regulation",
            "jurisdiction": "US",
            "status": "active",
            "impact_level": "high",
            "full_text": "All AI systems deployed in the US must...",
            "summary": "New transparency requirements for AI providers",
            "impact": {
                "affected_competitors": ["cc_002", "cc_004"],
                "compliance_cost": 50000000
            },
            "changes": ["Disclosure mandate", "Audit requirement"]
        },
        "pol_002": {
            "policy_id": "pol_002",
            "title": "EU Digital Markets Act Compliance",
            "description": "Regulates large digital platforms in the EU",
            "policy_type": "antitrust",
            "jurisdiction": "EU",
            "status": "active",
            "impact_level": "high",
            "full_text": "Gatekeeper platforms must...",
            "summary": "Antitrust regulation for big tech",
            "impact": {
                "affected_competitors": ["cc_001", "cc_004"],
                "compliance_cost": 30000000
            },
            "changes": ["Data sharing", "Interoperability"]
        },
        "pol_003": {
            "policy_id": "pol_003",
            "title": "Global Data Privacy Framework",
            "description": "Cross-border data transfer rules",
            "policy_type": "privacy",
            "jurisdiction": "Global",
            "status": "proposed",
            "impact_level": "medium",
            "full_text": "Data transfers between jurisdictions...",
            "summary": "Framework for international data flows",
            "impact": {
                "affected_competitors": ["cc_001", "cc_002", "cc_003"],
                "compliance_cost": 10000000
            },
            "changes": ["Standard contractual clauses"]
        },
        "pol_004": {
            "policy_id": "pol_004",
            "title": "US AI Transparency Act (Proposed Amendment)",
            "description": "Extended version of the original act",
            "policy_type": "ai_regulation",
            "jurisdiction": "US",
            "status": "proposed",
            "impact_level": "medium",
            "full_text": "Extended disclosure requirements...",
            "summary": "Amendment to transparency act (not yet in effect)",
            "impact": {
                "affected_competitors": ["cc_001", "cc_005"],
                "compliance_cost": 20000000
            },
            "changes": ["Extended timeline"]
        }
    }
    for pid, pdata in policies.items():
        with open(f"data/policies/{pid}.json", "w") as f:
            json.dump(pdata, f, indent=2)

    # 额外干扰文件
    os.makedirs("data/accounts", exist_ok=True)
    with open("data/accounts/acc_admin.json", "w") as f:
        json.dump({"account_id": "admin", "name": "Admin", "role": "system"}, f)
    os.makedirs("data/contacts", exist_ok=True)
    with open("data/contacts/contact_001.json", "w") as f:
        json.dump({"contact_id": "c001", "name": "Lisa", "email": "lisa@company.com"}, f)

if __name__ == "__main__":
    build_env()
