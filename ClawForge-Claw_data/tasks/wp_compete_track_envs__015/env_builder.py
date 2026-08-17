import os
import json
import random

def build_env():
    # 创建目录
    for d in ["competitors", "ops"]:
        os.makedirs(d, exist_ok=True)

    # 辅助：生成一个合法的 competitor 字典
    def competitor(comp_id, name, sector, market_cap, growth_rate, market_share,
                   version=1, revenue=1000, user_count=10000, products=None, news=None):
        if products is None:
            products = [{"name": "Core", "version": "v1"}]
        if news is None:
            news = [{"date": "2025-01-01", "title": "Launch"}]
        return {
            "competitor_id": comp_id,
            "name": name,
            "description": f"{name} description",
            "sector": sector,
            "market_cap": market_cap,
            "market_share": market_share,
            "revenue": revenue,
            "user_count": user_count,
            "growth_rate": growth_rate,
            "financials": {"eps": 1.5, "pe_ratio": 20},
            "products": products,
            "news": news,
            "version": version
        }

    # ========== 正确且合法的记录 ==========

    # 1. CloudMajor v1 (将被重复的 v2 覆盖)
    comp1 = competitor("C001", "CloudMajor", "Cloud Computing", 5000, 0.25, 0.15, version=1)

    # 2. DataFlow AI  – 增长率 0.35
    comp2 = competitor("C002", "DataFlow AI", "AI/ML", 2000, 0.35, 0.10, version=1)

    # 3. SmartSaaS  – 市值 800 (<1000, 应被排除)
    comp3 = competitor("C003", "SmartSaaS", "Consumer SaaS", 800, 0.45, 0.05, version=1)

    # 4. TechCorp  – 增长率 0.20
    comp4 = competitor("C004", "TechCorp", "Enterprise Software", 3000, 0.20, 0.20, version=1)

    # 5. CloudMajor v2 (同一 competitor_id，市值 6000, 增长率 0.30) – 应保留 v2
    comp5 = competitor("C001", "CloudMajor", "Cloud Computing", 6000, 0.30, 0.18, version=2,
                       revenue=1200, user_count=15000)

    # ========== 无效 / 脏数据 ==========

    # 6. 格式损坏（缺少闭合大括号）
    bad_json = '{"competitor_id": "C006", "name": "BadFile", "growth_rate": 0.1,'

    # 7. 缺少必需字段 growth_rate
    missing_field = {
        "competitor_id": "C007",
        "name": "MissingGrowth",
        "sector": "AI/ML",
        "market_cap": 1500,
        "market_share": 0.08,
        "revenue": 800,
        "user_count": 5000,
        # 缺少 growth_rate
        "version": 1
    }

    # 8. market_cap 为字符串 "N/A"
    str_cap = {
        "competitor_id": "C008",
        "name": "StringCap",
        "sector": "Cloud Computing",
        "market_cap": "N/A",
        "market_share": 0.12,
        "revenue": 2000,
        "user_count": 8000,
        "growth_rate": 0.15,
        "version": 1
    }

    # 写入文件
    files = {
        "competitors/competitor_001.json": json.dumps(comp1, indent=2),
        "competitors/competitor_002.json": json.dumps(comp2, indent=2),
        "competitors/competitor_003.json": json.dumps(comp3, indent=2),
        "competitors/competitor_004.json": json.dumps(comp4, indent=2),
        "competitors/competitor_005.json": json.dumps(comp5, indent=2),
        "competitors/competitor_006.json": bad_json,
        "competitors/competitor_007.json": json.dumps(missing_field, indent=2),
        "competitors/competitor_008.json": json.dumps(str_cap, indent=2),
        # 无关干扰文件
        "competitors/readme.txt": "This folder contains competitor snapshots."
    }

    for path, content in files.items():
        with open(path, "w") as f:
            f.write(content)

if __name__ == "__main__":
    build_env()
