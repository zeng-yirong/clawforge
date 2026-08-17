import os
import json
import random

def build_env():
    # 创建目录结构
    os.makedirs("data/competitors/archive", exist_ok=True)
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("data/users", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 有效竞品数据（满足条件：market_cap > 500 且 growth_rate > 20）
    competitors = [
        {
            "competitor_id": "C001",
            "name": "CloudMajor",
            "description": "Leading cloud infrastructure provider",
            "sector": "Cloud Computing",
            "market_cap": 600,
            "market_share": 0.35,
            "revenue": 5000,
            "user_count": 1500000,
            "growth_rate": 25,
            "financials": {"fiscal_year": 2025, "net_income": 1200},
            "products": ["Compute Engine", "Storage Suite"],
            "news": ["CloudMajor launches new AI chip", "Data center expansion in Asia"]
        },
        {
            "competitor_id": "C002",
            "name": "TechCorp",
            "description": "Enterprise software giant",
            "sector": "Enterprise Software",
            "market_cap": 700,
            "market_share": 0.25,
            "revenue": 4000,
            "user_count": 800000,
            "growth_rate": 22,
            "financials": {"fiscal_year": 2025, "net_income": 900},
            "products": ["CRM", "ERP"],
            "news": ["TechCorp acquires startup", "New cloud suite released"]
        }
    ]

    # 干扰竞品（不满足条件或格式有问题）
    distractors = [
        # 市值不够
        {
            "competitor_id": "C003",
            "name": "DataFlow AI",
            "market_cap": 400,
            "growth_rate": 30,
            "market_share": 0.15,
            "revenue": 2000,
            "user_count": 500000,
            "sector": "AI/ML",
            "description": "AI & data analytics platform",
            "financials": {"fiscal_year": 2025, "net_income": 300},
            "products": ["DataFlow Engine"],
            "news": ["Series C funding round closed"]
        },
        # 增长率不够
        {
            "competitor_id": "C004",
            "name": "SmartSaaS",
            "market_cap": 550,
            "growth_rate": 18,
            "market_share": 0.20,
            "revenue": 3000,
            "user_count": 600000,
            "sector": "Consumer SaaS",
            "description": "Productivity tools for consumers",
            "financials": {"fiscal_year": 2025, "net_income": 450},
            "products": ["SmartNote", "SmartCal"],
            "news": ["User growth slows down"]
        },
        # 旧备份（文件名带_backup，但内容有效且不满足条件）
        {
            "competitor_id": "C005",
            "name": "CloudMajor_old",
            "market_cap": 600,
            "growth_rate": 10,
            "market_share": 0.30,
            "revenue": 4500,
            "user_count": 1200000,
            "sector": "Cloud Computing",
            "description": "Old snapshot of CloudMajor",
            "financials": {"fiscal_year": 2024, "net_income": 1000},
            "products": ["Legacy Compute"],
            "news": ["Outdated data"]
        },
        # 测试文件（缺失关键字段 market_cap，无法判断）
        {
            "competitor_id": "C006",
            "name": "TestCompany",
            "growth_rate": 15,
            "market_share": 0.10,
            "revenue": 1000,
            "user_count": 100000,
            "sector": "Uncategorized",
            "description": "Test entry",
            "financials": {},
            "products": [],
            "news": []
        },
        # 完全无效的文件内容（非JSON串）
    ]

    # 写入有效竞品
    for comp in competitors:
        filename = f"data/competitors/{comp['name']}.json"
        with open(filename, "w") as f:
            json.dump(comp, f)

    # 写入干扰竞品到顶层
    distractor_names = ["DataFlow AI", "SmartSaaS"]
    for comp in distractors:
        if comp["name"] in distractor_names:
            filename = f"data/competitors/{comp['name']}.json"
            with open(filename, "w") as f:
                json.dump(comp, f)

    # 旧备份文件放入 archive 子目录
    backup_comp = [d for d in distractors if d["name"] == "CloudMajor_old"][0]
    with open("data/competitors/archive/CloudMajor_backup.json", "w") as f:
        json.dump(backup_comp, f)

    # 测试文件（缺失 market_cap）放入 archive
    test_comp = [d for d in distractors if d["name"] == "TestCompany"][0]
    with open("data/competitors/archive/TestCompany_missing.json", "w") as f:
        json.dump(test_comp, f)

    # 非 JSON 文件（干扰）
    with open("data/competitors/readme.txt", "w") as f:
        f.write("This directory contains competitor data snapshots.\n")

    # 创建 policies 和 users 简单填充（不需要用于评测，仅增加真实性）
    with open("data/policies/.gitkeep", "w") as f:
        pass
    with open("data/users/.gitkeep", "w") as f:
        pass

    # 确保 reports 目录存在但为空
    # 已在前面创建

if __name__ == "__main__":
    build_env()
