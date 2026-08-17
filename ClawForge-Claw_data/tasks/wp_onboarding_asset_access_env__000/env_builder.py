import os
import json

def build_env():
    # 确保目录存在
    os.makedirs("data/onboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 仅作为空占位，agent需要覆盖

    # 合同文件
    contracts = {
        "contracts": [
            {"employee_id": "E001", "employee_name": "Alice Wang", "status": "signed", "email": "alice@example.com"},
            {"employee_id": "E002", "employee_name": "Bob Li", "status": "signed", "email": "bob@example.com"},
            {"employee_id": "E003", "employee_name": "Charlie Zhang", "status": "signed", "email": "charlie@example.com"},
            {"employee_id": "E004", "employee_name": "Daisy Chen", "status": "pending", "email": "daisy@example.com"},
            {"employee_id": "E005", "employee_name": "Eve Liu", "status": "expired", "email": "eve@example.com"}
        ]
    }
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump(contracts, f, indent=2)

    # 账户文件
    accounts = {
        "accounts": [
            {"account_id": "A001", "display_name": "Alice Wang", "department": "engineering", "email": "alice@example.com", "permissions": []},
            {"account_id": "A002", "display_name": "Bob Li", "department": "marketing", "email": "bob@example.com", "permissions": []},
            {"account_id": "A003", "display_name": "Charlie Zhang", "department": "hr", "email": "charlie@example.com", "permissions": []},
            {"account_id": "A004", "display_name": "Daisy Chen", "department": "engineering", "email": "daisy@example.com", "permissions": []}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 权限包
    perm_packs = {
        "permission_packs": [
            {"pack_id": "eng_pack", "systems": ["jira", "github", "aws"]},
            {"pack_id": "mkt_pack", "systems": ["hubspot", "mailchimp", "google_ads"]},
            {"pack_id": "hr_pack", "systems": ["bamboohr", "workday"]},
            {"pack_id": "ops_pack", "systems": ["pagerduty", "datadog"]}
        ]
    }
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump(perm_packs, f, indent=2)

    # 设备库存
    equipment = {
        "equipment_inventory": [
            {"asset_tag": "LAP001", "asset_type": "laptop", "status": "available"},
            {"asset_tag": "LAP002", "asset_type": "laptop", "status": "available"},
            {"asset_tag": "MON001", "asset_type": "monitor", "status": "available"},
            {"asset_tag": "LAP003", "asset_type": "laptop", "status": "assigned"},
            {"asset_tag": "MON002", "asset_type": "monitor", "status": "broken"}
        ]
    }
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump(equipment, f, indent=2)

if __name__ == "__main__":
    build_env()
