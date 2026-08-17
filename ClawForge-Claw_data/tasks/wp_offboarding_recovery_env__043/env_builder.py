import json
import os

def build_env():
    # 保证目录存在
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 预留空目录，agent 需要创建文件

    # ---- exit_requests.json ----
    exit_requests = {
        "exit_requests": [
            {"employee_id": "E001", "employee_name": "Alice Wang", "approval_status": "approved"},
            {"employee_id": "E002", "employee_name": "Bob Li", "approval_status": "approved"},
            {"employee_id": "E003", "employee_name": "Carol Zhang", "approval_status": "pending"},
            {"employee_id": "E004", "employee_name": "David Chen", "approval_status": "rejected"}
        ]
    }
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump(exit_requests, f, indent=2)

    # ---- system_access.json ----
    system_access = {
        "system_access": [
            # E001 -> 两个系统，都是 active
            {"employee_id": "E001", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "E001", "system_name": "CRM", "status": "active"},
            # E002 -> 两个系统，都是 active
            {"employee_id": "E002", "system_name": "VPN", "status": "active"},
            {"employee_id": "E002", "system_name": "Email", "status": "active"},
            # 干扰：E003（pending）也有系统，但不应处理
            {"employee_id": "E003", "system_name": "GitLab", "status": "active"},
            # 干扰：E004（rejected）也有系统
            {"employee_id": "E004", "system_name": "Jira", "status": "active"},
            # 额外干扰：不存在的员工
            {"employee_id": "E999", "system_name": "Legacy", "status": "active"},
        ]
    }
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump(system_access, f, indent=2)

    # ---- equipment_assignments.json ----
    equipment_assignments = {
        "equipment_assignments": [
            # E001 设备
            {"employee_id": "E001", "asset_tag": "LT-2041", "status": "assigned"},
            # E002 设备
            {"employee_id": "E002", "asset_tag": "BG-8821", "status": "assigned"},
            # 干扰：E003 设备（pending）
            {"employee_id": "E003", "asset_tag": "MG-1122", "status": "assigned"},
            # 干扰：E004 设备（rejected）
            {"employee_id": "E004", "asset_tag": "TB-3301", "status": "assigned"},
            # 额外干扰：不存在的员工
            {"employee_id": "E999", "asset_tag": "XY-9999", "status": "assigned"},
        ]
    }
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump(equipment_assignments, f, indent=2)

    # ---- 可选干扰文件（accounts / contacts） ----
    os.makedirs("data", exist_ok=True)
    accounts = {
        "accounts": [
            {"account_id": "acc001", "display_name": "Alice Wang", "department": "Engineering", "email": "alice@example.com", "permissions": ["read", "write"]},
            {"account_id": "acc002", "display_name": "Bob Li", "department": "Sales", "email": "bob@example.com", "permissions": ["read"]},
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "HR Admin", "role": "offboarding", "email": "hr@example.com"},
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 建立空 ops 目录（确保存在）
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
