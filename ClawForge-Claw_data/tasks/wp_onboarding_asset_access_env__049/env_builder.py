import json, os

def build_env():
    # data/accounts.json - 已有一些账户，但无 Alex
    accounts = {
        "accounts": [
            {"account_id": "ACC-001", "display_name": "Jane Doe", "department": "Engineering", "email": "jane@example.com", "permissions": []},
            {"account_id": "ACC-002", "display_name": "Bob Smith", "department": "Marketing", "email": "bob@example.com", "permissions": []}
        ]
    }
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # data/contacts.json (可选干扰)
    contacts = {
        "contacts": [
            {"contact_id": "C-001", "name": "HR Manager", "role": "manager", "email": "hr@example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # data/onboarding/contracts.json - 多个合同，只有 Alex 是 signed
    contracts = {
        "contracts": [
            {
                "employee_id": "EMP-001",
                "employee_name": "Alex Chen",
                "status": "signed",
                "email": "alex.chen@example.com"
            },
            {
                "employee_id": "EMP-002",
                "employee_name": "Sarah Lee",
                "status": "draft",
                "email": "sarah.lee@example.com"
            },
            {
                "employee_id": "EMP-003",
                "employee_name": "Mike Johnson",
                "status": "pending_approval",
                "email": "mike.j@example.com"
            }
        ]
    }
    os.makedirs("data/onboarding", exist_ok=True)
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump(contracts, f, indent=2)

    # data/onboarding/equipment_inventory.json - 包含可用设备和已分配设备
    equipment = {
        "equipment_inventory": [
            {"asset_tag": "LAP-001", "asset_type": "laptop", "status": "available"},
            {"asset_tag": "LAP-002", "asset_type": "laptop", "status": "assigned"},
            {"asset_tag": "MON-001", "asset_type": "monitor", "status": "available"},
            {"asset_tag": "MON-002", "asset_type": "monitor", "status": "damaged"},
            {"asset_tag": "KB-001", "asset_type": "keyboard", "status": "available"}
        ]
    }
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump(equipment, f, indent=2)

    # data/onboarding/permission_packs.json
    packs = {
        "permission_packs": [
            {
                "pack_id": "pack_standard",
                "systems": ["CRM", "ERP", "HR"]
            },
            {
                "pack_id": "pack_admin",
                "systems": ["ALL"]
            }
        ]
    }
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump(packs, f, indent=2)

    # slack_cache 目录（空，让 agent 写入欢迎消息）
    os.makedirs("slack_cache", exist_ok=True)

    # ops 目录（空，让 agent 写入汇总文件）
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
