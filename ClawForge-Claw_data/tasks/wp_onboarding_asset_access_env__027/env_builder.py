import os
import json

def build_env():
    # Create directories
    os.makedirs("data/onboarding", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # contracts.json
    contracts = [
        {
            "employee_id": "EMP001",
            "employee_name": "Alice Wang",
            "status": "signed",
            "email": "alice.wang@company.com",
            "department": "Engineering"
        },
        {
            "employee_id": "EMP002",
            "employee_name": "Bob Li",
            "status": "signed",
            "email": "bob.li@company.com",
            "department": "Sales"
        },
        {
            "employee_id": "EMP003",
            "employee_name": "Charlie Zhang",
            "status": "pending",
            "email": "charlie.zhang@company.com",
            "department": "Engineering"
        },
        {
            "employee_id": "EMP004",
            "employee_name": "Diana Chen",
            "status": "rejected",
            "email": "diana.chen@company.com",
            "department": "HR"
        }
    ]
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump({"contracts": contracts}, f, indent=2)

    # permission_packs.json
    permission_packs = [
        {
            "pack_id": "Engineering",
            "systems": ["ERP", "CodeRepo", "CI/CD"]
        },
        {
            "pack_id": "Sales",
            "systems": ["CRM", "EmailMarketing", "SalesDashboard"]
        },
        {
            "pack_id": "HR",
            "systems": ["HRIS", "Payroll"]
        }
    ]
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump({"permission_packs": permission_packs}, f, indent=2)

    # equipment_inventory.json
    equipment = [
        {
            "asset_tag": "LT-001",
            "asset_type": "Laptop",
            "status": "available",
            "department": "Engineering"
        },
        {
            "asset_tag": "TB-001",
            "asset_type": "Tablet",
            "status": "available",
            "department": "Sales"
        },
        {
            "asset_tag": "LT-002",
            "asset_type": "Laptop",
            "status": "assigned",
            "department": "Engineering"
        },
        {
            "asset_tag": "PR-001",
            "asset_type": "Printer",
            "status": "available",
            "department": "Common"
        }
    ]
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump({"equipment_inventory": equipment}, f, indent=2)

    # accounts.json (distraction)
    accounts = [
        {"account_id": "ACC001", "display_name": "Alice Wang", "department": "Engineering", "email": "alice.wang@company.com", "permissions": ["read"]},
        {"account_id": "ACC002", "display_name": "Bob Li", "department": "Sales", "email": "bob.li@company.com", "permissions": ["read","write"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # contacts.json (distraction)
    contacts = [
        {"contact_id": "C001", "name": "Alice Wang", "role": "Engineer", "email": "alice.wang@company.com"},
        {"contact_id": "C002", "name": "Bob Li", "role": "Sales Rep", "email": "bob.li@company.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
