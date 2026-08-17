import json
import os

def build_env():
    # --- 目录结构 ---
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("backup", exist_ok=True)  # 干扰目录

    # ========== 1. 离职请求 ==========
    exit_requests = [
        {
            "employee_id": "E001",
            "employee_name": "Alice Wang",
            "department": "IT",
            "approval_status": "approved",
            "exit_date": "2025-04-07"
        },
        {
            "employee_id": "E002",
            "employee_name": "Bob Li",
            "department": "Finance",
            "approval_status": "pending"
        },
        {
            "employee_id": "E003",
            "employee_name": "Carol Chen",
            "department": "Sales",
            "approval_status": "rejected"
        },
        {
            "employee_id": "E004",
            "employee_name": "David Zhang",
            "department": "Engineering",
            "approval_status": "approved"   # 干扰：另一个 approved，但该员工名下没有 active 访问或已分配设备（见下文）
        }
    ]
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump({"exit_requests": exit_requests}, f, indent=2)

    # 旧记录干扰
    old_requests = [
        {"employee_id": "E001", "approval_status": "expired"}
    ]
    with open("data/offboarding/old_exit_requests.json", "w") as f:
        json.dump({"exit_requests": old_requests}, f, indent=2)

    # ========== 2. 系统访问 ==========
    system_access = [
        # Alice 的两个 active 系统
        {"employee_id": "E001", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "E001", "system_name": "CRM", "status": "active"},
        # Bob 的
        {"employee_id": "E002", "system_name": "Finance System", "status": "active"},
        # Carol 的（已撤销）
        {"employee_id": "E003", "system_name": "CRM", "status": "revoked"},
        # David（另一个 approved，但无任何 active 访问，只有 revoked）
        {"employee_id": "E004", "system_name": "VPN", "status": "revoked"},
        # 额外干扰
        {"employee_id": "E001", "system_name": "Old CRM", "status": "revoked"}
    ]
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump({"system_access": system_access}, f, indent=2)

    # ========== 3. 设备领用 ==========
    equipment_assignments = [
        # Alice 的笔记本（已分配，要回收）
        {"employee_id": "E001", "asset_tag": "LT-2041", "status": "assigned"},
        # Alice 的显示器（已归还，忽略）
        {"employee_id": "E001", "asset_tag": "BG-8821", "status": "returned"},
        # Bob 的
        {"employee_id": "E002", "asset_tag": "LT-8822", "status": "assigned"},
        # Carol 的（已回收）
        {"employee_id": "E003", "asset_tag": "LT-3030", "status": "returned"},
        # David（无 assigned 设备）
        {"employee_id": "E004", "asset_tag": "BG-1122", "status": "lost"}
    ]
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump({"equipment_assignments": equipment_assignments}, f, indent=2)

    # ========== 预置一个空 ops 目录，让 agent 写入 ==========
    # 无需额外操作

if __name__ == "__main__":
    build_env()
