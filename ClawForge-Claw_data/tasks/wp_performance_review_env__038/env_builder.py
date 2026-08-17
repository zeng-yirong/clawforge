import os
import json

def build_env():
    # Create data directories
    os.makedirs("data/employees", exist_ok=True)
    os.makedirs("data/ledgers", exist_ok=True)
    os.makedirs("data/rules", exist_ok=True)

    # Employees (4 employees, only E001 and E002 have matching output & rule)
    employees = [
        {
            "employee_id": "E001",
            "employee_name": "Alice",
            "department": "Engineering",
            "role_code": "DEV"
        },
        {
            "employee_id": "E002",
            "employee_name": "Bob",
            "department": "Marketing",
            "role_code": "MKT"
        },
        {
            "employee_id": "E003",
            "employee_name": "Charlie",
            "department": "QA",
            "role_code": "QA"          # no rule for QA
        },
        {
            "employee_id": "E004",
            "employee_name": "Diana",
            "department": "HR",
            "role_code": "HR"          # no rule for HR
        }
    ]
    with open("data/employees/employees.json", "w") as f:
        json.dump({"employees": employees}, f, indent=2)

    # Monthly outputs (E001, E002, and a decoy E005 with no employee record)
    outputs = [
        {
            "employee_id": "E001",
            "feature_delivery": 80,
            "quality_score": 90,
            "collaboration_score": 70
        },
        {
            "employee_id": "E002",
            "feature_delivery": 60,
            "quality_score": 70,
            "collaboration_score": 80
        },
        {
            "employee_id": "E005",
            "feature_delivery": 90,
            "quality_score": 80,
            "collaboration_score": 85
        }
    ]
    with open("data/ledgers/monthly_outputs.json", "w") as f:
        json.dump({"monthly_outputs": outputs}, f, indent=2)

    # Scoring rules (DEV, MKT, and a decoy ADMIN)
    rules = [
        {
            "role_code": "DEV",
            "feature_delivery_weight": 0.5,
            "quality_weight": 0.3,
            "collaboration_weight": 0.2
        },
        {
            "role_code": "MKT",
            "feature_delivery_weight": 0.4,
            "quality_weight": 0.4,
            "collaboration_weight": 0.2
        },
        {
            "role_code": "ADMIN",
            "feature_delivery_weight": 0.2,
            "quality_weight": 0.5,
            "collaboration_weight": 0.3
        }
    ]
    with open("data/rules/scoring_rules.json", "w") as f:
        json.dump({"scoring_rules": rules}, f, indent=2)

    # Decoy accounts & contacts files (realistic clutter)
    os.makedirs("data/accounts", exist_ok=True)
    with open("data/accounts/accounts.json", "w") as f:
        json.dump({"accounts": []}, f, indent=2)
    os.makedirs("data/contacts", exist_ok=True)
    with open("data/contacts/contacts.json", "w") as f:
        json.dump({"contacts": []}, f, indent=2)

if __name__ == "__main__":
    build_env()
