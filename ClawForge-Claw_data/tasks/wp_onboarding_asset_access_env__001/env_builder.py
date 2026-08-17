import json
import os

def build_env():
    # --- data/accounts.json (已有账号，其中包含 "alice.wang@company.com" 与一个合同冲突) ---
    accounts = [
        {"account_id": "ACC001", "display_name": "Alice Wang", "department": "Engineering", "email": "alice.wang@company.com", "permissions": ["gitlab"]},
        {"account_id": "ACC002", "display_name": "Bob Li", "department": "Marketing", "email": "bob.li@company.com", "permissions": ["salesforce"]},
        {"account_id": "ACC003", "display_name": "Carol Chen", "department": "Finance", "email": "carol.chen@company.com", "permissions": ["erp"]},
    ]
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # --- data/onboarding/contracts.json (5名员工，只有一名完全合格) ---
    # 员工1001: 已签, 邮箱已存在(冲突) -> 失败
    # 员工1002: 已签, 邮箱可用, 但需要的设备类型 "laptop" 在库存中没有可用 (只有 damaged 和 assigned) -> 失败
    # 员工1003: 已签, 邮箱可用, 有可用设备 "laptop" -> 成功
    # 员工1004: 待签, -> 失败
    # 员工1005: 待签, -> 失败
    contracts = [
        {"employee_id": "EMP1001", "employee_name": "David Zhao", "status": "signed", "email": "alice.wang@company.com", "asset_type": "monitor"},
        {"employee_id": "EMP1002", "employee_name": "Eva Liu", "status": "signed", "email": "eva.liu@company.com", "asset_type": "laptop"},
        {"employee_id": "EMP1003", "employee_name": "Frank Zhang", "status": "signed", "email": "frank.zhang@company.com", "asset_type": "laptop"},
        {"employee_id": "EMP1004", "employee_name": "Grace Wu", "status": "pending", "email": "grace.wu@company.com", "asset_type": "tablet"},
        {"employee_id": "EMP1005", "employee_name": "Henry Xu", "status": "pending", "email": "henry.xu@company.com", "asset_type": "laptop"},
    ]
    os.makedirs("data/onboarding", exist_ok=True)
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump({"contracts": contracts}, f, indent=2)

    # --- data/onboarding/equipment_inventory.json (共5台设备，只有一台可用笔记本) ---
    inventory = [
        {"asset_tag": "LT-001", "asset_type": "laptop", "status": "available"},
        {"asset_tag": "LT-002", "asset_type": "laptop", "status": "damaged"},
        {"asset_tag": "LT-003", "asset_type": "laptop", "status": "assigned"},
        {"asset_tag": "MN-001", "asset_type": "monitor", "status": "available"},
        {"asset_tag": "TB-001", "asset_type": "tablet", "status": "available"},
    ]
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump({"equipment_inventory": inventory}, f, indent=2)

    # --- data/onboarding/permission_packs.json ---
    packs = [
        {"pack_id": "PKG_ENG", "systems": ["gitlab", "jenkins", "aws-dev"]},
        {"pack_id": "PKG_MKT", "systems": ["salesforce", "hubspot"]},
        {"pack_id": "PKG_FIN", "systems": ["erp", "quickbooks"]},
    ]
    # 没有员工部门信息？为了简化，我们在合同里不加 department，而是让 agent 通过员工名称推断？不，我们需要明确。重新设计：在 contracts 中加入 department 字段，以便匹配权限包。
    # 但之前已经写了 contracts 结构，我们修改一下，加入 department。
    contracts = [
        {"employee_id": "EMP1001", "employee_name": "David Zhao", "department": "Engineering", "status": "signed", "email": "alice.wang@company.com", "asset_type": "monitor"},
        {"employee_id": "EMP1002", "employee_name": "Eva Liu", "department": "Engineering", "status": "signed", "email": "eva.liu@company.com", "asset_type": "laptop"},
        {"employee_id": "EMP1003", "employee_name": "Frank Zhang", "department": "Engineering", "status": "signed", "email": "frank.zhang@company.com", "asset_type": "laptop"},
        {"employee_id": "EMP1004", "employee_name": "Grace Wu", "department": "Marketing", "status": "pending", "email": "grace.wu@company.com", "asset_type": "tablet"},
        {"employee_id": "EMP1005", "employee_name": "Henry Xu", "department": "Finance", "status": "pending", "email": "henry.xu@company.com", "asset_type": "laptop"},
    ]
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump({"contracts": contracts}, f, indent=2)
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump({"permission_packs": packs}, f, indent=2)

    # --- 干扰：在根目录放一个无关的 note.txt ---
    with open("README.txt", "w") as f:
        f.write("Some random info, ignore.\n")

if __name__ == "__main__":
    build_env()
