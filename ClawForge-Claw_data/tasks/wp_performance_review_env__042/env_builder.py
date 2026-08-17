import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/employees", exist_ok=True)
    os.makedirs("data/ledgers", exist_ok=True)
    os.makedirs("data/rules", exist_ok=True)
    os.makedirs("old_data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 员工列表（其中一个角色码 INACTIVE 不在规则中）
    employees = [
        {"employee_id": "E001", "employee_name": "Alice", "department": "Engineering", "role_code": "ENG"},
        {"employee_id": "E002", "employee_name": "Bob",   "department": "Marketing",   "role_code": "MKT"},
        {"employee_id": "E003", "employee_name": "Charlie","department": "Data Science","role_code": "DS"},
        {"employee_id": "E004", "employee_name": "Diana",  "department": "Sales",      "role_code": "INACTIVE"}
    ]
    with open("data/employees/employees.json", "w") as f:
        json.dump({"employees": employees}, f, indent=2)

    # 评分规则
    rules = [
        {"role_code": "ENG", "feature_delivery_weight": 0.4, "quality_weight": 0.4, "collaboration_weight": 0.2},
        {"role_code": "MKT", "feature_delivery_weight": 0.3, "quality_weight": 0.3, "collaboration_weight": 0.4},
        {"role_code": "DS",  "feature_delivery_weight": 0.5, "quality_weight": 0.3, "collaboration_weight": 0.2}
    ]
    with open("data/rules/scoring_rules.json", "w") as f:
        json.dump({"scoring_rules": rules}, f, indent=2)

    # 最新月份输出台账（2025-03），包含一个无效员工 E005 作为脏数据
    monthly_outputs = [
        {"employee_id": "E001", "period": "2025-03", "feature_delivery": 80, "quality_score": 90, "collaboration_score": 70},
        {"employee_id": "E002", "period": "2025-03", "feature_delivery": 70, "quality_score": 80, "collaboration_score": 60},
        {"employee_id": "E003", "period": "2025-03", "feature_delivery": 90, "quality_score": 70, "collaboration_score": 80},
        {"employee_id": "E005", "period": "2025-03", "feature_delivery": 50, "quality_score": 50, "collaboration_score": 50}  # 脏数据，员工不存在
    ]
    with open("data/ledgers/monthly_outputs.json", "w") as f:
        json.dump({"monthly_outputs": monthly_outputs}, f, indent=2)

    # 旧数据干扰
    old_outputs = [
        {"employee_id": "E001", "period": "2025-02", "feature_delivery": 60, "quality_score": 70, "collaboration_score": 50},
        {"employee_id": "E002", "period": "2025-02", "feature_delivery": 50, "quality_score": 60, "collaboration_score": 40}
    ]
    with open("data/ledgers/old_outputs.json", "w") as f:
        json.dump({"monthly_outputs": old_outputs}, f, indent=2)

    # 另一个干扰文件夹
    old_employees = [
        {"employee_id": "E001", "employee_name": "Alice", "department": "Engineering", "role_code": "ENG"},
        {"employee_id": "E002", "employee_name": "Bob",   "department": "Marketing",   "role_code": "MKT"},
        {"employee_id": "E006", "employee_name": "Eve",   "department": "Support",    "role_code": "SUPPORT"}
    ]
    with open("old_data/employees.json", "w") as f:
        json.dump({"employees": old_employees}, f, indent=2)

    old_rules = [
        {"role_code": "ENG", "feature_delivery_weight": 0.5, "quality_weight": 0.3, "collaboration_weight": 0.2},
        {"role_code": "MKT", "feature_delivery_weight": 0.2, "quality_weight": 0.4, "collaboration_weight": 0.4}
    ]
    with open("old_data/rules.json", "w") as f:
        json.dump({"scoring_rules": old_rules}, f, indent=2)

if __name__ == "__main__":
    build_env()
