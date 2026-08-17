import os
import json
import random

def build_env():
    # ========================= employees =========================
    employees = {
        "EMP001": {"employee_id": "EMP001", "employee_name": "Alice Wang", "department": "Engineering", "role_code": "ENG"},
        "EMP002": {"employee_id": "EMP002", "employee_name": "Bob Li",     "department": "QA",          "role_code": "QA"},
        "EMP003": {"employee_id": "EMP003", "employee_name": "Carol Chen", "department": "Engineering", "role_code": "ENG"},
        "EMP004": {"employee_id": "EMP004", "employee_name": "David Liu",  "department": "DevOps",      "role_code": "OPS"},
        "EMP005": {"employee_id": "EMP005", "employee_name": "Eva Zhang",  "department": "Product",     "role_code": "PM"},
        # 干扰项：员工不在 ledgers 中（无产出数据）
        "EMP006": {"employee_id": "EMP006", "employee_name": "Frank Sun",  "department": "Engineering", "role_code": "ENG"},
        # 干扰项：员工在 ledgers 中但不在 employees 中（后面 ledgers 中添加 EMP007）
    }
    os.makedirs("data/employees", exist_ok=True)
    with open("data/employees/employees.json", "w") as f:
        json.dump({"employees": list(employees.values())}, f, indent=2)

    # ========================= ledgers (monthly outputs) =========================
    monthly_outputs = {
        "EMP001": {"employee_id": "EMP001", "feature_delivery": 85, "quality_score": 90, "collaboration_score": 75},
        "EMP002": {"employee_id": "EMP002", "feature_delivery": 70, "quality_score": 65, "collaboration_score": 80},
        "EMP003": {"employee_id": "EMP003", "feature_delivery": 95, "quality_score": 88, "collaboration_score": 92},
        "EMP004": {"employee_id": "EMP004", "feature_delivery": 60, "quality_score": 70, "collaboration_score": 65},
        # EMP005 有完整数据
        "EMP005": {"employee_id": "EMP005", "feature_delivery": 78, "quality_score": 82, "collaboration_score": 90},
        # 干扰项：额外员工 EMP007 不在 employees 列表中
        "EMP007": {"employee_id": "EMP007", "feature_delivery": 80, "quality_score": 80, "collaboration_score": 80},
        # 干扰项：重复记录（稍后也作为单独文件）
    }
    os.makedirs("data/ledgers", exist_ok=True)
    with open("data/ledgers/monthly_outputs.json", "w") as f:
        json.dump({"monthly_outputs": list(monthly_outputs.values())}, f, indent=2)

    # ========================= scoring rules =========================
    scoring_rules = [
        {"role_code": "ENG", "feature_delivery_weight": 0.4, "quality_weight": 0.4, "collaboration_weight": 0.2},
        {"role_code": "QA",  "feature_delivery_weight": 0.3, "quality_weight": 0.5, "collaboration_weight": 0.2},
        {"role_code": "OPS", "feature_delivery_weight": 0.5, "quality_weight": 0.3, "collaboration_weight": 0.2},
        {"role_code": "PM",  "feature_delivery_weight": 0.3, "quality_weight": 0.3, "collaboration_weight": 0.4},
        # 干扰项：额外的规则（不会影响任何员工）
        {"role_code": "HR",  "feature_delivery_weight": 0.2, "quality_weight": 0.6, "collaboration_weight": 0.2},
    ]
    os.makedirs("data/rules", exist_ok=True)
    with open("data/rules/scoring_rules.json", "w") as f:
        json.dump({"scoring_rules": scoring_rules}, f, indent=2)

    # ========================= 干扰文件 =========================
    # 1. 旧的 CSV 副本（格式错误）
    os.makedirs("backup", exist_ok=True)
    with open("backup/employees_old.csv", "w") as f:
        f.write("employee_id,name,dept\nEMP001,Alice,Eng\n")

    # 2. 不完整的规则文件（XML 风格，不是 JSON）
    with open("data/rules/invalid_rules.xml", "w") as f:
        f.write("<rules><rule role='ENG' weight='0.4'/></rules>")

    # 3. 多余的 ledgers 子目录
    os.makedirs("data/ledgers/archive", exist_ok=True)
    with open("data/ledgers/archive/monthly_outputs_202401.json", "w") as f:
        json.dump({"monthly_outputs": [{"employee_id": "EMP001", "feature_delivery": 80}]}, f, indent=2)

    # 4. 员工花名册的副本（不完整）
    with open("data/employees/employees_dup.json", "w") as f:
        json.dump({"employees": [employees["EMP001"]]}, f, indent=2)

    # ========================= 创建目标输出目录（但留空让 agent 写入） =========================
    os.makedirs("reports", exist_ok=True)   # agent 应在此写入 performance_summary.json

    print("Environment built successfully with all data and distractors.")

if __name__ == "__main__":
    build_env()
