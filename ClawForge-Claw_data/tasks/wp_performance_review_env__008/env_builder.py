import os
import json
import shutil

def build_env():
    # 清空工作区（谨慎，但测试环境会新建）
    # cwd 已保证是 
    # 但为了安全，只清理我们创建的目录
    for d in ["data", "output", "raw_logs", "ops"]:
        if os.path.exists(d):
            shutil.rmtree(d)

    # 创建全部目录
    os.makedirs("data/employees")
    os.makedirs("data/ledgers")
    os.makedirs("data/rules")
    os.makedirs("output")          # agent 将在这里生成文件
    os.makedirs("raw_logs")        # 干扰目录
    os.makedirs("ops")             # 干扰目录

    # ---- 1. 员工数据 ----
    employees = {
        "employees": [
            {"employee_id": "E001", "employee_name": "张三", "department": "Engineering", "role_code": "DEV"},
            {"employee_id": "E002", "employee_name": "李四", "department": "Engineering", "role_code": "DEV"},
            {"employee_id": "E003", "employee_name": "王五", "department": "Marketing",   "role_code": "MKT"},
            {"employee_id": "E004", "employee_name": "赵六", "department": "HR",          "role_code": "HR"},
            {"employee_id": "E005", "employee_name": "钱七", "department": "Engineering", "role_code": "INTERN"}
        ]
    }
    with open("data/employees/employees.json", "w", encoding="utf-8") as f:
        json.dump(employees, f, ensure_ascii=False, indent=2)

    # ---- 2. 产出数据（包含重复和缺失） ----
    monthly_outputs = {
        "monthly_outputs": [
            # E001 正常一条
            {"employee_id": "E001", "feature_delivery": 85, "quality_score": 90, "collaboration_score": 80},
            # E002 两条，最后一条应被采用
            {"employee_id": "E002", "feature_delivery": 70, "quality_score": 60, "collaboration_score": 50},
            {"employee_id": "E002", "feature_delivery": 80, "quality_score": 75, "collaboration_score": 70},
            # E003 缺失（不出现）
            # E004 一条
            {"employee_id": "E004", "feature_delivery": 95, "quality_score": 85, "collaboration_score": 90},
            # E005 实习生产出，但不应计入
            {"employee_id": "E005", "feature_delivery": 60, "quality_score": 70, "collaboration_score": 65}
        ]
    }
    with open("data/ledgers/monthly_outputs.json", "w", encoding="utf-8") as f:
        json.dump(monthly_outputs, f, ensure_ascii=False, indent=2)

    # ---- 3. 评分规则（正确版本） ----
    scoring_rules = {
        "scoring_rules": [
            {"role_code": "DEV",   "feature_delivery_weight": 0.4, "quality_weight": 0.3, "collaboration_weight": 0.3},
            {"role_code": "MKT",   "feature_delivery_weight": 0.3, "quality_weight": 0.4, "collaboration_weight": 0.3},
            {"role_code": "HR",    "feature_delivery_weight": 0.2, "quality_weight": 0.5, "collaboration_weight": 0.3},
            {"role_code": "INTERN","feature_delivery_weight": 0.5, "quality_weight": 0.3, "collaboration_weight": 0.2}
        ]
    }
    with open("data/rules/scoring_rules.json", "w", encoding="utf-8") as f:
        json.dump(scoring_rules, f, ensure_ascii=False, indent=2)

    # ---- 4. 干扰文件 ----
    # 旧版本规则（权重不同）
    old_rules = {
        "scoring_rules": [
            {"role_code": "DEV",   "feature_delivery_weight": 0.35, "quality_weight": 0.35, "collaboration_weight": 0.30},
            {"role_code": "MKT",   "feature_delivery_weight": 0.25, "quality_weight": 0.50, "collaboration_weight": 0.25}
        ]
    }
    with open("data/rules/old_scoring_rules.json", "w", encoding="utf-8") as f:
        json.dump(old_rules, f, ensure_ascii=False, indent=2)

    # 上个月的产出（干扰）
    prev_month = {
        "monthly_outputs": [
            {"employee_id": "E001", "feature_delivery": 90, "quality_score": 85, "collaboration_score": 70},
            {"employee_id": "E003", "feature_delivery": 70, "quality_score": 80, "collaboration_score": 75}
        ]
    }
    with open("data/ledgers/previous_month.json", "w", encoding="utf-8") as f:
        json.dump(prev_month, f, ensure_ascii=False, indent=2)

    # 实习生花名册（单独文件，干扰）
    intern_list = {"interns": [{"employee_id": "E005", "name": "钱七"}]}
    with open("data/employees/archived.json", "w", encoding="utf-8") as f:
        # 需要创建目录
        os.makedirs("data/employees", exist_ok=True)   # 已存在
        json.dump(intern_list, f, ensure_ascii=False, indent=2)

    # 一些无关的日志文件
    with open("raw_logs/server.log", "w") as f:
        f.write("2025-03-01 00:00:00 INFO 系统启动\n")
    with open("ops/note.txt", "w") as f:
        f.write("这里有个老版本规则，别用\n")

if __name__ == "__main__":
    build_env()
