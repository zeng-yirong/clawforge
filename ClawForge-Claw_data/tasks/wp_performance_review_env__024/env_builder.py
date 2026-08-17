import json
import os
import shutil
from datetime import datetime

def build_env():
    # 确保工作目录在.
    base = "."
    # 清理旧数据（如果存在）
    for d in ["data", "profiles"]:
        if os.path.exists(d):
            shutil.rmtree(d)

    # --- 1. 员工数据 ---
    os.makedirs("data/employees", exist_ok=True)
    employees = {
        "employees": [
            {
                "employee_id": "E001",
                "employee_name": "张伟",
                "department": "后端架构部",
                "role_code": "ARCH"
            },
            {
                "employee_id": "E002",
                "employee_name": "李娜",
                "department": "前端开发部",
                "role_code": "FE"
            },
            {
                "employee_id": "E003",
                "employee_name": "王强",
                "department": "测试部",
                "role_code": "QA"
            }
        ]
    }
    with open("data/employees/employees.json", "w", encoding="utf-8") as f:
        json.dump(employees, f, ensure_ascii=False, indent=2)

    # --- 2. 月度产出账本（含干扰项：E001的两条记录，一条旧一条新；E002的正常记录） ---
    os.makedirs("data/ledgers", exist_ok=True)
    monthly_outputs = {
        "monthly_outputs": [
            # 张伟的旧记录（上个月，已过期）
            {
                "employee_id": "E001",
                "period": "2025-01",
                "feature_delivery": 60,
                "quality_score": 75,
                "collaboration_score": 80
            },
            # 张伟的最新记录（本月）
            {
                "employee_id": "E001",
                "period": "2025-02",
                "feature_delivery": 95,
                "quality_score": 92,
                "collaboration_score": 88
            },
            # 李娜的正常记录
            {
                "employee_id": "E002",
                "period": "2025-02",
                "feature_delivery": 85,
                "quality_score": 90,
                "collaboration_score": 95
            },
            # 王强的记录（干扰：QA角色，但规则文件里有QA规则）
            {
                "employee_id": "E003",
                "period": "2025-02",
                "feature_delivery": 70,
                "quality_score": 80,
                "collaboration_score": 75
            }
        ]
    }
    with open("data/ledgers/monthly_outputs.json", "w", encoding="utf-8") as f:
        json.dump(monthly_outputs, f, ensure_ascii=False, indent=2)

    # --- 3. 评分规则（含干扰：旧版本规则和当前版本规则，需根据effective_date判断） ---
    os.makedirs("data/rules", exist_ok=True)
    scoring_rules = {
        "scoring_rules": [
            # 旧规则（2025-01生效，已过期）
            {
                "role_code": "ARCH",
                "feature_delivery_weight": 0.3,
                "quality_weight": 0.4,
                "collaboration_weight": 0.3,
                "effective_date": "2025-01-01"
            },
            # 当前规则（2025-02生效）
            {
                "role_code": "ARCH",
                "feature_delivery_weight": 0.5,
                "quality_weight": 0.35,
                "collaboration_weight": 0.15,
                "effective_date": "2025-02-01"
            },
            # FE 规则（当前）
            {
                "role_code": "FE",
                "feature_delivery_weight": 0.4,
                "quality_weight": 0.3,
                "collaboration_weight": 0.3,
                "effective_date": "2025-02-01"
            },
            # QA 规则（当前）
            {
                "role_code": "QA",
                "feature_delivery_weight": 0.2,
                "quality_weight": 0.5,
                "collaboration_weight": 0.3,
                "effective_date": "2025-02-01"
            }
        ]
    }
    with open("data/rules/scoring_rules.json", "w", encoding="utf-8") as f:
        json.dump(scoring_rules, f, ensure_ascii=False, indent=2)

    # --- 4. 确保 profiles 目录存在（答案将被写在这里）---
    os.makedirs("profiles", exist_ok=True)
    # 可以放一个空占位，但不需要，因为agent会创建

if __name__ == "__main__":
    build_env()
