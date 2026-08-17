import os
import json

def build_env():
    # ========== 离职请求 ==========
    exit_requests = {
        "exit_requests": [
            {
                "employee_id": "E-2024-042",
                "employee_name": "Wang Wei",
                "approval_status": "approved"
            },
            {
                "employee_id": "E-2024-015",
                "employee_name": "Li Ming",
                "approval_status": "pending"
            },
            {
                "employee_id": "E-2023-101",
                "employee_name": "Zhang San",
                "approval_status": "approved"          # 干扰：已批准但系统权限早已收回
            },
            {
                "employee_id": "E-2024-033",
                "employee_name": "Zhao Liu",
                "approval_status": "denied"
            }
        ]
    }

    # ========== 系统访问权限 ==========
    system_access = {
        "system_access": [
            {"employee_id": "E-2024-042", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "E-2024-042", "system_name": "CRM",          "status": "active"},
            {"employee_id": "E-2024-015", "system_name": "Admin Portal", "status": "active"},   # 未批准
            {"employee_id": "E-2023-101", "system_name": "CRM",          "status": "revoked"},   # 已提前撤销
            {"employee_id": "E-2024-033", "system_name": "Admin Portal", "status": "active"}     # 被拒绝
        ]
    }

    # ========== 设备分配 ==========
    equipment_assignments = {
        "equipment_assignments": [
            {"employee_id": "E-2024-042", "asset_tag": "LT-2041", "status": "assigned"},
            {"employee_id": "E-2024-015", "asset_tag": "BG-8821", "status": "assigned"},    # 未批准
            {"employee_id": "E-2023-101", "asset_tag": "LT-2041", "status": "returned"}     # 已归还
        ]
    }

    # ========== 额外干扰数据 ==========
    # 在 data/ 下放一个无关的 accounts 文件，增加迷惑
    accounts = {
        "accounts": [
            {"account_id": "acc-001", "display_name": "Wang Wei",  "department": "Engineering", "email": "wangwei@corp.com", "permissions": ["admin", "crm"]},
            {"account_id": "acc-002", "display_name": "Li Ming",   "department": "Sales",       "email": "liming@corp.com",  "permissions": ["salesforce"]},
            {"account_id": "acc-003", "display_name": "Zhang San", "department": "HR",          "email": "zhangsan@corp.com","permissions": ["hr_portal"]}
        ]
    }

    # 创建目录
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # 写入文件
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump(exit_requests, f, indent=2)
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump(system_access, f, indent=2)
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump(equipment_assignments, f, indent=2)
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

if __name__ == "__main__":
    build_env()
