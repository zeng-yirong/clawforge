import os
import json

def build_env():
    # Create directory structure
    os.makedirs("data/offboarding", exist_ok=True)

    # ---- exit_requests.json ----
    exit_requests = [
        {
            "employee_id": "EMP001",
            "employee_name": "李芳",
            "approval_status": "pending"
        },
        {
            "employee_id": "EMP002",
            "employee_name": "王强",
            "approval_status": "denied"
        },
        {
            "employee_id": "EMP003",
            "employee_name": "张伟",
            "approval_status": "approved"
        },
        {
            "employee_id": "EMP004",
            "employee_name": "赵敏",
            "approval_status": "approved"
        }
    ]
    # Add a second approved but already processed record (干扰项：已被回收，系统访问已撤销)
    # 这里故意让 EMP004 的系统访问状态都是 inactive，设备已回收，但 agent 不应处理已撤销的
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump(exit_requests, f, indent=2)

    # ---- system_access.json ----
    system_access = [
        {
            "employee_id": "EMP003",
            "system_name": "Admin Portal",
            "status": "active"
        },
        {
            "employee_id": "EMP003",
            "system_name": "CRM",
            "status": "active"
        },
        {
            "employee_id": "EMP004",
            "system_name": "Admin Portal",
            "status": "inactive"   # 已撤销
        },
        {
            "employee_id": "EMP004",
            "system_name": "CRM",
            "status": "inactive"
        },
        {
            "employee_id": "EMP001",
            "system_name": "Admin Portal",
            "status": "active"
        },
        {
            "employee_id": "EMP001",
            "system_name": "CRM",
            "status": "active"
        }
    ]
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump(system_access, f, indent=2)

    # ---- equipment_assignments.json ----
    equipment_assignments = [
        {
            "employee_id": "EMP003",
            "asset_tag": "LT-2041",
            "status": "assigned"
        },
        {
            "employee_id": "EMP003",
            "asset_tag": "BG-8821",
            "status": "assigned"
        },
        {
            "employee_id": "EMP004",
            "asset_tag": "LT-2041",
            "status": "returned"   # 已回收
        },
        {
            "employee_id": "EMP001",
            "asset_tag": "BG-8821",
            "status": "assigned"
        }
    ]
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump(equipment_assignments, f, indent=2)

    # ---- additional distraction data (optional, to simulate real environment) ----
    os.makedirs("backup", exist_ok=True)
    with open("backup/old_exit_requests.csv", "w") as f:
        f.write("employee_id,status\nEMP003,rejected\nEMP005,pending")
