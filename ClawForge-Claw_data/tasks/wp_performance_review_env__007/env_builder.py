import os
import json

def build_env():
    # Create directory structure
    os.makedirs("data/employees", exist_ok=True)
    os.makedirs("data/ledgers", exist_ok=True)
    os.makedirs("data/rules", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # for output
    os.makedirs("data/archived", exist_ok=True)  # distractor

    # employees.json (3 employees)
    employees = [
        {"employee_id": "E001", "employee_name": "Alice", "department": "Engineering", "role_code": "DEV"},
        {"employee_id": "E002", "employee_name": "Bob", "department": "QA", "role_code": "QA"},
        {"employee_id": "E003", "employee_name": "Charlie", "department": "Product", "role_code": "PM"},
    ]
    with open("data/employees/employees.json", "w") as f:
        json.dump({"employees": employees}, f, indent=2)

    # monthly_outputs.json
    outputs = [
        {"employee_id": "E001", "feature_delivery": 80, "quality_score": 70, "collaboration_score": 90},
        {"employee_id": "E002", "feature_delivery": 60, "quality_score": 85, "collaboration_score": 95},
        {"employee_id": "E003", "feature_delivery": 90, "quality_score": 80, "collaboration_score": 85},
    ]
    with open("data/ledgers/monthly_outputs.json", "w") as f:
        json.dump({"monthly_outputs": outputs}, f, indent=2)

    # scoring_rules.json
    rules = [
        {"role_code": "DEV", "feature_delivery_weight": 0.5, "quality_weight": 0.3, "collaboration_weight": 0.2},
        {"role_code": "QA", "feature_delivery_weight": 0.2, "quality_weight": 0.6, "collaboration_weight": 0.2},
        {"role_code": "PM", "feature_delivery_weight": 0.4, "quality_weight": 0.4, "collaboration_weight": 0.2},
    ]
    with open("data/rules/scoring_rules.json", "w") as f:
        json.dump({"scoring_rules": rules}, f, indent=2)

    # Distractor: an archived ledger with wrong numbers
    old_outputs = [
        {"employee_id": "E001", "feature_delivery": 100, "quality_score": 60, "collaboration_score": 80},
    ]
    with open("data/archived/deprecated_outputs.json", "w") as f:
        json.dump({"monthly_outputs": old_outputs}, f, indent=2)

    # Distractor: an old scoring rule with different weights
    old_rules = [
        {"role_code": "DEV", "feature_delivery_weight": 0.4, "quality_weight": 0.4, "collaboration_weight": 0.2},
    ]
    with open("data/archived/old_scoring_rules.json", "w") as f:
        json.dump({"scoring_rules": old_rules}, f, indent=2)

    # Ensure ops dir is empty initially
    pass

if __name__ == "__main__":
    build_env()
