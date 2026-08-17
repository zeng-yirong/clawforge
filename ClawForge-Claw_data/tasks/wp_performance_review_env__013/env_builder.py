import os
import json
import random

def build_env():
    # ----- 员工主表 -----
    employees = [
        {"employee_id": "E001", "employee_name": "Alice", "department": "Engineering", "role_code": "R01"},
        {"employee_id": "E002", "employee_name": "Bob",   "department": "Engineering", "role_code": "R01"},
        {"employee_id": "E003", "employee_name": "Carol", "department": "QA",          "role_code": "R02"},
        {"employee_id": "E004", "employee_name": "Dave",  "department": "Engineering", "role_code": "R03"},
        {"employee_id": "E005", "employee_name": "Eve",   "department": "Design",      "role_code": "R02"},
        {"employee_id": "E006", "employee_name": "Frank", "department": "Support",     "role_code": "R03"},
        # 诱饵：没有输出记录的角色
        {"employee_id": "E007", "employee_name": "Grace", "department": "Engineering", "role_code": "R01"},
        # 诱饵：角色代码不存在于规则中
        {"employee_id": "E008", "employee_name": "Heidi", "department": "Marketing",   "role_code": "R99"},
    ]
    os.makedirs("data/employees", exist_ok=True)
    with open("data/employees/employees.json", "w") as f:
        json.dump({"employees": employees}, f, indent=2)

    # ----- 月度输出 -----
    monthly_outputs = [
        {"employee_id": "E001", "feature_delivery": 80, "quality_score": 90, "collaboration_score": 70},
        {"employee_id": "E002", "feature_delivery": 60, "quality_score": 75, "collaboration_score": 85},
        {"employee_id": "E003", "feature_delivery": 95, "quality_score": 88, "collaboration_score": 92},
        {"employee_id": "E004", "feature_delivery": 70, "quality_score": 65, "collaboration_score": 80},
        {"employee_id": "E005", "feature_delivery": 100, "quality_score": 95, "collaboration_score": 90},
        {"employee_id": "E006", "feature_delivery": 50, "quality_score": 60, "collaboration_score": 55},
        # 诱饵：额外输出记录，员工不存在
        {"employee_id": "E099", "feature_delivery": 40, "quality_score": 40, "collaboration_score": 40},
    ]
    os.makedirs("data/ledgers", exist_ok=True)
    with open("data/ledgers/monthly_outputs.json", "w") as f:
        json.dump({"monthly_outputs": monthly_outputs}, f, indent=2)

    # ----- 评分规则 -----
    # 最新规则文件
    scoring_rules = [
        {"role_code": "R01", "feature_delivery_weight": 0.40, "quality_weight": 0.35, "collaboration_weight": 0.25},
        {"role_code": "R02", "feature_delivery_weight": 0.30, "quality_weight": 0.40, "collaboration_weight": 0.30},
        {"role_code": "R03", "feature_delivery_weight": 0.50, "quality_weight": 0.30, "collaboration_weight": 0.20},
    ]
    os.makedirs("data/rules", exist_ok=True)
    with open("data/rules/scoring_rules.json", "w") as f:
        json.dump({"scoring_rules": scoring_rules}, f, indent=2)

    # 干扰：旧版本规则（权重不同）
    old_rules = [
        {"role_code": "R01", "feature_delivery_weight": 0.50, "quality_weight": 0.25, "collaboration_weight": 0.25},
        {"role_code": "R02", "feature_delivery_weight": 0.35, "quality_weight": 0.35, "collaboration_weight": 0.30},
        {"role_code": "R03", "feature_delivery_weight": 0.40, "quality_weight": 0.40, "collaboration_weight": 0.20},
    ]
    with open("data/rules/scoring_rules_old.json", "w") as f:
        json.dump({"scoring_rules": old_rules}, f, indent=2)

    # 干扰：更旧的版本 v1
    old_rules_v1 = [
        {"role_code": "R01", "feature_delivery_weight": 0.60, "quality_weight": 0.20, "collaboration_weight": 0.20},
        {"role_code": "R02", "feature_delivery_weight": 0.40, "quality_weight": 0.30, "collaboration_weight": 0.30},
        {"role_code": "R03", "feature_delivery_weight": 0.30, "quality_weight": 0.50, "collaboration_weight": 0.20},
    ]
    with open("data/rules/scoring_rules_v1.json", "w") as f:
        json.dump({"scoring_rules": old_rules_v1}, f, indent=2)

    # 诱饵：一个txt文件
    with open("data/rules/README.txt", "w") as f:
        f.write("Please use scoring_rules.json for the latest weights.")

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
