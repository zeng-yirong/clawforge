import os
import json

def build_env():
    # Ensure base asset directory (cwd is already .)
    # Create subdirectories
    os.makedirs("data/onboarding", exist_ok=True)
    os.makedirs("ops/slack_cache", exist_ok=True)

    # === accounts.json ===
    accounts = {
        "accounts": [
            {"account_id": "emp001", "display_name": "Sarah Connor", "department": "engineering", "email": "sarah.connor@company.com", "permissions": []},
            {"account_id": "emp002", "display_name": "Mike Davis", "department": "sales", "email": "mike.davis@company.com", "permissions": []},
            {"account_id": "emp003", "display_name": "John Doe (old)", "department": "hr", "email": "john.doe@company.com", "permissions": []}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # === contacts.json (distractor) ===
    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Alice", "role": "manager", "email": "alice@company.com"},
            {"contact_id": "c002", "name": "Bob", "role": "it", "email": "bob@company.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # === contracts.json (the key source) ===
    contracts = {
        "contracts": [
            {"employee_id": "emp001", "employee_name": "Sarah Connor", "status": "signed", "email": "sarah.connor@company.com"},
            {"employee_id": "emp002", "employee_name": "Mike Davis", "status": "signed", "email": "mike.davis@company.com"},
            {"employee_id": "emp003", "employee_name": "Old John", "status": "draft", "email": "john.doe@company.com"}  # not signed – ignore
        ]
    }
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump(contracts, f, indent=2)

    # === equipment_inventory.json ===
    equipment = {
        "equipment_inventory": [
            {"asset_tag": "LAPTOP-001", "asset_type": "laptop", "status": "available"},
            {"asset_tag": "LAPTOP-002", "asset_type": "laptop", "status": "assigned"},   # already used
            {"asset_tag": "MONITOR-001", "asset_type": "monitor", "status": "available"},
            {"asset_tag": "DOCK-001", "asset_type": "docking_station", "status": "available"},
            {"asset_tag": "KEYBOARD-001", "asset_type": "keyboard", "status": "lost"}     # not available
        ]
    }
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump(equipment, f, indent=2)

    # === permission_packs.json ===
    perm_packs = {
        "permission_packs": [
            {"pack_id": "engineering", "systems": ["jenkins", "code_repo", "monitoring", "jira"]},
            {"pack_id": "sales", "systems": ["crm", "email_marketing", "reporting"]},
            {"pack_id": "hr", "systems": ["hr_portal", "payroll"]}
        ]
    }
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump(perm_packs, f, indent=2)

    # === Additional distractor: old_drafts.txt ===
    with open("data/onboarding/old_drafts.txt", "w") as f:
        f.write("These are legacy drafts - ignore them.\n")

if __name__ == "__main__":
    build_env()
