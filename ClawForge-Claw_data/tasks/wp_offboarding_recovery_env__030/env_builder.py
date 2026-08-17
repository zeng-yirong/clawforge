import json
import os

def build_env():
    # Create directories
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("archive", exist_ok=True)

    # ---- exit_requests.json ----
    exit_requests = [
        {"employee_id": "E001", "employee_name": "Alice Wang", "approval_status": "approved"},
        {"employee_id": "E002", "employee_name": "Bob Li", "approval_status": "approved", "note": "no systems assigned"},
        {"employee_id": "E003", "employee_name": "Carol Chen", "approval_status": "approved"},
        {"employee_id": "E004", "employee_name": "David Zhang", "approval_status": "pending"},
        {"employee_id": "E005", "employee_name": "Eva Liu", "approval_status": "approved"},
        {"employee_id": "E006", "employee_name": "Frank Wu", "approval_status": "rejected"},
        {"employee_id": "E007", "employee_name": "Grace Zhou", "approval_status": "approved", "note": "already partly done"},
    ]
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump({"exit_requests": exit_requests}, f, indent=2)

    # ---- system_access.json ----
    system_access = [
        # E001 - two active systems
        {"employee_id": "E001", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "E001", "system_name": "CRM", "status": "active"},
        # E002 - no system records (should be handled gracefully)
        # E003 - one active, one already revoked (干扰)
        {"employee_id": "E003", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "E003", "system_name": "CRM", "status": "revoked"},
        # E004 - pending exit, should not be touched
        {"employee_id": "E004", "system_name": "Admin Portal", "status": "active"},
        # E005 - one active system
        {"employee_id": "E005", "system_name": "CRM", "status": "active"},
        # E006 - rejected, should not be touched (but still has records)
        {"employee_id": "E006", "system_name": "Admin Portal", "status": "active"},
        # E007 - already fully revoked (干扰)
        {"employee_id": "E007", "system_name": "Admin Portal", "status": "revoked"},
        {"employee_id": "E007", "system_name": "CRM", "status": "revoked"},
        # Extra interference: non-existent employee E008
        {"employee_id": "E008", "system_name": "Admin Portal", "status": "active"},
    ]
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump({"system_access": system_access}, f, indent=2)

    # ---- equipment_assignments.json ----
    equipment_assignments = [
        # E001 - one assigned device
        {"employee_id": "E001", "asset_tag": "BG-8821", "status": "assigned"},
        # E002 - no equipment (graceful)
        # E003 - one assigned, one already reclaimed (干扰)
        {"employee_id": "E003", "asset_tag": "LT-2041", "status": "assigned"},
        {"employee_id": "E003", "asset_tag": "BG-8821", "status": "reclaimed"},
        # E004 - pending
        {"employee_id": "E004", "asset_tag": "LT-2041", "status": "assigned"},
        # E005 - one assigned device
        {"employee_id": "E005", "asset_tag": "BG-8821", "status": "assigned"},
        # E006 - rejected
        {"employee_id": "E006", "asset_tag": "LT-2041", "status": "assigned"},
        # E007 - already reclaimed
        {"employee_id": "E007", "asset_tag": "BG-8821", "status": "reclaimed"},
        # Extra interference: employee E008 (no exit request)
        {"employee_id": "E008", "asset_tag": "LT-2041", "status": "assigned"},
    ]
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump({"equipment_assignments": equipment_assignments}, f, indent=2)

    # ---- accounts.json (irrelevant but present for realism) ----
    accounts = [
        {"account_id": "E001", "display_name": "Alice Wang", "department": "Finance", "email": "alice@company.com", "permissions": ["read", "write"]},
        {"account_id": "E003", "display_name": "Carol Chen", "department": "HR", "email": "carol@company.com", "permissions": ["read"]},
        {"account_id": "E005", "display_name": "Eva Liu", "department": "IT", "email": "eva@company.com", "permissions": ["admin"]},
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # ---- contacts.json (decoy) ----
    contacts = [
        {"contact_id": "C001", "name": "Amy Li", "role": "Manager", "email": "amy@company.com"},
        {"contact_id": "C002", "name": "Bob Zhang", "role": "HRBP", "email": "bob@company.com"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ---- archive/deprecated_exit_requests.json (干扰，过期备份) ----
    deprecated = [
        {"employee_id": "E001", "approval_status": "approved"},  # same, but different location
    ]
    with open("archive/deprecated_exit_requests.json", "w") as f:
        json.dump(deprecated, f, indent=2)

    # ---- pending_review.json (干扰) ----
    pending = [
        {"employee_id": "E009", "approval_status": "pending"},
    ]
    with open("data/offboarding/pending_review.json", "w") as f:
        json.dump(pending, f, indent=2)

if __name__ == "__main__":
    build_env()
