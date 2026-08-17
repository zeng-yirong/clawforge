import sys
import json
import os
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查 ops 目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory ops/ found."})
        total_score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory ops/ not found."})

    # 2. 检查 performance_profile.json 是否存在且合法 JSON (20分)
    profile_path = os.path.join(ops_dir, "performance_profile.json")
    if not os.path.isfile(profile_path):
        details.append({"item": "performance_profile.json exists", "score": 0, "max_score": 20, "passed": False, "reason": "File not found."})
        write_score(details, total_score, max_total, workspace)
        return

    try:
        with open(profile_path, "r") as f:
            profile_data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 20, "passed": False, "reason": f"Invalid JSON: {str(e)}"})
        write_score(details, total_score, max_total, workspace)
        return

    if not isinstance(profile_data, list):
        details.append({"item": "valid JSON", "score": 0, "max_score": 20, "passed": False, "reason": "Root is not a list."})
        write_score(details, total_score, max_total, workspace)
        return
    details.append({"item": "valid JSON with list root", "score": 20, "max_score": 20, "passed": True, "reason": "File exists and is a valid JSON list."})
    total_score += 20

    # 3. 检查记录数 (期望3个有效员工) (10分)
    expected_count = 3
    actual_count = len(profile_data)
    if actual_count == expected_count:
        details.append({"item": "record count", "score": 10, "max_score": 10, "passed": True, "reason": f"Exactly {expected_count} records."})
        total_score += 10
    else:
        details.append({"item": "record count", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {expected_count}, got {actual_count}."})

    # 4. 剔除无效角色和脏数据检查 (30分)
    # 检查是否包含 Diana (E004) 或 E005
    employee_ids = [rec.get("employee_id") for rec in profile_data]
    invalid_ids = [eid for eid in employee_ids if eid in ["E004", "E005"]]
    if not invalid_ids:
        details.append({"item": "exclude invalid employees", "score": 30, "max_score": 30, "passed": True, "reason": "No Diana (INACTIVE) or E005 (non-existent employee) included."})
        total_score += 30
    else:
        details.append({"item": "exclude invalid employees", "score": 0, "max_score": 30, "passed": False, "reason": f"Found invalid IDs: {invalid_ids}"})

    # 5. 检查字段完整性 (10分)
    required_fields = ["employee_id", "employee_name", "department", "role_code", "score"]
    field_ok = True
    for rec in profile_data:
        for field in required_fields:
            if field not in rec:
                field_ok = False
                break
        if not field_ok:
            break
    if field_ok:
        details.append({"item": "required fields present", "score": 10, "max_score": 10, "passed": True, "reason": "All records contain employee_id, employee_name, department, role_code, score."})
        total_score += 10
    else:
        details.append({"item": "required fields present", "score": 0, "max_score": 10, "passed": False, "reason": "Missing some fields in at least one record."})

    # 6. 分数计算准确性 (20分)
    # 需要引用原始数据来计算期望值
    # 从工作区读取原始文件
    emp_path = os.path.join(workspace, "data/employees/employees.json")
    out_path = os.path.join(workspace, "data/ledgers/monthly_outputs.json")
    rule_path = os.path.join(workspace, "data/rules/scoring_rules.json")
    try:
        with open(emp_path) as f:
            emp_data = json.load(f)["employees"]
        with open(out_path) as f:
            out_data = json.load(f)["monthly_outputs"]
        with open(rule_path) as f:
            rule_data = json.load(f)["scoring_rules"]
    except Exception as e:
        details.append({"item": "score calculation", "score": 0, "max_score": 20, "passed": False, "reason": f"Cannot read source data: {str(e)}"})
        write_score(details, total_score, max_total, workspace)
        return

    # 构建查询字典
    emp_dict = {e["employee_id"]: e for e in emp_data}
    rule_dict = {r["role_code"]: r for r in rule_data}
    # 只取最新月份 (2025-03) 的输出
    out_dict = {}
    for o in out_data:
        if o["period"] == "2025-03":
            out_dict[o["employee_id"]] = o

    # 期望结果：只包含有角色规则且在最新输出中有记录的员工
    expected = []
    for eid, emp in emp_dict.items():
        if eid not in out_dict:
            continue
        role = emp["role_code"]
        if role not in rule_dict:
            continue
        rule = rule_dict[role]
        o = out_dict[eid]
        score = (rule["feature_delivery_weight"] * o["feature_delivery"] +
                 rule["quality_weight"] * o["quality_score"] +
                 rule["collaboration_weight"] * o["collaboration_score"])
        score = round(score, 2)
        expected.append({
            "employee_id": eid,
            "employee_name": emp["employee_name"],
            "department": emp["department"],
            "role_code": role,
            "score": score
        })

    # 按 employee_id 排序以比较
    expected_sorted = sorted(expected, key=lambda x: x["employee_id"])
    actual_sorted = sorted(profile_data, key=lambda x: x.get("employee_id", ""))

    if len(expected_sorted) != len(actual_sorted):
        details.append({"item": "score calculation", "score": 0, "max_score": 20, "passed": False, "reason": f"Count mismatch: expected {len(expected_sorted)}, got {len(actual_sorted)}."})
    else:
        calc_ok = True
        for e, a in zip(expected_sorted, actual_sorted):
            if (e["employee_id"] != a.get("employee_id") or
                e["employee_name"] != a.get("employee_name") or
                e["department"] != a.get("department") or
                e["role_code"] != a.get("role_code")):
                calc_ok = False
                break
            # 比较分数，允许浮点误差
            exp_score = e["score"]
            act_score = a.get("score")
            if not isinstance(act_score, (int, float)):
                calc_ok = False
                break
            if not math.isclose(exp_score, act_score, abs_tol=1e-9):
                calc_ok = False
                break
        if calc_ok:
            details.append({"item": "score calculation", "score": 20, "max_score": 20, "passed": True, "reason": "All scores computed correctly."})
            total_score += 20
        else:
            details.append({"item": "score calculation", "score": 0, "max_score": 20, "passed": False, "reason": "Mismatch in one or more records."})

    write_score(details, total_score, max_total, workspace)

def write_score(details, total, max_total, workspace):
    score_data = {
        "total_score": min(total, max_total),
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score_data, f, indent=2)

if __name__ == "__main__":
    main()
