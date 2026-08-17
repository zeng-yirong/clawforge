import os
import json
import random

def build_env():
    # --- 竞品数据 ---
    comp_dir = "data/competitors"
    os.makedirs(comp_dir, exist_ok=True)

    # 正常竞品
    competitors = {
        "smart_saas_001.json": {
            "competitor_id": "smart_saas_001",
            "name": "SmartSaaS",
            "description": "下一代智能 SaaS 平台，专注于中小企业数字化转型",
            "sector": "Consumer SaaS",
            "market_cap": 2_500_000_000,
            "market_share": 12.5,
            "revenue": 420_000_000,
            "user_count": 850_000,
            "growth_rate": 8.3,
            "financials": {"fiscal_year": 2025, "net_income": 80_000_000, "r_d_spend": 95_000_000},
            "products": ["SmartCRM", "SmartERP", "SmartAnalytics"],
            "news": [{"date": "2025-09-15", "headline": "SmartSaaS 获新一轮融资 4 亿美元"}]
        },
        "cloud_major_002.json": {
            "competitor_id": "cloud_major_002",
            "name": "CloudMajor",
            "description": "头部云服务商，覆盖 IaaS/PaaS",
            "sector": "Cloud Computing",
            "market_cap": 180_000_000_000,
            "market_share": 25.0,
            "revenue": 90_000_000_000,
            "user_count": 5_000_000,
            "growth_rate": 5.2,
            "financials": {"fiscal_year": 2025, "net_income": 25_000_000_000, "r_d_spend": 30_000_000_000},
            "products": ["CloudCompute", "CloudStorage", "CloudAI"],
            "news": [{"date": "2025-10-01", "headline": "CloudMajor 发布新一代量子计算服务"}]
        },
        "dataflow_003.json": {
            "competitor_id": "dataflow_003",
            "name": "DataFlow AI",
            "description": "AI 平台公司，专注数据流水线和模型部署",
            "sector": "AI/ML",
            "market_cap": 8_000_000_000,
            "market_share": 18.0,
            "revenue": 1_200_000_000,
            "user_count": 2_100_000,
            "growth_rate": 12.1,
            "financials": {"fiscal_year": 2025, "net_income": 200_000_000, "r_d_spend": 350_000_000},
            "products": ["DataFlow Studio", "ModelHub", "PipelinePro"],
            "news": [{"date": "2025-08-20", "headline": "DataFlow AI 收购数据治理初创公司"}]
        },
        "techcorp_004.json": {
            "competitor_id": "techcorp_004",
            "name": "TechCorp",
            "description": "企业软件巨头，横跨 ERP、HRM 和 DevOps",
            "sector": "Enterprise Software",
            "market_cap": 42_000_000_000,
            "market_share": 10.0,
            "revenue": 7_500_000_000,
            "user_count": 1_800_000,
            "growth_rate": 6.7,
            "financials": {"fiscal_year": 2025, "net_income": 1_500_000_000, "r_d_spend": 2_000_000_000},
            "products": ["TechERP", "TechHR", "TechDevOps"],
            "news": [{"date": "2025-09-28", "headline": "TechCorp 宣布与微软深度集成"}]
        }
    }
    for fname, data in competitors.items():
        with open(os.path.join(comp_dir, fname), "w") as f:
            json.dump(data, f, indent=2)

    # 干扰项：缺失 market_share 字段
    missing_field = {
        "competitor_id": "smart_saas_incomplete",
        "name": "SmartSaaS",
        "description": "旧版本记录，字段不完整",
        "sector": "Consumer SaaS",
        "market_cap": 100_000_000,
        "revenue": 10_000_000,
        "user_count": 5000,
        "growth_rate": 2.0,
        "financials": {},
        "products": [],
        "news": []
    }
    with open(os.path.join(comp_dir, "incomplete_smart.json"), "w") as f:
        json.dump(missing_field, f, indent=2)

    # 干扰项：格式错误的文件（非 JSON）
    with open(os.path.join(comp_dir, "corrupted_smart.json"), "w") as f:
        f.write("这不是 JSON，是垃圾内容 %^&*")

    # 干扰项：名字相似但无关的竞品（SmartSaaS 的变体）
    legacy = {
        "competitor_id": "smart_legacy_001",
        "name": "SmartSaaS Legacy",
        "description": "已停止维护的旧产品线",
        "sector": "Consumer SaaS",
        "market_cap": 50_000_000,
        "market_share": 0.5,
        "revenue": 2_000_000,
        "user_count": 20000,
        "growth_rate": -1.5,
        "financials": {"fiscal_year": 2023, "net_income": -5_000_000, "r_d_spend": 1_000_000},
        "products": ["SmartCRM Lite"],
        "news": []
    }
    with open(os.path.join(comp_dir, "smart_legacy.json"), "w") as f:
        json.dump(legacy, f, indent=2)

    # --- 政策数据 ---
    pol_dir = "data/policies"
    os.makedirs(pol_dir, exist_ok=True)

    policies = {
        "pol_01.json": {
            "policy_id": "pol_01",
            "title": "EU Digital Markets Act Compliance",
            "description": "欧盟数字市场法案合规要求",
            "policy_type": "antitrust",
            "jurisdiction": "EU",
            "status": "active",
            "impact_level": "high",
            "full_text": "...long text...",
            "summary": "要求大型平台开放数据，避免自我优待",
            "impact": {"affected_competitors": ["smart_saas_001", "dataflow_003"]},
            "changes": [{"date": "2025-06-01", "description": "正式生效"}]
        },
        "pol_02.json": {
            "policy_id": "pol_02",
            "title": "Global Data Privacy Framework",
            "description": "全球数据隐私框架提案",
            "policy_type": "privacy",
            "jurisdiction": "Global",
            "status": "proposed",
            "impact_level": "medium",
            "full_text": "...",
            "summary": "提议建立跨境数据流动的统一标准",
            "impact": {"affected_competitors": ["smart_saas_001", "cloud_major_002"]},
            "changes": [{"date": "2025-11-01", "description": "进入征求意见阶段"}]
        },
        "pol_03.json": {
            "policy_id": "pol_03",
            "title": "US AI Transparency Act",
            "description": "美国 AI 透明度法案",
            "policy_type": "ai_regulation",
            "jurisdiction": "US",
            "status": "active",
            "impact_level": "medium",
            "full_text": "...",
            "summary": "要求 AI 系统提供可解释性和透明度报告",
            "impact": {"affected_competitors": ["cloud_major_002", "dataflow_003"]},
            "changes": [{"date": "2025-07-15", "description": "参议院通过"}]
        }
    }
    for fname, data in policies.items():
        with open(os.path.join(pol_dir, fname), "w") as f:
            json.dump(data, f, indent=2)

    # 干扰项：格式不正确的政策文件
    with open(os.path.join(pol_dir, "corrupt_policy.json"), "w") as f:
        f.write("{'这不是': '合法的 JSON'")

    # 创建 ops 目录（要求产出目录）
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
