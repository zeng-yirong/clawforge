import os
import json

def build_env():
    # 员工目录
    os.makedirs("data/employees", exist_ok=True)
    employees = [
        {"employee_id": "E001", "employee_name": "Alice", "department": "Engineering", "role_code": "DEV"},
        {"employee_id": "E002", "employee_name": "Bob", "department": "Engineering", "role_code": "DEV"},
        {"employee_id": "E003", "employee_name": "Charlie", "department": "QA", "role_code": "QA"}
    ]
    with open("data/employees/employees.json", "w") as f:
        json.dump({"employees": employees}, f, indent=2)

    # 产出目录（包含干扰记录）
    os.makedirs("data/ledgers", exist_ok=True)
    monthly_outputs = [
        {"employee_id": "E001", "feature_delivery": 80, "quality_score": 90, "collaboration_score": 85},
        {"employee_id": "E002", "feature_delivery": 70, "quality_score": 75, "collaboration_score": 80},
        {"employee_id": "E003", "feature_delivery": 90, "quality_score": 85, "collaboration_score": 95},
        {"employee_id": "E999", "feature_delivery": 100, "quality_score": 100, "collaboration_score": 100}  # 干扰项
    ]
    with open("data/ledgers/monthly_outputs.json", "w") as f:
        json.dump({"monthly_outputs": monthly_outputs}, f, indent=2)

    # 权重规则
    os.makedirs("data/rules", exist_ok=True)
    scoring_rules = [
        {"role_code": "DEV", "feature_delivery_weight": 0.4, "quality_weight": 0.3, "collaboration_weight": 0.3},
        {"role_code": "QA", "feature_delivery_weight": 0.2, "quality_weight": 0.5, "collaboration_weight": 0.3}
    ]
    with open("data/rules/scoring_rules.json", "w") as f:
        json.dump({"scoring_rules": scoring_rules}, f, indent=2)

if __name__ == "__main__":
    build_env()
