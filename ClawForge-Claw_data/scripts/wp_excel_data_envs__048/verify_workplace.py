import sys
import os
import json
import csv
import math

def compute_expected(workspace):
    path = os.path.join(workspace, "data/raw_data/sales_raw.csv")
    seen = set()
    categories = {}
    with open(path, newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row or len(row) < 11:
                continue
            tid = row[0].strip()
            if tid in seen:
                continue
            seen.add(tid)
            amount_str = row[10].strip()
            if amount_str == '':
                continue
            try:
                amount = float(amount_str)
            except:
                continue
            if amount < 0:
                continue
            category = row[4].strip()
            if category not in categories:
                categories[category] = []
            categories[category].append(amount)
    summary = []
    for cat, amounts in sorted(categories.items()):
        total = round(sum(amounts), 2)
        avg = round(total / len(amounts), 2)
        summary.append({"category": cat, "total_sales": total, "average_order": avg})
    return summary

def verify(workspace):
    details = []
    score = 0

    # 1. check reports/summary.json exists
    json_path = os.path.join(workspace, "reports", "summary.json")
    if not os.path.exists(json_path):
        details.append({"item": "reports/summary.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f)
        return
    else:
        details.append({"item": "reports/summary.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File exists"})
        score += 10

    # 2. parse JSON and check basic structure
    try:
        with open(json_path) as f:
            data = json.load(f)
    except:
        details.append({"item": "JSON valid", "score": 0, "max_score": 10, "passed": False, "reason": "Invalid JSON"})
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f)
        return

    if not isinstance(data, dict) or "category_summary" not in data:
        details.append({"item": "Contains category_summary", "score": 0, "max_score": 10, "passed": False, "reason": "Missing 'category_summary' key"})
        total = score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f)
        return
    else:
        details.append({"item": "JSON valid with category_summary", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON with key"})
        score += 10

    cat_list = data["category_summary"]
    if not isinstance(cat_list, list):
        details.append({"item": "category_summary is list", "score": 0, "max_score": 10, "passed": False, "reason": "Not a list"})
        total = score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f)
        return
    else:
        details.append({"item": "category_summary is list", "score": 0, "max_score": 0, "passed": True, "reason": "Is a list"})  # no extra points

    # 3. check each item has required fields
    required_fields = {"category", "total_sales", "average_order"}
    missing_fields = False
    for item in cat_list:
        if not all(f in item for f in required_fields):
            missing_fields = True
            break
    if missing_fields:
        details.append({"item": "All items have required fields", "score": 0, "max_score": 10, "passed": False, "reason": "Missing field(s) in some items"})
    else:
        details.append({"item": "All items have required fields", "score": 10, "max_score": 10, "passed": True, "reason": "Fields present"})
        score += 10

    # 4. compute expected
    expected_summary = compute_expected(workspace)
    expected_dict = {item["category"]: item for item in expected_summary}
    agent_dict = {item["category"]: item for item in cat_list}

    # 5. check category completeness
    expected_cats = set(expected_dict.keys())
    agent_cats = set(agent_dict.keys())
    if expected_cats != agent_cats:
        missing_cats = expected_cats - agent_cats
        extra_cats = agent_cats - expected_cats
        reason = ""
        if missing_cats:
            reason += f"Missing categories: {missing_cats}. "
        if extra_cats:
            reason += f"Extra categories: {extra_cats}. "
        details.append({"item": "Correct categories (no missing/extra)", "score": 0, "max_score": 20, "passed": False, "reason": reason})
    else:
        details.append({"item": "Correct categories (no missing/extra)", "score": 20, "max_score": 20, "passed": True, "reason": "All categories match"})
        score += 20

    # 6. check total_sales values
    sales_ok = True
    for cat, expected in expected_dict.items():
        if cat not in agent_dict:
            sales_ok = False
            break
        actual = agent_dict[cat]["total_sales"]
        if not math.isclose(actual, expected["total_sales"], rel_tol=1e-9):
            sales_ok = False
            break
    if sales_ok:
        details.append({"item": "Total sales values correct", "score": 25, "max_score": 25, "passed": True, "reason": "All totals match"})
        score += 25
    else:
        details.append({"item": "Total sales values correct", "score": 0, "max_score": 25, "passed": False, "reason": "One or more total sales are incorrect"})

    # 7. check average_order values
    avg_ok = True
    for cat, expected in expected_dict.items():
        if cat not in agent_dict:
            avg_ok = False
            break
        actual = agent_dict[cat]["average_order"]
        if not math.isclose(actual, expected["average_order"], rel_tol=1e-9):
            avg_ok = False
            break
    if avg_ok:
        details.append({"item": "Average order values correct", "score": 25, "max_score": 25, "passed": True, "reason": "All averages match"})
        score += 25
    else:
        details.append({"item": "Average order values correct", "score": 0, "max_score": 25, "passed": False, "reason": "One or more average orders are incorrect"})

    total_score = score
    out = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(out, f)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
