import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # ------------------ exit_requests.json ------------------
    exit_requests = [
        {"employee_id": "E001", "employee_name": "Alice Wang", "approval_status": "approved"},
        {"employee_id": "E002", "employee_name": "Bob Li", "approval_status": "approved"},
        {"employee_id": "E003", "employee_name": "Carol Zhang", "approval_status": "pending"},
        {"employee_id": "E004", "employee_name": "Dave Chen", "approval_status": "rejected"},
        {"employee_id": "E005", "employee_name": "Eve Zhou", "approval_status": "approved"},
    ]
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump({"exit_requests": exit_requests}, f, indent=2)

    # ------------------ system_access.json ------------------
    system_access = [
        {"employee_id": "E001", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "E001", "system_name": "CRM", "status": "active"},
        {"employee_id": "E002", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "E002", "system_name": "CRM", "status": "active"},
        {"employee_id": "E003", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "E003", "system_name": "CRM", "status": "active"},
        {"employee_id": "E004", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "E004", "system_name": "CRM", "status": "active"},
        {"employee_id": "E005", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "E005", "system_name": "CRM", "status": "active"},
        # 干扰：一个已经离职的人（不在exit_requests中）
        {"employee_id": "E099", "system_name": "Admin Portal", "status": "revoked"},
    ]
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump({"system_access": system_access}, f, indent=2)

    # ------------------ equipment_assignments.json ------------------
    equipment_assignments = [
        {"employee_id": "E001", "asset_tag": "LT-2041", "status": "assigned"},
        {"employee_id": "E002", "asset_tag": "BG-8821", "status": "assigned"},
        {"employee_id": "E003", "asset_tag": "LT-2042", "status": "assigned"},
        {"employee_id": "E004", "asset_tag": "BG-8822", "status": "assigned"},
        {"employee_id": "E005", "asset_tag": "LT-2043", "status": "assigned"},
        # 干扰：已经回收的设备
        {"employee_id": "E099", "asset_tag": "BG-8888", "status": "reclaimed"},
    ]
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump({"equipment_assignments": equipment_assignments}, f, indent=2)

    # ------------------ 诱饵文件：accounts.json (无用但存在) ------------------
    accounts = [
        {"account_id": "A001", "display_name": "Alice Wang", "department": "Engineering", "email": "alice@example.com", "permissions": ["read", "write"]},
        {"account_id": "A002", "display_name": "Bob Li", "department": "Sales", "email": "bob@example.com", "permissions": ["read"]},
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # ------------------ 诱饵文件：contacts.json ------------------
    contacts = [
        {"contact_id": "C001", "name": "HR Ops", "role": "HR", "email": "hr@example.com"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
