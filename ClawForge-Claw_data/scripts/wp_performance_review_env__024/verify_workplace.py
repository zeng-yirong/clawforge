import json
import os
import sys
import math

def verify(workspace="."):
    details = []
    total_score = 0
    max_total = 100

    # ---------- 1. 目录结构检查（10分）----------
    required_dirs = [
        "data/employees",
        "data/ledgers",
        "data/rules",
        "profiles"
    ]
    dir_score = 0
    max_dir = 10
    for d in required_dirs:
        full_path = os.path.join(workspace, d)
        if os.path.isdir(full_path):
            dir_score += 2.5
        else:
            details.append({
                "item": f"Directory {d} exists",
                "score": 0,
                "max_score": 2.5,
                "passed": False,
                "reason": f"Missing directory: {d}"
            })
    details.append({
        "item": "Required directories present",
        "score": dir_score,
        "max_score": max_dir,
        "passed": dir_score == max_dir,
        "reason": f"Found {dir_score}/{max_dir} directories"
    })
    total_score += dir_score

    # ---------- 2. 关键文件存在性与格式（10分）----------
    file_checks = [
        ("data/employees/employees.json", "employees JSON"),
        ("data/ledgers/monthly_outputs.json", "ledgers JSON"),
        ("data/rules/scoring_rules.json", "rules JSON"),
        ("profiles/performance_profile.json", "output profile JSON"),
    ]
    file_score = 0
    max_file = 10
    for rel_path, label in file_checks:
        full_path = os.path.join(workspace, rel_path)
        if not os.path.isfile(full_path):
            details.append({
                "item": f"File {rel_path} exists",
                "score": 0,
                "max_score": 2.5,
                "passed": False,
                "reason": f"Missing file: {rel_path}"
            })
            continue
        # 尝试解析JSON
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                json.load(f)
            file_score += 2.5
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            details.append({
                "item": f"File {rel_path} is valid JSON",
                "score": 0,
                "max_score": 2.5,
                "passed": False,
                "reason": f"Invalid JSON: {e}"
            })
            continue
    details.append({
        "item": "Required files exist and are valid JSON",
        "score": file_score,
        "max_score": max_file,
        "passed": file_score == max_file,
        "reason": f"Found {file_score}/{max_file} valid files"
    })
    total_score += file_score

    # ---------- 3. 读取input数据 并计算期望答案（60分）----------
    # 3.1 读取员工数据
    emp_path = os.path.join(workspace, "data/employees/employees.json")
    with open(emp_path, "r", encoding="utf-8") as f:
        emp_data = json.load(f)
    employees = {e["employee_id"]: e for e in emp_data.get("employees", [])}
    if "E001" not in employees:
        details.append({"item": "Employee E001 exists", "score": 0, "max_score": 5, "passed": False, "reason": "Missing E001"})
    else:
        details.append({"item": "Employee E001 exists", "score": 5, "max_score": 5, "passed": True, "reason": "Found"})
        total_score += 5

    # 3.2 读取账本，筛选出E001的最新period
    ledg_path = os.path.join(workspace, "data/ledgers/monthly_outputs.json")
    with open(ledg_path, "r", encoding="utf-8") as f:
        ledg_data = json.load(f)
    outputs = ledg_data.get("monthly_outputs", [])
    e001_records = [r for r in outputs if r.get("employee_id") == "E001"]
    if not e001_records:
        # 给0分
        details.append({"item": "E001 ledger record(s) exist", "score": 0, "max_score": 10, "passed": False, "reason": "No record for E001"})
    else:
        # 找出最新period（按字符串比较，假设格式YYYY-MM可比较）
        def period_key(r):
            return r.get("period", "")
        latest = max(e001_records, key=period_key)
        # 判断是否选对了最新记录（这里只是检查，但实际得分看输出）
        details.append({
            "item": "E001 has valid ledger records",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Found {len(e001_records)} records, latest period={latest['period']}"
        })
        total_score += 10

    # 3.3 读取规则，找出ARCH角色最新生效的规则
    rule_path = os.path.join(workspace, "data/rules/scoring_rules.json")
    with open(rule_path, "r", encoding="utf-8") as f:
        rule_data = json.load(f)
    all_rules = rule_data.get("scoring_rules", [])
    arch_rules = [r for r in all_rules if r.get("role_code") == "ARCH"]
    # 按生效日期降序，取最新的
    arch_rules_sorted = sorted(arch_rules, key=lambda r: r.get("effective_date", ""), reverse=True)
    if not arch_rules_sorted:
        details.append({"item": "ARCH scoring rule exists", "score": 0, "max_score": 10, "passed": False, "reason": "No ARCH rule"})
    else:
        current_rule = arch_rules_sorted[0]  # 最新
        details.append({
            "item": "ARCH scoring rule (latest) identified",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Rule effective {current_rule['effective_date']}"
        })
        total_score += 10

    # 3.4 计算期望得分
    if 'latest' in locals() and 'current_rule' in locals():
        fd = latest["feature_delivery"]
        qs = latest["quality_score"]
        cs = latest["collaboration_score"]
        w_fd = current_rule["feature_delivery_weight"]
        w_q = current_rule["quality_weight"]
        w_c = current_rule["collaboration_weight"]
        expected_fd_score = fd * w_fd
        expected_q_score = qs * w_q
        expected_c_score = cs * w_c
        expected_total = expected_fd_score + expected_q_score + expected_c_score
        expected_total = round(expected_total, 1)  # 保留一位小数
    else:
        # 如果前面失败了，给0分
        expected_fd_score = None
        expected_q_score = None
        expected_c_score = None
        expected_total = None

    # ---------- 4. 验证输出的profile（60分中剩余部分）----------
    profile_path = os.path.join(workspace, "profiles/performance_profile.json")
    if not os.path.isfile(profile_path):
        details.append({
            "item": "Output profile file exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing profiles/performance_profile.json"
        })
        total_score += 0
    else:
        # 读取并解析
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                profile = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            details.append({
                "item": "Output profile is valid JSON",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Invalid JSON: {e}"
            })
            total_score += 0
            # 停止进一步检查
            profile = None

    # 如果profile存在且解析成功，逐字段检查
    profile_checks = []
    if profile:
        # employee_id
        if profile.get("employee_id") == "E001":
            profile_checks.append(("employee_id", 5, True, "Correct"))
        else:
            profile_checks.append(("employee_id", 0, False, f"Expected E001, got {profile.get('employee_id')}"))
        # employee_name
        if profile.get("employee_name") == "张伟":
            profile_checks.append(("employee_name", 5, True, "Correct"))
        else:
            profile_checks.append(("employee_name", 0, False, f"Expected 张伟, got {profile.get('employee_name')}"))
        # department
        if profile.get("department") == "后端架构部":
            profile_checks.append(("department", 5, True, "Correct"))
        else:
            profile_checks.append(("department", 0, False, f"Expected 后端架构部, got {profile.get('department')}"))
        # role_code
        if profile.get("role_code") == "ARCH":
            profile_checks.append(("role_code", 5, True, "Correct"))
        else:
            profile_checks.append(("role_code", 0, False, f"Expected ARCH, got {profile.get('role_code')}"))

        # 数值计算（细粒度梯度）
        if expected_total is not None:
            # feature_delivery_score
            actual_fd = profile.get("feature_delivery_score")
            if actual_fd is not None and isinstance(actual_fd, (int, float)):
                if math.isclose(actual_fd, expected_fd_score, rel_tol=1e-6):
                    profile_checks.append(("feature_delivery_score", 10, True, f"Correct: {actual_fd}"))
                else:
                    profile_checks.append(("feature_delivery_score", 0, False, f"Expected {expected_fd_score}, got {actual_fd}"))
            else:
                profile_checks.append(("feature_delivery_score", 0, False, f"Missing or invalid type: {actual_fd}"))

            actual_q = profile.get("quality_score")
            if actual_q is not None and isinstance(actual_q, (int, float)):
                if math.isclose(actual_q, expected_q_score, rel_tol=1e-6):
                    profile_checks.append(("quality_score", 10, True, f"Correct: {actual_q}"))
                else:
                    profile_checks.append(("quality_score", 0, False, f"Expected {expected_q_score}, got {actual_q}"))
            else:
                profile_checks.append(("quality_score", 0, False, f"Missing or invalid type: {actual_q}"))

            actual_c = profile.get("collaboration_score")
            if actual_c is not None and isinstance(actual_c, (int, float)):
                if math.isclose(actual_c, expected_c_score, rel_tol=1e-6):
                    profile_checks.append(("collaboration_score", 10, True, f"Correct: {actual_c}"))
                else:
                    profile_checks.append(("collaboration_score", 0, False, f"Expected {expected_c_score}, got {actual_c}"))
            else:
                profile_checks.append(("collaboration_score", 0, False, f"Missing or invalid type: {actual_c}"))

            actual_total = profile.get("total_score")
            if actual_total is not None and isinstance(actual_total, (int, float)):
                # 保留一位小数比较
                if math.isclose(actual_total, expected_total, rel_tol=1e-6):
                    profile_checks.append(("total_score", 10, True, f"Correct: {actual_total}"))
                else:
                    profile_checks.append(("total_score", 0, False, f"Expected {expected_total}, got {actual_total}"))
            else:
                profile_checks.append(("total_score", 0, False, f"Missing or invalid type: {actual_total}"))
        else:
            # 无法计算期望，全部0分
            for field in ["feature_delivery_score", "quality_score", "collaboration_score", "total_score"]:
                profile_checks.append((field, 0, False, "Cannot compute expected value (data issue)"))

    # 将profile_checks加入details，并累加分数
    for field, score, passed, reason in profile_checks:
        details.append({
            "item": f"Profile field '{field}' correct",
            "score": score,
            "max_score": 5 if field in ["employee_id","employee_name","department","role_code"] else 10,
            "passed": passed,
            "reason": reason
        })
        total_score += score

    # 确保总分不超过100
    total_score = min(total_score, 100)

    # 输出score文件
    result = {
        "total_score": total_score,
        "details": details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 打印最终得分（可调试）
    print(f"Total score: {total_score}/100")
    return total_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
