import os
import sys
import json
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    max_total = 100

    # Item 1: performance_review directory exists (5 pts)
    review_dir = os.path.join(workspace, "performance_review")
    dir_ok = os.path.isdir(review_dir)
    details.append({
        "item": "performance_review directory exists",
        "score": 5 if dir_ok else 0,
        "max_score": 5,
        "passed": dir_ok,
        "reason": "Directory found" if dir_ok else "Directory missing"
    })
    if dir_ok:
        total_score += 5

    # Item 2: monthly_scores.json exists (5 pts)
    scores_path = os.path.join(review_dir, "monthly_scores.json")
    file_ok = os.path.isfile(scores_path)
    details.append({
        "item": "monthly_scores.json exists",
        "score": 5 if file_ok else 0,
        "max_score": 5,
        "passed": file_ok,
        "reason": "File found" if file_ok else "File missing"
    })
    if file_ok:
        total_score += 5

    # Item 3: JSON format is a list (10 pts)
    records = None
    format_ok = False
    if file_ok:
        try:
            with open(scores_path, "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                format_ok = True
                records = data
        except Exception:
            pass
    details.append({
        "item": "JSON is a list of records",
        "score": 10 if format_ok else 0,
        "max_score": 10,
        "passed": format_ok,
        "reason": "Valid list" if format_ok else "Not a list or parse error"
    })
    if format_ok:
        total_score += 10

    # Prepare expected data
    expected_ids = {"E001", "E002"}
    expected_scores = {"E001": 81.0, "E002": 68.0}  # computed from weights

    found_ids = set()
    score_map = {}
    count_ok = False
    ids_ok = False
    e001_ok = False
    e002_ok = False

    if format_ok:
        # Count check (20 pts)
        count_ok = len(records) == 2
        details.append({
            "item": "Exactly 2 records",
            "score": 20 if count_ok else 0,
            "max_score": 20,
            "passed": count_ok,
            "reason": f"Found {len(records)} record(s)" if not count_ok else "Correct count"
        })
        if count_ok:
            total_score += 20

        # Extract employee_id and total_score
        for rec in records:
            if not isinstance(rec, dict):
                continue
            eid = rec.get("employee_id")
            score = rec.get("total_score")
            if eid is None or score is None:
                continue
            try:
                score = float(score)
            except (ValueError, TypeError):
                continue
            found_ids.add(eid)
            score_map[eid] = score

        # ID set check (20 pts)
        ids_ok = found_ids == expected_ids
        details.append({
            "item": "Employee IDs match expected (E001, E002)",
            "score": 20 if ids_ok else 0,
            "max_score": 20,
            "passed": ids_ok,
            "reason": f"IDs found: {found_ids}" if not ids_ok else "IDs correct"
        })
        if ids_ok:
            total_score += 20

        # Score correctness for E001 (20 pts)
        if "E001" in score_map:
            e001_ok = math.isclose(score_map["E001"], expected_scores["E001"], rel_tol=1e-9)
        details.append({
            "item": "E001 total_score correct (81.0)",
            "score": 20 if e001_ok else 0,
            "max_score": 20,
            "passed": e001_ok,
            "reason": f"Got {score_map.get('E001', 'N/A')}" if not e001_ok else "Correct"
        })
        if e001_ok:
            total_score += 20

        # Score correctness for E002 (20 pts)
        if "E002" in score_map:
            e002_ok = math.isclose(score_map["E002"], expected_scores["E002"], rel_tol=1e-9)
        details.append({
            "item": "E002 total_score correct (68.0)",
            "score": 20 if e002_ok else 0,
            "max_score": 20,
            "passed": e002_ok,
            "reason": f"Got {score_map.get('E002', 'N/A')}" if not e002_ok else "Correct"
        })
        if e002_ok:
            total_score += 20

    else:
        # Assign zero for remaining items when format is invalid
        for item_name in ["Exactly 2 records", "Employee IDs match", "E001 score correct", "E002 score correct"]:
            details.append({
                "item": item_name,
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "Format invalid, cannot verify"
            })

    # Cap total to 100
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": details
    }
    result_path = os.path.join(workspace, "workplace_score.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
