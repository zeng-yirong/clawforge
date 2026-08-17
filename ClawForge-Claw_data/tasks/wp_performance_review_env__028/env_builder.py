import os
import json
import shutil

def build_env():
    # Clean slate
    if os.path.exists("data"):
        shutil.rmtree("data")
    if os.path.exists("performance_profiles.json"):
        os.remove("performance_profiles.json")

    ########## Employee data (with distractors) ##########
    os.makedirs("data/employees", exist_ok=True)
    employees = [
        {"employee_id": "E001", "employee_name": "Alice Chen", "department": "Engineering", "role_code": "ENG"},
        {"employee_id": "E002", "employee_name": "Bob Liu", "department": "Management", "role_code": "MGR"},
        {"employee_id": "E003", "employee_name": "Carol Wang", "department": "Design", "role_code": "DSG"},
        {"employee_id": "E004", "employee_name": "Dave Li", "department": "Engineering", "role_code": "ENG"},
        {"employee_id": "E999", "employee_name": "Zoe Xu", "department": "HR", "role_code": "MGR"}  # 离职，无产出记录
    ]
    with open("data/employees/employees.json", "w") as f:
        json.dump({"employees": employees}, f, indent=2)

    # Old version employee list (distractor)
    old_employees = [
        {"employee_id": "E005", "employee_name": "Eve Zhang", "department": "Ops", "role_code": "OPS"},
        {"employee_id": "E006", "employee_name": "Frank Wu", "department": "Engineering", "role_code": "ENG"}
    ]
    with open("data/employees/old_employees.json", "w") as f:
        json.dump({"employees": old_employees}, f, indent=2)

    ########## Monthly outputs (with dirty data) ##########
    os.makedirs("data/ledgers", exist_ok=True)
    monthly_outputs = [
        {"employee_id": "E001", "feature_delivery": 95, "quality_score": 88, "collaboration_score": 90},
        {"employee_id": "E002", "feature_delivery": 70, "quality_score": 85, "collaboration_score": 92},
        {"employee_id": "E003", "feature_delivery": 80, "quality_score": 75, "collaboration_score": 70},
        {"employee_id": "E004", "feature_delivery": 60, "quality_score": 50, "collaboration_score": 40},
        # Dirty records
        {"employee_id": "E999", "feature_delivery": 100, "quality_score": 100, "collaboration_score": 100},  # 离职但仍有产出（应排除）
        {"employee_id": "E001", "feature_delivery": 99, "quality_score": -5, "collaboration_score": 10},      # 重复记录且含负数脏数据
        {"employee_id": "E002", "feature_delivery": 85, "quality_score": 90, "collaboration_score": -20}      # 负分干扰
    ]
    with open("data/ledgers/monthly_outputs.json", "w") as f:
        json.dump({"monthly_outputs": monthly_outputs}, f, indent=2)

    ########## Scoring rules ##########
    os.makedirs("data/rules", exist_ok=True)
    scoring_rules = [
        {"role_code": "ENG", "feature_delivery_weight": 0.5, "quality_weight": 0.3, "collaboration_weight": 0.2},
        {"role_code": "MGR", "feature_delivery_weight": 0.3, "quality_weight": 0.4, "collaboration_weight": 0.3},
        {"role_code": "DSG", "feature_delivery_weight": 0.4, "quality_weight": 0.4, "collaboration_weight": 0.2},
        {"role_code": "OPS", "feature_delivery_weight": 0.2, "quality_weight": 0.5, "collaboration_weight": 0.3}  # 无用规则，无对应在职员工
    ]
    with open("data/rules/scoring_rules.json", "w") as f:
        json.dump({"scoring_rules": scoring_rules}, f, indent=2)

    # Extra rule file with wrong weights (distractor)
    old_rules = [
        {"role_code": "ENG", "feature_delivery_weight": 0.1, "quality_weight": 0.1, "collaboration_weight": 0.8}
    ]
    with open("data/rules/old_scoring_rules.json", "w") as f:
        json.dump({"scoring_rules": old_rules}, f, indent=2)

if __name__ == "__main__":
    build_env()
