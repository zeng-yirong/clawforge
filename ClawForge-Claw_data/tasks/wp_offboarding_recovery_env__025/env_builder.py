import os
import json

def build_env():
    # 创建数据目录
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 预留空目录，agent 可覆盖

    # 1. exit_requests.json
    exit_requests = {
        "exit_requests": [
            {"employee_id": "EMP001", "employee_name": "Jane Doe", "approval_status": "approved"},
            {"employee_id": "EMP002", "employee_name": "John Smith", "approval_status": "pending"},
            {"employee_id": "EMP003", "employee_name": "Alice Jones", "approval_status": "approved"}
        ]
    }
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump(exit_requests, f, indent=2)

    # 2. system_access.json
    system_access = {
        "system_access": [
            {"employee_id": "EMP001", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "EMP001", "system_name": "CRM", "status": "active"},
            {"employee_id": "EMP002", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "EMP003", "system_name": "Admin Portal", "status": "revoked"},
            {"employee_id": "EMP003", "system_name": "CRM", "status": "revoked"}
        ]
    }
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump(system_access, f, indent=2)

    # 3. equipment_assignments.json
    equipment_assignments = {
        "equipment_assignments": [
            {"employee_id": "EMP001", "asset_tag": "BG-8821", "status": "assigned"},
            {"employee_id": "EMP002", "asset_tag": "LT-2041", "status": "assigned"},
            {"employee_id": "EMP003", "asset_tag": "MB-9012", "status": "reclaimed"}
        ]
    }
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump(equipment_assignments, f, indent=2)

    # 4. 干扰文件：旧归档（无实际用途）
    os.makedirs("data/offboarding/archive", exist_ok=True)

if __name__ == "__main__":
    build_env()
