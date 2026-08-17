import os
import json

def build_env():
    # Create required directories
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # empty directory for agent to write into

    # --- Offboarding exit requests ---
    exit_requests = {
        "exit_requests": [
            {"employee_id": "E001", "employee_name": "Alice Wang", "department": "Engineering", "approval_status": "approved"},
            {"employee_id": "E002", "employee_name": "Bob Li", "department": "Marketing", "approval_status": "approved"},
            {"employee_id": "E003", "employee_name": "Charlie Chen", "department": "Finance", "approval_status": "pending"}
        ]
    }
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump(exit_requests, f, indent=2)

    # --- System Access ---
    system_access = {
        "system_access": [
            # Alice: both active → need revocation
            {"employee_id": "E001", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "E001", "system_name": "CRM", "status": "active"},
            # Bob: all systems already inactive → no action needed
            {"employee_id": "E002", "system_name": "Admin Portal", "status": "inactive"},
            {"employee_id": "E002", "system_name": "CRM", "status": "inactive"},
            # Charlie: pending, but has active system (should not be processed)
            {"employee_id": "E003", "system_name": "Admin Portal", "status": "active"}
        ]
    }
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump(system_access, f, indent=2)

    # --- Equipment Assignments ---
    equipment_assignments = {
        "equipment_assignments": [
            # Alice: still assigned → need reclaim
            {"employee_id": "E001", "asset_tag": "LT-2041", "status": "assigned"},
            # Bob: already returned → no action
            {"employee_id": "E002", "asset_tag": "BG-8821", "status": "returned"},
            # Charlie: pending, but assigned asset (should not be listed)
            {"employee_id": "E003", "asset_tag": "BG-8821", "status": "assigned"}
        ]
    }
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump(equipment_assignments, f, indent=2)

    # --- Distractor: accounts (not used in answer, but adds realism) ---
    accounts = {
        "accounts": [
            {"account_id": "A001", "display_name": "Alice Wang", "department": "Engineering", "email": "alice@corp.com", "permissions": ["admin"]},
            {"account_id": "A002", "display_name": "Bob Li", "department": "Marketing", "email": "bob@corp.com", "permissions": ["read"]},
            {"account_id": "A003", "display_name": "Charlie Chen", "department": "Finance", "email": "charlie@corp.com", "permissions": ["read"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # --- Distractor: contacts ---
    contacts = {
        "contacts": [
            {"contact_id": "C001", "name": "HR Manager", "role": "HR", "email": "hr@corp.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
