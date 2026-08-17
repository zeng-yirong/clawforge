import os
import json
import shutil

def build_env():
    # 清理可能存在的旧数据（确保从干净状态开始）
    for path in ["data", "backups", "ops", "old"]:
        if os.path.exists(path):
            shutil.rmtree(path)

    # ---------- 员工 ----------
    os.makedirs("data/employees")
    employees = {
        "employees": [
            {"employee_id": "E001", "employee_name": "Alice", "department": "Engineering", "role_code": "dev"},
            {"employee_id": "E002", "employee_name": "Bob", "department": "QA", "role_code": "qa"},
            {"employee_id": "E003", "employee_name": "Charlie", "department": "Product", "role_code": "pm"},
            # 诱饵：E004 不存在于员工表，但会在 outputs 中出现
        ]
    }
    with open("data/employees/employees.json", "w") as f:
        json.dump(employees, f, indent=2)

    # ---------- 产出明细 ----------
    os.makedirs("data/ledgers")
    monthly_outputs = {
        "monthly_outputs": [
            {"employee_id": "E001", "feature_delivery": 90, "quality_score": 80, "collaboration_score": 70},
            {"employee_id": "E002", "feature_delivery": 70, "quality_score": 85, "collaboration_score": 90},
            {"employee_id": "E003", "feature_delivery": 60, "quality_score": 75, "collaboration_score": 95},
            # 脏数据：E001 的重复记录，但分数超出合理范围（>100），应被过滤
            {"employee_id": "E001", "feature_delivery": 200, "quality_score": 50, "collaboration_score": 50},
            # 诱饵：员工 E004 有产出但员工表中不存在
            {"employee_id": "E004", "feature_delivery": 80, "quality_score": 80, "collaboration_score": 80},
        ]
    }
    with open("data/ledgers/monthly_outputs.json", "w") as f:
        json.dump(monthly_outputs, f, indent=2)

    # ---------- 评分规则 ----------
    os.makedirs("data/rules")
    scoring_rules = {
        "scoring_rules": [
            {"role_code": "dev", "feature_delivery_weight": 0.5, "quality_weight": 0.3, "collaboration_weight": 0.2},
            {"role_code": "qa", "feature_delivery_weight": 0.3, "quality_weight": 0.5, "collaboration_weight": 0.2},
            {"role_code": "pm", "feature_delivery_weight": 0.2, "quality_weight": 0.3, "collaboration_weight": 0.5},
        ]
    }
    with open("data/rules/scoring_rules.json", "w") as f:
        json.dump(scoring_rules, f, indent=2)

    # ---------- 干扰文件 ----------
    # 1. 备份目录中的旧产出（格式正确但内容无关）
    os.makedirs("backups")
    old_outputs = {
        "monthly_outputs": [
            {"employee_id": "E001", "feature_delivery": 0, "quality_score": 0, "collaboration_score": 0},
        ]
    }
    with open("backups/outputs_backup.json", "w") as f:
        json.dump(old_outputs, f, indent=2)

    # 2. 旧员工表（包含 E004 等虚拟员工）
    old_employees = {
        "employees": [
            {"employee_id": "E004", "employee_name": "David", "department": "Temp", "role_code": "dev"},
        ]
    }
    with open("old/old_employees.json", "w") as f:
        json.dump(old_employees, f, indent=2)

    # 3. 非 JSON 垃圾文件
    with open("data/ledgers/note.txt", "w") as f:
        f.write("这是笔记，不是JSON文件，请忽略。")

    # 4. 确保 ops 目录存在（空）
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
