import os
import json
import random

def build_env():
    # ========== 1. 合同数据 ==========
    contracts = [
        {
            "employee_id": "E001",
            "employee_name": "Alice Wang",
            "status": "signed",
            "email": "alice@company.com",
            "department": "Engineering"
        },
        {
            "employee_id": "E002",
            "employee_name": "Bob Li",
            "status": "pending",
            "email": "bob@company.com",
            "department": "Marketing"
        },
        {
            "employee_id": "E003",
            "employee_name": "Carol Zhang",
            "status": "rejected",
            "email": "carol@company.com",
            "department": "Sales"
        },
        {
            "employee_id": "E004",
            "employee_name": "Dave Chen",
            "status": "signed",
            "email": "dave@oldcompany.com",
            "department": "Engineering",
            "expired": True
        }
    ]
    os.makedirs("data/onboarding", exist_ok=True)
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump({"contracts": contracts}, f, indent=2)

    # ========== 2. 账户数据 ==========
    accounts = [
        {"account_id": "E001", "display_name": "Alice Wang", "department": "Engineering", "email": "alice@company.com", "permissions": []},
        {"account_id": "E002", "display_name": "Bob Li", "department": "Marketing", "email": "bob@company.com", "permissions": []},
        {"account_id": "E003", "display_name": "Carol Zhang", "department": "Sales", "email": "carol@company.com", "permissions": []},
        {"account_id": "E004", "display_name": "Dave Chen", "department": "Engineering", "email": "dave@oldcompany.com", "permissions": []}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # ========== 3. 权限包 ==========
    permission_packs = [
        {"pack_id": "eng", "systems": ["gitlab", "jenkins", "k8s-dev", "jira"]},
        {"pack_id": "mkt", "systems": ["mailchimp", "hubspot"]},
        {"pack_id": "sales", "systems": ["salesforce", "outreach"]}
    ]
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump({"permission_packs": permission_packs}, f, indent=2)

    # ========== 4. 设备库存 ==========
    equipment_inventory = [
        {"asset_tag": "LAP-001", "asset_type": "laptop", "status": "available"},
        {"asset_tag": "LAP-002", "asset_type": "laptop", "status": "assigned"},
        {"asset_tag": "LAP-003", "asset_type": "laptop", "status": "damaged"},
        {"asset_tag": "MON-001", "asset_type": "monitor", "status": "available"}
    ]
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump({"equipment_inventory": equipment_inventory}, f, indent=2)

    # ========== 5. 联系人数据（用作干扰） ==========
    contacts = [
        {"contact_id": "C001", "name": "IT Support", "role": "admin", "email": "it@company.com"},
        {"contact_id": "C002", "name": "HR", "role": "hr", "email": "hr@company.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
