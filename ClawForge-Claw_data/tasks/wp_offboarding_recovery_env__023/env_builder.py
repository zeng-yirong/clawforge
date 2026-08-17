import os
import json

def build_env():
    # Create directory structure
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # ====== exit_requests.json (wrapper: exit_requests) ======
    exit_requests = {
        "exit_requests": [
            {
                "employee_id": "E-1001",
                "employee_name": "Alice",
                "department": "Engineering",
                "approval_status": "approved"
            },
            {
                "employee_id": "E-2001",
                "employee_name": "Bob",
                "department": "Sales",
                "approval_status": "pending"
            },
            {
                "employee_id": "E-3001",
                "employee_name": "Charlie",
                "department": "Marketing",
                "approval_status": "denied"
            },
            {
                "employee_id": "E-4001",
                "employee_name": "Diana",
                "department": "Finance",
                "approval_status": "approved"
            }
        ]
    }
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump(exit_requests, f, indent=2)

    # ====== system_access.json (wrapper: system_access) ======
    system_access = {
        "system_access": [
            # Alice – active systems need revoking
            {"employee_id": "E-1001", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "E-1001", "system_name": "CRM", "status": "active"},
            # Bob – active but not approved yet (should be left untouched)
            {"employee_id": "E-2001", "system_name": "Admin Portal", "status": "active"},
            # Charlie – denied, already inactive
            {"employee_id": "E-3001", "system_name": "CRM", "status": "inactive"},
            # Diana – approved but systems already revoked (trick: should not be changed again)
            {"employee_id": "E-4001", "system_name": "Admin Portal", "status": "revoked"},
            {"employee_id": "E-4001", "system_name": "CRM", "status": "revoked"}
        ]
    }
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump(system_access, f, indent=2)

    # ====== equipment_assignments.json (wrapper: equipment_assignments) ======
    equipment_assignments = {
        "equipment_assignments": [
            # Alice – assigned laptop
            {"employee_id": "E-1001", "asset_tag": "LT-2041", "status": "assigned"},
            # Bob – assigned but no approved request
            {"employee_id": "E-2001", "asset_tag": "BG-8821", "status": "assigned"},
            # Charlie – returned
            {"employee_id": "E-3001", "asset_tag": "LT-2041", "status": "returned"},
            # Diana – already reclaimed
            {"employee_id": "E-4001", "asset_tag": "BG-8821", "status": "reclaimed"}
        ]
    }
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump(equipment_assignments, f, indent=2)

    # ====== Interfering files (old data, different format, etc.) ======
    # Old backup (should not be used)
    old_records = {
        "2024-08-01": [
            {"employee_id": "E-1001", "status": "exit_completed"}
        ]
    }
    with open("data/offboarding/old_records.json", "w") as f:
        json.dump(old_records, f, indent=2)

    # accounts.json for reference (some employees)
    accounts = {
        "accounts": [
            {"account_id": "a1001", "display_name": "Alice", "department": "Engineering", "email": "alice@company.com", "permissions": ["admin", "crm"]},
            {"account_id": "a2001", "display_name": "Bob", "department": "Sales", "email": "bob@company.com", "permissions": ["crm"]},
            {"account_id": "a3001", "display_name": "Charlie", "department": "Marketing", "email": "charlie@company.com", "permissions": ["read"]},
            {"account_id": "a4001", "display_name": "Diana", "department": "Finance", "email": "diana@company.com", "permissions": ["admin", "finance"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # contacts.json (unrelated)
    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "IT Support", "role": "admin", "email": "it@company.com"},
            {"contact_id": "c002", "name": "HR", "role": "manager", "email": "hr@company.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

if __name__ == "__main__":
    build_env()
