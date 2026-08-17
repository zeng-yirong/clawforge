#!/usr/bin/env python3
"""Verify the generated Q1 2024 summary Markdown report."""
import sys
import os
import csv
import json
import re
from pathlib import Path

def load_ledger_csv(path):
    """Load a valid CSV ledger and return list of rows."""
    rows = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        # Check required column names
        if 'period' not in reader.fieldnames or 'metric_code' not in reader.fieldnames or 'metric_value' not in reader.fieldnames:
            return None  # invalid header
        for row in reader:
            if row['period'] and row['metric_code'] and row['metric_value']:
                try:
                    val = float(row['metric_value'])
                    rows.append((row['period'], row['metric_code'], val))
                except ValueError:
                    pass
    return rows if rows else None

def compute_expected(workspace):
    """Read the three correct ledgers and aggregate metric_value for period=2024-Q1."""
    expected = {}
    correct_files = [
        "data/ledgers/customer_ledger.csv",
        "data/ledgers/ops_ledger.csv",
        "data/ledgers/product_ledger.csv"
    ]
    for rel_path in correct_files:
        full_path = os.path.join(workspace, rel_path)
        if not os.path.isfile(full_path):
            continue
        rows = load_ledger_csv(full_path)
        if rows is None:
            continue
        for period, code, val in rows:
            if period == "2024-Q1":
                expected[code] = expected.get(code, 0.0) + val
    return expected

def parse_report(workspace):
    """Parse agent's Markdown report and extract metric_code->value mapping."""
    report_path = os.path.join(workspace, "reports", "Q1_2024_summary.md")
    if not os.path.isfile(report_path):
        return None, "Report file not found"
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Check basic Markdown structure: must contain ## headings and list items
    headings = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
    if len(headings) < 3:
        return None, "Report does not contain at least three ## sections"
    # Extract all list items: - metric_code: value
    items = re.findall(r'^\s*-\s+([\w_]+)\s*:\s*([\d.]+)\s*$', content, re.MULTILINE)
    if not items:
        return None, "No metric list items found in report"
    metrics = {}
    for code, val_str in items:
        try:
            metrics[code] = float(val_str)
        except ValueError:
            pass
    return metrics, content

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."

    details = []
    total_score = 0

    # 1. Check that 'reports/' directory exists (5 pts)
    reports_dir = os.path.join(workspace, "reports")
    if os.path.isdir(reports_dir):
        details.append({"item": "reports directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "Directory present"})
        total_score += 5
    else:
        details.append({"item": "reports directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "Directory missing"})

    # 2. Check report file exists (10 pts)
    report_file = os.path.join(reports_dir, "Q1_2024_summary.md")
    if os.path.isfile(report_file):
        details.append({"item": "Q1_2024_summary.md exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
        total_score += 10
    else:
        details.append({"item": "Q1_2024_summary.md exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # No need to continue if file missing
        print(json.dumps({"total_score": total_score, "details": details}))
        sys.exit(0)

    # 3. Compute expected metrics from ledger files (ground truth)
    expected = compute_expected(workspace)
    if not expected:
        details.append({"item": "expected metrics computation", "score": 0, "max_score": 10, "passed": False, "reason": "Could not compute expected values from ledgers"})
        total_score += 0
    else:
        details.append({"item": "expected metrics computed", "score": 10, "max_score": 10, "passed": True, "reason": f"Found {len(expected)} metrics"})
        total_score += 10

    # 4. Parse report
    parse_result = parse_report(workspace)
    if parse_result[0] is None:
        details.append({"item": "report parsing", "score": 0, "max_score": 15, "passed": False, "reason": parse_result[1]})
        total_score += 0
        # Still output partial result
        print(json.dumps({"total_score": total_score, "details": details}))
        sys.exit(0)
    else:
        reported_metrics, content = parse_result
        # Check for at least one ## section heading (bonus, already implied)
        details.append({"item": "report parseable with metric items", "score": 15, "max_score": 15, "passed": True, "reason": f"Found {len(reported_metrics)} metrics in report"})
        total_score += 15

    # 5. Compare each metric value (60 pts total, spread across metrics)
    metric_score_per_item = 60 // len(expected) if expected else 0
    metric_remainder = 60 % len(expected) if expected else 0
    all_metrics_correct = True
    matched_count = 0
    for code, exp_val in expected.items():
        if code in reported_metrics:
            rep_val = reported_metrics[code]
            # Allow tiny floating tolerance
            if abs(rep_val - exp_val) < 0.001:
                matched_count += 1
                continue
        # else missing or wrong
        all_metrics_correct = False
    # Scoring: each correct metric gets share of 60, but cap at 60
    if expected:
        score_for_metrics = int((matched_count / len(expected)) * 60)
    else:
        score_for_metrics = 0
    details.append({
        "item": "metric values correctness",
        "score": score_for_metrics,
        "max_score": 60,
        "passed": all_metrics_correct,
        "reason": f"Matched {matched_count} out of {len(expected)} metrics correctly"
    })
    total_score += score_for_metrics

    # Ensure total is integer 0-100
    total_score = min(max(total_score, 0), 100)

    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
