import os
import json

def build_env():
    # Employee data
    employees = [
        {"employee_id": "E001", "employee_name": "Alice", "department": "Sales", "role_code": "SALES"},
        {"employee_id": "E002", "employee_name": "Bob", "department": "Engineering", "role_code": "ENG"},
        {"employee_id": "E003", "employee_name": "Charlie", "department": "Operations", "role_code": "OPS"},
        # 干扰项：有员工ID但无 output 记录（故意在 monthly_outputs 中缺失）
        {"employee_id": "E004", "employee_name": "Diana", "department": "Sales", "role_code": "SALES"},
    ]

    # Monthly outputs
    monthly_outputs = [
        {"employee_id": "E001", "feature_delivery": 80, "quality_score": 90, "collaboration_score": 70},
        {"employee_id": "E002", "feature_delivery": 60, "quality_score": 75, "collaboration_score": 85},
        {"employee_id": "E003", "feature_delivery": 95, "quality_score": 60, "collaboration_score": 80},
        # 干扰：一个旧版本 output（应忽略，因为存放于干扰目录）
    ]

    # Scoring rules
    scoring_rules = [
        {"role_code": "SALES", "feature_delivery_weight": 0.4, "quality_weight": 0.35, "collaboration_weight": 0.25},
        {"role_code": "ENG",   "feature_delivery_weight": 0.3, "quality_weight": 0.4,  "collaboration_weight": 0.3},
        {"role_code": "OPS",   "feature_delivery_weight": 0.5, "quality_weight": 0.2,  "collaboration_weight": 0.3},
    ]

    # Build directory structure
    os.makedirs("data/employees", exist_ok=True)
    os.makedirs("data/ledgers/archive", exist_ok=True)
    os.makedirs("data/rules", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 仅占位，不写文件

    # Write main files
    with open("data/employees/employees.json", "w") as f:
        json.dump({"employees": employees}, f, indent=2)

    with open("data/ledgers/monthly_outputs.json", "w") as f:
        json.dump({"monthly_outputs": monthly_outputs}, f, indent=2)

    with open("data/rules/scoring_rules.json", "w") as f:
        json.dump({"scoring_rules": scoring_rules}, f, indent=2)

    # Write decoy files (old/unrelated)
    # Decoy employee backup
    backup_employees = [
        {"employee_id": "E001", "employee_name": "Alice (old)", "department": "Sales", "role_code": "SALES"}
    ]
    with open("data/employees/employees_backup.json", "w") as f:
        json.dump({"employees": backup_employees}, f, indent=2)

    # Decoy old outputs
    old_outputs = [
        {"employee_id": "E001", "feature_delivery": 50, "quality_score": 60, "collaboration_score": 55},
        {"employee_id": "E002", "feature_delivery": 40, "quality_score": 70, "collaboration_score": 65},
    ]
    with open("data/ledgers/archive/old_outputs.json", "w") as f:
        json.dump({"monthly_outputs": old_outputs}, f, indent=2)

    # Decoy outdated scoring rule (missing OPS)
    old_rules = [
        {"role_code": "SALES", "feature_delivery_weight": 0.5, "quality_weight": 0.3, "collaboration_weight": 0.2},
        {"role_code": "ENG",   "feature_delivery_weight": 0.2, "quality_weight": 0.5, "collaboration_weight": 0.3},
    ]
    with open("data/rules/scoring_rules_v2.json", "w") as f:
        json.dump({"scoring_rules": old_rules}, f, indent=2)

if __name__ == "__main__":
    build_env()
