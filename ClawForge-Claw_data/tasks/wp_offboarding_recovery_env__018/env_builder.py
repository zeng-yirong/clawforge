import os
import json
import shutil

def build_env():
    # 清除旧的构建目录（如果存在），确保干净初始状态
    for d in ["data", "ops", "raw_logs"]:
        if os.path.exists(d):
            shutil.rmtree(d)
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("raw_logs", exist_ok=True)

    # 1. accounts.json —— 正常账户，包含 Carol 和其他人
    accounts = {
        "accounts": [
            {
                "account_id": "E-1024",
                "display_name": "Carol Danvers",
                "department": "Engineering",
                "email": "carol.danvers@example.com",
                "permissions": ["read", "write", "admin"]
            },
            {
                "account_id": "E-1025",
                "display_name": "Bob Smith",
                "department": "Sales",
                "email": "bob.smith@example.com",
                "permissions": ["read"]
            },
            {
                "account_id": "E-1026",
                "display_name": "Eve Johnson",
                "department": "Marketing",
                "email": "eve.johnson@example.com",
                "permissions": ["read", "write"]
            },
            {
                "account_id": "E-1027",
                "display_name": "Alice Cooper",
                "department": "HR",
                "email": "alice.cooper@example.com",
                "permissions": ["read", "write", "admin"]
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 2. contacts.json —— 联系人，无关但存在
    contacts = {
        "contacts": [
            {"contact_id": "C-001", "name": "Nick Fury", "role": "Director", "email": "nick.fury@example.com"},
            {"contact_id": "C-002", "name": "Maria Hill", "role": "Deputy Director", "email": "maria.hill@example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 3. exit_requests.json —— 只有 Carol 的是 approved，其余干扰项
    exit_requests = {
        "exit_requests": [
            {"employee_id": "E-1024", "employee_name": "Carol Danvers", "approval_status": "approved"},
            {"employee_id": "E-1025", "employee_name": "Bob Smith", "approval_status": "pending"},
            {"employee_id": "E-1026", "employee_name": "Eve Johnson", "approval_status": "rejected"},
            {"employee_id": "E-1027", "employee_name": "Alice Cooper", "approval_status": "cancelled"},
            # 额外迷惑项：另一个已批准的员工？不，只有一个，否则答案不唯一。
            # 但可以加一个名字相似但状态是 pending 的
            {"employee_id": "E-1028", "employee_name": "Carla Davison", "approval_status": "pending"}
        ]
    }
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump(exit_requests, f, indent=2)

    # 4. system_access.json —— Carol 两条 active，其他人也有 active
    system_access = {
        "system_access": [
            {"employee_id": "E-1024", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "E-1024", "system_name": "CRM", "status": "active"},
            {"employee_id": "E-1025", "system_name": "Salesforce", "status": "active"},
            {"employee_id": "E-1026", "system_name": "Analytics", "status": "active"},
            {"employee_id": "E-1027", "system_name": "HR System", "status": "active"}
        ]
    }
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump(system_access, f, indent=2)

    # 5. equipment_assignments.json —— Carol 有设备，其他人也有
    equipment = {
        "equipment_assignments": [
            {"employee_id": "E-1024", "asset_tag": "LT-2041", "status": "assigned"},
            {"employee_id": "E-1025", "asset_tag": "BG-8821", "status": "assigned"},
            {"employee_id": "E-1026", "asset_tag": "LT-3050", "status": "assigned"},
            {"employee_id": "E-1027", "asset_tag": "MN-6700", "status": "assigned"}
        ]
    }
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump(equipment, f, indent=2)

    # 6. 无关干扰文件 —— raw_logs/ 下的日志、旧备份
    with open("raw_logs/old_backup.json", "w") as f:
        json.dump({"note": "this is an old backup, ignore"}, f)
    with open("ops/readme.txt", "w") as f:
        f.write("Operations folder for handover artifacts.\n")

if __name__ == "__main__":
    build_env()
