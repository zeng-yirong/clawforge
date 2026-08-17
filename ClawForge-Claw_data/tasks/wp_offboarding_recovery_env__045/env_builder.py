import os
import json

def build_env():
    # 员工离职请求
    exit_requests = [
        {"employee_id": "E001", "employee_name": "Alice Wang", "approval_status": "approved"},
        {"employee_id": "E002", "employee_name": "Bob Li", "approval_status": "approved"},
        {"employee_id": "E003", "employee_name": "Carol Zhang", "approval_status": "pending"},
        {"employee_id": "E004", "employee_name": "David Chen", "approval_status": "rejected"},
        {"employee_id": "E005", "employee_name": "Eva Liu", "approval_status": "approved"}
    ]

    # 系统访问记录
    system_access = [
        {"employee_id": "E001", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "E001", "system_name": "CRM", "status": "active"},
        {"employee_id": "E002", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "E003", "system_name": "CRM", "status": "active"},          # pending 员工，不处理
        {"employee_id": "E004", "system_name": "Admin Portal", "status": "active"}  # rejected 员工，不处理
        # E005 没有任何系统访问记录（边缘情况）
    ]

    # 设备分配记录
    equipment_assignments = [
        {"employee_id": "E001", "asset_tag": "BG-8821", "status": "assigned"},
        {"employee_id": "E002", "asset_tag": "LT-2041", "status": "assigned"},
        # E003 无设备
        {"employee_id": "E004", "asset_tag": "BG-8821", "status": "assigned"},      # rejected 员工
        # E005 无设备
    ]

    os.makedirs("data/offboarding", exist_ok=True)
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump(exit_requests, f, indent=2)
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump(system_access, f, indent=2)
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump(equipment_assignments, f, indent=2)

if __name__ == "__main__":
    build_env()
