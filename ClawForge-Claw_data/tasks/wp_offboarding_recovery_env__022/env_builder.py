import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # exit_requests.json  – 只有 EMP-007 是已审批且待处理的
    exit_requests = {
        "exit_requests": [
            {"employee_id": "EMP-007", "employee_name": "Alice Wang", "approval_status": "approved"},
            {"employee_id": "EMP-001", "employee_name": "Bob Li", "approval_status": "approved"},
            {"employee_id": "EMP-002", "employee_name": "Charlie Chen", "approval_status": "pending"},
            {"employee_id": "EMP-003", "employee_name": "Diana Zhang", "approval_status": "rejected"}
        ]
    }
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump(exit_requests, f, indent=2)

    # system_access.json  – EMP-007 两条 active，EMP-001 已 revoked，EMP-002 还有 active
    system_access = {
        "system_access": [
            {"employee_id": "EMP-007", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "EMP-007", "system_name": "CRM", "status": "active"},
            {"employee_id": "EMP-001", "system_name": "Admin Portal", "status": "revoked"},
            {"employee_id": "EMP-001", "system_name": "CRM", "status": "revoked"},
            {"employee_id": "EMP-002", "system_name": "VPN", "status": "active"},
            {"employee_id": "EMP-002", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "EMP-003", "system_name": "CRM", "status": "active"}
        ]
    }
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump(system_access, f, indent=2)

    # equipment_assignments.json  – EMP-007 已分配，EMP-001 已回收，EMP-002、EMP-003 还有分配
    equipment_assignments = {
        "equipment_assignments": [
            {"employee_id": "EMP-007", "asset_tag": "LT-2041", "status": "assigned"},
            {"employee_id": "EMP-001", "asset_tag": "BG-8821", "status": "reclaimed"},
            {"employee_id": "EMP-002", "asset_tag": "LT-2041", "status": "assigned"},
            {"employee_id": "EMP-003", "asset_tag": "BG-8821", "status": "assigned"}
        ]
    }
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump(equipment_assignments, f, indent=2)

    # accounts.json – 必需的员工详细信息
    accounts = {
        "accounts": [
            {"account_id": "EMP-007", "display_name": "Alice Wang", "department": "Engineering", "email": "alice@company.com", "permissions": ["admin", "crm"]},
            {"account_id": "EMP-001", "display_name": "Bob Li", "department": "Finance", "email": "bob@company.com", "permissions": ["finance"]},
            {"account_id": "EMP-002", "display_name": "Charlie Chen", "department": "Marketing", "email": "charlie@company.com", "permissions": ["marketing"]},
            {"account_id": "EMP-003", "display_name": "Diana Zhang", "department": "Engineering", "email": "diana@company.com", "permissions": ["dev"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # contacts.json – 干扰文件，无需使用
    contacts = {
        "contacts": [
            {"contact_id": "C001", "name": "HR Help", "role": "HR", "email": "hr@company.com"},
            {"contact_id": "C002", "name": "IT Support", "role": "IT", "email": "it@company.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

if __name__ == "__main__":
    build_env()
