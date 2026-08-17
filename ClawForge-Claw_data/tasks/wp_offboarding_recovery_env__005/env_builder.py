import os
import json
import random

def build_env():
    # 创建目录结构
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("data/accounts", exist_ok=True)
    os.makedirs("data/contacts", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 用于 agent 输出

    # --- accounts.json (干扰数据，不参与任务) ---
    accounts = {
        "A001": {"account_id": "A001", "display_name": "Alice Wang", "department": "Engineering", "email": "alice@company.com", "permissions": ["read", "write"]},
        "A002": {"account_id": "A002", "display_name": "Bob Li", "department": "Sales", "email": "bob@company.com", "permissions": ["read"]},
        "A003": {"account_id": "A003", "display_name": "Charlie Chen", "department": "Marketing", "email": "charlie@company.com", "permissions": ["read", "write"]},
        "A004": {"account_id": "A004", "display_name": "Diana Zhang", "department": "HR", "email": "diana@company.com", "permissions": ["admin"]},
        "A005": {"account_id": "A005", "display_name": "Eve Liu", "department": "Finance", "email": "eve@company.com", "permissions": ["read"]}
    }
    with open("data/accounts/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # --- contacts.json (干扰数据) ---
    contacts = {
        "C001": {"contact_id": "C001", "name": "HR Contact", "role": "HR Manager", "email": "hr@company.com"},
        "C002": {"contact_id": "C002", "name": "IT Admin", "role": "IT Support", "email": "it@company.com"}
    }
    with open("data/contacts/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # --- exit_requests.json (核心数据) ---
    exit_requests = {
        "E001": {"employee_id": "E001", "employee_name": "Alice Wang", "department": "Engineering", "approval_status": "Approved"},
        "E002": {"employee_id": "E002", "employee_name": "Bob Li", "department": "Sales", "approval_status": "Approved"},
        "E003": {"employee_id": "E003", "employee_name": "Charlie Chen", "department": "Marketing", "approval_status": "Pending"},
        "E004": {"employee_id": "E004", "employee_name": "Diana Zhang", "department": "HR", "approval_status": "Rejected"},
        "E005": {"employee_id": "E005", "employee_name": "Eve Liu", "department": "Finance", "approval_status": "Approved"}
    }
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump({"exit_requests": exit_requests}, f, indent=2)

    # --- system_access.json (核心数据) ---
    system_access = {
        "E001": {"employee_id": "E001", "system_name": "Admin Portal", "status": "Active"},
        "E001_2": {"employee_id": "E001", "system_name": "CRM", "status": "Active"},
        "E002": {"employee_id": "E002", "system_name": "Admin Portal", "status": "Active"},
        "E003": {"employee_id": "E003", "system_name": "CRM", "status": "Active"},
        "E004": {"employee_id": "E004", "system_name": "Admin Portal", "status": "Active"},
        "E005_1": {"employee_id": "E005", "system_name": "Admin Portal", "status": "Revoked"},
        "E005_2": {"employee_id": "E005", "system_name": "CRM", "status": "Revoked"}
    }
    # 注意：这里用了一个非标准的 key（employee_id + 序号），但 wrapper 是 system_access，key 实际不要求严格，只要 content 有 employee_id 即可
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump({"system_access": system_access}, f, indent=2)

    # --- equipment_assignments.json (核心数据) ---
    equipment_assignments = {
        "E001": {"employee_id": "E001", "asset_tag": "LT-2041", "status": "Assigned"},
        "E002": {"employee_id": "E002", "asset_tag": "BG-8821", "status": "Assigned"},
        "E003": {"employee_id": "E003", "asset_tag": "BG-8821", "status": "Assigned"},
        "E004": {"employee_id": "E004", "asset_tag": "LT-2041", "status": "Assigned"},
        "E005": {"employee_id": "E005", "asset_tag": "BG-8821", "status": "Reclaimed"}
    }
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump({"equipment_assignments": equipment_assignments}, f, indent=2)

    # 添加一些干扰文件/目录
    os.makedirs("data/offboarding/backup", exist_ok=True)
    with open("data/offboarding/backup/exit_requests_old.json", "w") as f:
        json.dump({"exit_requests": {"E001": {"employee_id": "E001", "approval_status": "Rejected"}}}, f, indent=2)

if __name__ == "__main__":
    build_env()
