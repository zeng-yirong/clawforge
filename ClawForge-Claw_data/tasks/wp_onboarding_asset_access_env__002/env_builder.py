import os
import json

def build_env():
    os.makedirs("data/onboarding", exist_ok=True)
    
    contracts = [
        {
            "employee_id": "EMP003",
            "employee_name": "张三",
            "department": "Engineering",
            "email": "zhangsan@company.com",
            "status": "signed"
        },
        {
            "employee_id": "EMP004",
            "employee_name": "张三",
            "department": "Sales",
            "email": "zhangsan2@company.com",
            "status": "revoked"
        },
        {
            "employee_id": "EMP001",
            "employee_name": "李四",
            "department": "Sales",
            "email": "lisi@company.com",
            "status": "signed"
        },
        {
            "employee_id": "EMP002",
            "employee_name": "王五",
            "department": "HR",
            "email": "wangwu@company.com",
            "status": "pending"
        }
    ]
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump({"contracts": contracts}, f, indent=2)
    
    equipment = [
        {"asset_tag": "LP-001", "asset_type": "laptop", "status": "available"},
        {"asset_tag": "LP-002", "asset_type": "laptop", "status": "assigned"},
        {"asset_tag": "LP-003", "asset_type": "laptop", "status": "broken"},
        {"asset_tag": "MN-001", "asset_type": "monitor", "status": "available"}
    ]
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump({"equipment_inventory": equipment}, f, indent=2)
    
    permission_packs = [
        {"pack_id": "engineering-std", "department": "Engineering", "systems": ["gitlab", "jira", "confluence", "aws"]},
        {"pack_id": "sales-std", "department": "Sales", "systems": ["salesforce", "hubspot"]},
        {"pack_id": "hr-std", "department": "HR", "systems": ["bamboohr", "workday"]}
    ]
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump({"permission_packs": permission_packs}, f, indent=2)

if __name__ == "__main__":
    build_env()
