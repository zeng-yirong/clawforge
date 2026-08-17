import os
import json

def build_env():
    # 创建 data 子目录
    os.makedirs("data/onboarding", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    # 创建 output 目录（空目录，便于验证）
    os.makedirs("output", exist_ok=True)

    # ---------- 合同数据 ----------
    contracts = [
        {
            "employee_id": "E-1001",
            "employee_name": "Alex Johnson",
            "status": "signed",
            "email": "johnson.alex@external.com",
            "department": "Engineering",
            "permission_pack_id": "pack_engineering"
        },
        {
            "employee_id": "E-1002",
            "employee_name": "Maria Chen",
            "status": "pending",
            "email": "maria.chen@external.com",
            "department": "Marketing",
            "permission_pack_id": "pack_marketing"
        },
        {
            "employee_id": "E-1003",
            "employee_name": "Bob Smith",
            "status": "cancelled",
            "email": "bob.smith@external.com",
            "department": "Finance",
            "permission_pack_id": "pack_finance"
        },
        {
            "employee_id": "E-1004",
            "employee_name": "Diana Torres",
            "status": "signed",
            "email": "diana.torres@external.com",
            "department": "Marketing",
            "permission_pack_id": "pack_marketing"
        }
    ]
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump({"contracts": contracts}, f, indent=2)

    # ---------- 权限包 ----------
    permission_packs = [
        {
            "pack_id": "pack_engineering",
            "systems": ["jenkins", "jira", "github"]
        },
        {
            "pack_id": "pack_marketing",
            "systems": ["mailchimp", "hubspot"]
        },
        {
            "pack_id": "pack_finance",
            "systems": ["quickbooks", "oracle"]
        }
    ]
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump({"permission_packs": permission_packs}, f, indent=2)

    # ---------- 设备库存 ----------
    equipment_inventory = [
        {"asset_tag": "LT-001", "asset_type": "laptop", "status": "available"},
        {"asset_tag": "LT-002", "asset_type": "laptop", "status": "assigned"},
        {"asset_tag": "LT-003", "asset_type": "laptop", "status": "damaged"},
        {"asset_tag": "MN-001", "asset_type": "monitor", "status": "available"},
        {"asset_tag": "KB-001", "asset_type": "keyboard", "status": "available"}
    ]
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump({"equipment_inventory": equipment_inventory}, f, indent=2)

    # ---------- 干扰数据：accounts 和 contacts ----------
    accounts = [
        {"account_id": "A-001", "display_name": "System Admin", "department": "IT", "email": "admin@company.com", "permissions": ["all"]},
        {"account_id": "A-002", "display_name": "Old Employee", "department": "Engineering", "email": "old.employee@company.com", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "C-001", "name": "HR Manager", "role": "hr", "email": "hr@company.com"},
        {"contact_id": "C-002", "name": "Office Admin", "role": "admin", "email": "admin@company.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
