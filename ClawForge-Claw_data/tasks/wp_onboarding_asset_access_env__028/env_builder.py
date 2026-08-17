import os
import json
import random

def build_env():
    # Ensure cwd is 
    # Create directories
    os.makedirs("data/onboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=False)  # deliberately not created, agent creates it

    # --- Contracts (interference includes pending/cancelled)
    contracts = {
        "contracts": [
            {"employee_id": "E001", "employee_name": "Alice", "status": "signed", "email": "alice@company.com"},
            {"employee_id": "E002", "employee_name": "Bob", "status": "signed", "email": "bob@company.com"},
            {"employee_id": "E003", "employee_name": "Charlie", "status": "signed", "email": "charlie@company.com"},
            {"employee_id": "E004", "employee_name": "David", "status": "pending", "email": "david@company.com"},
            {"employee_id": "E005", "employee_name": "Eve", "status": "cancelled", "email": "eve@company.com"},
            {"employee_id": "E006", "employee_name": "Frank", "status": "signed", "email": "frank@company.com"},  # extra signed – but equipment only 3 available → Frank gets null
        ]
    }
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump(contracts, f, indent=2)

    # --- Permission packs (include decoy packs)
    permission_packs = {
        "permission_packs": [
            {"pack_id": "standard", "systems": ["crm", "intranet", "email"]},
            {"pack_id": "admin", "systems": ["all_systems", "audit_logs"]},
            {"pack_id": "guest", "systems": ["meeting_room"]}
        ]
    }
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump(permission_packs, f, indent=2)

    # --- Equipment inventory (interference: assigned/retired, only 3 available)
    equipment_inventory = {
        "equipment_inventory": [
            {"asset_tag": "EQ001", "asset_type": "laptop", "status": "available"},
            {"asset_tag": "EQ002", "asset_type": "monitor", "status": "assigned"},
            {"asset_tag": "EQ003", "asset_type": "laptop", "status": "available"},
            {"asset_tag": "EQ004", "asset_type": "tablet", "status": "retired"},
            {"asset_tag": "EQ005", "asset_type": "keyboard", "status": "available"},
            {"asset_tag": "EQ006", "asset_type": "mouse", "status": "available"},  # extra available but only 3 needed? Actually we have 4 signed, but Frank is 4th signed. So 3 available for first 3, Frank gets null. But we need unique answer: assign first available to first 3 sorted by employee_id.
        ]
    }
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump(equipment_inventory, f, indent=2)

    # --- Add some irrelevant files to increase difficulty
    os.makedirs("data/accounts", exist_ok=True)
    accounts = {
        "accounts": [
            {"account_id": "A001", "display_name": "Alice", "department": "Engineering", "email": "alice@company.com", "permissions": ["crm", "intranet"]},
            {"account_id": "A002", "display_name": "Bob", "department": "Sales", "email": "bob@company.com", "permissions": ["crm"]}
        ]
    }
    with open("data/accounts/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # old log file as distractor
    with open("data/onboarding/old_note.txt", "w") as f:
        f.write("ignored\n")

if __name__ == "__main__":
    build_env()
