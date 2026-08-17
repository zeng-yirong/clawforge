import sys
import json
import os
import math

def score_item(details, name, score, max_score, passed, reason):
    details.append({
        "item": name,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. 检查 reports 目录是否存在 (5分)
    reports_dir = os.path.join(workspace, "reports")
    if os.path.isdir(reports_dir):
        score_item(details, "reports directory exists", 5, 5, True, "Found reports/")
        total_score += 5
    else:
        score_item(details, "reports directory exists", 0, 5, False, "Missing reports/ directory")
        # 如果目录不存在，直接结束，因为后面的check无法进行
        write_score(total_score, details)
        return

    # 2. 检查 performance_review.json 是否存在 (5分)
    result_path = os.path.join(reports_dir, "performance_review.json")
    if os.path.isfile(result_path):
        score_item(details, "performance_review.json exists", 5, 5, True, "File found")
        total_score += 5
    else:
        score_item(details, "performance_review.json exists", 0, 5, False, "Missing file")
        write_score(total_score, details)
        return

    # 3. 文件可解析为JSON (10分)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            score_item(details, "JSON is a list", 10, 10, True, "Parsed as list")
            total_score += 10
        else:
            score_item(details, "JSON is a list", 0, 10, False, "Not a list")
            write_score(total_score, details)
            return
    except Exception as e:
        score_item(details, "JSON parseable", 0, 10, False, str(e))
        write_score(total_score, details)
        return

    # 4. 每个条目有正确的字段 (10分)
    required_fields = {"employee_id", "total_score", "grade"}
    missing_fields = False
    for item in data:
        if not required_fields.issubset(item.keys()):
            missing_fields = True
            break
    if not missing_fields:
        score_item(details, "All items have required fields (employee_id, total_score, grade)", 10, 10, True, "")
        total_score += 10
    else:
        score_item(details, "All items have required fields", 0, 10, False, "Some items missing fields")
        write_score(total_score, details)
        return

    # 5. 员工ID集合正确 (包含所有5个有效员工，没有多余) (30分)
    expected_ids = {"E001", "E002", "E003", "E004", "E005"}
    actual_ids = {item["employee_id"] for item in data}
    if actual_ids == expected_ids:
        score_item(details, "Employee ID set matches exactly (E001-E005)", 30, 30, True, "")
        total_score += 30
    elif expected_ids.issubset(actual_ids) and len(actual_ids) > len(expected_ids):
        extra = actual_ids - expected_ids
        score_item(details, "Employee ID set", 15, 30, False, f"Has extra IDs: {extra}")
        total_score += 15
    elif actual_ids.issubset(expected_ids) and len(actual_ids) < len(expected_ids):
        missing = expected_ids - actual_ids
        score_item(details, "Employee ID set", 10, 30, False, f"Missing IDs: {missing}")
        total_score += 10
    else:
        score_item(details, "Employee ID set", 0, 30, False, f"Unexpected set: {actual_ids}")
        # 继续检查分数，但已经偏离太多，后面分数可能不准

    # 6. 每个员工的总分和等级精确匹配 (40分，每人8分)
    # 预期计算结果
    rules = {
        "ENG": (0.4, 0.35, 0.25),
        "MGR": (0.3, 0.4, 0.3),
        "QA": (0.2, 0.5, 0.3)
    }
    employee_role = {
        "E001": "ENG",
        "E002": "MGR",
        "E003": "ENG",
        "E004": "QA",
        "E005": "MGR"
    }
    employee_scores = {
        "E001": (80, 75, 70),
        "E002": (90, 85, 80),
        "E003": (60, 55, 50),
        "E004": (70, 80, 90),
        "E005": (100, 95, 90)
    }

    def compute_total(emp_id):
        fe, qu, co = employee_scores[emp_id]
        w_fe, w_qu, w_co = rules[employee_role[emp_id]]
        total = fe * w_fe + qu * w_qu + co * w_co
        # 保留两位小数，但实际计算可能浮点误差，我们用round处理
        return round(total, 2)

    def compute_grade(total):
        if total >= 90:
            return "A"
        elif total >= 75:
            return "B"
        elif total >= 60:
            return "C"
        else:
            return "D"

    scores_ok = True
    for item in data:
        eid = item["employee_id"]
        if eid not in expected_ids:
            continue  # 额外ID已经扣过分
        expected_total = compute_total(eid)
        expected_grade = compute_grade(expected_total)
        actual_total = item.get("total_score")
        actual_grade = item.get("grade")
        # 允许浮点误差 1e-9
        if isinstance(actual_total, (int, float)) and abs(actual_total - expected_total) < 1e-9 and actual_grade == expected_grade:
            continue
        else:
            scores_ok = False
            break

    if scores_ok:
        score_item(details, "All 5 employees have correct total_score and grade", 40, 40, True, "")
        total_score += 40
    else:
        # 逐一检查，每个匹配得8分
        earned = 0
        for item in data:
            eid = item["employee_id"]
            if eid not in expected_ids:
                continue
            expected_total = compute_total(eid)
            expected_grade = compute_grade(expected_total)
            actual_total = item.get("total_score")
            actual_grade = item.get("grade")
            if isinstance(actual_total, (int, float)) and abs(actual_total - expected_total) < 1e-9 and actual_grade == expected_grade:
                earned += 8
        score_item(details, "Per-employee score/grade accuracy", earned, 40, earned == 40,
                   f"Correct for {earned//8} out of 5 employees")
        total_score += earned

    # 总分不能超过100
    total_score = min(total_score, 100)
    write_score(total_score, details)

def write_score(total, details):
    output = {
        "total_score": total,
        "details": details
    }
    # 写入 workplace_score.json 到当前目录 (verify脚本所在目录? 题目要求写入 workplace_score.json)
    # 写入工作区根目录
    score_file = "workplace_score.json"
    with open(score_file, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
