import json
import sys
import os
from pathlib import Path

def score_item(name, max_score, condition, reason=""):
    return {
        "item": name,
        "score": max_score if condition else 0,
        "max_score": max_score,
        "passed": condition,
        "reason": reason if not condition else "OK"
    }

def verify():
    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    results = []
    total_score = 0
    max_total = 100

    # 1. File existence (10 pts)
    target_file = workspace / "performance_profiles.json"
    file_exists = target_file.exists()
    results.append(score_item("performance_profiles.json exists", 10, file_exists, "File missing"))
    if not file_exists:
        # early exit because nothing else to check
        total_score = sum(r["score"] for r in results)
        final = {"total_score": total_score, "details": results}
        with open(workspace / "workplace_score.json", "w") as f:
            json.dump(final, f, indent=2)
        return

    # 2. JSON validity (15 pts)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        results.append(score_item("JSON parseable", 15, True))
    except Exception as e:
        results.append(score_item("JSON parseable", 15, False, f"Parse error: {e}"))
        total_score = sum(r["score"] for r in results)
        final = {"total_score": total_score, "details": results}
        with open(workspace / "workplace_score.json", "w") as f:
            json.dump(final, f, indent=2)
        return

    # 3. Top-level structure (10 pts) - must be a list (or dict? we expect list of profiles)
    if isinstance(data, list):
        structure_ok = True
    elif isinstance(data, dict) and "profiles" in data:
        structure_ok = True
        data = data["profiles"]
    else:
        structure_ok = False
    results.append(score_item("Top-level list or dict with 'profiles' key", 10, structure_ok, "Unexpected structure"))

    # 4. Correct number of employees (only E001, E002, E003, E004) (15 pts)
    expected_ids = {"E001", "E002", "E003", "E004"}
    actual_ids = set()
    for entry in data:
        eid = entry.get("employee_id")
        if eid:
            actual_ids.add(eid)
    ids_match = (actual_ids == expected_ids)
    results.append(score_item("Employee ID set correct (E001,E002,E003,E004 only)", 15, ids_match,
                              f"Got {actual_ids}, expected {expected_ids}"))

    # 5. Required fields per entry (10 pts)
    field_errors = []
    for entry in data:
        eid = entry.get("employee_id")
        for field in ["employee_id", "department", "role_code", "scores", "total_score"]:
            if field not in entry:
                field_errors.append(f"{eid} missing {field}")
        scores = entry.get("scores", {})
        for sub in ["feature_delivery", "quality_score", "collaboration_score"]:
            if sub not in scores:
                field_errors.append(f"{eid} missing scores.{sub}")
    fields_ok = len(field_errors) == 0
    results.append(score_item("All required fields present", 10, fields_ok, "; ".join(field_errors[:5])))

    # 6. Numerical correctness (40 pts total, 10 per employee)
    # Precompute expected total scores using only valid rules and clean data
    # Valid rules (from data/rules/scoring_rules.json – the real one, not old)
    rules = {
        "ENG": {"fdw": 0.5, "qw": 0.3, "cw": 0.2},
        "MGR": {"fdw": 0.3, "qw": 0.4, "cw": 0.3},
        "DSG": {"fdw": 0.4, "qw": 0.4, "cw": 0.2}
    }
    # Clean output records: only valid employees, take first occurrence if multiple, require all scores >=0
    # From env_builder: acceptable records (non-negative, distinct employee)
    clean_records = {
        "E001": {"f": 95, "q": 88, "c": 90},   # first positive record
        "E002": {"f": 70, "q": 85, "c": 92},   # first positive (70 vs 85, take 70)
        "E003": {"f": 80, "q": 75, "c": 70},
        "E004": {"f": 60, "q": 50, "c": 40}
    }
    # Employee dept/role from builder
    emp_info = {
        "E001": {"dept": "Engineering", "role": "ENG"},
        "E002": {"dept": "Management", "role": "MGR"},
        "E003": {"dept": "Design", "role": "DSG"},
        "E004": {"dept": "Engineering", "role": "ENG"}
    }
    expected_totals = {}
    for eid, rec in clean_records.items():
        r = emp_info[eid]["role"]
        w = rules[r]
        total = rec["f"]*w["fdw"] + rec["q"]*w["qw"] + rec["c"]*w["cw"]
        expected_totals[eid] = round(total, 2)

    numeric_scores = []
    for entry in data:
        eid = entry.get("employee_id")
        if eid not in expected_totals:
            continue
        actual_total = entry.get("total_score")
        expected = expected_totals[eid]
        # allow floating rounding difference within 0.02
        if actual_total is None or abs(actual_total - expected) > 0.02:
            numeric_scores.append(score_item(f"{eid} total_score", 10, False,
                                             f"Got {actual_total}, expected {expected}"))
        else:
            numeric_scores.append(score_item(f"{eid} total_score", 10, True))

    # sum numeric scores (each employee 10 pts, max 40)
    numeric_score_total = sum(s["score"] for s in numeric_scores)
    # we already counted each employee's check, so we can add them as separate items
    for s in numeric_scores:
        results.append(s)

    # 7. No extra fields in entries (optional bonus deduction) – not scored positively but can deduct
    # We'll check for unexpected top-level keys like "old" etc. but lenient
    # Actually we don't enforce strict schema; just ensure no hidden fields that break scoring

    total_score = sum(r["score"] for r in results)
    final = {"total_score": total_score, "details": results}
    with open(workspace / "workplace_score.json", "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    verify()
