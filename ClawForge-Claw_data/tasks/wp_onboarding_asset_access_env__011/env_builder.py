import json
import os

def build_env():
    # 1. 创建 accounts.json
    accounts = [
        {"account_id": "A001", "display_name": "Alice Wang", "department": "Engineering", "email": "alice@company.com", "permissions": ["dev", "prod"]},
        {"account_id": "A002", "display_name": "Bob Li", "department": "Sales", "email": "bob@company.com", "permissions": ["crm"]},
        {"account_id": "A003", "display_name": "Sarah Johnson", "department": "Marketing", "email": "sarah.j@company.com", "permissions": []},
        {"account_id": "A004", "display_name": "Charlie Zhang", "department": "HR", "email": "charlie@company.com", "permissions": ["hr_system"]}
    ]
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # 2. 创建 onboarding/contracts.json (包含干扰项)
    contracts = [
        # 目标：Sarah Johnson，active 且 email_created false
        {"employee_id": "EMP003", "employee_name": "Sarah Johnson", "status": "active", "email": "sarah.j@company.com", "email_created": False, "permission_pack_id": "pack_mkt", "equipment_asset_tag": "ASST-MKT-003"},
        # 干扰：已处理过的active合同
        {"employee_id": "EMP001", "employee_name": "Alice Wang", "status": "active", "email": "alice@company.com", "email_created": True, "permission_pack_id": "pack_eng", "equipment_asset_tag": "ASST-ENG-001"},
        # 干扰：pending状态
        {"employee_id": "EMP002", "employee_name": "Bob Li", "status": "pending", "email": "bob@company.com", "email_created": False, "permission_pack_id": "pack_sales", "equipment_asset_tag": "ASST-SLS-002"},
        # 干扰：cancelled状态
        {"employee_id": "EMP004", "employee_name": "Charlie Zhang", "status": "cancelled", "email": "charlie@company.com", "email_created": False, "permission_pack_id": "pack_hr", "equipment_asset_tag": "ASST-HR-004"},
        # 干扰：另一个active但email_created false，但设备已分配（状态非available）——稍后设备库存里该设备状态为assigned
        {"employee_id": "EMP005", "employee_name": "Diana Chen", "status": "active", "email": "diana@company.com", "email_created": False, "permission_pack_id": "pack_eng", "equipment_asset_tag": "ASST-ENG-005"}
    ]
    os.makedirs("data/onboarding", exist_ok=True)
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump({"contracts": contracts}, f, indent=2)

    # 3. 创建 permission_packs.json
    permission_packs = [
        {"pack_id": "pack_eng", "systems": ["Jenkins", "K8s", "GitLab"]},
        {"pack_id": "pack_sales", "systems": ["Salesforce", "HubSpot"]},
        {"pack_id": "pack_mkt", "systems": ["Marketo", "Google Analytics", "WordPress"]},
        {"pack_id": "pack_hr", "systems": ["BambooHR", "Workday"]}
    ]
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump({"permission_packs": permission_packs}, f, indent=2)

    # 4. 创建 equipment_inventory.json (干扰：ASST-ENG-005 状态为 assigned)
    equipment = [
        {"asset_tag": "ASST-ENG-001", "asset_type": "Laptop", "status": "available"},
        {"asset_tag": "ASST-SLS-002", "asset_type": "Tablet", "status": "available"},
        {"asset_tag": "ASST-MKT-003", "asset_type": "Laptop", "status": "available"},
        {"asset_tag": "ASST-HR-004", "asset_type": "Desktop", "status": "available"},
        {"asset_tag": "ASST-ENG-005", "asset_type": "Laptop", "status": "assigned"}  # 干扰项，设备已被分配
    ]
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump({"equipment_inventory": equipment}, f, indent=2)

if __name__ == "__main__":
    build_env()
