import os
import json

def build_env():
    # 创建必要目录
    os.makedirs("data/onboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("slack_cache", exist_ok=True)

    # 已有员工账户（干扰项）
    accounts = {
        "accounts": [
            {"account_id": "A001", "display_name": "Li Ming", "department": "Marketing",
             "email": "li.ming@company.com", "permissions": ["crm"]},
            {"account_id": "A002", "display_name": "Zhao Yan", "department": "Engineering",
             "email": "zhao.yan@company.com", "permissions": ["crm", "erp", "hr"]},
            {"account_id": "A003", "display_name": "Wang Lei", "department": "Finance",
             "email": "wang.lei@company.com", "permissions": ["erp"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 联系人（干扰项）
    contacts = {
        "contacts": [
            {"contact_id": "C001", "name": "HR Admin", "role": "admin", "email": "hr@company.com"},
            {"contact_id": "C002", "name": "IT Support", "role": "tech", "email": "it@company.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 入职合同：正确目标 + 多个干扰项
    contracts = {
        "contracts": [
            # 正确目标 —— Zhang Wei，部门 Engineering
            {"employee_id": "E2024-024", "employee_name": "Zhang Wei", "status": "signed",
             "email": "", "department": "Engineering"},
            # 干扰：已过期
            {"employee_id": "E2024-020", "employee_name": "Chen Jie", "status": "expired",
             "email": "", "department": "Marketing"},
            # 干扰：pending
            {"employee_id": "E2024-023", "employee_name": "Wang Fang", "status": "pending",
             "email": "", "department": "Marketing"},
            # 干扰：另一个 signed 但部门不同，且设备库存中无可用 Desktop
            {"employee_id": "E2024-022", "employee_name": "Liu Qiang", "status": "signed",
             "email": "", "department": "Finance"}
        ]
    }
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump(contracts, f, indent=2)

    # 设备清单：只有一台 Laptop 可用
    equipment = {
        "equipment_inventory": [
            {"asset_tag": "LAPTOP-042", "asset_type": "Laptop", "status": "available"},
            {"asset_tag": "LAPTOP-039", "asset_type": "Laptop", "status": "assigned"},
            {"asset_tag": "DESKTOP-001", "asset_type": "Desktop", "status": "assigned"},
            {"asset_tag": "MONITOR-007", "asset_type": "Monitor", "status": "retired"}
        ]
    }
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump(equipment, f, indent=2)

    # 权限包：Engineering 对应系统列表
    permission_packs = {
        "permission_packs": [
            {"pack_id": "Engineering", "systems": ["crm", "erp", "hr"]},
            {"pack_id": "Marketing", "systems": ["crm"]},
            {"pack_id": "Finance", "systems": ["erp"]}
        ]
    }
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump(permission_packs, f, indent=2)

if __name__ == "__main__":
    build_env()
