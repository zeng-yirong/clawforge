import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/onboarding", exist_ok=True)

    # 合同文件 ── 包含干扰项：同名不同部门、不同状态
    contracts = {
        "contracts": [
            {
                "employee_id": "EMP013",
                "employee_name": "Bob Smith",
                "status": "pending",
                "email": "bob@company.com",
                "department": "Sales"
            },
            {
                "employee_id": "EMP014",
                "employee_name": "Alice Wang",
                "status": "active",
                "email": "alice.wang@company.com",
                "department": "Engineering"
            },
            {
                "employee_id": "EMP015",
                "employee_name": "Charlie Lee",
                "status": "expired",
                "email": "charlie@company.com",
                "department": "Marketing"
            },
            {
                "employee_id": "EMP016",
                "employee_name": "Alice Wang",
                "status": "active",
                "email": "alice2@company.com",
                "department": "HR"
            }
        ]
    }
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump(contracts, f, indent=2)

    # 权限包 ── 仅 Engineering 包与部门对应
    permission_packs = {
        "permission_packs": [
            {
                "pack_id": "eng_standard",
                "systems": ["github", "jira", "confluence"],
                "department": "Engineering"
            },
            {
                "pack_id": "sales_pro",
                "systems": ["salesforce", "outlook"],
                "department": "Sales"
            },
            {
                "pack_id": "hr_base",
                "systems": ["workday", "bamboo"],
                "department": "HR"
            }
        ]
    }
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump(permission_packs, f, indent=2)

    # 设备清单 ── 仅一台可用笔记本，其余干扰
    equipment_inventory = {
        "equipment_inventory": [
            {"asset_tag": "LT-2024-042", "asset_type": "laptop", "status": "available"},
            {"asset_tag": "LT-2024-041", "asset_type": "laptop", "status": "assigned"},
            {"asset_tag": "MN-2024-001", "asset_type": "monitor", "status": "available"},
            {"asset_tag": "KB-2024-001", "asset_type": "keyboard", "status": "available"}
        ]
    }
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump(equipment_inventory, f, indent=2)

if __name__ == "__main__":
    build_env()
