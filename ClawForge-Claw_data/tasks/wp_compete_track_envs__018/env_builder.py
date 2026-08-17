import os
import json
import random

def build_env():
    # 清理工作区
    if os.path.exists("data"):
        import shutil
        shutil.rmtree("data")
    if os.path.exists("ops"):
        shutil.rmtree("ops")

    os.makedirs("data/competitors", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---- 正式竞品数据 ----
    competitors = [
        {
            "competitor_id": "cm-001",
            "name": "CloudMajor",
            "sector": "Cloud Computing",
            "market_share": 34.2,
            "growth_rate": 15.0,
            "revenue": 5000,
            "user_count": 80000,
            "financials": {"profit": 1200, "r&d": 800},
            "products": ["CloudPlatform", "AI Suite"],
            "news": ["New data center in EU"]
        },
        {
            "competitor_id": "df-002",
            "name": "DataFlow AI",
            "sector": "AI/ML",
            "market_share": 12.8,
            "growth_rate": 25.0,
            "revenue": 1800,
            "user_count": 25000,
            "financials": {"profit": 300, "r&d": 400},
            "products": ["DataFlow Engine", "ML Studio"],
            "news": ["Raised Series C"]
        },
        {
            "competitor_id": "ss-003",
            "name": "SmartSaaS",
            "sector": "AI/ML",
            "market_share": 8.5,
            "growth_rate": 22.0,
            "revenue": 1200,
            "user_count": 15000,
            "financials": {"profit": 150, "r&d": 250},
            "products": ["SmartCRM", "Predictor"],
            "news": ["Acquired startup"]
        },
        {
            "competitor_id": "tc-004",
            "name": "TechCorp",
            "sector": "Enterprise Software",
            "market_share": 18.0,
            "growth_rate": 12.0,
            "revenue": 3500,
            "user_count": 60000,
            "financials": {"profit": 600, "r&d": 500},
            "products": ["Enterprise OS", "Cloud Sync"],
            "news": ["Patent lawsuit"]
        }
    ]

    for comp in competitors:
        with open(f"data/competitors/{comp['competitor_id']}.json", "w") as f:
            json.dump(comp, f, indent=2)

    # ---- 干扰文件 ----
    # 1. 旧备份文件（字段不完整，growth_rate 不同）
    os.makedirs("data/competitors/backup_2024", exist_ok=True)
    backup_cloud = {
        "competitor_id": "cm-001",
        "name": "CloudMajor",
        "sector": "Cloud Computing",
        "growth_rate": 10.0,  # 旧数据
        "revenue": 4000
    }
    with open("data/competitors/backup_2024/CloudMajor_backup.json", "w") as f:
        json.dump(backup_cloud, f, indent=2)

    # 2. 损坏的 JSON（语法错误）
    with open("data/competitors/corrupt.json", "w") as f:
        f.write('{"competitor_id": "x", "name": "Broken", "sector": "AI/ML", "growth_rate": 30.0')

    # 3. 诱饵文件：sector 拼写为 "AI_ML"（下划线），但 growth_rate 合格
    bait = {
        "competitor_id": "bait-999",
        "name": "FakeAI",
        "sector": "AI_ML",
        "growth_rate": 28.0,
        "revenue": 500
    }
    with open("data/competitors/bait_ai.json", "w") as f:
        json.dump(bait, f, indent=2)

    # 4. 临时日志文件（非 JSON）
    with open("data/competitors/readme.txt", "w") as f:
        f.write("This is a placeholder, not a competitor file.\n")

    # 5. 另一个备份目录中的无关文件
    os.makedirs("data/backup_old", exist_ok=True)
    with open("data/backup_old/competitors_2023.json", "w") as f:
        json.dump([], f)

    print("工作区初始化完成，干扰项已布置。")

if __name__ == "__main__":
    build_env()
