import os
import json
import random

def build_env():
    # Ensure base directories exist
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- accounts.json (for reference, not directly needed in task but realistic) ---
    accounts = [
        {"account_id": "EMP-001", "display_name": "Alice Wang", "department": "Engineering", "email": "alice@company.com", "permissions": ["read", "write"]},
        {"account_id": "EMP-002", "display_name": "Bob Li", "department": "Sales", "email": "bob@company.com", "permissions": ["read"]},
        {"account_id": "EMP-003", "display_name": "John Doe", "department": "IT", "email": "john.doe@company.com", "permissions": ["admin", "read", "write"]},
        {"account_id": "EMP-004", "display_name": "Carol Chen", "department": "HR", "email": "carol@company.com", "permissions": ["read", "write"]},
        {"account_id": "EMP-005", "display_name": "David Kim", "department": "Finance", "email": "david@company.com", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # --- contacts.json (distractor) ---
    contacts = [
        {"contact_id": "C-001", "name": "IT Helpdesk", "role": "support", "email": "it@company.com"},
        {"contact_id": "C-002", "name": "HR Team", "role": "hr", "email": "hr@company.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # --- exit_requests.json (core) ---
    exit_requests = [
        {"employee_id": "EMP-001", "employee_name": "Alice Wang", "approval_status": "pending"},
        {"employee_id": "EMP-002", "employee_name": "Bob Li", "approval_status": "rejected"},
        {"employee_id": "EMP-003", "employee_name": "John Doe", "approval_status": "approved"},
        {"employee_id": "EMP-004", "employee_name": "Carol Chen", "approval_status": "approved"},
        {"employee_id": "EMP-005", "employee_name": "David Kim", "approval_status": "approved"}
    ]
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump({"exit_requests": exit_requests}, f, indent=2)

    # --- system_access.json ---
    system_access = [
        # EMP-003 active accesses (to be revoked)
        {"employee_id": "EMP-003", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "EMP-003", "system_name": "CRM", "status": "active"},
        # EMP-004 already revoked (distractor)
        {"employee_id": "EMP-004", "system_name": "Admin Portal", "status": "revoked"},
        {"employee_id": "EMP-004", "system_name": "HR System", "status": "revoked"},
        # EMP-005 has no active systems (just for confusion)
        {"employee_id": "EMP-005", "system_name": "Finance Tool", "status": "active"},
        # other employees
        {"employee_id": "EMP-001", "system_name": "Engineering Dashboard", "status": "active"},
        {"employee_id": "EMP-002", "system_name": "Salesforce", "status": "active"}
    ]
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump({"system_access": system_access}, f, indent=2)

    # --- equipment_assignments.json ---
    equipment_assignments = [
        # EMP-003 assigned equipment (to be reclaimed)
        {"employee_id": "EMP-003", "asset_tag": "BG-8821", "status": "assigned"},
        # EMP-004 already reclaimed
        {"employee_id": "EMP-004", "asset_tag": "LT-2041", "status": "reclaimed"},
        # EMP-005 assigned but not in scope (approved but no system access? just distractor)
        {"employee_id": "EMP-005", "asset_tag": "BG-9912", "status": "assigned"},
        # other employees
        {"employee_id": "EMP-001", "asset_tag": "LT-1234", "status": "assigned"},
        {"employee_id": "EMP-002", "asset_tag": "BG-5678", "status": "assigned"}
    ]
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump({"equipment_assignments": equipment_assignments}, f, indent=2)

    # --- distractor files in ops/ ---
    # old checklist (should be ignored)
    old_checklist = [{"employee": "EMP-004", "date": "2025-01-15", "completed": True}]
    with open("ops/archive_checklist.json", "w") as f:
        json.dump(old_checklist, f, indent=2)
    # dummy log
    with open("ops/recent_offboarding.log", "w") as f:
        f.write("2025-02-10 14:32: EMP-004 processed\n")
        f.write("2025-02-11 09:15: EMP-005 pending\n")

if __name__ == "__main__":
    build_env()
