import os
import json

def build_env():
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    accounts = {
        "accounts": [
            {"account_id": "EMP-001", "display_name": "John Doe", "department": "Engineering", "email": "john@company.com", "permissions": ["read", "write"]},
            {"account_id": "EMP-002", "display_name": "Jane Smith", "department": "Marketing", "email": "jane@company.com", "permissions": ["read"]},
            {"account_id": "EMP-003", "display_name": "Bob Johnson", "department": "Finance", "email": "bob@company.com", "permissions": ["admin", "read", "write"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    contacts = {
        "contacts": [
            {"contact_id": "C001", "name": "Alice Wang", "role": "HR Manager", "email": "alice@company.com"},
            {"contact_id": "C002", "name": "Tom Lee", "role": "IT Support", "email": "tom@company.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    exit_requests = {
        "exit_requests": [
            {"employee_id": "EMP-001", "employee_name": "John Doe", "approval_status": "pending"},
            {"employee_id": "EMP-002", "employee_name": "Jane Smith", "approval_status": "rejected"},
            {"employee_id": "EMP-003", "employee_name": "Bob Johnson", "approval_status": "approved"}
        ]
    }
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump(exit_requests, f, indent=2)

    system_access = {
        "system_access": [
            {"employee_id": "EMP-001", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "EMP-003", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "EMP-003", "system_name": "CRM", "status": "active"},
            {"employee_id": "EMP-002", "system_name": "CRM", "status": "suspended"}
        ]
    }
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump(system_access, f, indent=2)

    equipment_assignments = {
        "equipment_assignments": [
            {"employee_id": "EMP-001", "asset_tag": "BG-8821", "status": "assigned"},
            {"employee_id": "EMP-003", "asset_tag": "LT-2041", "status": "assigned"},
            {"employee_id": "EMP-002", "asset_tag": "LT-2041", "status": "returned"}
        ]
    }
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump(equipment_assignments, f, indent=2)

    # 干扰文件，不影响业务
    with open("ops/note_old.txt", "w") as f:
        f.write("This is just an old note, ignore.\n")

if __name__ == "__main__":
    build_env()
