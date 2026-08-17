#!/usr/bin/env python3
"""
Verify the agent's output for task wp_cloud_cost_ledger_env__030.
Checks that output/cost_report_030.json exists, is valid JSON, and contains the correct total_cost.
"""
import sys
import json
import os
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "output", "cost_report_030.json")

    details = []
    total_score = 0
    max_total = 100

    # 1. File existence (10 pts)
    exists = os.path.isfile(report_path)
    details.append({
        "item": "Output file exists",
        "score": 10 if exists else 0,
        "max_score": 10,
        "passed": exists,
        "reason": "File found" if exists else "Missing output/cost_report_030.json"
    })
    if exists:
        total_score += 10

    # 2. Valid JSON (10 pts)
    valid_json = False
    data = None
    if exists:
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            valid_json = True
        except (json.JSONDecodeError, Exception) as e:
            valid_json = False
    details.append({
        "item": "JSON is valid",
        "score": 10 if valid_json else 0,
        "max_score": 10,
        "passed": valid_json,
        "reason": "Parsed successfully" if valid_json else "Invalid JSON content"
    })
    if valid_json:
        total_score += 10

    # 3. Contains total_cost field (20 pts)
    has_total_cost = valid_json and isinstance(data, dict) and "total_cost" in data
    details.append({
        "item": "total_cost field present",
        "score": 20 if has_total_cost else 0,
        "max_score": 20,
        "passed": has_total_cost,
        "reason": "Key found" if has_total_cost else "Missing 'total_cost' key"
    })
    if has_total_cost:
        total_score += 20

    # 4. Correct total_cost value (60 pts) - expected 82.0
    correct_value = False
    if has_total_cost:
        tc = data["total_cost"]
        # Accept both int and float, compare with tolerance
        expected = 82.0
        if isinstance(tc, (int, float)):
            if math.isclose(tc, expected, rel_tol=1e-3):
                correct_value = True
    details.append({
        "item": "total_cost value matches expected (82.0)",
        "score": 60 if correct_value else 0,
        "max_score": 60,
        "passed": correct_value,
        "reason": "Value is 82.0" if correct_value else f"Expected 82.0, got {data.get('total_cost') if valid_json else 'N/A'}"
    })
    if correct_value:
        total_score += 60

    # Write results
    result = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    main()
