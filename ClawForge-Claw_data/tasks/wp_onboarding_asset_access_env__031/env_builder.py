import json
import os

def build_env():
    # Create directory structure
    os.makedirs("data/onboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("old_backups", exist_ok=True)   # distraction

    # --- Contracts (interference: multiple contracts, only one signed for Alice) ---
    contracts = [
        {"employee_id": "E001", "employee_name": "Alice Johnson", "status": "signed", "email": "alice.johnson@corp.com", "department": "Engineering"},
        {"employee_id": "E002", "employee_name": "Bob Smith", "status": "pending", "email": "bob.smith@corp.com", "department": "Sales"},
        {"employee_id": "E003", "employee_name": "Carol Lee", "status": "expired", "email": "carol.lee@corp.com", "department": "HR"},
        {"employee_id": "E004", "employee_name": "David Brown", "status": "signed", "email": "david.brown@corp.com", "department": "Sales"}  # distractor: also signed but different dept
    ]
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump({"contracts": contracts}, f, indent=2)

    # --- Permission Packs ---
    packs = [
        {"pack_id": "pack_eng", "systems": ["gitlab", "jira", "kubernetes", "internal-docs", "ci-cd"]},
        {"pack_id": "pack_sales", "systems": ["crm", "mailchimp", "slack", "salesforce"]},
        {"pack_id": "pack_hr", "systems": ["bamboo", "workday", "okta", "slack"]}
    ]
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump({"permission_packs": packs}, f, indent=2)

    # --- Equipment Inventory (status mix: available/assigned/retired) ---
    inventory = [
        {"asset_tag": "LT-001", "asset_type": "laptop", "status": "available"},
        {"asset_tag": "LT-002", "asset_type": "laptop", "status": "assigned"},
        {"asset_tag": "LT-003", "asset_type": "laptop", "status": "retired"},
        {"asset_tag": "LT-004", "asset_type": "laptop", "status": "available"},
        {"asset_tag": "MON-001", "asset_type": "monitor", "status": "available"},
        {"asset_tag": "DOCK-001", "asset_type": "docking_station", "status": "available"}
    ]
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump({"equipment_inventory": inventory}, f, indent=2)

    # --- Distractor files (old backups, temp logs) ---
    with open("old_backups/contracts_2023.json", "w") as f:
        json.dump({"ignore": "stale data"}, f)
    with open("old_backups/inventory_2023.json", "w") as f:
        json.dump({"ignore": "stale data"}, f)
    # Create a dummy CSV that looks relevant but is not
    with open("data/onboarding/temp.csv", "w") as f:
        f.write("employee_id,note\nE001,ignore this\n")

if __name__ == "__main__":
    build_env()
