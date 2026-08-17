"""
Verify the generated quarterly report.
Expected: report/quarterly_report.md contains a Markdown table with:
- Customer Revenue total = 159000
- Product Units Sold total = 1990
- Ops Downtime Minutes average = 24.93 (rounded to 2 decimals)
Dirty data (NULL, empty, non-numeric) must be ignored.
Score: 100 total.
"""
import os
import sys
import json
import re
import csv
from decimal import Decimal, ROUND_HALF_UP

def parse_value_from_line(line, expected_label):
    """
    Try to extract numeric value from a Markdown table row like '| Customer | revenue | 159000 |'
    or '| Customer Revenue | 159000 |'. Flexible pattern.
    """
    # Split by '|' and strip
    parts = [p.strip() for p in line.split('|') if p.strip() != '']
    # We expect 3 parts: label, metric, value OR 2 parts: combined label, value
    for p in parts:
        if expected_label.lower() in p.lower():
            # Look for a number in the same row (next part or previous)
            pass
    # Simple approach: find all numbers in the line
    numbers = re.findall(r'[-+]?\d*\.?\d+', line)
    if numbers:
        # Return the last number as the value (assuming label precedes number)
        return numbers[-1]
    return None

def verify(workspace):
    details = []
    total_score = 0
    max_total = 100

    # 1. Check directory structure (prompt mentions data/ledgers/ and report/)
    report_path = os.path.join(workspace, "report", "quarterly_report.md")
    if os.path.isfile(report_path):
        details.append({
            "item": "Report file exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "report/quarterly_report.md found"
        })
        total_score += 5
    else:
        details.append({
            "item": "Report file exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "report/quarterly_report.md not found"
        })
        # If report missing, we cannot continue further meaningful checks
        details.append({
            "item": "Content verification (skipped due to missing report)",
            "score": 0,
            "max_score": 95,
            "passed": False,
            "reason": "Report file missing"
        })
        total_score = 0
        # Write partial result
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 2. Read report content
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 3. Check report is valid Markdown (contains at least one table or heading)
    if '|' in content or content.startswith('#'):
        details.append({
            "item": "Report contains table or heading",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Markdown structure detected"
        })
        total_score += 5
    else:
        details.append({
            "item": "Report contains table or heading",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "No table or heading found"
        })

    # 4. Pre-calculate ground truth values from the original data (simulate agent's calculation)
    # We'll compute manually based on env_builder's clean data (ignoring dirty rows)
    customer_revenue_total = 125000 + 34000   # = 159000
    product_units_total = 890 + 1100          # = 1990
    ops_downtime_avg = (34.5 + 12.0 + 28.3) / 3  # = 24.93333... -> round to 2 decimals: 24.93
    ops_downtime_avg_rounded = round(ops_downtime_avg, 2)

    # 5. Extract values from report using pattern matching
    # We'll search for lines that likely contain the numbers.
    lines = content.split('\n')
    found_customer = None
    found_product = None
    found_ops = None

    # Define search patterns (case insensitive)
    patterns = {
        'customer': ['customer revenue', 'customer', 'revenue'],
        'product': ['product units', 'product', 'units sold', 'units_sold'],
        'ops': ['downtime', 'ops', 'downtime minutes']
    }

    for line in lines:
        line_lower = line.lower()
        # Try to find numbers
        numbers_in_line = re.findall(r'[-+]?\d+\.?\d*', line)
        if not numbers_in_line:
            continue
        # Use last number as assumed value
        value = numbers_in_line[-1]

        # Check which category this line matches
        if any(pat in line_lower for pat in patterns['customer']):
            try:
                found_customer = float(value.replace(',', ''))
            except:
                continue
        if any(pat in line_lower for pat in patterns['product']):
            try:
                found_product = float(value.replace(',', ''))
            except:
                continue
        if any(pat in line_lower for pat in patterns['ops']):
            try:
                found_ops = float(value.replace(',', ''))
            except:
                continue

    # 6. Compare extracted values with ground truth (allow small floating tolerance)
    tolerance = 0.01

    def compare(expected, found, name, weight):
        nonlocal total_score
        if found is None:
            details.append({
                "item": f"{name} value found in report",
                "score": 0,
                "max_score": weight,
                "passed": False,
                "reason": f"Could not extract {name} value from report"
            })
            return
        if abs(found - expected) <= tolerance:
            details.append({
                "item": f"{name} value correct",
                "score": weight,
                "max_score": weight,
                "passed": True,
                "reason": f"Expected {expected}, found {found}"
            })
            total_score += weight
        else:
            details.append({
                "item": f"{name} value correct",
                "score": 0,
                "max_score": weight,
                "passed": False,
                "reason": f"Expected {expected}, found {found}, difference {abs(found-expected)}"
            })

    compare(159000, found_customer, "Customer Revenue", 30)
    compare(1990, found_product, "Product Units Sold", 30)
    compare(24.93, found_ops, "Ops Downtime Average", 25)

    # 7. Bonus: check that dirty data was ignored (no NaN or invalid in report)
    # We can't directly verify, but no negative scoring.

    # Ensure total score is integer between 0 and 100
    total_score = min(int(total_score), 100)

    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
