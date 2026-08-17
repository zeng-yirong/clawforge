import sys
import os
import json
import math

def load_json(workspace, path):
    full = os.path.join(workspace, path)
    if not os.path.isfile(full):
        return None
    with open(full, "r") as f:
        return json.load(f)

def calculate_expected_scores(workspace):
    # Load employees
    emp_data = load_json(workspace, "data/employees/employees.json")
    if emp_data is None:
        return None, "Missing employees.json"
    employees = emp_data.get("employees", [])
    
    # Load outputs
    out_data = load_json(workspace, "data/ledgers/monthly_outputs.json")
    if out_data is None:
        return None, "Missing monthly_outputs.json"
    outputs = out_data.get("monthly_outputs", [])
    
    # Load rules
    rule_data = load_json(workspace, "data/rules/scoring_rules.json")
    if rule_data is None:
        return None, "Missing scoring_rules.json"
    rules = rule_data.get("scoring_rules", [])
    
    # Build lookup
    rule_by_role = {r["role_code"]: r for r in rules}
    output_by_emp = {o["employee_id"]: o for o in outputs}
    
    expected = []
    for emp in employees:
        eid = emp["employee_id"]
        if eid not in output_by_emp:
            continue
        role_code = emp["role_code"]
        if role_code not in rule_by_role:
            continue
        rule = rule_by_role[role_code]
        out = output_by_emp[eid]
        total = (out["feature_delivery"] * rule["feature_delivery_weight"] +
                 out["quality_score"] * rule["quality_weight"] +
                 out["collaboration_score"] * rule["collaboration_weight"])
        total = round(total, 2)  # keep two decimals
        expected.append({
            "employee_id": eid,
            "employee_name": emp["employee_name"],
            "department": emp["department"],
            "total_score": total
        })
    return expected, None

def check_structure(report):
    # report must be a dict with key "employees" --> list
    if not isinstance(report, dict):
        return False, "Report root is not a dict"
    if "employees" not in report:
        return False, "Missing 'employees' key"
    emps = report["employees"]
    if not isinstance(emps, list):
        return False, "'employees' is not a list"
    for e in emps:
        if not isinstance(e, dict):
            return False, "Employee entry is not a dict"
        for key in ("employee_id", "employee_name", "department", "total_score"):
            if key not in e:
                return False, f"Employee missing field '{key}'"
        if not isinstance(e["total_score"], (int, float)):
            return False, "'total_score' is not numeric"
    return True, ""

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []

    # 1. Check that ops/review/performance_review.json exists
    report_path = os.path.join(workspace, "ops/review/performance_review.json")
    if not os.path.isfile(report_path):
        score_details.append({
            "item": "File existence: ops/review/performance_review.json",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # Early exit – nothing else to check
        final_score = 0
        write_score(workspace, final_score, score_details)
        return
    else:
        score_details.append({
            "item": "File existence: ops/review/performance_review.json",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File exists"
        })

    # 2. Load and validate report structure
    with open(report_path, "r") as f:
        try:
            report = json.load(f)
        except Exception as e:
            score_details.append({
                "item": "JSON parsing",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Invalid JSON: {str(e)}"
            })
            final_score = sum(d["score"] for d in score_details)
            write_score(workspace, final_score, score_details)
            return
    valid, msg = check_structure(report)
    if not valid:
        score_details.append({
            "item": "Report structure correctness",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": msg
        })
        final_score = sum(d["score"] for d in score_details)
        write_score(workspace, final_score, score_details)
        return
    else:
        score_details.append({
            "item": "Report structure correctness",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Valid keys and types"
        })

    # 3. Calculate expected scores
    expected, err = calculate_expected_scores(workspace)
    if err:
        score_details.append({
            "item": "Reference data availability",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": err
        })
        final_score = sum(d["score"] for d in score_details)
        write_score(workspace, final_score, score_details)
        return
    else:
        score_details.append({
            "item": "Reference data availability",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All required source files present"
        })

    # 4. Compare employee entries
    submitted = report["employees"]
    # Build map for easy comparison
    sub_map = {}
    for e in submitted:
        sub_map[e["employee_id"]] = e

    # Count matches
    total_expected = len(expected)
    matches = 0
    missing_ids = []
    wrong_scores = []
    extra_ids = []
    for exp in expected:
        eid = exp["employee_id"]
        if eid not in sub_map:
            missing_ids.append(eid)
            continue
        sub = sub_map[eid]
        # check name and department (optional but good practice)
        if sub.get("employee_name") != exp["employee_name"]:
            wrong_scores.append(f"{eid}: name mismatch")
        elif sub.get("department") != exp["department"]:
            wrong_scores.append(f"{eid}: department mismatch")
        elif abs(sub["total_score"] - exp["total_score"]) > 0.02:
            wrong_scores.append(f"{eid}: score expected {exp['total_score']}, got {sub['total_score']}")
        else:
            matches += 1

    # Check for extra employees (submitted but not expected)
    for eid in sub_map:
        if not any(e["employee_id"] == eid for e in expected):
            extra_ids.append(eid)

    # Scoring: 10 points for base structure, 20 for correct employee coverage, 40 for correct scores
    # Coverage: 20 points if no missing and no extra
    coverage_score = 0
    if not missing_ids and not extra_ids:
        coverage_score = 20
    else:
        coverage_score = max(0, 20 - 5*len(missing_ids) - 5*len(extra_ids))
    score_details.append({
        "item": "Employee set coverage (no missing/extra)",
        "score": coverage_score,
        "max_score": 20,
        "passed": len(missing_ids)==0 and len(extra_ids)==0,
        "reason": f"missing={missing_ids}, extra={extra_ids}"
    })

    # Score accuracy: each correct match 40/len(expected) points, but ensure integer final
    score_accuracy = 0
    if total_expected > 0:
        per_employee = 40 // total_expected  # floor, will distribute remainder
        remainder_pts = 40 - per_employee * total_expected
        score_accuracy = matches * per_employee
        # give remainder to first few matches
        if matches > 0:
            score_accuracy += min(remainder_pts, matches)  # not perfect but fine
    else:
        # If no expected employees (should not happen)
        pass
    score_details.append({
        "item": "Score accuracy per employee",
        "score": score_accuracy,
        "max_score": 40,
        "passed": matches == total_expected,
        "reason": f"correct matches: {matches}/{total_expected}"
    })

    total_score = sum(d["score"] for d in score_details)
    write_score(workspace, total_score, score_details)

def write_score(workspace, total, details):
    score_file = os.path.join(workspace, "workplace_score.json")
    with open(score_file, "w") as f:
        json.dump({"total_score": total, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
