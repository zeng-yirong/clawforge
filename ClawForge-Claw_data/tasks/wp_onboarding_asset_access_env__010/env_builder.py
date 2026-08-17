import json
import os

def build_env():
    # data/onboarding/contracts.json
    contracts = {
        "contracts": [
            {"employee_id": "E001", "employee_name": "Alice Wang", "department": "Engineering", "status": "signed", "email": "alice@example.com"},
            {"employee_id": "E002", "employee_name": "Bob Li", "department": "Engineering", "status": "signed", "email": "bob@example.com"},
            {"employee_id": "E003", "employee_name": "Charlie Zhang", "department": "Marketing", "status": "pending", "email": "charlie@example.com"},
            {"employee_id": "E004", "employee_name": "Diana Chen", "department": "Engineering", "status": "signed", "email": "diana@example.com"}
        ]
    }
    os.makedirs("data/onboarding", exist_ok=True)
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump(contracts, f, indent=2)

    # data/accounts.json
    accounts = {
        "accounts": [
            {"account_id": "A001", "display_name": "Alice Wang", "department": "Engineering", "email": "alice@example.com", "permissions": ["user"]},
            {"account_id": "A002", "display_name": "Eve Liu", "department": "Marketing", "email": "eve@example.com", "permissions": ["admin"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # data/contacts.json
    contacts = {
        "contacts": [
            {"contact_id": "C001", "name": "HR Bot", "role": "admin", "email": "hr_bot@company.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # data/onboarding/equipment_inventory.json
    equipment = {
        "equipment_inventory": [
            {"asset_tag": "LAPTOP-E001", "asset_type": "laptop", "status": "available"},
            {"asset_tag": "LAPTOP-E002", "asset_type": "laptop", "status": "available"},
            {"asset_tag": "LAPTOP-E004", "asset_type": "laptop", "status": "available"},
            {"asset_tag": "MONITOR-E001", "asset_type": "monitor", "status": "available"},
            {"asset_tag": "MONITOR-E002", "asset_type": "monitor", "status": "available"},
            {"asset_tag": "MONITOR-E004", "asset_type": "monitor", "status": "available"}
        ]
    }
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump(equipment, f, indent=2)

    # data/onboarding/permission_packs.json
    packs = {
        "permission_packs": [
            {"pack_id": "pack_engineering", "systems": ["crm", "erp", "git"]},
            {"pack_id": "pack_marketing", "systems": ["crm", "analytics"]}
        ]
    }
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump(packs, f, indent=2)

if __name__ == "__main__":
    build_env()
