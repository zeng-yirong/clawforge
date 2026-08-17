import os
import json

def build_env():
    # 目录结构
    os.makedirs("data/onboarding", exist_ok=True)
    os.makedirs("data/slack_cache", exist_ok=True)

    # 合同数据（包含干扰项）
    contracts = {
        "contracts": [
            {
                "employee_id": "E001",
                "employee_name": "Alice Wang",
                "status": "signed",
                "email": "alice.wang@corp.com",
                "department": "engineering"
            },
            {
                "employee_id": "E002",
                "employee_name": "Bob Li",
                "status": "signed",
                "email": "bob.li@corp.com",
                "department": "design"
            },
            {
                "employee_id": "E003",
                "employee_name": "Charlie Zhang",
                "status": "pending",
                "email": "charlie.zhang@corp.com",
                "department": "engineering"
            },
            {
                "employee_id": "E004",
                "employee_name": "Diana Chen",
                "status": "cancelled",
                "email": "diana.chen@corp.com",
                "department": "marketing"
            }
        ]
    }
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump(contracts, f, indent=2)

    # 权限包模板
    permission_packs = {
        "permission_packs": [
            {"pack_id": "engineering", "systems": ["jira", "github", "vpn"]},
            {"pack_id": "design", "systems": ["figma", "slack", "vpn"]},
            {"pack_id": "marketing", "systems": ["hubspot", "slack"]}
        ]
    }
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump(permission_packs, f, indent=2)

    # 设备库存（包含已分配、维修中等干扰项）
    equipment_inventory = {
        "equipment_inventory": [
            {"asset_tag": "LT-001", "asset_type": "laptop", "status": "available"},
            {"asset_tag": "LT-002", "asset_type": "laptop", "status": "available"},
            {"asset_tag": "LT-003", "asset_type": "laptop", "status": "assigned", "assigned_to": "E003"},
            {"asset_tag": "LT-004", "asset_type": "laptop", "status": "maintenance"},
            {"asset_tag": "MN-001", "asset_type": "monitor", "status": "available"}
        ]
    }
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump(equipment_inventory, f, indent=2)

    # 空的 Slack 缓存
    slack_cache = {"messages": []}
    with open("data/slack_cache/messages.json", "w") as f:
        json.dump(slack_cache, f, indent=2)

if __name__ == "__main__":
    build_env()
