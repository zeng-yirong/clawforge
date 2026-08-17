import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/onboarding", exist_ok=True)
    os.makedirs("data/archived", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---------- contracts （含干扰项）----------
    contracts = [
        {"employee_id": "E001", "employee_name": "Alice", "status": "signed", "email": "alice@company.com", "department": "Engineering"},
        {"employee_id": "E002", "employee_name": "Bob", "status": "signed", "email": "bob@company.com", "department": "Engineering"},
        {"employee_id": "E003", "employee_name": "Charlie", "status": "pending", "email": "charlie@company.com", "department": "Sales"},
        {"employee_id": "E004", "employee_name": "Diana", "status": "expired", "email": "diana@company.com", "department": "Engineering"},
        {"employee_id": "E005", "employee_name": "Eve", "status": "signed", "email": "eve@company.com", "department": "HR"}
    ]
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump({"contracts": contracts}, f, indent=2)

    # 干扰存档合同
    old_contracts = [
        {"employee_id": "E000", "employee_name": "Old", "status": "signed", "email": "old@company.com", "department": "Engineering"}
    ]
    with open("data/archived/old_contracts.json", "w") as f:
        json.dump({"archived_contracts": old_contracts}, f, indent=2)

    # ---------- equipment_inventory ----------
    equipment = [
        {"asset_tag": "LAP-001", "asset_type": "laptop", "status": "available"},
        {"asset_tag": "LAP-002", "asset_type": "laptop", "status": "available"},
        {"asset_tag": "MON-001", "asset_type": "monitor", "status": "assigned"},
        {"asset_tag": "PHN-001", "asset_type": "phone", "status": "available"}
    ]
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump({"equipment_inventory": equipment}, f, indent=2)

    # ---------- permission_packs ----------
    packs = [
        {"pack_id": "eng_pack", "systems": ["gitlab", "jira", "jenkins"]},
        {"pack_id": "sales_pack", "systems": ["crm", "salesforce"]},
        {"pack_id": "hr_pack", "systems": ["hr_system", "payroll"]}
    ]
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump({"permission_packs": packs}, f, indent=2)

    # ---------- accounts （干扰，不用于主要逻辑）----------
    accounts = [
        {"account_id": "A001", "display_name": "Alice", "department": "Engineering", "email": "alice@company.com", "permissions": []},
        {"account_id": "A002", "display_name": "Bob", "department": "Engineering", "email": "bob@company.com", "permissions": []},
        {"account_id": "A003", "display_name": "Charlie", "department": "Sales", "email": "charlie@company.com", "permissions": []},
        {"account_id": "A004", "display_name": "Diana", "department": "Engineering", "email": "diana@company.com", "permissions": []},
        {"account_id": "A005", "display_name": "Eve", "department": "HR", "email": "eve@company.com", "permissions": []}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # ---------- contacts （纯干扰）----------
    contacts = [
        {"contact_id": "C001", "name": "Manager", "role": "IT Admin", "email": "manager@company.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
