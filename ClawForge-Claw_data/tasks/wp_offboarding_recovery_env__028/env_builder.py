import os
import json

def build_env():
    # Ensure directory structure exists
    dirs = ["data/offboarding", "ops"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # Exit requests - 5 employees, 4 approved, 1 pending
    exit_requests = {
        "exit_requests": [
            {"employee_id": "E001", "employee_name": "Alice Wang", "approval_status": "approved"},
            {"employee_id": "E002", "employee_name": "Bob Li", "approval_status": "approved"},
            {"employee_id": "E003", "employee_name": "Charlie Zhang", "approval_status": "approved"},
            {"employee_id": "E004", "employee_name": "David Chen", "approval_status": "pending"},
            {"employee_id": "E005", "employee_name": "Eve Liu", "approval_status": "approved"}
        ]
    }
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump(exit_requests, f, indent=2)

    # System access - multiple records per employee, some already revoked
    system_access = {
        "system_access": [
            {"employee_id": "E001", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "E001", "system_name": "CRM", "status": "active"},
            {"employee_id": "E002", "system_name": "Admin Portal", "status": "revoked"},
            {"employee_id": "E002", "system_name": "CRM", "status": "active"},
            {"employee_id": "E003", "system_name": "Admin Portal", "status": "revoked"},
            {"employee_id": "E003", "system_name": "CRM", "status": "revoked"},
            {"employee_id": "E004", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "E005", "system_name": "Admin Portal", "status": "active"}
        ]
    }
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump(system_access, f, indent=2)

    # Equipment assignments - some already reclaimed
    equipment_assignments = {
        "equipment_assignments": [
            {"employee_id": "E001", "asset_tag": "BG-8821", "status": "assigned"},
            {"employee_id": "E002", "asset_tag": "LT-2041", "status": "assigned"},
            {"employee_id": "E003", "asset_tag": "BG-8821", "status": "reclaimed"},
            {"employee_id": "E004", "asset_tag": "LT-2041", "status": "assigned"}
        ]
    }
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump(equipment_assignments, f, indent=2)

    # Distractor files (contacts and accounts) - not used in this task
    contacts = {
        "contacts": [
            {"contact_id": "C001", "name": "Alice Wang", "role": "Engineer", "email": "alice@example.com"},
            {"contact_id": "C002", "name": "Bob Li", "role": "Analyst", "email": "bob@example.com"},
            {"contact_id": "C003", "name": "Charlie Zhang", "role": "Manager", "email": "charlie@example.com"},
            {"contact_id": "C004", "name": "David Chen", "role": "Intern", "email": "david@example.com"},
            {"contact_id": "C005", "name": "Eve Liu", "role": "Engineer", "email": "eve@example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    accounts = {
        "accounts": [
            {"account_id": "A001", "display_name": "Alice Wang", "department": "Engineering", "email": "alice@example.com", "permissions": ["read", "write"]},
            {"account_id": "A002", "display_name": "Bob Li", "department": "Sales", "email": "bob@example.com", "permissions": ["read"]},
            {"account_id": "A003", "display_name": "Charlie Zhang", "department": "Engineering", "email": "charlie@example.com", "permissions": ["admin"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

if __name__ == "__main__":
    build_env()
