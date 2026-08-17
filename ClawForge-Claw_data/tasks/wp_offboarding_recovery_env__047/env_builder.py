import os
import json

def build_env():
    # Create data directory structure
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/offboarding", exist_ok=True)

    # --- accounts.json ---
    accounts = [
        {"account_id": "EMP001", "display_name": "Alice Wang", "department": "Marketing", "email": "alice@company.com", "permissions": ["read"]},
        {"account_id": "EMP002", "display_name": "Bob Smith", "department": "Finance", "email": "bob@company.com", "permissions": ["read", "write"]},
        {"account_id": "EMP003", "display_name": "Mark Johnson", "department": "Engineering", "email": "mark.j@company.com", "permissions": ["read", "write", "admin"]},
        {"account_id": "EMP004", "display_name": "Diana Lee", "department": "Engineering", "email": "diana@company.com", "permissions": ["read"]},
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # --- contacts.json ---
    contacts = [
        {"contact_id": "C001", "name": "Sarah Lee", "role": "Engineering Manager", "email": "sarah.lee@company.com"},
        {"contact_id": "C002", "name": "IT Helpdesk", "role": "Support", "email": "help@company.com"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # --- exit_requests.json (in data/offboarding/) ---
    exit_requests = [
        {"employee_id": "EMP001", "employee_name": "Alice Wang", "approval_status": "pending"},
        {"employee_id": "EMP002", "employee_name": "Bob Smith", "approval_status": "rejected"},
        {"employee_id": "EMP003", "employee_name": "Mark Johnson", "approval_status": "approved"},
        {"employee_id": "EMP004", "employee_name": "Diana Lee", "approval_status": "approved"},
        {"employee_id": "EMP005", "employee_name": "Eve Chen", "approval_status": "pending"},
    ]
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump(exit_requests, f, indent=2)

    # --- system_access.json (in data/offboarding/) ---
    system_access = [
        {"employee_id": "EMP001", "system_name": "CRM", "status": "active"},
        {"employee_id": "EMP001", "system_name": "Admin Portal", "status": "suspended"},
        {"employee_id": "EMP002", "system_name": "CRM", "status": "active"},
        {"employee_id": "EMP003", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "EMP003", "system_name": "CRM", "status": "active"},
        {"employee_id": "EMP004", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "EMP004", "system_name": "CRM", "status": "active"},
        {"employee_id": "EMP005", "system_name": "CRM", "status": "active"},
    ]
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump(system_access, f, indent=2)

    # --- equipment_assignments.json (in data/offboarding/) ---
    equipment_assignments = [
        {"employee_id": "EMP001", "asset_tag": "LT-2041", "status": "assigned"},
        {"employee_id": "EMP002", "asset_tag": "BG-8821", "status": "assigned"},
        {"employee_id": "EMP003", "asset_tag": "BG-8821", "status": "assigned"},
        {"employee_id": "EMP004", "asset_tag": "LT-2041", "status": "assigned"},
    ]
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump(equipment_assignments, f, indent=2)

    # --- some irrelevant noise files ---
    with open("data/offboarding/old_notes.txt", "w") as f:
        f.write("This is an old note.\n")
    with open("data/offboarding/backup_exit_requests.json", "w") as f:
        json.dump([{"employee_id": "EMP003", "approval_status": "draft"}], f)

if __name__ == "__main__":
    build_env()
