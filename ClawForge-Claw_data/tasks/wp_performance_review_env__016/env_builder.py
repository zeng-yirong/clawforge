import os
import json

def build_env():
    # 确保基础目录存在
    for d in ["data/employees", "data/ledgers", "data/rules", "ops"]:
        os.makedirs(d, exist_ok=True)

    # ========== 正式数据 ==========
    # 1. 员工花名册 (3人，其中E003没有产出记录)
    employees = [
        {"employee_id": "E001", "employee_name": "Zhang Wei", "department": "Engineering", "role_code": "dev"},
        {"employee_id": "E002", "employee_name": "Li Na",    "department": "QA",          "role_code": "qa"},
        {"employee_id": "E003", "employee_name": "Wang Fang", "department": "Engineering", "role_code": "dev"}
    ]
    with open("data/employees/employees.json", "w") as f:
        json.dump({"employees": employees}, f, indent=2)

    # 2. 月度产出 (只有E001, E002；E003缺失)
    outputs = [
        {"employee_id": "E001", "feature_delivery": 10, "quality_score": 8, "collaboration_score": 9},
        {"employee_id": "E002", "feature_delivery": 7,  "quality_score": 9, "collaboration_score": 6}
    ]
    with open("data/ledgers/monthly_outputs.json", "w") as f:
        json.dump({"monthly_outputs": outputs}, f, indent=2)

    # 3. 评分规则 (dev / qa)
    rules = [
        {"role_code": "dev", "feature_delivery_weight": 0.5, "quality_weight": 0.3, "collaboration_weight": 0.2},
        {"role_code": "qa",  "feature_delivery_weight": 0.4, "quality_weight": 0.4, "collaboration_weight": 0.2}
    ]
    with open("data/rules/scoring_rules.json", "w") as f:
        json.dump({"scoring_rules": rules}, f, indent=2)

    # ========== 干扰项 ==========
    # 1. 旧版本员工名单 (离职人员)
    former = [
        {"employee_id": "E004", "employee_name": "Old Liu", "department": "Sales", "role_code": "sales"}
    ]
    with open("data/employees/former_employees.json", "w") as f:
        json.dump({"former_employees": former}, f, indent=2)

    # 2. 备用评分规则 (旧版权重，容易让人混淆)
    old_rules = [
        {"role_code": "dev", "feature_delivery_weight": 0.6, "quality_weight": 0.2, "collaboration_weight": 0.2}
    ]
    with open("data/rules/old_rules.json", "w") as f:
        json.dump({"scoring_rules": old_rules}, f, indent=2)

    # 3. 额外的产出备份 (含有E003但已过期)
    backup = [
        {"employee_id": "E003", "feature_delivery": 5, "quality_score": 6, "collaboration_score": 7},
        {"employee_id": "E004", "feature_delivery": 8, "quality_score": 7, "collaboration_score": 9}
    ]
    with open("data/ledgers/backup_outputs.json", "w") as f:
        json.dump({"monthly_outputs": backup}, f, indent=2)

    # 4. 一个空目录，用来测试agent是否能正确处理非必要路径
    os.makedirs("logs", exist_ok=True)
    with open("logs/.gitkeep", "w") as f:
        f.write("")

if __name__ == "__main__":
    build_env()
