import os
import json

def build_env():
    # Create contracts.json with multiple entries, only one active for Alice Wang with Engineering
    contracts = [
        {"employee_id": "E001", "employee_name": "Alice Wang", "status": "active", "email": "alice@company.com", "department": "Engineering"},
        {"employee_id": "E002", "employee_name": "Bob Smith", "status": "pending", "email": "bob@company.com", "department": "Marketing"},
        {"employee_id": "E003", "employee_name": "Alice Wang", "status": "cancelled", "email": "alice.old@company.com", "department": "Engineering"},
        {"employee_id": "E004", "employee_name": "Charlie Brown", "status": "active", "email": "charlie@company.com", "department": "Marketing"},
        {"employee_id": "E005", "employee_name": "Alice Wang", "status": "pending", "email": "alice.pending@company.com", "department": "Engineering"},
        {"employee_id": "E006", "employee_name": "Diana Lee", "status": "active", "email": "diana@company.com", "department": "HR"}
    ]
    with open("contracts.json", "w") as f:
        json.dump(contracts, f, indent=2)

    # Create permission_packs.json – one per department
    permission_packs = [
        {"pack_id": "engineering_pack", "department": "Engineering", "systems": ["gitlab", "jenkins", "aws"]},
        {"pack_id": "marketing_pack", "department": "Marketing", "systems": ["salesforce", "mailchimp"]},
        {"pack_id": "hr_pack", "department": "HR", "systems": ["workday", "bamboo"]}
    ]
    with open("permission_packs.json", "w") as f:
        json.dump(permission_packs, f, indent=2)

    # Create equipment_inventory.json – multiple assets, only one available laptop
    equipment_inventory = [
        {"asset_tag": "LT-001", "asset_type": "laptop", "status": "available"},
        {"asset_tag": "LT-002", "asset_type": "laptop", "status": "assigned"},
        {"asset_tag": "LT-003", "asset_type": "laptop", "status": "retired"},
        {"asset_tag": "MN-001", "asset_type": "monitor", "status": "available"},
        {"asset_tag": "DK-001", "asset_type": "docking_station", "status": "available"}
    ]
    with open("equipment_inventory.json", "w") as f:
        json.dump(equipment_inventory, f, indent=2)

if __name__ == "__main__":
    build_env()
