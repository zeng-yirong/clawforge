import os
import json

def build_env():
    # create directory structure
    os.makedirs("data/onboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # empty, will be populated by agent

    # accounts.json - multiple accounts, only EMP007 matches Alice
    accounts = {
        "accounts": [
            {"account_id": "EMP001", "display_name": "Bob", "department": "Sales", "email": "bob@example.com", "permissions": ["sales_team"]},
            {"account_id": "EMP007", "display_name": "Alice Johnson", "department": "Engineering", "email": "alice@example.com", "permissions": []},
            {"account_id": "EMP010", "display_name": "Eve", "department": "HR", "email": "eve@example.com", "permissions": ["hr_base"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # contacts.json - irrelevant but present
    contacts = {
        "contacts": [
            {"contact_id": "C001", "name": "Manager", "role": "Lead", "email": "manager@example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # contracts.json - only EMP007 is signed and has a matching account
    contracts = {
        "contracts": [
            {"employee_id": "EMP001", "employee_name": "Bob", "status": "pending", "email": "bob@example.com"},
            {"employee_id": "EMP003", "employee_name": "Charlie", "status": "signed", "email": "charlie@example.com"},
            {"employee_id": "EMP007", "employee_name": "Alice Johnson", "status": "signed", "email": "alice@example.com"},
            {"employee_id": "EMP004", "employee_name": "Diana", "status": "rejected", "email": "diana@example.com"},
            {"employee_id": "EMP006", "employee_name": "Frank", "status": "signed", "email": "frank@example.com"}
        ]
    }
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump(contracts, f, indent=2)

    # equipment_inventory.json - only LAP-001 is an available laptop
    equipment = {
        "equipment_inventory": [
            {"asset_tag": "MON-001", "asset_type": "monitor", "status": "available"},
            {"asset_tag": "LAP-001", "asset_type": "laptop", "status": "available"},
            {"asset_tag": "LAP-002", "asset_type": "laptop", "status": "assigned"},
            {"asset_tag": "KB-001", "asset_type": "keyboard", "status": "available"},
            {"asset_tag": "LAP-003", "asset_type": "laptop", "status": "lost"}
        ]
    }
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump(equipment, f, indent=2)

    # permission_packs.json - engineering pack matches Alice's department
    permission_packs = {
        "permission_packs": [
            {"pack_id": "engineering", "systems": ["DevOps", "CodeRepo"]},
            {"pack_id": "sales", "systems": ["CRM", "ERP"]},
            {"pack_id": "hr", "systems": ["HRIS"]}
        ]
    }
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump(permission_packs, f, indent=2)

    # additional distraction: old data in a subfolder
    os.makedirs("data/onboarding/archive", exist_ok=True)
    with open("data/onboarding/archive/contracts_backup.json", "w") as f:
        json.dump({"contracts": []}, f)

if __name__ == "__main__":
    build_env()
