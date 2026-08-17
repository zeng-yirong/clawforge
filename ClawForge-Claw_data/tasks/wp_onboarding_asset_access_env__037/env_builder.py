import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/onboarding", exist_ok=True)
    os.makedirs("backups", exist_ok=True)
    os.makedirs("old", exist_ok=True)

    # ==================== contracts.json (主文件) ====================
    contracts = [
        {
            "employee_id": "EMP-037",
            "employee_name": "Alice Johnson",
            "status": "signed",
            "email": "alice.johnson@external.com"
        },
        {
            "employee_id": "EMP-038",
            "employee_name": "Bob Smith",
            "status": "signed",
            "email": "bob.smith@external.com"
        },
        {
            "employee_id": "EMP-039",
            "employee_name": "Charlie Wang",
            "status": "pending",
            "email": "charlie.wang@external.com"
        },
        {
            "employee_id": "EMP-040",
            "employee_name": "David Lee",
            "status": "rejected",
            "email": "david.lee@external.com"
        }
    ]
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump({"contracts": contracts}, f, indent=2)

    # ==================== contracts_backup.json (干扰 - 过期副本) ====================
    backup_contracts = [
        {
            "employee_id": "EMP-037",
            "employee_name": "Alice Johnson",
            "status": "expired",
            "email": "alice.johnson@old.com"
        },
        {
            "employee_id": "EMP-041",
            "employee_name": "Eve Taylor",
            "status": "signed",
            "email": "eve.taylor@external.com"
        }
    ]
    with open("data/onboarding/contracts_backup.json", "w") as f:
        json.dump({"contracts": backup_contracts}, f, indent=2)

    # ==================== equipment_inventory.json ====================
    equipment = [
        {"asset_tag": "LAP-041", "asset_type": "laptop", "status": "assigned"},
        {"asset_tag": "LAP-042", "asset_type": "laptop", "status": "available"},
        {"asset_tag": "LAP-043", "asset_type": "laptop", "status": "maintenance"},
        {"asset_tag": "DESK-001", "asset_type": "desktop", "status": "available"},
        {"asset_tag": "MON-001", "asset_type": "monitor", "status": "available"}
    ]
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump({"equipment_inventory": equipment}, f, indent=2)

    # ==================== permission_packs.json ====================
    packs = [
        {
            "pack_id": "PACK-001",
            "description": "Sales Standard",
            "systems": ["crm", "erp"]
        },
        {
            "pack_id": "PACK-002",
            "description": "R&D Standard",
            "systems": ["slack", "portal", "email"]
        },
        {
            "pack_id": "PACK-003",
            "description": "HR Standard",
            "systems": ["hrms", "payroll"]
        }
    ]
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump({"permission_packs": packs}, f, indent=2)

    # ==================== 装饰性文件 (干扰) ====================
    contacts = [
        {"contact_id": "C001", "name": "HR Lead", "role": "HR", "email": "hr@company.com"},
        {"contact_id": "C002", "name": "IT Support", "role": "IT", "email": "it@company.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    accounts = [
        {"account_id": "A001", "display_name": "Alice Johnson", "department": "R&D", "email": "alice.johnson@company.com", "permissions": []}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # 旧的备份目录
    with open("backups/old_contracts_2024.json", "w") as f:
        f.write('{"contracts": []}')

    with open("old/irrelevant_notes.txt", "w") as f:
        f.write("This folder is not used.\n")

if __name__ == "__main__":
    build_env()
