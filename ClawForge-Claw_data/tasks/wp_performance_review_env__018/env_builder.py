import os
import json

def build_env():
    # 创建目录结构
    dirs = ["employees", "ledgers", "ledgers/old", "rules", "reports"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 员工信息 (5名员工 + 1名无效员工无产出)
    employees = {
        "employees": [
            {"employee_id": "E001", "employee_name": "Alice", "department": "Engineering", "role_code": "ENG"},
            {"employee_id": "E002", "employee_name": "Bob", "department": "Management", "role_code": "MGR"},
            {"employee_id": "E003", "employee_name": "Charlie", "department": "Engineering", "role_code": "ENG"},
            {"employee_id": "E004", "employee_name": "Diana", "department": "QA", "role_code": "QA"},
            {"employee_id": "E005", "employee_name": "Eve", "department": "Management", "role_code": "MGR"},
            {"employee_id": "E006", "employee_name": "Frank", "department": "HR", "role_code": "HR"}  # 干扰员工，无产出
        ]
    }
    with open("employees/employees.json", "w") as f:
        json.dump(employees, f, indent=2)

    # 评分规则
    rules = {
        "scoring_rules": [
            {"role_code": "ENG", "feature_delivery_weight": 0.4, "quality_weight": 0.35, "collaboration_weight": 0.25},
            {"role_code": "MGR", "feature_delivery_weight": 0.3, "quality_weight": 0.4, "collaboration_weight": 0.3},
            {"role_code": "QA", "feature_delivery_weight": 0.2, "quality_weight": 0.5, "collaboration_weight": 0.3}
        ]
    }
    with open("rules/scoring_rules.json", "w") as f:
        json.dump(rules, f, indent=2)

    # 正确月份（2025年3月）产出
    correct_monthly = {
        "monthly_outputs": [
            {"employee_id": "E001", "feature_delivery": 80, "quality_score": 75, "collaboration_score": 70},
            {"employee_id": "E002", "feature_delivery": 90, "quality_score": 85, "collaboration_score": 80},
            {"employee_id": "E003", "feature_delivery": 60, "quality_score": 55, "collaboration_score": 50},
            {"employee_id": "E004", "feature_delivery": 70, "quality_score": 80, "collaboration_score": 90},
            {"employee_id": "E005", "feature_delivery": 100, "quality_score": 95, "collaboration_score": 90}
        ]
    }
    with open("ledgers/2025_03_outputs.json", "w") as f:
        json.dump(correct_monthly, f, indent=2)

    # 干扰月份（2025年2月）产出，数值不同
    old_monthly = {
        "monthly_outputs": [
            {"employee_id": "E001", "feature_delivery": 70, "quality_score": 65, "collaboration_score": 60},
            {"employee_id": "E003", "feature_delivery": 50, "quality_score": 45, "collaboration_score": 40}
        ]
    }
    with open("ledgers/2025_02_outputs.json", "w") as f:
        json.dump(old_monthly, f, indent=2)

    # 额外干扰：无效记录文件
    with open("ledgers/old/draft_outputs.json", "w") as f:
        json.dump({"dummy": "data"}, f, indent=2)

    # 杂项文件
    with open("README.txt", "w") as f:
        f.write("Performance review data for March 2025.\n")

if __name__ == "__main__":
    build_env()
