import json
import os

def build_env():
    # 创建目录结构
    os.makedirs("data/onboarding", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    # 干扰项：其他部门的合同（未签署）
    contracts = {
        "EMP_001": {"employee_id": "EMP_001", "employee_name": "John Doe", "status": "pending", "email": "john.doe@company.com", "department": "Sales"},
        "EMP_002": {"employee_id": "EMP_002", "employee_name": "Jane Smith", "status": "expired", "email": "jane.smith@company.com", "department": "HR"},
        "EMP_003": {"employee_id": "EMP_003", "employee_name": "Bob Lee", "status": "signed", "email": "bob.lee@old-company.com", "department": "Engineering"},  # 诱饵：邮箱域名不同
        "EMP_007": {"employee_id": "EMP_007", "employee_name": "Emma Chen", "status": "signed", "email": "emma.chen@company.com", "department": "Engineering"},
        "EMP_008": {"employee_id": "EMP_008", "employee_name": "Tom Green", "status": "signed", "email": "tom.green@company.com", "department": "Sales"}
    }
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump({"contracts": list(contracts.values())}, f, indent=2)

    # 权限包
    permission_packs = {
        "engineering": {"pack_id": "engineering", "systems": ["github", "jenkins", "aws", "k8s"]},
        "sales": {"pack_id": "sales", "systems": ["crm", "emailer"]},
        "hr": {"pack_id": "hr", "systems": ["hr-portal", "payroll"]}
    }
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump({"permission_packs": list(permission_packs.values())}, f, indent=2)

    # 设备库存（含干扰项）
    inventory = [
        {"asset_tag": "LAPTOP-001", "asset_type": "laptop", "status": "assigned"},
        {"asset_tag": "LAPTOP-002", "asset_type": "laptop", "status": "faulty"},
        {"asset_tag": "LAPTOP-003", "asset_type": "laptop", "status": "available"},
        {"asset_tag": "LAPTOP-004", "asset_type": "laptop", "status": "available"},  # 多一台可用，但后续可指定唯一性？需要唯一答案，我们设定只有LAPTOP-003是合适的？
        {"asset_tag": "MONITOR-001", "asset_type": "monitor", "status": "available"},
        {"asset_tag": "DOCK-001", "asset_type": "dock", "status": "available"}
    ]
    # 为了唯一性，我们规定分配给Emma的必须是LAPTOP-003，因为其他可用笔记本中LAPTOP-004的asset_type虽然是laptop但我们在验证中通过条件指定（例如最近采购的？）但最好通过唯一性设计：让LAPTOP-004属于另一个部门？但库存没有部门字段。
    # 简单处理：在验证中，我们只要求agent分配任意一台available的laptop，但为了唯一答案，我们设定只有一台available的laptop：去掉LAPTOP-004。
    # 修正：只保留一台可用laptop
    inventory = [
        {"asset_tag": "LAPTOP-001", "asset_type": "laptop", "status": "assigned"},
        {"asset_tag": "LAPTOP-002", "asset_type": "laptop", "status": "faulty"},
        {"asset_tag": "LAPTOP-003", "asset_type": "laptop", "status": "available"},
        {"asset_tag": "MONITOR-001", "asset_type": "monitor", "status": "available"},
        {"asset_tag": "DOCK-001", "asset_type": "dock", "status": "available"}
    ]
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump({"equipment_inventory": inventory}, f, indent=2)

    # 创建一些干扰目录和文件
    os.makedirs("old_backups", exist_ok=True)
    with open("old_backups/contracts_backup.json", "w") as f:
        json.dump({"dummy": True}, f)
    os.makedirs("output", exist_ok=True)  # 预先创建空的output目录作为陷阱？但agent会覆盖，没关系
    with open("output/email_profile.json", "w") as f:
        f.write("{}")  # 空的干扰文件

if __name__ == "__main__":
    build_env()
