import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 写入离职申请数据 (exit_requests.json)
    exit_requests = [
        {"employee_id": "E001", "employee_name": "Alice Wang", "approval_status": "approved"},
        {"employee_id": "E002", "employee_name": "Bob Li", "approval_status": "approved"},
        {"employee_id": "E003", "employee_name": "Charlie Zhang", "approval_status": "pending"},
        {"employee_id": "E004", "employee_name": "Diana Chen", "approval_status": "approved"},
        {"employee_id": "E005", "employee_name": "Eve Zhao", "approval_status": "disapproved"}
    ]
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump({"exit_requests": exit_requests}, f, indent=2)

    # 写入系统权限数据 (system_access.json)
    system_access = [
        {"employee_id": "E001", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "E001", "system_name": "CRM", "status": "active"},
        {"employee_id": "E002", "system_name": "Admin Portal", "status": "revoked"},
        {"employee_id": "E002", "system_name": "CRM", "status": "active"},
        {"employee_id": "E003", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "E004", "system_name": "Admin Portal", "status": "revoked"},
        {"employee_id": "E005", "system_name": "CRM", "status": "active"}
    ]
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump({"system_access": system_access}, f, indent=2)

    # 写入设备分配数据 (equipment_assignments.json)
    equipment_assignments = [
        {"employee_id": "E001", "asset_tag": "LT-2041", "status": "assigned"},
        {"employee_id": "E002", "asset_tag": "BG-8821", "status": "returned"},
        {"employee_id": "E003", "asset_tag": "LT-2041", "status": "assigned"},
        {"employee_id": "E004", "asset_tag": "BG-8821", "status": "assigned"},
        {"employee_id": "E005", "asset_tag": "BG-8821", "status": "assigned"}
    ]
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump({"equipment_assignments": equipment_assignments}, f, indent=2)

    # 干扰文件：旧的离职请求（过时版本）
    old_exit = [
        {"employee_id": "E001", "employee_name": "Alice Wang", "approval_status": "pending"},
        {"employee_id": "E003", "employee_name": "Charlie Zhang", "approval_status": "approved"}
    ]
    with open("data/offboarding/old_exit_requests.json", "w") as f:
        json.dump({"exit_requests": old_exit}, f, indent=2)

    # 干扰文件：一个无关的说明文档
    with open("data/offboarding/README.txt", "w") as f:
        f.write("离职流程数据存放目录，请勿直接修改。\n")

if __name__ == "__main__":
    build_env()
