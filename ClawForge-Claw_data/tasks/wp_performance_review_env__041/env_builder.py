import json
import os

def build_env():
    # 创建目录
    os.makedirs("data/employees", exist_ok=True)
    os.makedirs("data/ledgers", exist_ok=True)
    os.makedirs("data/rules", exist_ok=True)
    os.makedirs("reports", exist_ok=True)  # 留空，由 agent 写入

    # 1. 员工花名册（含一个无产出记录的干扰员工 E005）
    employees = {
        "employees": [
            {"employee_id": "E001", "employee_name": "Alice", "department": "Engineering", "role_code": "SE"},
            {"employee_id": "E002", "employee_name": "Bob",   "department": "Engineering", "role_code": "SE"},
            {"employee_id": "E003", "employee_name": "Carol", "department": "QA",         "role_code": "QA"},
            {"employee_id": "E004", "employee_name": "Dave",  "department": "Ops",        "role_code": "OPS"},
            {"employee_id": "E005", "employee_name": "Eve",   "department": "Engineering", "role_code": "SE"}
        ]
    }
    with open("data/employees/employees.json", "w") as f:
        json.dump(employees, f, indent=2)

    # 2. 月度产出明细（只给前4人数据，E005无记录）
    monthly_outputs = {
        "monthly_outputs": [
            {"employee_id": "E001", "feature_delivery": 90, "quality_score": 85, "collaboration_score": 80},
            {"employee_id": "E002", "feature_delivery": 70, "quality_score": 60, "collaboration_score": 75},
            {"employee_id": "E003", "feature_delivery": 80, "quality_score": 90, "collaboration_score": 70},
            {"employee_id": "E004", "feature_delivery": 50, "quality_score": 60, "collaboration_score": 80}
        ]
    }
    with open("data/ledgers/monthly_outputs.json", "w") as f:
        json.dump(monthly_outputs, f, indent=2)

    # 3. 评分规则
    scoring_rules = {
        "scoring_rules": [
            {"role_code": "SE",  "feature_delivery_weight": 0.4, "quality_weight": 0.3, "collaboration_weight": 0.3},
            {"role_code": "QA",  "feature_delivery_weight": 0.2, "quality_weight": 0.5, "collaboration_weight": 0.3},
            {"role_code": "OPS", "feature_delivery_weight": 0.3, "quality_weight": 0.3, "collaboration_weight": 0.4}
        ]
    }
    with open("data/rules/scoring_rules.json", "w") as f:
        json.dump(scoring_rules, f, indent=2)

    # 4. 干扰文件：上月备份（避免 agent 误读）
    os.makedirs("data/ledgers/archive", exist_ok=True)
    old_data = {
        "monthly_outputs": [
            {"employee_id": "E001", "feature_delivery": 80, "quality_score": 70, "collaboration_score": 60}
        ]
    }
    with open("data/ledgers/archive/monthly_outputs_2022.json", "w") as f:
        json.dump(old_data, f, indent=2)

if __name__ == "__main__":
    build_env()
