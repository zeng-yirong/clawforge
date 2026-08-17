import os
import json

def build_env():
    # data directory
    os.makedirs("data/offboarding", exist_ok=True)

    # exit requests – 3 approved, 1 pending, 1 rejected, plus a pending-only file as distractor
    exit_requests = {
        "exit_requests": [
            {"employee_id": "EMP001", "employee_name": "Alice Smith",   "approval_status": "approved"},
            {"employee_id": "EMP002", "employee_name": "Bob Johnson",   "approval_status": "approved"},
            {"employee_id": "EMP003", "employee_name": "Charlie Brown", "approval_status": "pending"},
            {"employee_id": "EMP004", "employee_name": "Diana Prince",  "approval_status": "approved"},
            {"employee_id": "EMP005", "employee_name": "Eve Wilson",    "approval_status": "rejected"}
        ]
    }
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump(exit_requests, f, indent=2)

    # system access – some already inactive, one distractor employee
    system_access = {
        "system_access": [
            {"employee_id": "EMP001", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "EMP001", "system_name": "CRM",          "status": "active"},
            {"employee_id": "EMP002", "system_name": "CRM",          "status": "active"},
            {"employee_id": "EMP003", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "EMP004", "system_name": "Admin Portal", "status": "inactive"},
            {"employee_id": "EMP005", "system_name": "CRM",          "status": "active"},
            # distractor – employee id not in exit_requests
            {"employee_id": "EMP999", "system_name": "Admin Portal", "status": "active"}
        ]
    }
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump(system_access, f, indent=2)

    # equipment assignments – each approved employee has one, plus distractor
    equipment_assignments = {
        "equipment_assignments": [
            {"employee_id": "EMP001", "asset_tag": "BG-8821", "status": "assigned"},
            {"employee_id": "EMP002", "asset_tag": "LT-2041", "status": "assigned"},
            {"employee_id": "EMP003", "asset_tag": "BG-8821", "status": "assigned"},   # pending – should not be reclaimed
            {"employee_id": "EMP004", "asset_tag": "BG-8821", "status": "assigned"},
            {"employee_id": "EMP005", "asset_tag": "LT-2041", "status": "assigned"}    # rejected – should not be reclaimed
        ]
    }
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump(equipment_assignments, f, indent=2)

    # distractor: a separate pending file that should be left untouched
    pending = {
        "pending_requests": [
            {"employee_id": "EMP006", "employee_name": "Frank Zappa", "approval_status": "pending"}
        ]
    }
    with open("data/offboarding/pending_requests.json", "w") as f:
        json.dump(pending, f, indent=2)

    # additional distractor files (not related to offboarding)
    accounts = {
        "accounts": [
            {"account_id": "A001", "display_name": "Alice Smith", "department": "Engineering", "email": "alice@example.com", "permissions": ["read", "write"]},
            {"account_id": "A002", "display_name": "Bob Johnson", "department": "Sales", "email": "bob@example.com", "permissions": ["read"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    contacts = {
        "contacts": [
            {"contact_id": "C001", "name": "Sarah Connor", "role": "IT Admin", "email": "sarah@example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

if __name__ == "__main__":
    build_env()
