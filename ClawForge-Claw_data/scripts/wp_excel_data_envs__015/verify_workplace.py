#!/usr/bin/env python3
import csv
import json
import math
import os
import sys

def compute_expected_result(workspace):
    """Compute expected average per category from the original CSV after dedup and missing removal."""
    csv_path = os.path.join(workspace, "data/raw_data/sales_raw.csv")
    if not os.path.isfile(csv_path):
        return None, "missing raw data file"

    with open(csv_path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        # find column indices
        try:
            cat_idx = header.index("category")
            amt_idx = header.index("sales_amount")
        except ValueError:
            return None, "missing required columns in raw data"

        rows = list(reader)
        # Deduplicate by complete row (tuple)
        seen = set()
        clean_rows = []
        for row in rows:
            tup = tuple(row)
            if tup not in seen:
                seen.add(tup)
                # Remove rows where sales_amount is empty or not convertible
                raw_amt = row[amt_idx].strip()
                if raw_amt == "":
                    continue
                try:
                    float(raw_amt)
                except ValueError:
                    continue
                clean_rows.append(row)

    # Group by category and compute average
    sums = {}
    counts = {}
    for row in clean_rows:
        cat = row[cat_idx]
        amt = float(row[amt_idx])
        sums[cat] = sums.get(cat, 0.0) + amt
        counts[cat] = counts.get(cat, 0) + 1

    expected = {}
    for cat in sorted(sums.keys()):
        expected[cat] = round(sums[cat] / counts[cat], 2) if counts[cat] > 0 else 0.0
    return expected, None

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result_path = os.path.join(workspace, "ops/average_order.json")

    details = []
    total_score = 0

    # 1. Check ops directory exists
    ops_dir = os.path.join(workspace, "ops")
    exists_ops = os.path.isdir(ops_dir)
    details.append({
        "item": "ops directory exists",
        "score": 10 if exists_ops else 0,
        "max_score": 10,
        "passed": exists_ops,
        "reason": "ops directory found" if exists_ops else "ops directory missing"
    })
    if exists_ops:
        total_score += 10

    # 2. Check average_order.json exists
    exists_file = os.path.isfile(result_path)
    details.append({
        "item": "average_order.json exists",
        "score": 10 if exists_file else 0,
        "max_score": 10,
        "passed": exists_file,
        "reason": "file found" if exists_file else "file missing"
    })
    if exists_file:
        total_score += 10

    # 3. Parse JSON and validate structure
    if exists_file:
        try:
            with open(result_path) as f:
                result = json.load(f)
            if not isinstance(result, dict):
                raise ValueError("result is not a dict")
            # All values should be numbers
            for k, v in result.items():
                if not isinstance(v, (int, float)):
                    raise ValueError(f"value for {k} is not number: {v}")
            valid_json = True
            json_reason = "valid JSON dict with numeric values"
        except Exception as e:
            valid_json = False
            json_reason = f"invalid JSON or structure: {e}"
    else:
        valid_json = False
        json_reason = "file not found, cannot parse"

    details.append({
        "item": "JSON format and structure",
        "score": 10 if valid_json else 0,
        "max_score": 10,
        "passed": valid_json,
        "reason": json_reason
    })
    if valid_json:
        total_score += 10

    # 4. Compute expected result
    expected, err = compute_expected_result(workspace)
    if err:
        details.append({
            "item": "computed expected result",
            "score": 0,
            "max_score": 0,  # skip if raw data missing
            "passed": False,
            "reason": f"cannot compute expected result: {err}"
        })
        # No further scoring possible, but we already gave points for file existence etc.
        # Write score and exit
        final_score = total_score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": details}, f, indent=2)
        sys.exit(0)

    # 5. Check keys match exactly (all expected categories present, no extra)
    expected_keys = set(expected.keys())
    result_keys = set(result.keys()) if valid_json else set()
    keys_correct = (result_keys == expected_keys)
    details.append({
        "item": "category keys match expected",
        "score": 20 if keys_correct else 0,
        "max_score": 20,
        "passed": keys_correct,
        "reason": f"expected keys {expected_keys}, got {result_keys}" if not keys_correct else "keys match"
    })
    if keys_correct:
        total_score += 20

    # 6. Compare numeric values
    if valid_json and expected_keys and keys_correct:
        numeric_score = 0
        numeric_max = 50  # 10 per category, 5 categories
        per_cat_max = 10
        cat_errors = []
        for cat in expected_keys:
            exp_val = expected[cat]
            got_val = result[cat]
            if math.isclose(exp_val, got_val, rel_tol=1e-5):
                numeric_score += per_cat_max
            else:
                cat_errors.append(f"{cat}: expected {exp_val}, got {got_val}")
        passed_numeric = numeric_score == numeric_max
        details.append({
            "item": "average values correctness",
            "score": numeric_score,
            "max_score": numeric_max,
            "passed": passed_numeric,
            "reason": "; ".join(cat_errors) if cat_errors else "all values correct"
        })
        total_score += numeric_score
    else:
        details.append({
            "item": "average values correctness",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": "skipped due to earlier failures"
        })

    # Write final score
    final_score = total_score
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": final_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
