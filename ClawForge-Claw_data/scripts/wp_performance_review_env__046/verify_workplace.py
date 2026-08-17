import os
import sys
import json
import math

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def grade_from_score(score, cutoffs):
    if score >= cutoffs["A"]:
        return "A"
    elif score >= cutoffs["B"]:
        return "B"
    else:
        return "C"

def main():
    if len(sys.argv) > 1:
        workspace = sys.argv[1]
    else:
        workspace = "."
    # paths relative to workspace
    emp_path = os.path.join(workspace, "data/employees/employees.json")
    rule_path = os.path.join(workspace, "data/rules/scoring_rules.json")
    ledger_path = os.path.join(workspace, "data/ledgers/monthly_outputs.json")
    result_path = os.path.join(workspace, "ops/performance_review.json")

    score_items = []
    total_max = 100

    # --- 1. Directory structure (10 pts) ---
    max_dir = 10
    dir_pass = True
    dir_checks = [
        os.path.isdir(os.path.join(workspace, "data/employees")),
        os.path.isdir(os.path.join(workspace, "data/ledgers")),
        os.path.isdir(os.path.join(workspace, "data/rules")),
        os.path.isdir(os.path.join(workspace, "ops")),
    ]
    if not all(dir_checks):
        dir_pass = False
        score_items.append({"item": "Directory structure", "score": 0, "max_score": max_dir, "passed": False,
                            "reason": "One or more required directories missing."})
    else:
        score_items.append({"item": "Directory structure", "score": max_dir, "max_score": max_dir, "passed": True,
                            "reason": "All required directories present."})

    # --- 2. Input files exist and are valid JSON (10 pts) ---
    max_input = 10
    try:
        employees_data = load_json(emp_path)
        rules_data = load_json(rule_path)
        ledger_data = load_json(ledger_path)
        score_items.append({"item": "Input file validity", "score": max_input, "max_score": max_input, "passed": True,
                            "reason": "All input files exist and are valid JSON."})
    except Exception as e:
        score_items.append({"item": "Input file validity", "score": 0, "max_score": max_input, "passed": False,
                            "reason": f"Error reading input files: {e}"})
        # cannot proceed further
        details = score_items
        total = sum(i["score"] for i in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        return

    # --- 3. Result file exists and is valid JSON (10 pts) ---
    max_result = 10
    if not os.path.exists(result_path):
        score_items.append({"item": "Result file existence", "score": 0, "max_score": max_result, "passed": False,
                            "reason": "ops/performance_review.json not found."})
        # stop further checks
        total = sum(i["score"] for i in score_items)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": score_items}, f, indent=2)
        return
    try:
        result = load_json(result_path)
        if not isinstance(result, list):
            raise ValueError("Result must be a list.")
        score_items.append({"item": "Result file format", "score": max_result, "max_score": max_result, "passed": True,
                            "reason": "Result file exists and is a valid JSON array."})
    except Exception as e:
        score_items.append({"item": "Result file format", "score": 0, "max_score": max_result, "passed": False,
                            "reason": f"Invalid result file: {e}"})
        total = sum(i["score"] for i in score_items)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": score_items}, f, indent=2)
        return

    # --- 4. Content correctness (70 pts) ---
    # Build expected results
    employees = employees_data["employees"]
    emp_map = {emp["employee_id"]: emp for emp in employees}
    rules = rules_data["scoring_rules"]
    rule_map = {r["role_code"]: r for r in rules}

    # Filter March records, remove invalid (negative any score) and unknown employees
    ledger = ledger_data["monthly_outputs"]
    march_records = [r for r in ledger if r.get("month") == "2025-03"]
    valid_records = []
    for rec in march_records:
        eid = rec["employee_id"]
        if eid not in emp_map:
            continue
        if rec["feature_delivery"] < 0 or rec["quality_score"] < 0 or rec["collaboration_score"] < 0:
            continue
        valid_records.append(rec)

    # For duplicate employee_ids, keep the one with highest quality_score (tie-break: first encountered)
    best = {}
    for rec in valid_records:
        eid = rec["employee_id"]
        if eid not in best:
            best[eid] = rec
        else:
            # keep the one with larger quality_score (or any deterministic rule)
            if rec["quality_score"] > best[eid]["quality_score"]:
                best[eid] = rec
    expected = []
    for eid, rec in best.items():
        emp = emp_map[eid]
        role = emp["role_code"]
        rule = rule_map[role]
        score = (rec["feature_delivery"] * rule["feature_delivery_weight"] +
                 rec["quality_score"] * rule["quality_weight"] +
                 rec["collaboration_score"] * rule["collaboration_weight"])
        score = round(score, 1)
        grade = grade_from_score(score, rule["grade_cutoffs"])
        expected.append({"employee_id": eid, "total_score": score, "grade": grade})

    # Build map from result for easy comparison
    result_map = {r["employee_id"]: r for r in result}
    expected_map = {r["employee_id"]: r for r in expected}

    max_content = 70
    content_passed = True
    content_reason = ""

    # Check count
    if len(result) != len(expected):
        content_passed = False
        content_reason = f"Expected {len(expected)} employees in result, got {len(result)}."
    else:
        # Check each expected employee
        errors = []
        for eid, exp in expected_map.items():
            if eid not in result_map:
                errors.append(f"Missing employee {eid}")
                continue
            res = result_map[eid]
            # Check fields
            if set(res.keys()) != {"employee_id", "total_score", "grade"}:
                errors.append(f"{eid}: extra or missing fields")
                continue
            if not math.isclose(res["total_score"], exp["total_score"], abs_tol=0.15):
                errors.append(f"{eid}: total_score mismatch (got {res['total_score']}, expected {exp['total_score']})")
            if res["grade"] != exp["grade"]:
                errors.append(f"{eid}: grade mismatch (got {res['grade']}, expected {exp['grade']})")
        if errors:
            content_passed = False
            content_reason = "; ".join(errors)
        else:
            content_reason = "All employees' scores and grades correctly computed."

    if content_passed:
        score_items.append({"item": "Content correctness", "score": max_content, "max_score": max_content, "passed": True,
                            "reason": content_reason})
    else:
        # partial scoring: each employee worth 70/4 = 17.5, but we give proportional
        # simpler: 10 points per employee, rest 30 for overall correctness
        correct_count = 0
        for eid, exp in expected_map.items():
            if eid in result_map:
                res = result_map[eid]
                if (set(res.keys()) == {"employee_id", "total_score", "grade"} and
                    math.isclose(res["total_score"], exp["total_score"], abs_tol=0.15) and
                    res["grade"] == exp["grade"]):
                    correct_count += 1
        if correct_count == len(expected):
            partial_score = max_content
        else:
            # each correct employee gets 15, plus 10 for overall structure
            partial_score = correct_count * 15
            if partial_score > max_content:
                partial_score = max_content
        score_items.append({"item": "Content correctness", "score": partial_score, "max_score": max_content,
                            "passed": False, "reason": content_reason if content_reason else "Partial correctness."})

    # --- Final score ---
    total_score = sum(i["score"] for i in score_items)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_items}, f, indent=2)
    print(f"Verification complete. Total score: {total_score}/100")

if __name__ == "__main__":
    main()
