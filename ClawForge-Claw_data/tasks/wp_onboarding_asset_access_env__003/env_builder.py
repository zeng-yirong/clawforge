import os
import json

def build_env():
    # Ensure base directories exist
    os.makedirs("data/onboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("raw_logs", exist_ok=True)   # distraction

    # --- contracts.json ---
    contracts = {
        "contracts": [
            {
                "employee_id": "E001",
                "employee_name": "Alice Chen",
                "status": "signed",
                "email": "alice@company.com"
            },
            {
                "employee_id": "E002",
                "employee_name": "Bob Smith",
                "status": "pending",
                "email": "bob@company.com"
            }
        ]
    }
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump(contracts, f, indent=2)

    # --- accounts.json ---
    accounts = {
        "accounts": [
            {
                "account_id": "A001",
                "display_name": "Alice Chen",
                "department": "Engineering",
                "email": "alice@company.com",
                "permissions": []
            },
            # extra account that doesn't match any signed contract
            {
                "account_id": "A002",
                "display_name": "Charlie Doe",
                "department": "HR",
                "email": "charlie@company.com",
                "permissions": []
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # --- contacts.json (distraction) ---
    contacts = {
        "contacts": [
            {"contact_id": "C001", "name": "Maya", "role": "HR", "email": "maya@company.com"},
            {"contact_id": "C002", "name": "IT Support", "role": "Support", "email": "it@company.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # --- permission_packs.json ---
    permission_packs = {
        "permission_packs": [
            {"pack_id": "P1", "department": "Engineering", "systems": ["git", "jira", "wiki"]},
            {"pack_id": "P2", "department": "HR", "systems": ["hr-system", "calendar"]},
            {"pack_id": "P3", "department": "Finance", "systems": ["erp", "reporting"]}
        ]
    }
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump(permission_packs, f, indent=2)

    # --- equipment_inventory.json ---
    equipment_inventory = {
        "equipment_inventory": [
            {"asset_tag": "LAP001", "asset_type": "laptop", "status": "available"},
            {"asset_tag": "LAP002", "asset_type": "laptop", "status": "assigned"},
            {"asset_tag": "MON001", "asset_type": "monitor", "status": "retired"},
            {"asset_tag": "MON002", "asset_type": "monitor", "status": "available"}  # monitor, not laptop
        ]
    }
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump(equipment_inventory, f, indent=2)

    # --- distraction files in ops/ ---
    with open("ops/old_debug.log", "w") as f:
        f.write("[2025-01-01] dummy log entry\n")

    # empty distraction directory
    with open("raw_logs/.gitkeep", "w") as f:
        pass

if __name__ == "__main__":
    build_env()
