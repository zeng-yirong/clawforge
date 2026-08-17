import os
import sys
import json
import csv

def verify(workspace):
    score = 0
    details = []
    total_max = 100

    # 1) Directory structure (10 points)
    report_dir = os.path.join(workspace, "report")
    if os.path.isdir(report_dir):
        details.append({
            "item": "report directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "report/ directory found"
        })
        score += 10
    else:
        details.append({
            "item": "report directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "report/ directory not found"
        })

    # 2) product_summary.json exists and is valid JSON (10 points)
    summary_path = os.path.join(report_dir, "product_summary.json")
    if not os.path.isfile(summary_path):
        details.append({
            "item": "product_summary.json file exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "file not found"
        })
        # Cannot continue further checks
        details.append({
            "item": "JSON is valid and format correct",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "file missing"
        })
        details.append({
            "item": "Correct keys and values",
            "score": 0,
            "max_score": 70,
            "passed": False,
            "reason": "file missing, cannot validate"
        })
        write_score(workspace, score, details)
        return

    try:
        with open(summary_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "product_summary.json file exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "file exists but may be invalid JSON"
        })
        details.append({
            "item": "JSON is valid and format correct",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        details.append({
            "item": "Correct keys and values",
            "score": 0,
            "max_score": 70,
            "passed": False,
            "reason": "JSON invalid"
        })
        write_score(workspace, score, details)
        return

    details.append({
        "item": "product_summary.json file exists",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "file exists"
    })

    # 3) JSON is a valid object (not list) with expected keys (10 points)
    if isinstance(data, dict) and len(data) > 0:
        details.append({
            "item": "JSON is valid and format correct",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON is a non-empty dictionary"
        })
        score += 10
    else:
        details.append({
            "item": "JSON is valid and format correct",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Expected a dictionary object, got {}".format(type(data).__name__)
        })
        # Still can try to check if data is something else

    # 4) Correct categories and values (70 points total)
    # First compute expected answer from input data
    expected = compute_expected(workspace)
    if expected is None:
        details.append({
            "item": "Correct keys and values",
            "score": 0,
            "max_score": 70,
            "passed": False,
            "reason": "Could not compute expected from source"
        })
        write_score(workspace, score, details)
        return

    # Compare
    max_category_score = 70 // len(expected) if expected else 70
    category_total = 0
    category_max = 70
    for cat, expected_sum in expected.items():
        if cat in data:
            actual = data[cat]
            if isinstance(actual, (int, float)):
                if abs(actual - expected_sum) < 0.001:
                    category_total += max_category_score
                else:
                    # partial credit if close? we give 0 for simplicity
                    pass
            # else: wrong type
        # missing key: no points

    # check for extra categories (should not have anything else)
    extra_keys = set(data.keys()) - set(expected.keys())
    if extra_keys:
        # penalize: lose all category points? or deduct part. Let's deduct 5 per extra
        penalty = len(extra_keys) * 5
        category_total = max(0, category_total - penalty)

    # Also ensure no missing required categories (penalty already captured)
    missing_keys = set(expected.keys()) - set(data.keys())
    # missing keys already gave 0 points for those categories

    # Cap at max
    category_total = min(category_total, category_max)
    passed = category_total >= (category_max * 0.8)  # 80% correct
    details.append({
        "item": "Correct keys and values",
        "score": category_total,
        "max_score": category_max,
        "passed": passed,
        "reason": f"Matched {category_total}/{category_max} points. Expected keys: {list(expected.keys())}, got: {list(data.keys())}"
    })
    score += category_total

    write_score(workspace, score, details)


def compute_expected(workspace):
    """Read the raw CSV, apply exact dedup, fill empty names, remove junk, then aggregate."""
    csv_path = os.path.join(workspace, "data", "sales_raw.csv")
    if not os.path.isfile(csv_path):
        return None

    # Read all rows preserving order
    rows = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # 1) Deduplicate by transaction_id, keep first occurrence
    seen = set()
    deduped = []
    for r in rows:
        tid = r["transaction_id"]
        if tid not in seen:
            seen.add(tid)
            deduped.append(r)

    # 2) Fill missing product_name from other rows with same product_id
    # Build a mapping from product_id -> first non-empty product_name
    name_map = {}
    for r in deduped:
        pid = r["product_id"]
        pn = r["product_name"].strip()
        if pn and pid not in name_map:
            name_map[pid] = pn

    for r in deduped:
        if not r["product_name"].strip() and r["product_id"] in name_map:
            r["product_name"] = name_map[r["product_id"]]

    # 3) Drop junk: sales_amount <= 0 or quantity <= 0
    valid = []
    for r in deduped:
        try:
            amt = float(r["sales_amount"])
            qty = int(r["quantity"])
        except (ValueError, TypeError):
            continue
        if amt > 0 and qty > 0:
            valid.append(r)

    # 4) Group by category and sum sales_amount
    aggregation = {}
    for r in valid:
        cat = r["category"]
        amt = float(r["sales_amount"])
        aggregation[cat] = aggregation.get(cat, 0.0) + amt

    # Round to 2 decimals (match typical precision)
    for k in aggregation:
        aggregation[k] = round(aggregation[k], 2)

    return aggregation


def write_score(workspace, total, details):
    result = {
        "total_score": total,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    ws = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(ws)
