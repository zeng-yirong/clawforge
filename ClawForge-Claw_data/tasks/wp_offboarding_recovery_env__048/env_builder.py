import json
import os
import shutil

def build_env():
    # 目录结构
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---------- exit_requests ----------
    exit_requests = [
        {
            "employee_id": "E-1024",
            "employee_name": "James Carter",
            "department": "Engineering",
            "approval_status": "approved",
            "exit_date": "2025-04-01"
        },
        {
            "employee_id": "E-2048",
            "employee_name": "Linda Wu",
            "department": "Marketing",
            "approval_status": "pending"
        },
        {
            "employee_id": "E-3072",
            "employee_name": "Kevin Brown",
            "department": "Finance",
            "approval_status": "rejected"
        },
        {
            "employee_id": "E-4096",
            "employee_name": "Sophie Miller",
            "department": "Engineering",
            "approval_status": "approved",
            "exit_date": "2025-03-15"
        }
    ]
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump({"exit_requests": exit_requests}, f, indent=2)

    # ---------- system_access ----------
    system_access = [
        {
            "employee_id": "E-1024",
            "system_name": "Admin Portal",
            "status": "active"
        },
        {
            "employee_id": "E-1024",
            "system_name": "CRM",
            "status": "active"
        },
        {
            "employee_id": "E-2048",
            "system_name": "Admin Portal",
            "status": "active"
        },
        {
            "employee_id": "E-3072",
            "system_name": "CRM",
            "status": "revoked"
        },
        {
            "employee_id": "E-4096",
            "system_name": "Admin Portal",
            "status": "active"
        },
        {
            "employee_id": "E-4096",
            "system_name": "CRM",
            "status": "active"
        }
    ]
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump({"system_access": system_access}, f, indent=2)

    # ---------- equipment_assignments ----------
    equipment_assignments = [
        {
            "employee_id": "E-1024",
            "asset_tag": "BG-8821",
            "type": "Monitor",
            "status": "assigned"
        },
        {
            "employee_id": "E-1024",
            "asset_tag": "LT-2041",
            "type": "Laptop",
            "status": "assigned"
        },
        {
            "employee_id": "E-2048",
            "asset_tag": "LT-3001",
            "type": "Laptop",
            "status": "assigned"
        },
        {
            "employee_id": "E-3072",
            "asset_tag": "BG-1122",
            "type": "Monitor",
            "status": "returned"
        },
        {
            "employee_id": "E-4096",
            "asset_tag": "LT-4050",
            "type": "Laptop",
            "status": "assigned"
        }
    ]
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump({"equipment_assignments": equipment_assignments}, f, indent=2)

    # ---------- accounts (辅助信息，agent 可能用来查部门) ----------
    accounts = [
        {"account_id": "acct-1024", "display_name": "James Carter", "department": "Engineering", "email": "j.carter@corp.com", "permissions": ["admin"]},
        {"account_id": "acct-2048", "display_name": "Linda Wu", "department": "Marketing", "email": "l.wu@corp.com", "permissions": ["read"]},
        {"account_id": "acct-3072", "display_name": "Kevin Brown", "department": "Finance", "email": "k.brown@corp.com", "permissions": ["read","write"]},
        {"account_id": "acct-4096", "display_name": "Sophie Miller", "department": "Engineering", "email": "s.miller@corp.com", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # ---------- contacts (交接联系人) ----------
    contacts = [
        {"contact_id": "con-001", "name": "Maria Gonzalez", "role": "handover", "email": "m.gonzalez@corp.com"},
        {"contact_id": "con-002", "name": "David Kim", "role": "manager", "email": "d.kim@corp.com"},
        {"contact_id": "con-003", "name": "Sarah Chen", "role": "hr", "email": "s.chen@corp.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
