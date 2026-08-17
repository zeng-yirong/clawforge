import os
import json

def build_env():
    # 创建必要的目录
    dirs = [
        "data/offboarding",
        "data",
        "ops",
        "backup"  # 干扰目录
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # ---------- exit_requests.json ----------
    exit_requests = {
        "exit_requests": [
            {
                "employee_id": "EMP003",
                "employee_name": "张三",
                "approval_status": "approved"
            },
            {
                "employee_id": "EMP001",
                "employee_name": "李四",
                "approval_status": "pending"
            },
            {
                "employee_id": "EMP002",
                "employee_name": "王五",
                "approval_status": "rejected"
            },
            {
                "employee_id": "EMP004",
                "employee_name": "赵六",
                "approval_status": "approved"  # 干扰：但此人在 system_access 中无记录，设备也无分配
            }
        ]
    }
    with open("data/offboarding/exit_requests.json", "w", encoding="utf-8") as f:
        json.dump(exit_requests, f, ensure_ascii=False, indent=2)

    # ---------- system_access.json ----------
    system_access = {
        "system_access": [
            {
                "employee_id": "EMP003",
                "system_name": "Admin Portal",
                "status": "active"
            },
            {
                "employee_id": "EMP003",
                "system_name": "CRM",
                "status": "active"
            },
            {
                "employee_id": "EMP003",
                "system_name": "Legacy Portal",
                "status": "inactive"   # 已失效，不需要撤销
            },
            {
                "employee_id": "EMP001",
                "system_name": "Admin Portal",
                "status": "active"     # 干扰：李四的权限，但离职未批准
            },
            {
                "employee_id": "EMP002",
                "system_name": "CRM",
                "status": "active"     # 干扰：王五被拒
            },
            {
                "employee_id": "EMP005",
                "system_name": "Email System",
                "status": "active"     # 无关员工
            }
        ]
    }
    with open("data/offboarding/system_access.json", "w", encoding="utf-8") as f:
        json.dump(system_access, f, ensure_ascii=False, indent=2)

    # ---------- equipment_assignments.json ----------
    equipment_assignments = {
        "equipment_assignments": [
            {
                "employee_id": "EMP003",
                "asset_tag": "LT-2041",
                "status": "assigned"
            },
            {
                "employee_id": "EMP001",
                "asset_tag": "BG-8821",
                "status": "assigned"      # 干扰：李四的设备
            },
            {
                "employee_id": "EMP099",
                "asset_tag": "BG-8821",
                "status": "reclaimed"     # 已回收，干扰
            }
        ]
    }
    with open("data/offboarding/equipment_assignments.json", "w", encoding="utf-8") as f:
        json.dump(equipment_assignments, f, ensure_ascii=False, indent=2)

    # ---------- accounts.json (提供部门信息) ----------
    accounts = {
        "accounts": [
            {
                "account_id": "EMP003",
                "display_name": "张三",
                "department": "Finance",
                "email": "zhangsan@example.com",
                "permissions": []
            },
            {
                "account_id": "EMP001",
                "display_name": "李四",
                "department": "Engineering",
                "email": "lisi@example.com",
                "permissions": ["code_push"]
            },
            {
                "account_id": "EMP002",
                "display_name": "王五",
                "department": "Marketing",
                "email": "wangwu@example.com",
                "permissions": ["campaign_edit"]
            },
            {
                "account_id": "EMP004",
                "display_name": "赵六",
                "department": "HR",
                "email": "zhaoliu@example.com",
                "permissions": []
            }
        ]
    }
    with open("data/accounts.json", "w", encoding="utf-8") as f:
        json.dump(accounts, f, ensure_ascii=False, indent=2)

    # ---------- 干扰文件 ----------
    # 创建一个旧的备份文件
    with open("backup/exit_requests_old.json", "w", encoding="utf-8") as f:
        json.dump({"exit_requests": [{"employee_id": "OLD", "approval_status": "approved"}]}, f, ensure_ascii=False)

    # 创建一个无关的 contacts.json
    contacts = {
        "contacts": [
            {"contact_id": "C001", "name": "张三", "role": "Employee", "email": "zhangsan@example.com"},
            {"contact_id": "C002", "name": "李四", "role": "Manager", "email": "lisi@example.com"}
        ]
    }
    with open("data/contacts.json", "w", encoding="utf-8") as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build_env()
