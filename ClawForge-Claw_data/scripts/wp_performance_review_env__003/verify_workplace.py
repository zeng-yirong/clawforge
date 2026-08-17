"""
Verify the agent's output for performance review task.
Checks:
- reports/ directory exists
- performance_summary.json exists and is valid JSON
- Contains only valid employees (with both employee record and output record)
- Fields: employee_id, employee_name, total_score, grade
- Score calculation is correct using weights from scoring_rules
- No extra employees or fields
"""
import json
import os
import sys
import math

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def compute_grade(score):
    if score >= 90:
        return "A"
    elif score >= 75:
        return "B"
    elif score >= 60:
        return "C"
    else:
        return "D"

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    max_total = 100

    # 1. Directory structure (10 points)
    reports_dir = os.path.join(workspace, "reports")
    if os.path.isdir(reports_dir):
        details.append({"item": "reports directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "reports/ directory found"})
    else:
        details.append({"item": "reports directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "reports/ directory missing"})
        # cannot continue if reports dir missing
        final = {"total_score": 0, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        print("FAIL: reports directory not found")
        return

    # 2. performance_summary.json exists (10 points)
    summary_path = os.path.join(reports_dir, "performance_summary.json")
    if os.path.isfile(summary_path):
        details.append({"item": "performance_summary.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
    else:
        details.append({"item": "performance_summary.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        final = {"total_score": 0, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        print("FAIL: performance_summary.json not found")
        return

    # 3. Valid JSON (10 points)
    try:
        data = load_json(summary_path)
        details.append({"item": "JSON is valid", "score": 10, "max_score": 10, "passed": True, "reason": "parsed successfully"})
    except Exception as e:
        details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": f"parse error: {e}"})
        final = {"total_score": sum(d["score"] for d in details), "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    # 4. Structure check: must be a list or dict with list? we allow list or dict with key "employees"
    # Allow both: list or dict with "employees" key
    if isinstance(data, list):
        employees_result = data
    elif isinstance(data, dict):
        employees_result = data.get("employees", [])
        if not isinstance(employees_result, list):
            details.append({"item": "result structure", "score": 0, "max_score": 10, "passed": False, "reason": "'employees' key is not a list"})
            employees_result = []
    else:
        details.append({"item": "result structure", "score": 0, "max_score": 10, "passed": False, "reason": "expected list or dict"})
        employees_result = []
    if len(employees_result) > 0:
        details.append({"item": "result structure", "score": 10, "max_score": 10, "passed": True, "reason": f"found {len(employees_result)} employee entries"})
    else:
        details.append({"item": "result structure", "score": 0, "max_score": 10, "passed": False, "reason": "empty result list"})

    # Load ground truth data
    # employees
    with open(os.path.join(workspace, "data/employees/employees.json")) as f:
        emp_data = json.load(f)
    emp_map = {e["employee_id"]: e for e in emp_data["employees"]}
    # ledgers
    with open(os.path.join(workspace, "data/ledgers/monthly_outputs.json")) as f:
        led_data = json.load(f)
    output_map = {o["employee_id"]: o for o in led_data["monthly_outputs"]}
    # rules
    with open(os.path.join(workspace, "data/rules/scoring_rules.json")) as f:
        rule_data = json.load(f)
    rule_map = {r["role_code"]: r for r in rule_data["scoring_rules"]}

    # Determine valid employees (both in emp_map and output_map)
    valid_ids = set(emp_map.keys()) & set(output_map.keys())
    # expected results
    expected = {}
    for eid in valid_ids:
        emp = emp_map[eid]
        out = output_map[eid]
        rule = rule_map.get(emp["role_code"])
        if rule is None:
            continue  # should not happen with our data, but skip
        fd = out["feature_delivery"]
        qs = out["quality_score"]
        cs = out["collaboration_score"]
        total = fd * rule["feature_delivery_weight"] + qs * rule["quality_weight"] + cs * rule["collaboration_weight"]
        grade = compute_grade(total)
        expected[eid] = {
            "employee_id": eid,
            "employee_name": emp["employee_name"],
            "total_score": round(total, 2),  # round to 2 decimals
            "grade": grade
        }

    # 5. Check each employee entry for correctness (40 points total, 5 per valid employee)
    # We have 5 valid employees: EMP001, EMP002, EMP003, EMP004, EMP005
    expected_ids = set(expected.keys())
    result_ids = set(e.get("employee_id") for e in employees_result if isinstance(e, dict) and "employee_id" in e)

    # Check for extra employees (10 points)
    extra = result_ids - expected_ids
    if extra:
        details.append({"item": "no extra employees", "score": 0, "max_score": 10, "passed": False, "reason": f"unexpected employee(s): {extra}"})
    else:
        details.append({"item": "no extra employees", "score": 10, "max_score": 10, "passed": True, "reason": "all employee IDs are valid"})

    # Check for missing employees (10 points)
    missing = expected_ids - result_ids
    if missing:
        details.append({"item": "all valid employees present", "score": 0, "max_score": 10, "passed": False, "reason": f"missing employee(s): {missing}"})
    else:
        details.append({"item": "all valid employees present", "score": 10, "max_score": 10, "passed": True, "reason": "all expected employees found"})

    # Now check field correctness per employee (20 points, 4 per employee)
    field_score = 0
    field_max = 20
    field_fail_reasons = []
    for eid in expected_ids:
        exp = expected[eid]
        # find result entry
        res = None
        for r in employees_result:
            if isinstance(r, dict) and r.get("employee_id") == eid:
                res = r
                break
        if res is None:
            field_fail_reasons.append(f"{eid}: missing in result")
            continue
        # check fields
        if "employee_name" not in res:
            field_fail_reasons.append(f"{eid}: missing employee_name")
        elif res["employee_name"] != exp["employee_name"]:
            field_fail_reasons.append(f"{eid}: wrong name '{res.get('employee_name')}'")
        else:
            field_score += 1
        if "total_score" not in res:
            field_fail_reasons.append(f"{eid}: missing total_score")
        elif not isinstance(res["total_score"], (int, float)):
            field_fail_reasons.append(f"{eid}: total_score not numeric")
        else:
            if abs(res["total_score"] - exp["total_score"]) < 0.01:
                field_score += 1
            else:
                field_fail_reasons.append(f"{eid}: total_score expected {exp['total_score']:.2f}, got {res['total_score']}")
        if "grade" not in res:
            field_fail_reasons.append(f"{eid}: missing grade")
        elif res["grade"] != exp["grade"]:
            field_fail_reasons.append(f"{eid}: grade expected {exp['grade']}, got {res['grade']}")
        else:
            field_score += 1
        # check no extra fields? we'll deduct if extra, but not mandatory
        # just ensure at least these three
    if field_fail_reasons:
        details.append({"item": "field correctness (score, grade, name)", "score": field_score, "max_score": field_max, "passed": False, "reason": "; ".join(field_fail_reasons[:3])})
    else:
        details.append({"item": "field correctness (score, grade, name)", "score": field_score, "max_score": field_max, "passed": True, "reason": "all fields correct"})

    # Check for extra fields in entries (10 points)
    extra_fields_found = False
    extra_field_reason = ""
    for r in employees_result:
        if not isinstance(r, dict):
            continue
        allowed = {"employee_id", "employee_name", "total_score", "grade"}
        extra = set(r.keys()) - allowed
        if extra:
            extra_fields_found = True
            extra_field_reason = f"extra fields in {r.get('employee_id','?')}: {extra}"
            break
    if extra_fields_found:
        details.append({"item": "no extra fields in entries", "score": 0, "max_score": 10, "passed": False, "reason": extra_field_reason})
    else:
        details.append({"item": "no extra fields in entries", "score": 10, "max_score": 10, "passed": True, "reason": "no extra fields"})

    # Summary
    total_score = sum(d["score"] for d in details)
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Score: {total_score}/{max_total}")

if __name__ == "__main__":
    main()
