import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # accounts.json – 所有员工主数据
    accounts = {
        "accounts": [
            {"account_id": "E-0431", "display_name": "Emma Johnson", "department": "Engineering", "email": "emma.j@example.com", "permissions": ["read", "write"]},
            {"account_id": "E-0123", "display_name": "John Smith", "department": "Marketing", "email": "john.s@example.com", "permissions": ["read"]},
            {"account_id": "E-0789", "display_name": "Alice Wang", "department": "Finance", "email": "alice.w@example.com", "permissions": ["admin"]},
            {"account_id": "E-0567", "display_name": "Bob Lee", "department": "IT", "email": "bob.l@example.com", "permissions": ["read", "write", "admin"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # contacts.json – 联系人（干扰项，不参与核心逻辑）
    contacts = {
        "contacts": [
            {"contact_id": "C-1001", "name": "Lisa Wong", "role": "HR Manager", "email": "lisa.w@example.com"},
            {"contact_id": "C-1002", "name": "Mike Chen", "role": "IT Support", "email": "mike.c@example.com"},
            {"contact_id": "C-1003", "name": "Sarah Lee", "role": "Finance Lead", "email": "sarah.l@example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # exit_requests.json
    exit_requests = {
        "exit_requests": [
            {"employee_id": "E-0431", "employee_name": "Emma Johnson", "approval_status": "approved"},
            {"employee_id": "E-0123", "employee_name": "John Smith", "approval_status": "pending"},
            {"employee_id": "E-0789", "employee_name": "Alice Wang", "approval_status": "approved"},
            {"employee_id": "E-0567", "employee_name": "Bob Lee", "approval_status": "rejected"}
        ]
    }
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump(exit_requests, f, indent=2)

    # system_access.json
    system_access = {
        "system_access": [
            {"employee_id": "E-0431", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "E-0431", "system_name": "CRM", "status": "active"},
            {"employee_id": "E-0123", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "E-0789", "system_name": "Admin Portal", "status": "revoked"},
            {"employee_id": "E-0789", "system_name": "CRM", "status": "revoked"},
            {"employee_id": "E-0567", "system_name": "CRM", "status": "active"}
        ]
    }
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump(system_access, f, indent=2)

    # equipment_assignments.json
    equipment_assignments = {
        "equipment_assignments": [
            {"employee_id": "E-0431", "asset_tag": "BG-8821", "status": "assigned"},
            {"employee_id": "E-0123", "asset_tag": "BG-8821", "status": "assigned"},
            {"employee_id": "E-0789", "asset_tag": "LT-2041", "status": "returned"},
            {"employee_id": "E-0567", "asset_tag": "LT-2041", "status": "assigned"}
        ]
    }
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump(equipment_assignments, f, indent=2)

if __name__ == "__main__":
    build_env()
