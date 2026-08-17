import os
import json
import shutil

def build_env():
    # Clean slate
    if os.path.exists("data"):
        shutil.rmtree("data")

    # --- employees ---
    employees = {
        "employees": [
            {"employee_id": "E001", "employee_name": "Alice", "department": "Engineering", "role_code": "dev"},
            {"employee_id": "E002", "employee_name": "Bob",   "department": "QA",         "role_code": "qa"},
            {"employee_id": "E003", "employee_name": "Carol", "department": "Engineering", "role_code": "dev"},
            # 干扰：有员工记录但无output
            {"employee_id": "E004", "employee_name": "David", "department": "Engineering", "role_code": "dev"},
        ]
    }
    os.makedirs("data/employees", exist_ok=True)
    with open("data/employees/employees.json", "w") as f:
        json.dump(employees, f, indent=2)

    # --- monthly outputs (正确月份) ---
    monthly_outputs = {
        "monthly_outputs": [
            {"employee_id": "E001", "feature_delivery": 90, "quality_score": 90, "collaboration_score": 90},
            {"employee_id": "E002", "feature_delivery": 70, "quality_score": 85, "collaboration_score": 90},
            {"employee_id": "E003", "feature_delivery": 95, "quality_score": 95, "collaboration_score": 95},
            # 干扰：有output但无员工记录
            {"employee_id": "E005", "feature_delivery": 100, "quality_score": 100, "collaboration_score": 100},
        ]
    }
    os.makedirs("data/ledgers", exist_ok=True)
    with open("data/ledgers/monthly_outputs.json", "w") as f:
        json.dump(monthly_outputs, f, indent=2)

    # --- 过期的输出（干扰） ---
    old_outputs = {
        "monthly_outputs": [
            {"employee_id": "E001", "feature_delivery": 60, "quality_score": 70, "collaboration_score": 80},
        ]
    }
    os.makedirs("data/archived", exist_ok=True)
    with open("data/archived/old_monthly_outputs.json", "w") as f:
        json.dump(old_outputs, f, indent=2)

    # --- scoring rules ---
    scoring_rules = {
        "scoring_rules": [
            {"role_code": "dev", "feature_delivery_weight": 0.4, "quality_weight": 0.4, "collaboration_weight": 0.2},
            {"role_code": "qa",  "feature_delivery_weight": 0.3, "quality_weight": 0.5, "collaboration_weight": 0.2},
            # 干扰：规则多余角色
            {"role_code": "manager", "feature_delivery_weight": 0.5, "quality_weight": 0.3, "collaboration_weight": 0.2},
        ]
    }
    os.makedirs("data/rules", exist_ok=True)
    with open("data/rules/scoring_rules.json", "w") as f:
        json.dump(scoring_rules, f, indent=2)

if __name__ == "__main__":
    build_env()
