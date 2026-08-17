#!/usr/bin/env python3
"""verify_workplace.py – code-only evaluation of the generated quarterly report."""
import sys
import os
import csv
import json
import re
from pathlib import Path
from collections import defaultdict

EXPECTED_GRAND_TOTAL = 8944  # computed from ground truth data after dedup & cleaning

def load_ledgers(workspace):
    """Parse all CSV ledgers, filter 2024-Q4, deduplicate, return list of (metric_code, value)."""
    records = []
    seen = set()
    ledger_dir = os.path.join(workspace, "data/ledgers")
    for fname in os.listdir(ledger_dir):
        if not fname.endswith(".csv"):
            continue
        fpath = os.path.join(ledger_dir, fname)
        with open(fpath, newline="") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header is None:
                continue
            # validate header
            if len(header) < 3 or header[0].strip().lower() != "period":
                continue
            for row in reader:
                # skip malformed: must have exactly 3 fields, period and metric_code not empty
                if len(row) != 3:
                    continue
                period, code, val_str = [x.strip() for x in row]
                if not period or not code:
                    continue
                if period != "2024-Q4":
                    continue
                try:
                    value = int(val_str)
                except ValueError:
                    continue
                # dedup by (period, code, value) — note: duplicate rows are exact copies
                key = (period, code, value)
                if key in seen:
                    continue
                seen.add(key)
                records.append((code, value))
    return records

def extract_report_data(report_path):
    """Parse the Markdown report and extract metric totals from the table, plus grand total.""" 
    with open(report_path) as f:
        content = f.read()
    
    # Extract table rows (assuming simple Markdown table with | delimiters)
    lines = content.splitlines()
    table_started = False
    metric_totals = []
    grand_total = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and "Metric Code" in stripped:
            table_started = True
            continue
        if table_started:
            # skip header separator (e.g., |---|---|---|)
            if re.match(r'^\|[\s\-:]+\|', stripped):
                continue
            if not stripped.startswith("|"):
                break  # table ended
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if not cells:
                continue
            if cells[0].lower() == "grand total":
                try:
                    grand_total = int(cells[-1].replace(",", ""))
                except ValueError:
                    pass
                break
            if len(cells) >= 2:
                try:
                    metric_totals.append((cells[0], int(cells[-1].replace(",", ""))))
                except ValueError:
                    pass
    return metric_totals, grand_total

def evaluate(workspace):
    details = []
    score = 0

    # 1. Check report file exists (10 points)
    report_path = os.path.join(workspace, "reports", "quarterly_review.md")
    if os.path.isfile(report_path):
        details.append({
            "item": "report file exists at reports/quarterly_review.md",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found."
        })
        score += 10
    else:
        details.append({
            "item": "report file exists at reports/quarterly_review.md",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found."
        })
        # Cannot continue, but we still report partial
        _write_score(workspace, score, details)
        return

    # 2. Check file is valid Markdown (has some headers or table) (10 points)
    with open(report_path) as f:
        content = f.read()
    has_header = bool(re.search(r'^#', content, re.MULTILINE))
    has_table = bool(re.search(r'\|.*\|', content))
    if has_header and has_table:
        details.append({
            "item": "report is valid Markdown with headers and a table",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Contains Markdown headers and table."
        })
        score += 10
    else:
        details.append({
            "item": "report is valid Markdown with headers and a table",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Missing headers={has_header}, table={has_table}."
        })

    # 3. Extract and validate metric totals against ground truth (50 points)
    metrics, grand_total = extract_report_data(report_path)
    # Build ground truth from actual ledger data (re-run same logic)
    true_records = load_ledgers(workspace)
    true_agg = defaultdict(int)
    for code, val in true_records:
        true_agg[code] += val
    true_grand = sum(true_agg.values())

    # Check that all metrics in ground truth appear in report (order not important)
    metric_matches = 0
    for code, true_val in true_agg.items():
        for rep_code, rep_val in metrics:
            if rep_code == code and rep_val == true_val:
                metric_matches += 1
                break
    total_metrics = len(true_agg)
    if metric_matches == total_metrics:
        details.append({
            "item": "metric totals match ground truth",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"All {total_metrics} metric codes have correct total values."
        })
        score += 30
    else:
        details.append({
            "item": "metric totals match ground truth",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"Only {metric_matches}/{total_metrics} metric codes matched correctly."
        })

    # Grand total check (20 points)
    if grand_total == true_grand:
        details.append({
            "item": "grand total matches ground truth",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"Grand total is {grand_total}, expected {true_grand}."
        })
        score += 20
    else:
        details.append({
            "item": "grand total matches ground truth",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Grand total is {grand_total}, expected {true_grand}."
        })

    # 4. Bonus: ensure table has no extra/missing codes (10 points) – optional but nice
    # Actually we already did metric_matches; we can also check no extra codes.
    rep_codes = {c for c,_ in metrics}
    true_codes = set(true_agg.keys())
    if rep_codes == true_codes:
        details.append({
            "item": "no extra or missing metric codes in table",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Report only contains expected metric codes."
        })
        score += 10
    else:
        extra = rep_codes - true_codes
        missing = true_codes - rep_codes
        details.append({
            "item": "no extra or missing metric codes in table",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Extra codes: {extra}, missing: {missing}."
        })

    # Total out of 80? Actually max so far: 10+10+30+20+10 = 80, we have 20 remaining for structure? Let's adjust.
    # We'll make it out of 100 by adding a check for directory structure (10) and for correct dedup (10).
    # Actually we already did many. Let's add a check for no disallowed directories? Not needed.
    # Add a check that the report does not include non-2024-Q4 data (10 points)
    # Use simple string check
    if "2024-Q3" not in content and "2025-Q1" not in content:
        details.append({
            "item": "report contains no data from other periods",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "No other periods found."
        })
        score += 10
    else:
        details.append({
            "item": "report contains no data from other periods",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Contains references to Q3 2024 or Q1 2025."
        })

    # Final score cap at 100
    total_score = min(score, 100)
    _write_score(workspace, total_score, details)

def _write_score(workspace, total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    evaluate(workspace)
