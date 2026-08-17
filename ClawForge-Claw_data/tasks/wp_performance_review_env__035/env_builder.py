import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/employees", exist_ok=True)
    os.makedirs("data/ledgers", exist_ok=True)
    os.makedirs("data/rules", exist_ok=True)
    os.makedirs("performance", exist_ok=True)

    # ---------- 员工花名册 ----------
    employees = [
        {"employee_id": "emp001", "employee_name": "Alice", "department": "Engineering", "role_code": "SE"},
        {"employee_id": "emp002", "employee_name": "Bob", "department": "Engineering", "role_code": "SE"},
        {"employee_id": "emp003", "employee_name": "Charlie", "department": "QA", "role_code": "QA"},
        {"employee_id": "emp004", "employee_name": "Diana", "department": "HR", "role_code": "HR"},
        {"employee_id": "emp005", "employee_name": "Eve", "department": "Engineering", "role_code": "SE"},  # 员工存在但无台账
    ]
    with open("data/employees/employees.json", "w") as f:
        json.dump({"employees": employees}, f, indent=2)

    # ---------- 产出台账 ----------
    monthly_outputs = [
        {"employee_id": "emp001", "feature_delivery": 100, "quality_score": 80, "collaboration_score": 90},
        {"employee_id": "emp002", "feature_delivery": 90, "quality_score": 85, "collaboration_score": 70},
        {"employee_id": "emp003", "feature_delivery": 70, "quality_score": 90, "collaboration_score": 80},
        {"employee_id": "emp004", "feature_delivery": 60, "quality_score": 70, "collaboration_score": 80},  # 有台账但无规则
        {"employee_id": "emp999", "feature_delivery": 50, "quality_score": 50, "collaboration_score": 50},  # 不在员工列表中
    ]
    with open("data/ledgers/monthly_outputs.json", "w") as f:
        json.dump({"monthly_outputs": monthly_outputs}, f, indent=2)

    # ---------- 评分规则 ----------
    scoring_rules = [
        {"role_code": "SE", "feature_delivery_weight": 0.5, "quality_weight": 0.3, "collaboration_weight": 0.2},
        {"role_code": "QA", "feature_delivery_weight": 0.4, "quality_weight": 0.4, "collaboration_weight": 0.2},
    ]
    with open("data/rules/scoring_rules.json", "w") as f:
        json.dump({"scoring_rules": scoring_rules}, f, indent=2)

if __name__ == "__main__":
    build_env()
