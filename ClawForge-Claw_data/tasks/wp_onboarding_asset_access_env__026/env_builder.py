import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/onboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("logs", exist_ok=True)  # 干扰目录

    # contracts.json —— 多个合同，只有一个是 signed
    contracts = {
        "contracts": [
            {
                "employee_id": "E001",
                "employee_name": "Xiao Ming",
                "status": "signed",
                "email": "xiao.ming@personal.com",
                "department": "Engineering"
            },
            {
                "employee_id": "E002",
                "employee_name": "Li Hua",
                "status": "signed",
                "email": "li.hua@personal.com",
                "department": "Marketing"
            },
            {
                "employee_id": "E003",
                "employee_name": "Wang Fang",
                "status": "draft",
                "email": "wang.fang@personal.com",
                "department": "Engineering"
            },
            {
                "employee_id": "E004",
                "employee_name": "Zhang Wei",
                "status": "expired",
                "email": "zhang.wei@personal.com",
                "department": "Ops"
            }
        ]
    }
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump(contracts, f, indent=2)

    # permission_packs.json —— 多个权限包，Engineering 对应 dev
    permission_packs = {
        "permission_packs": [
            {
                "pack_id": "dev",
                "systems": ["jenkins", "github", "jira"],
                "department": "Engineering"
            },
            {
                "pack_id": "marketing",
                "systems": ["hubspot", "mailchimp", "canva"],
                "department": "Marketing"
            },
            {
                "pack_id": "ops",
                "systems": ["grafana", "prometheus", "pagerduty"],
                "department": "Ops"
            }
        ]
    }
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump(permission_packs, f, indent=2)

    # equipment_inventory.json —— 多台设备，只有一台可用笔记本
    equipment_inventory = {
        "equipment_inventory": [
            {
                "asset_tag": "LAP-001",
                "asset_type": "laptop",
                "status": "available"
            },
            {
                "asset_tag": "LAP-002",
                "asset_type": "laptop",
                "status": "assigned"
            },
            {
                "asset_tag": "MON-001",
                "asset_type": "monitor",
                "status": "available"
            },
            {
                "asset_tag": "LAP-003",
                "asset_type": "laptop",
                "status": "damaged"
            },
            {
                "asset_tag": "DESK-001",
                "asset_type": "desktop",
                "status": "available"
            }
        ]
    }
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump(equipment_inventory, f, indent=2)

    # 额外干扰文件：不相关的 accounts.json（但 agent 不需要读）
    accounts = {
        "accounts": [
            {"account_id": "A001", "display_name": "Li Hua", "department": "Marketing", "email": "li.hua@acme.com", "permissions": ["hubspot"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 干扰文件：contacts.json（一些旧联系人）
    contacts = {
        "contacts": [
            {"contact_id": "C001", "name": "Old Employee", "role": "ex-employee", "email": "old@acme.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 干扰目录和文件
    with open("logs/access_2024.log", "w") as f:
        f.write("some old log\n")

if __name__ == "__main__":
    build_env()
