import os
import json

def build_env():
    # 确保目录存在
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("raw_logs", exist_ok=True)  # 干扰目录

    # 1. 日期文件
    with open("data/offboarding/today_date.txt", "w") as f:
        f.write("2025-03-20\n")

    # 2. exit_requests.json（包含已批准、待审批、已拒绝，及一个诱饵员工）
    exit_requests = [
        {"employee_id": "E001", "employee_name": "张三", "department": "Engineering", "approval_status": "approved"},
        {"employee_id": "E002", "employee_name": "李四", "department": "Marketing", "approval_status": "approved"},
        {"employee_id": "E003", "employee_name": "王五", "department": "Finance", "approval_status": "approved"},
        {"employee_id": "E004", "employee_name": "赵六", "department": "Ops", "approval_status": "pending"},
        {"employee_id": "E005", "employee_name": "孙七", "department": "HR", "approval_status": "denied"},
        # 诱饵：没有系统或设备记录的已批准员工（但不应出现，这里额外加一个不存在的员工ID）
        {"employee_id": "E010", "employee_name": "周八", "department": "IT", "approval_status": "approved"}
    ]
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump({"exit_requests": exit_requests}, f, indent=2)

    # 3. system_access.json（包含所有员工，有active和inactive，以及诱饵员工E006）
    system_access = [
        {"employee_id": "E001", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "E001", "system_name": "CRM", "status": "active"},
        {"employee_id": "E002", "system_name": "Admin Portal", "status": "active"},
        {"employee_id": "E003", "system_name": "CRM", "status": "active"},
        {"employee_id": "E003", "system_name": "Admin Portal", "status": "inactive"},   # 干扰：已经失效
        {"employee_id": "E004", "system_name": "Admin Portal", "status": "active"},      # 未批准，不应处理
        {"employee_id": "E005", "system_name": "CRM", "status": "inactive"},             # 已拒绝
        # 诱饵员工，不在exit_requests里
        {"employee_id": "E006", "system_name": "Admin Portal", "status": "active"},
        # 另一个诱饵：E001已经有一条inactive的CRM？上面两条都是active，没问题
    ]
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump({"system_access": system_access}, f, indent=2)

    # 4. equipment_assignments.json（设备分配）
    equipment_assignments = [
        {"employee_id": "E001", "asset_tag": "BG-8821", "type": "Badge", "status": "assigned"},
        {"employee_id": "E002", "asset_tag": "LT-2041", "type": "Laptop", "status": "assigned"},
        {"employee_id": "E003", "asset_tag": "BG-8822", "type": "Badge", "status": "assigned"},
        {"employee_id": "E004", "asset_tag": "LT-2042", "type": "Laptop", "status": "assigned"},   # 未批准
        # 诱饵：已回收的设备
        {"employee_id": "E005", "asset_tag": "BG-8823", "type": "Badge", "status": "reclaimed"},
        # 诱饵：E001的另一台设备（但已回收）
        {"employee_id": "E001", "asset_tag": "LT-2043", "type": "Laptop", "status": "reclaimed"},
    ]
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump({"equipment_assignments": equipment_assignments}, f, indent=2)

    # 5. 干扰文件：logs目录下的无关日志
    for i in range(3):
        with open(f"raw_logs/app_{i}.log", "w") as f:
            f.write("2025-03-19 10:00:00 INFO some log\n")
    # 干扰文件：ops下的旧文件
    with open("ops/old_checklist.json", "w") as f:
        json.dump({"note": "old"}, f)

if __name__ == "__main__":
    build_env()
