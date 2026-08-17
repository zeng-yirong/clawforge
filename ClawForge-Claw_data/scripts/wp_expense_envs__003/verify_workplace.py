import sys
import json
import csv
import os
import pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    # 评分明细
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查目录结构 (10分)
    required_files = [
        "data/employee_profile.json",
        "data/travel_policies.json",
        "data/consumption_records.csv"
    ]
    dir_score = 0
    dir_max = 10
    for rel_path in required_files:
        full = os.path.join(workspace, rel_path)
        if os.path.isfile(full):
            dir_score += 3
        else:
            dir_score += 0
    # ops/budget_check.json 存在检查
    result_path = os.path.join(workspace, "ops", "budget_check.json")
    if os.path.isfile(result_path):
        dir_score += 1
    else:
        dir_score += 0
    passed = dir_score == dir_max
    details.append({
        "item": "Required files exist",
        "score": dir_score,
        "max_score": dir_max,
        "passed": passed,
        "reason": f"Found {dir_score}/{dir_max} necessary files."
    })
    total_score += dir_score

    # 2. 结果JSON合法性 (10分)
    score_valid = 0
    max_valid = 10
    try:
        with open(result_path, "r", encoding="utf-8") as f:
            result = json.load(f)
        score_valid = 10
    except Exception as e:
        details.append({
            "item": "Result JSON is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Cannot parse JSON: {e}"
        })
        total_score += 0
        # 后续检查无法进行，直接写总分返回
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    details.append({
        "item": "Result JSON is valid",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "JSON parsed successfully."
    })
    total_score += score_valid

    # 3. 字段完整性 (15分)
    required_fields = [
        "employee_id", "tier", "destination", "duration_days",
        "categories", "total_budget", "total_actual",
        "overall_over_budget", "over_budget_categories"
    ]
    fields_present = 0
    for field in required_fields:
        if field in result:
            fields_present += 1
    # categories 内每个条目必含字段
    cat_ok = True
    if "categories" in result and isinstance(result["categories"], list):
        for cat in result["categories"]:
            for field in ["name", "budget", "actual", "excess", "over_budget"]:
                if field not in cat:
                    cat_ok = False
                    break
            if not cat_ok:
                break
    else:
        cat_ok = False
    completeness_score = 0
    completeness_max = 15
    if fields_present == len(required_fields) and cat_ok:
        completeness_score = 15
    else:
        # 部分得分
        completeness_score = fields_present * 1 + (10 if cat_ok else 0)
        if completeness_score > 15:
            completeness_score = 15
    passed = completeness_score == 15
    details.append({
        "item": "Result contains all required fields",
        "score": completeness_score,
        "max_score": 15,
        "passed": passed,
        "reason": f"Full fields {fields_present}/{len(required_fields)}; categories structure ok: {cat_ok}"
    })
    total_score += completeness_score

    # 4. 数值正确性 (50分) - 核心
    # 先从初始文件计算预期值
    try:
        with open(os.path.join(workspace, "data/employee_profile.json"), "r", encoding="utf-8") as f:
            profile = json.load(f)
        with open(os.path.join(workspace, "data/travel_policies.json"), "r", encoding="utf-8") as f:
            policies = json.load(f)
        with open(os.path.join(workspace, "data/consumption_records.csv"), "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            all_records = list(reader)
    except Exception as e:
        details.append({
            "item": "Numerical correctness",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": f"Cannot read initial data files: {e}"
        })
        total_score += 0
        # 写最终分数
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 找到匹配的政策
    matched_policy = None
    for pol in policies:
        if (pol["tier"] == profile["tier"] and
            pol["destination"] == profile["destination"] and
            pol["duration_days"] == profile["trip_duration_days"]):
            matched_policy = pol
            break
    if matched_policy is None:
        details.append({
            "item": "Numerical correctness",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": "No matching policy found in initial data"
        })
        total_score += 0
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 按员工ID筛选消费记录
    emp_id = profile["employee_id"]
    emp_records = [r for r in all_records if r["employee_id"] == emp_id]
    # 按类别汇总实际金额
    actual_by_category = {}
    for r in emp_records:
        cat = r["category"]
        amount = float(r["amount"])
        actual_by_category[cat] = actual_by_category.get(cat, 0.0) + amount

    # 构建预期 categories
    expected_categories = []
    total_budget = 0.0
    total_actual = 0.0
    for cat_def in matched_policy["categories"]:
        name = cat_def["name"]
        budget = cat_def["budget"]
        actual = actual_by_category.get(name, 0.0)
        excess = actual - budget
        over = excess > 0.0
        expected_categories.append({
            "name": name,
            "budget": budget,
            "actual": actual,
            "excess": excess,
            "over_budget": over
        })
        total_budget += budget
        total_actual += actual
    overall_over = total_actual > total_budget
    over_budget_categories = [c["name"] for c in expected_categories if c["over_budget"]]
    expected = {
        "employee_id": profile["employee_id"],
        "tier": profile["tier"],
        "destination": profile["destination"],
        "duration_days": profile["trip_duration_days"],
        "categories": expected_categories,
        "total_budget": total_budget,
        "total_actual": total_actual,
        "overall_over_budget": overall_over,
        "over_budget_categories": over_budget_categories
    }

    # 比对
    num_score = 0
    num_max = 50
    # 比较各字段
    checks = [
        ("employee_id", str, expected["employee_id"]),
        ("tier", str, expected["tier"]),
        ("destination", str, expected["destination"]),
        ("duration_days", (int, float), expected["duration_days"]),
        ("total_budget", (int, float), expected["total_budget"]),
        ("total_actual", (int, float), expected["total_actual"]),
        ("overall_over_budget", bool, expected["overall_over_budget"]),
    ]
    passed_checks = 0
    for field, typ, exp_val in checks:
        if field not in result:
            continue
        val = result[field]
        if not isinstance(val, typ):
            continue
        if isinstance(exp_val, float):
            # 允许微小误差
            if abs(val - exp_val) > 0.001:
                continue
        elif val != exp_val:
            continue
        passed_checks += 1
    # categories 比对
    cat_checks = 0
    if "categories" in result and isinstance(result["categories"], list):
        if len(result["categories"]) == len(expected_categories):
            for i, exp_cat in enumerate(expected_categories):
                rc = result["categories"][i] if i < len(result["categories"]) else {}
                for key, exp_val in exp_cat.items():
                    if key not in rc:
                        continue
                    val = rc[key]
                    if isinstance(exp_val, float):
                        if abs(val - exp_val) > 0.001:
                            continue
                    elif val != exp_val:
                        continue
                    cat_checks += 1
    # over_budget_categories 比对
    obc_ok = False
    if "over_budget_categories" in result and isinstance(result["over_budget_categories"], list):
        if sorted(result["over_budget_categories"]) == sorted(expected["over_budget_categories"]):
            obc_ok = True
            cat_equal = (len(result["over_budget_categories"]) == len(expected["over_budget_categories"]))
            if cat_equal:
                obc_ok = True
    # 计算数值得分
    num_score = (passed_checks / len(checks)) * 25  # 25分
    num_score += (cat_checks / (len(expected_categories)*5)) * 20  # 20分
    num_score += (10 if obc_ok else 0)  # 5分  (over_budget_categories)
    num_score = min(num_score, num_max)
    num_score = round(num_score)
    passed_num = num_score == num_max
    details.append({
        "item": "Numerical correctness (comparison against expected)",
        "score": num_score,
        "max_score": num_max,
        "passed": passed_num,
        "reason": f"Primary fields matched {passed_checks}/{len(checks)}, categories details {cat_checks}/{len(expected_categories)*5}, over_budget_categories correct: {obc_ok}"
    })
    total_score += num_score

    # 5. 无多余字段 (5分)
    extra_fields = set(result.keys()) - set(required_fields + ["details"])  # details可能来自其他，忽略
    extra_score = 0
    extra_max = 5
    if len(extra_fields) == 0:
        extra_score = 5
    else:
        extra_score = 0
    details.append({
        "item": "No extra fields",
        "score": extra_score,
        "max_score": extra_max,
        "passed": extra_score == extra_max,
        "reason": f"Extra fields found: {extra_fields}" if extra_score == 0 else "No extra fields."
    })
    total_score += extra_score

    # 6. 无缺失字段 (5分) - 已经在完整性里部分覆盖，单独检查
    missing_fields = [f for f in required_fields if f not in result]
    missing_cat_fields = []
    if "categories" in result:
        for i, cat in enumerate(result["categories"]):
            for f in ["name", "budget", "actual", "excess", "over_budget"]:
                if f not in cat:
                    missing_cat_fields.append(f"categories[{i}].{f}")
    all_missing = missing_fields + missing_cat_fields
    missing_score = 0
    missing_max = 5
    if len(all_missing) == 0:
        missing_score = 5
    else:
        missing_score = 0
    details.append({
        "item": "No missing fields (beyond the completeness check)",
        "score": missing_score,
        "max_score": missing_max,
        "passed": missing_score == missing_max,
        "reason": f"Missing fields: {all_missing}" if missing_score == 0 else "All required fields present."
    })
    total_score += missing_score

    # 写入最终评分
    final_score = min(int(total_score), 100)
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": final_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
