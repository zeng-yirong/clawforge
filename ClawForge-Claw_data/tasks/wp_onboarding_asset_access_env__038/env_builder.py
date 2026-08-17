import os
import json
import random

def build_env():
    # 确保工作区干净
    os.makedirs("data/onboarding", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("email_profiles", exist_ok=True)
    os.makedirs("system_access", exist_ok=True)
    os.makedirs("equipment/assigned", exist_ok=True)
    os.makedirs("slack", exist_ok=True)

    # ---- contracts.json ----
    contracts = [
        {
            "employee_id": "EMP-101",
            "employee_name": "Alice Smith",
            "status": "active",
            "email": "alice.smith@external.com",
            "department": "Engineering"
        },
        {
            "employee_id": "EMP-202",
            "employee_name": "Bob Lee",
            "status": "expired",
            "email": "bob.lee@external.com",
            "department": "Engineering"
        },
        {
            "employee_id": "EMP-303",
            "employee_name": "Carol Chen",
            "status": "revoked",
            "email": "carol.chen@external.com",
            "department": "Marketing"
        },
        {
            "employee_id": "EMP-404",
            "employee_name": "Dave Wang",
            "status": "active",
            "email": "dave.wang@external.com",
            "department": "Sales"
        }
    ]
    # 插入一个额外干扰：离职员工但状态不明
    contracts.append({
        "employee_id": "EMP-505",
        "employee_name": "Eve Zhang",
        "status": "terminated",
        "email": "eve.zhang@external.com",
        "department": "Engineering"
    })
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump({"contracts": contracts}, f, indent=2)

    # ---- permission_packs.json ----
    packs = [
        {"pack_id": "eng_standard", "department": "Engineering", "systems": ["gitlab", "jenkins", "aws-dev", "jira"]},
        {"pack_id": "mkt_standard", "department": "Marketing", "systems": ["hubspot", "canva", "adobe"]},
        {"pack_id": "sales_standard", "department": "Sales", "systems": ["salesforce", "outreach", "zoom"]}
    ]
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump({"permission_packs": packs}, f, indent=2)

    # ---- equipment_inventory.json ----
    equipment = [
        {"asset_tag": "LAP-001", "asset_type": "laptop", "status": "available"},
        {"asset_tag": "LAP-002", "asset_type": "laptop", "status": "assigned"},
        {"asset_tag": "LAP-003", "asset_type": "laptop", "status": "retired"},
        {"asset_tag": "MON-001", "asset_type": "monitor", "status": "available"},
        {"asset_tag": "LAP-004", "asset_type": "laptop", "status": "available"}  # 干扰：还有一台可用，但Alice的分配规则取第一个可用
    ]
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump({"equipment_inventory": equipment}, f, indent=2)

    # ---- 额外数据文件（背景干扰） ----
    accounts = [
        {"account_id": "acc_alice", "display_name": "Alice Smith", "department": "Engineering", "email": "alice.smith@external.com", "permissions": []},
        {"account_id": "acc_bob", "display_name": "Bob Lee", "department": "Engineering", "email": "bob.lee@external.com", "permissions": []}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "ct_001", "name": "Nancy HR", "role": "HR", "email": "nancy@company.com"},
        {"contact_id": "ct_002", "name": "IT Support", "role": "IT", "email": "it@company.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
