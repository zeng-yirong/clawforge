import os
import sys
import json
import math

def evaluate(workspace):
    scores = []
    total_score = 0
    max_score = 100

    # 1. 检查 output 目录是否存在 (10分)
    profiles_dir = os.path.join(workspace, "performance_profiles")
    exists = os.path.isdir(profiles_dir)
    scores.append({
        "item": "Directory performance_profiles exists",
        "score": 10 if exists else 0,
        "max_score": 10,
        "passed": exists,
        "reason": "" if exists else "Missing directory performance_profiles"
    })
    if not exists:
        # 如果目录不存在，后续检查无从谈起，直接给0分
        scores.append({"item": "Generated profiles (skip due to missing dir)", "score": 0, "max_score": 90, "passed": False, "reason": "Directory missing, cannot check files"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": scores}, f)
        return

    # 2. 加载原始数据用于验证
    employees_path = os.path.join(workspace, "data/employees/employees.json")
    outputs_path = os.path.join(workspace, "data/ledgers/monthly_outputs.json")
    rules_path = os.path.join(workspace, "data/rules/scoring_rules.json")

    # 如果原始数据缺失，不能全责
    if not all(os.path.isfile(p) for p in [employees_path, outputs_path, rules_path]):
        scores.append({"item": "Source data files exist", "score": 0, "max_score": 90, "passed": False, "reason": "Critical source files missing"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": scores}, f)
        return

    with open(employees_path) as f:
        emp_data = json.load(f)
    with open(outputs_path) as f:
        out_data = json.load(f)
    with open(rules_path) as f:
        rule_data = json.load(f)

    employees = emp_data.get("employees", [])
    outputs = out_data.get("monthly_outputs", [])
    rules = rule_data.get("scoring_rules", [])

    # 构建映射
    output_map = {o["employee_id"]: o for o in outputs}
    rule_map = {r["role_code"]: r for r in rules}

    # 应该生成的 employee_ids (有输出且有对应规则)
    expected = []
    missing = []
    for emp in employees:
        eid = emp["employee_id"]
        role = emp.get("role_code", "")
        if eid in output_map and role in rule_map:
            expected.append(eid)
        else:
            missing.append(eid)

    # 检查生成的文件
    generated_files = [f for f in os.listdir(profiles_dir) if f.endswith(".json")]
    generated_ids = set(f.replace(".json", "") for f in generated_files)
    missing_files = [eid for eid in expected if eid not in generated_ids]
    extra_files = [fid for fid in generated_ids if fid not in expected]

    # 如果缺失或多余文件，扣分
    file_penalty = 0
    file_ok = True
    if missing_files:
        file_ok = False
        file_penalty += 10   # 每个缺失扣10，但最多扣30
    if extra_files:
        file_ok = False
        file_penalty += 5    # 多余文件每个扣5

    file_score = max(0, 30 - file_penalty)
    scores.append({
        "item": "Correct set of profile files (no missing, no extra)",
        "score": file_score,
        "max_score": 30,
        "passed": file_ok,
        "reason": f"Missing: {missing_files}, Extra: {extra_files}" if not file_ok else "All expected files present and no extras"
    })

    # 3. 验证每个生成文件的结构与数值 (50分)
    calc_errors = []
    format_errors = []
    score_sum = 0
    max_calc = 50
    for eid in expected:
        fname = os.path.join(profiles_dir, f"{eid}.json")
        if not os.path.isfile(fname):
            calc_errors.append(f"{eid}: file missing")
            continue
        try:
            with open(fname) as f:
                profile = json.load(f)
        except (json.JSONDecodeError, ValueError):
            format_errors.append(f"{eid}: invalid JSON")
            continue

        emp = next(e for e in employees if e["employee_id"] == eid)
        role = emp["role_code"]
        out = output_map[eid]
        rule = rule_map[role]
        w_f = rule["feature_delivery_weight"]
        w_q = rule["quality_weight"]
        w_c = rule["collaboration_weight"]
        expected_total = out["feature_delivery"] * w_f + out["quality_score"] * w_q + out["collaboration_score"] * w_c
        expected_total = round(expected_total, 2)

        # 检查字段
        if "total_score" not in profile:
            format_errors.append(f"{eid}: missing total_score")
            continue
        if "breakdown" not in profile:
            format_errors.append(f"{eid}: missing breakdown")
            continue
        bd = profile["breakdown"]
        if not isinstance(bd, dict):
            format_errors.append(f"{eid}: breakdown not dict")
            continue
        # 可选检查 breakdown 中各项
        if "feature_delivery" not in bd or "quality_score" not in bd or "collaboration_score" not in bd:
            format_errors.append(f"{eid}: breakdown missing one of the components")
            continue

        # 计算值检查
        actual_total = profile["total_score"]
        if not isinstance(actual_total, (int, float)):
            calc_errors.append(f"{eid}: total_score not numeric")
            continue
        if abs(actual_total - expected_total) > 0.01:
            calc_errors.append(f"{eid}: expected {expected_total}, got {actual_total}")
            continue

        # 检查 breakdown 中的加权分
        expected_f = round(out["feature_delivery"] * w_f, 2)
        expected_q = round(out["quality_score"] * w_q, 2)
        expected_c = round(out["collaboration_score"] * w_c, 2)
        actual_f = bd.get("feature_delivery")
        actual_q = bd.get("quality_score")
        actual_c = bd.get("collaboration_score")
        if not isinstance(actual_f, (int, float)) or abs(actual_f - expected_f) > 0.01:
            calc_errors.append(f"{eid}: breakdown feature_delivery mismatch")
        if not isinstance(actual_q, (int, float)) or abs(actual_q - expected_q) > 0.01:
            calc_errors.append(f"{eid}: breakdown quality_score mismatch")
        if not isinstance(actual_c, (int, float)) or abs(actual_c - expected_c) > 0.01:
            calc_errors.append(f"{eid}: breakdown collaboration_score mismatch")

    # 计算这部分得分
    # 格式错误：每项扣5, 最多扣15
    format_penalty = min(len(format_errors) * 5, 15)
    calc_penalty = min(len(calc_errors) * 5, 35)
    calc_score = max(0, max_calc - format_penalty - calc_penalty)

    scores.append({
        "item": "Profile correctness (structure and calculation)",
        "score": calc_score,
        "max_score": max_calc,
        "passed": (len(format_errors) == 0 and len(calc_errors) == 0),
        "reason": f"Format errors: {len(format_errors)} -> penalty {format_penalty}; Calc errors: {len(calc_errors)} -> penalty {calc_penalty}" if (format_errors or calc_errors) else "All profiles correct"
    })

    # 4. 额外检查：没有使用旧规则 (10分) —— 检查是否生成了不应有的员工
    # 我们已通过 expected 保证了，如果 agent 用了旧规则，某些角色权重不同导致数值不同，会被上面检测到
    # 但也可能 agent 错误地为缺少输出的员工生成文件，那些已经在 extra_files 中扣分
    # 这里再检查一下是否有 E007 或 E008 的档案（不应该有）
    unwanted = {"E007", "E008"}
    unwanted_found = [eid for eid in generated_ids if eid in unwanted]
    if unwanted_found:
        scores.append({
            "item": "No files for employees without outputs or missing role rule",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Generated unwanted profiles: {unwanted_found}"
        })
    else:
        scores.append({
            "item": "No files for employees without outputs or missing role rule",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "No unwanted profiles"
        })

    # 合计总分
    total_score = sum(s["score"] for s in scores)
    result = {
        "total_score": total_score,
        "details": scores
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total_score}")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    evaluate(workspace)
