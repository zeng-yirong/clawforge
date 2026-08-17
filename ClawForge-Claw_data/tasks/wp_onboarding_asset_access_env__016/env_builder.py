import os
import json

def build_env():
    # 创建 contracts 目录，存放合同文件
    os.makedirs("contracts", exist_ok=True)
    contracts = {
        "contracts": [
            {
                "employee_id": "EMP001",
                "employee_name": "John Smith",
                "status": "draft",
                "email": "john.smith@company.com"
            },
            {
                "employee_id": "EMP002",
                "employee_name": "Alice Wang",
                "status": "terminated",
                "email": "alice.wang@company.com"
            },
            {
                "employee_id": "EMP003",
                "employee_name": "Jane Doe",
                "status": "signed",
                "email": "jane.doe@company.com",
                "department": "Engineering"
            },
            {
                "employee_id": "EMP004",
                "employee_name": "Bob Lee",
                "status": "signed",
                "email": "bob.lee@company.com",
                "department": "Sales"
            }
        ]
    }
    with open("contracts/contracts.json", "w") as f:
        json.dump(contracts, f, indent=2)

    # 创建 permissions 目录，存放权限包
    os.makedirs("permissions", exist_ok=True)
    permission_packs = {
        "permission_packs": [
            {
                "pack_id": "ENG_FULL",
                "department": "Engineering",
                "systems": ["Jira", "GitLab", "Confluence", "AWS-Dev", "DockerHub"]
            },
            {
                "pack_id": "SALES_BASIC",
                "department": "Sales",
                "systems": ["Salesforce", "HubSpot", "Slack-ReadOnly"]
            }
        ]
    }
    with open("permissions/permission_packs.json", "w") as f:
        json.dump(permission_packs, f, indent=2)

    # 创建 equipment 目录，存放设备库存
    os.makedirs("equipment", exist_ok=True)
    equipment = {
        "equipment_inventory": [
            {"asset_tag": "LT-101", "asset_type": "Laptop", "status": "assigned", "assigned_to": "EMP001"},
            {"asset_tag": "LT-102", "asset_type": "Laptop", "status": "available", "assigned_to": None},
            {"asset_tag": "LT-103", "asset_type": "Laptop", "status": "available", "assigned_to": None},
            {"asset_tag": "MN-201", "asset_type": "Monitor", "status": "available", "assigned_to": None},
            {"asset_tag": "KB-301", "asset_type": "Keyboard", "status": "available", "assigned_to": None}
        ]
    }
    with open("equipment/equipment_inventory.json", "w") as f:
        json.dump(equipment, f, indent=2)

    # 创建 ops 目录（可能为空，agent 后续写入结果）
    os.makedirs("ops", exist_ok=True)

    # 额外干扰文件：一些无关的笔记
    with open("notes.txt", "w") as f:
        f.write("Remember to order more monitors next week.\n")

if __name__ == "__main__":
    build_env()
