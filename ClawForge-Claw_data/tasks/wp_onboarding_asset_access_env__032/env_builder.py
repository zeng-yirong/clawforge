import os
import json
import shutil

def build_env():
    # 确保根目录干净（cwd 已经是 .）
    # 但 builder 可能会被多次调用，先清理已有内容
    for item in os.listdir('.'):
        if os.path.isfile(item):
            os.remove(item)
        elif os.path.isdir(item) and item not in ('.', '..'):
            shutil.rmtree(item)

    # 创建目录结构
    os.makedirs('data/onboarding', exist_ok=True)
    os.makedirs('ops', exist_ok=True)
    os.makedirs('raw_logs', exist_ok=True)  # 干扰目录

    # 1. contracts.json — 包含多个合同，只有一个是 active + Engineering
    contracts = {
        "contracts": [
            {
                "employee_id": "E2024-089",
                "employee_name": "Zhang San",
                "status": "active",
                "email": "zhang.san@company.com",
                "department": "Engineering"
            },
            {
                "employee_id": "E2024-088",
                "employee_name": "Li Si",
                "status": "active",
                "email": "li.si@company.com",
                "department": "Marketing"
            },
            {
                "employee_id": "E2024-090",
                "employee_name": "Wang Wu",
                "status": "pending",
                "email": "wang.wu@company.com",
                "department": "Engineering"
            },
            {
                "employee_id": "E2023-045",
                "employee_name": "Old Employee",
                "status": "expired",
                "email": "old@company.com",
                "department": "Engineering"
            }
        ]
    }
    with open('data/onboarding/contracts.json', 'w') as f:
        json.dump(contracts, f, indent=2)

    # 2. equipment_inventory.json — 只有一台可用笔记本，其余已分配/损坏
    inventory = {
        "equipment_inventory": [
            {
                "asset_tag": "LAP-0083",
                "asset_type": "laptop",
                "status": "available"
            },
            {
                "asset_tag": "LAP-0082",
                "asset_type": "laptop",
                "status": "assigned"
            },
            {
                "asset_tag": "LAP-0081",
                "asset_type": "laptop",
                "status": "damaged"
            },
            {
                "asset_tag": "MON-0012",
                "asset_type": "monitor",
                "status": "available"
            }
        ]
    }
    with open('data/onboarding/equipment_inventory.json', 'w') as f:
        json.dump(inventory, f, indent=2)

    # 3. permission_packs.json — 唯一一个 Engineering 可用包，另一个废弃
    packs = {
        "permission_packs": [
            {
                "pack_id": "eng_std",
                "department": "Engineering",
                "systems": ["git", "jira", "confluence"]
            },
            {
                "pack_id": "eng_legacy",
                "department": "Engineering",
                "systems": ["svn", "bugzilla"],
                "deprecated": True
            },
            {
                "pack_id": "mkt_std",
                "department": "Marketing",
                "systems": ["salesforce", "hubspot"]
            }
        ]
    }
    with open('data/onboarding/permission_packs.json', 'w') as f:
        json.dump(packs, f, indent=2)

    # 4. 干扰文件 — raw_logs 下放一些无关日志
    with open('raw_logs/access.log', 'w') as f:
        f.write("2025-03-21 08:12:33 user:E2024-088 login\n")
        f.write("2025-03-21 08:15:01 user:E2024-089 login\n")

    # 5. 额外干扰 — data/accounts.json 和 data/contacts.json（业务骨架要求）
    accounts = {
        "accounts": [
            {
                "account_id": "A001",
                "display_name": "Li Si",
                "department": "Marketing",
                "email": "li.si@company.com",
                "permissions": ["campaign"]
            }
        ]
    }
    with open('data/accounts.json', 'w') as f:
        json.dump(accounts, f, indent=2)

    contacts = {
        "contacts": [
            {
                "contact_id": "C001",
                "name": "HR Li",
                "role": "HR Manager",
                "email": "hr.li@company.com"
            }
        ]
    }
    with open('data/contacts.json', 'w') as f:
        json.dump(contacts, f, indent=2)

if __name__ == "__main__":
    build_env()
