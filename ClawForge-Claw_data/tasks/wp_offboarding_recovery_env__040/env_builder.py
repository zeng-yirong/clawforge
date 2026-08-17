import os
import json
import random

def build_env():
    # 创建目录结构
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    
    # 退出请求数据（包含已批准和未批准，以及干扰项）
    exit_requests = [
        {"employee_id": "E001", "employee_name": "Alice Wang", "approval_status": "approved"},
        {"employee_id": "E002", "employee_name": "Bob Li", "approval_status": "approved"},
        {"employee_id": "E003", "employee_name": "Charlie Chen", "approval_status": "pending"},
        {"employee_id": "E004", "employee_name": "Diana Zhang", "approval_status": "denied"},
        {"employee_id": "E005", "employee_name": "Eva Liu", "approval_status": "approved"},  # 已批准但系统中无对应访问/设备？为了增加干扰，E005 在 system_access 和 equipment 中都没有记录
    ]
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump({"exit_requests": exit_requests}, f, indent=2)
    
    # 系统访问记录（E001, E002 有 active 记录；E003 pending 但也有记录；E004 denied 也有记录；E005 无记录）
    system_access = [
        {"employee_id": "E001", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "E001", "system_name": "CRM", "status": "active"},
        {"employee_id": "E002", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "E003", "system_name": "Admin Portal", "status": "active"},  # 未批准，不应被处理
        {"employee_id": "E004", "system_name": "CRM", "status": "active"},            # 未批准
    ]
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump({"system_access": system_access}, f, indent=2)
    
    # 设备分配记录
    equipment_assignments = [
        {"employee_id": "E001", "asset_tag": "BG-8821", "status": "assigned"},
        {"employee_id": "E002", "asset_tag": "LT-2041", "status": "assigned"},
        {"employee_id": "E003", "asset_tag": "BG-8821", "status": "assigned"},  # 未批准
        {"employee_id": "E004", "asset_tag": "LT-2041", "status": "returned"},  # 已归还，但未批准
    ]
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump({"equipment_assignments": equipment_assignments}, f, indent=2)
    
    # 额外干扰文件（accounts.json 和 contacts.json，但不影响任务）
    accounts = [
        {"account_id": "A001", "display_name": "Alice Wang", "department": "Engineering", "email": "alice@company.com", "permissions": ["admin"]},
        {"account_id": "A002", "display_name": "Bob Li", "department": "Sales", "email": "bob@company.com", "permissions": ["read"]},
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)
    contacts = [
        {"contact_id": "C001", "name": "HR Manager", "role": "HR", "email": "hr@company.com"},
        {"contact_id": "C002", "name": "IT Support", "role": "IT", "email": "it@company.com"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
