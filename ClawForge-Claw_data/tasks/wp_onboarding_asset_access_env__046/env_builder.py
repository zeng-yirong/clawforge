import json
import os

def build_env():
    # ============ accounts.json ============
    accounts = {
        "accounts": [
            {"account_id": "acc_alice", "display_name": "Alice Wang", "department": "Engineering",
             "email": "alice.wang@company.com", "permissions": ["read", "write"]},
            {"account_id": "acc_bob", "display_name": "Bob Lee", "department": "HR",
             "email": "bob.lee@company.com", "permissions": ["read"]},
            {"account_id": "acc_eve", "display_name": "Eve Zhang", "department": "Finance",
             "email": "eve.zhang@company.com", "permissions": ["read", "admin"]}
        ]
    }
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ============ contacts.json (干扰) ============
    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Alice Wang", "role": "Engineer", "email": "alice.wang@company.com"},
            {"contact_id": "c002", "name": "Bob Lee", "role": "HR Manager", "email": "bob.lee@company.com"},
            {"contact_id": "c003", "name": "System Admin", "role": "IT", "email": "it@company.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ============ onboarding/contracts.json ============
    os.makedirs("data/onboarding", exist_ok=True)
    contracts = {
        "contracts": [
            {"employee_id": "E046", "employee_name": "Alice Wang", "status": "signed", "email": "alice.wang@company.com"},
            {"employee_id": "E999", "employee_name": "Pending Guy", "status": "pending", "email": "pending@company.com"},
            {"employee_id": "E047", "employee_name": "Bob Lee", "status": "signed", "email": "bob.lee@company.com"},
            {"employee_id": "E888", "employee_name": "Rejected Gal", "status": "rejected", "email": "reject@company.com"}
        ]
    }
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump(contracts, f, indent=2)

    # ============ onboarding/equipment_inventory.json ============
    equipment = {
        "equipment_inventory": [
            {"asset_tag": "LAPTOP-042", "asset_type": "laptop", "status": "available"},
            {"asset_tag": "LAPTOP-033", "asset_type": "laptop", "status": "in_use"},
            {"asset_tag": "MONITOR-007", "asset_type": "monitor", "status": "available"},
            {"asset_tag": "TABLET-001", "asset_type": "tablet", "status": "lost"}
        ]
    }
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump(equipment, f, indent=2)

    # ============ onboarding/permission_packs.json ============
    packs = {
        "permission_packs": [
            {"pack_id": "eng_standard", "systems": ["jira", "github", "aws"]},
            {"pack_id": "hr_standard", "systems": ["hr_platform", "time_tracking"]},
            {"pack_id": "fin_standard", "systems": ["sap", "expense"]}
        ]
    }
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump(packs, f, indent=2)

    # ============ ops/ 空目录 (用于放置结果) ============
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
