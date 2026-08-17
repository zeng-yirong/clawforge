import os, json

def build():
    # 创建目录结构
    os.makedirs("data/onboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("slack_cache", exist_ok=True)

    # 干扰项：已有欢迎消息
    with open("slack_cache/previous_welcome.log", "w") as f:
        f.write("Welcome Bob Smith!\n")

    # 合同数据
    contracts = [
        {"employee_id": "E001", "employee_name": "Emily Chen", "status": "signed", "email": "emily.c@personal.com", "department": "Engineering"},
        {"employee_id": "E002", "employee_name": "Bob Smith", "status": "draft", "email": "bob@test.com", "department": "Marketing"},
        {"employee_id": "E003", "employee_name": "Alice Wang", "status": "expired", "email": "alice@old.com", "department": "Engineering"}
    ]
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump(contracts, f, indent=2)

    # 设备库存
    equipments = [
        {"asset_tag": "LAPTOP-001", "asset_type": "laptop", "status": "available"},
        {"asset_tag": "LAPTOP-002", "asset_type": "laptop", "status": "assigned"},
        {"asset_tag": "PHONE-001", "asset_type": "phone", "status": "available"}
    ]
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump(equipments, f, indent=2)

    # 权限包
    packs = [
        {"pack_id": "P001", "systems": ["CRM", "ERP"], "department": "Engineering"},
        {"pack_id": "P002", "systems": ["CMS"], "department": "Marketing"}
    ]
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump(packs, f, indent=2)

if __name__ == "__main__":
    build()
