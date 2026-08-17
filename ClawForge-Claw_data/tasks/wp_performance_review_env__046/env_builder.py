import os
import json
import random

def build_env():
    # Ensure target directories exist
    os.makedirs("data/employees", exist_ok=True)
    os.makedirs("data/ledgers", exist_ok=True)
    os.makedirs("data/rules", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- Employees ---
    employees = [
        {"employee_id": "E001", "employee_name": "Alice", "department": "Engineering", "role_code": "DEV"},
        {"employee_id": "E002", "employee_name": "Bob",   "department": "QA",           "role_code": "QA"},
        {"employee_id": "E003", "employee_name": "Charlie", "department": "Marketing",  "role_code": "MKT"},
        {"employee_id": "E004", "employee_name": "Diana",  "department": "Engineering", "role_code": "DEV"},
    ]
    with open("data/employees/employees.json", "w") as f:
        json.dump({"employees": employees}, f, indent=2)

    # --- Scoring Rules (with per‑role weights and grade thresholds) ---
    scoring_rules = [
        {"role_code": "DEV", "feature_delivery_weight": 0.5, "quality_weight": 0.3, "collaboration_weight": 0.2,
         "grade_cutoffs": {"A": 90, "B": 75}},
        {"role_code": "QA",  "feature_delivery_weight": 0.4, "quality_weight": 0.4, "collaboration_weight": 0.2,
         "grade_cutoffs": {"A": 85, "B": 70}},
        {"role_code": "MKT", "feature_delivery_weight": 0.3, "quality_weight": 0.4, "collaboration_weight": 0.3,
         "grade_cutoffs": {"A": 80, "B": 65}},
    ]
    with open("data/rules/scoring_rules.json", "w") as f:
        json.dump({"scoring_rules": scoring_rules}, f, indent=2)

    # --- Monthly Outputs (array, includes test months, invalid records, unknown employee) ---
    monthly_outputs = [
        # January (test data – should be ignored)
        {"employee_id": "E001", "month": "2025-01", "feature_delivery": 80, "quality_score": 70, "collaboration_score": 60},
        {"employee_id": "E002", "month": "2025-01", "feature_delivery": 85, "quality_score": 75, "collaboration_score": 65},
        # February (test data – should be ignored)
        {"employee_id": "E001", "month": "2025-02", "feature_delivery": 88, "quality_score": 78, "collaboration_score": 72},
        {"employee_id": "E002", "month": "2025-02", "feature_delivery": 92, "quality_score": 80, "collaboration_score": 70},
        {"employee_id": "E003", "month": "2025-02", "feature_delivery": 55, "quality_score": 65, "collaboration_score": 75},
        # March (correct month)
        # E001 – two records, one with negative quality (invalid)
        {"employee_id": "E001", "month": "2025-03", "feature_delivery": 90, "quality_score": -5,  "collaboration_score": 80},
        {"employee_id": "E001", "month": "2025-03", "feature_delivery": 90, "quality_score": 80,  "collaboration_score": 80},
        {"employee_id": "E002", "month": "2025-03", "feature_delivery": 70, "quality_score": 75,  "collaboration_score": 60},
        {"employee_id": "E003", "month": "2025-03", "feature_delivery": 50, "quality_score": 60,  "collaboration_score": 70},
        {"employee_id": "E004", "month": "2025-03", "feature_delivery": 95, "quality_score": 90,  "collaboration_score": 85},
        # E005 – exists only in ledger, not in employees (must be ignored)
        {"employee_id": "E005", "month": "2025-03", "feature_delivery": 60, "quality_score": 70,  "collaboration_score": 80},
    ]
    # Shuffle to avoid trivial ordering
    random.shuffle(monthly_outputs)
    with open("data/ledgers/monthly_outputs.json", "w") as f:
        json.dump({"monthly_outputs": monthly_outputs}, f, indent=2)

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
