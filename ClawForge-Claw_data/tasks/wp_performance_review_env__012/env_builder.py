import os
import json

def build_env():
    # 创建数据目录
    os.makedirs("data/employees", exist_ok=True)
    os.makedirs("data/ledgers", exist_ok=True)
    os.makedirs("data/rules", exist_ok=True)

    # 员工数据（5人，含3种角色）
    employees = [
        {"employee_id": "E001", "employee_name": "Alice", "department": "Engineering", "role_code": "engineer"},
        {"employee_id": "E002", "employee_name": "Bob",   "department": "Engineering", "role_code": "engineer"},
        {"employee_id": "E003", "employee_name": "Carol", "department": "Marketing",   "role_code": "marketer"},
        {"employee_id": "E004", "employee_name": "Dave",  "department": "Sales",       "role_code": "sales"},
        {"employee_id": "E005", "employee_name": "Eve",   "department": "Sales",       "role_code": "sales"}
    ]
    with open("data/employees/employees.json", "w") as f:
        json.dump({"employees": employees}, f, indent=2)

    # 月度产出（5条正常记录 + 2条干扰）
    monthly_outputs = [
        # 正常记录
        {"employee_id": "E001", "feature_delivery": 80, "quality_score": 90, "collaboration_score": 85},
        {"employee_id": "E002", "feature_delivery": 70, "quality_score": 65, "collaboration_score": 75},
        {"employee_id": "E003", "feature_delivery": 90, "quality_score": 85, "collaboration_score": 80},
        {"employee_id": "E004", "feature_delivery": 60, "quality_score": 75, "collaboration_score": 70},
        {"employee_id": "E005", "feature_delivery": 85, "quality_score": 80, "collaboration_score": 90},
        # 干扰1：已离职员工（不在员工列表中）
        {"employee_id": "E099", "feature_delivery": 50, "quality_score": 50, "collaboration_score": 50},
        # 干扰2：旧月份数据（假装是去年的快照）
        {"employee_id": "E001", "feature_delivery": 100, "quality_score": 100, "collaboration_score": 100}
    ]
    with open("data/ledgers/monthly_outputs.json", "w") as f:
        json.dump({"monthly_outputs": monthly_outputs}, f, indent=2)

    # 评分规则（三种角色）
    scoring_rules = [
        {"role_code": "engineer", "feature_delivery_weight": 0.4, "quality_weight": 0.4, "collaboration_weight": 0.2},
        {"role_code": "marketer", "feature_delivery_weight": 0.3, "quality_weight": 0.3, "collaboration_weight": 0.4},
        {"role_code": "sales",    "feature_delivery_weight": 0.5, "quality_weight": 0.3, "collaboration_weight": 0.2}
    ]
    with open("data/rules/scoring_rules.json", "w") as f:
        json.dump({"scoring_rules": scoring_rules}, f, indent=2)

if __name__ == "__main__":
    build_env()
