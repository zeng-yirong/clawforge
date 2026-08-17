import os
import json

def build_env():
    # 确保基础目录存在
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("data/offboarding/archive", exist_ok=True)

    # 干扰数据：accounts.json 和 contacts.json
    accounts = {
        "accounts": [
            {"account_id": "a001", "display_name": "Alice", "department": "Engineering", "email": "alice@corp.com", "permissions": ["read"]},
            {"account_id": "a002", "display_name": "Bob", "department": "HR", "email": "bob@corp.com", "permissions": ["read","write"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Charlie", "role": "Manager", "email": "charlie@corp.com"},
            {"contact_id": "c002", "name": "Diana", "role": "Employee", "email": "diana@corp.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 核心数据
    exit_requests = {
        "exit_requests": [
            {"employee_id": "EMP001", "employee_name": "Alice", "approval_status": "approved"},
            {"employee_id": "EMP002", "employee_name": "Bob", "approval_status": "pending"},
            {"employee_id": "EMP003", "employee_name": "Charlie", "approval_status": "approved"},
            {"employee_id": "EMP004", "employee_name": "Diana", "approval_status": "rejected"},
            {"employee_id": "EMP005", "employee_name": "Eve", "approval_status": "approved"},
            {"employee_id": "EMP006", "employee_name": "Frank", "approval_status": "approved"}
        ]
    }
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump(exit_requests, f, indent=2)

    system_access = {
        "system_access": [
            {"employee_id": "EMP001", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "EMP003", "system_name": "CRM", "status": "revoked"},
            {"employee_id": "EMP005", "system_name": "Admin Portal", "status": "revoked"},
            {"employee_id": "EMP006", "system_name": "Admin Portal", "status": "revoked"},
            {"employee_id": "EMP006", "system_name": "CRM", "status": "active"}
        ]
    }
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump(system_access, f, indent=2)

    equipment_assignments = {
        "equipment_assignments": [
            {"employee_id": "EMP001", "asset_tag": "BG-8821", "status": "active"},
            {"employee_id": "EMP003", "asset_tag": "LT-2041", "status": "returned"},
            {"employee_id": "EMP005", "asset_tag": "BG-8821", "status": "returned"},
            {"employee_id": "EMP006", "asset_tag": "LT-2041", "status": "returned"}
        ]
    }
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump(equipment_assignments, f, indent=2)

    # 干扰存档（旧版本）
    old_exit = {
        "exit_requests": [
            {"employee_id": "EMP999", "employee_name": "Ghost", "approval_status": "approved"}
        ]
    }
    with open("data/offboarding/archive/exit_requests_backup.json", "w") as f:
        json.dump(old_exit, f, indent=2)

if __name__ == "__main__":
    build_env()
