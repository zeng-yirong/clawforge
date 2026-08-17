import os
import json
import random

def build_env():
    # 创建必要的子目录
    os.makedirs("data/employees", exist_ok=True)
    os.makedirs("data/ledgers", exist_ok=True)
    os.makedirs("data/rules", exist_ok=True)
    # profiles 目录由 agent 创建，我们不留空目录

    # 员工数据
    employees = {
        "employees": [
            {
                "employee_id": "E001",
                "employee_name": "Alice",
                "department": "Engineering",
                "role_code": "engineer"
            },
            {
                "employee_id": "E002",
                "employee_name": "Bob",
                "department": "Marketing",
                "role_code": "marketer"
            },
            {
                "employee_id": "E003",
                "employee_name": "Charlie",
                "department": "Engineering",
                "role_code": "engineer"
            }
        ]
    }
    with open("data/employees/employees.json", "w") as f:
        json.dump(employees, f, indent=2)

    # 月度产出账本
    monthly_outputs = {
        "monthly_outputs": [
            {
                "employee_id": "E001",
                "feature_delivery": 80,
                "quality_score": 90,
                "collaboration_score": 70
            },
            {
                "employee_id": "E002",
                "feature_delivery": 75,
                "quality_score": 85,
                "collaboration_score": 80
            },
            {
                "employee_id": "E003",
                "feature_delivery": 95,
                "quality_score": 88,
                "collaboration_score": 92
            },
            # 干扰项：不存在的员工记录
            {
                "employee_id": "E099",
                "feature_delivery": 50,
                "quality_score": 60,
                "collaboration_score": 55
            }
        ]
    }
    with open("data/ledgers/monthly_outputs.json", "w") as f:
        json.dump(monthly_outputs, f, indent=2)

    # 评分规则：包含一个最新版本和两个旧版本干扰
    valid_rules = [
        {
            "role_code": "engineer",
            "feature_delivery_weight": 0.5,
            "quality_weight": 0.3,
            "collaboration_weight": 0.2,
            "version": "v2025-03"
        },
        {
            "role_code": "marketer",
            "feature_delivery_weight": 0.4,
            "quality_weight": 0.4,
            "collaboration_weight": 0.2,
            "version": "v2025-03"
        }
    ]
    old_rules = [
        {
            "role_code": "engineer",
            "feature_delivery_weight": 0.6,
            "quality_weight": 0.2,
            "collaboration_weight": 0.2,
            "version": "v2025-01"
        },
        {
            "role_code": "engineer",
            "feature_delivery_weight": 0.3,
            "quality_weight": 0.4,
            "collaboration_weight": 0.3,
            "version": "v2025-02"
        }
    ]
    # 主文件只放最新规则
    scoring_rules = { "scoring_rules": valid_rules }
    with open("data/rules/scoring_rules.json", "w") as f:
        json.dump(scoring_rules, f, indent=2)
    # 旧版本干扰文件
    for i, old in enumerate(old_rules, 1):
        with open(f"data/rules/scoring_rules_backup_{i}.json", "w") as f:
            json.dump({"scoring_rules": [old]}, f, indent=2)

    # 额外干扰：一个空的或格式错误的文件
    with open("data/rules/old_weights.txt", "w") as f:
        f.write("role_code,feature_weight,quality_weight,collaboration_weight\nengineer,0.5,0.3,0.2\n")

    print("环境文件构建完成。")

if __name__ == "__main__":
    build_env()
