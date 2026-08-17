import json
import os

def build_env():
    # Create directory structure
    os.makedirs("data/onboarding", exist_ok=True)
    # data/accounts.json (distractor)
    accounts = [
        {"account_id": "A-001", "display_name": "John Doe", "department": "Engineering", "email": "john.doe@company.com", "permissions": ["basic"]},
        {"account_id": "A-002", "display_name": "Jane Smith", "department": "Marketing", "email": "jane.smith@company.com", "permissions": ["basic"]},
        {"account_id": "A-003", "display_name": "Bob Lee", "department": "HR", "email": "bob.lee@company.com", "permissions": ["basic"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # data/contacts.json (distractor, not used but present)
    contacts = [
        {"contact_id": "C-001", "name": "Hiring Manager", "role": "manager", "email": "hm@company.com"},
        {"contact_id": "C-002", "name": "IT Support", "role": "support", "email": "it@company.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # data/onboarding/contracts.json
    contracts = [
        {
            "employee_id": "E-001",
            "employee_name": "John Doe",
            "status": "signed",
            "email": "john.doe@company.com",
            "department": "Engineering"
        },
        {
            "employee_id": "E-002",
            "employee_name": "Jane Smith",
            "status": "pending",
            "email": "jane.smith@company.com",
            "department": "Marketing"
        },
        {
            "employee_id": "E-003",
            "employee_name": "Bob Lee",
            "status": "signed",
            "email": "bob.lee@company.com",
            "department": "HR"
        }
    ]
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump(contracts, f, indent=2)

    # data/onboarding/permission_packs.json
    permission_packs = [
        {"pack_id": "eng", "systems": ["CRM", "ERP", "Git"], "department": "Engineering"},
        {"pack_id": "hr", "systems": ["HRIS", "Payroll"], "department": "HR"},
        {"pack_id": "mkt", "systems": ["Mailchimp", "Analytics"], "department": "Marketing"}
    ]
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump(permission_packs, f, indent=2)

    # data/onboarding/equipment_inventory.json
    equipment_inventory = [
        {"asset_tag": "LAP-101", "asset_type": "laptop", "status": "available"},
        {"asset_tag": "MON-202", "asset_type": "monitor", "status": "available"},
        {"asset_tag": "LAP-102", "asset_type": "laptop", "status": "assigned"},
        {"asset_tag": "MON-203", "asset_type": "monitor", "status": "retired"},
        {"asset_tag": "PRN-001", "asset_type": "printer", "status": "available"},
        {"asset_tag": "KEY-001", "asset_type": "keyboard", "status": "available"}
    ]
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump(equipment_inventory, f, indent=2)

if __name__ == "__main__":
    build_env()
