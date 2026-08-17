import os
import json
import shutil

def build_env():
    # 确保工作目录干净
    base = "."
    # 创建必要目录
    for d in ["data/employees", "data/ledgers", "data/rules", "ops"]:
        os.makedirs(os.path.join(base, d), exist_ok=True)

    # ---- 有效员工列表 ----
    employees = [
        {"employee_id": "E001", "employee_name": "李明", "department": "工程部", "role_code": "ENG"},
        {"employee_id": "E002", "employee_name": "王芳", "department": "销售部", "role_code": "SALES"},
        {"employee_id": "E003", "employee_name": "张伟", "department": "管理部", "role_code": "MGR"},
    ]
    with open(os.path.join(base, "data/employees/employees.json"), "w") as f:
        json.dump({"employees": employees}, f, indent=2)

    # ---- 干扰：旧版员工（含过期员工和角色码错误） ----
    old_employees = [
        {"employee_id": "E001", "employee_name": "李明(旧)", "department": "工程部", "role_code": "ENG"},
        {"employee_id": "E004", "employee_name": "赵强", "department": "财务部", "role_code": "FIN"},
        {"employee_id": "E002", "employee_name": "王芳", "department": "销售部", "role_code": "SALES"},  # 重复ID但名字不同
        {"employee_id": "E005", "employee_name": "刘梅", "department": "行政部", "role_code": "ADMIN"},
    ]
    with open(os.path.join(base, "data/employees/employees_backup.json"), "w") as f:
        json.dump({"employees": old_employees}, f, indent=2)

    # ---- 有效月度产出日志 ----
    outputs = [
        {"employee_id": "E001", "feature_delivery": 85, "quality_score": 90, "collaboration_score": 78},
        {"employee_id": "E002", "feature_delivery": 70, "quality_score": 65, "collaboration_score": 80},
        {"employee_id": "E003", "feature_delivery": 92, "quality_score": 88, "collaboration_score": 95},
    ]
    with open(os.path.join(base, "data/ledgers/monthly_outputs.json"), "w") as f:
        json.dump({"monthly_outputs": outputs}, f, indent=2)

    # ---- 干扰：旧版产出（含缺失字段） ----
    old_outputs = [
        {"employee_id": "E001", "feature_delivery": 80, "quality_score": 85},  # 缺少collaboration_score
        {"employee_id": "E004", "feature_delivery": 60, "quality_score": 70, "collaboration_score": 65},
        {"employee_id": "E002", "feature_delivery": 75, "quality_score": 72, "collaboration_score": 78},  # 与有效记录冲突
    ]
    with open(os.path.join(base, "data/ledgers/old_monthly_outputs.json"), "w") as f:
        json.dump({"monthly_outputs": old_outputs}, f, indent=2)

    # ---- 有效评分规则 ----
    rules = [
        {"role_code": "ENG", "feature_delivery_weight": 0.5, "quality_weight": 0.3, "collaboration_weight": 0.2},
        {"role_code": "SALES", "feature_delivery_weight": 0.2, "quality_weight": 0.3, "collaboration_weight": 0.5},
        {"role_code": "MGR", "feature_delivery_weight": 0.4, "quality_weight": 0.4, "collaboration_weight": 0.2},
    ]
    with open(os.path.join(base, "data/rules/scoring_rules.json"), "w") as f:
        json.dump({"scoring_rules": rules}, f, indent=2)

    # ---- 干扰：旧规则（权重异常） ----
    old_rules = [
        {"role_code": "ENG", "feature_delivery_weight": 0.6, "quality_weight": 0.2, "collaboration_weight": 0.2},
        {"role_code": "FIN", "feature_delivery_weight": 0.3, "quality_weight": 0.4, "collaboration_weight": 0.3},
    ]
    with open(os.path.join(base, "data/rules/scoring_rules_old.json"), "w") as f:
        json.dump({"scoring_rules": old_rules}, f, indent=2)

    # ---- 额外干扰：一个无关的txt文件 ----
    with open(os.path.join(base, "data/README.txt"), "w") as f:
        f.write("这个文件夹包含员工绩效数据，请忽略.txt文件。\n")

    print("环境构建完成：有效员工3人，干扰文件3+，请AI从正确路径提取数据。")

if __name__ == "__main__":
    build_env()
