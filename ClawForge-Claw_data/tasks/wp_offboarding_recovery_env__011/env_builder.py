import json
import os

def build_env():
    # 创建必要的目录
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. 员工账户信息
    accounts = [
        {"account_id": "E001", "display_name": "李四", "department": "Finance", "email": "lisi@corp.com", "permissions": ["read"]},
        {"account_id": "E002", "display_name": "王五", "department": "HR", "email": "wangwu@corp.com", "permissions": ["read", "write"]},
        {"account_id": "E003", "display_name": "张三", "department": "Engineering", "email": "zhangsan@corp.com", "permissions": ["read", "write", "admin"]},
        {"account_id": "E004", "display_name": "赵六", "department": "Sales", "email": "zhaoliu@corp.com", "permissions": ["read"]},
        {"account_id": "E005", "display_name": "钱七", "department": "IT", "email": "qianqi@corp.com", "permissions": ["read", "write"]}
    ]
    with open("data/accounts.json", "w", encoding="utf-8") as f:
        json.dump({"accounts": accounts}, f, ensure_ascii=False, indent=2)

    # 2. 离职请求（干扰项：已批准但已处理、待处理、已拒绝等）
    exit_requests = [
        {"employee_id": "E001", "employee_name": "李四", "approval_status": "approved"},
        {"employee_id": "E002", "employee_name": "王五", "approval_status": "pending"},
        {"employee_id": "E003", "employee_name": "张三", "approval_status": "approved"},
        {"employee_id": "E004", "employee_name": "赵六", "approval_status": "approved"},
        {"employee_id": "E005", "employee_name": "钱七", "approval_status": "rejected"}
    ]
    with open("data/offboarding/exit_requests.json", "w", encoding="utf-8") as f:
        json.dump({"exit_requests": exit_requests}, f, ensure_ascii=False, indent=2)

    # 3. 系统访问（干扰项：E001已撤销，E004未撤销但未批准？E004是approved但未处理，让agent区分）
    system_access = [
        {"employee_id": "E001", "system_name": "Admin Portal", "status": "revoked"},
        {"employee_id": "E001", "system_name": "CRM", "status": "revoked"},
        {"employee_id": "E002", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "E003", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "E004", "system_name": "CRM", "status": "active"},
        {"employee_id": "E005", "system_name": "Admin Portal", "status": "active"}
    ]
    with open("data/offboarding/system_access.json", "w", encoding="utf-8") as f:
        json.dump({"system_access": system_access}, f, ensure_ascii=False, indent=2)

    # 4. 设备分配（干扰项类似）
    equipment = [
        {"employee_id": "E001", "asset_tag": "LT-2041", "status": "reclaimed"},
        {"employee_id": "E002", "asset_tag": "BG-8821", "status": "assigned"},
        {"employee_id": "E003", "asset_tag": "BG-8821", "status": "assigned"},
        {"employee_id": "E004", "asset_tag": "LT-2041", "status": "assigned"},
        {"employee_id": "E005", "asset_tag": "BG-8821", "status": "assigned"}
    ]
    with open("data/offboarding/equipment_assignments.json", "w", encoding="utf-8") as f:
        json.dump({"equipment_assignments": equipment}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build_env()
