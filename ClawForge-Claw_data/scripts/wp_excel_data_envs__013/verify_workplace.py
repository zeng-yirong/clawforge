import json
import os
import sys
import math
from pathlib import Path

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
workspace = Path(workspace)

score_details = []
total_score = 0

def check(condition, item_name, max_score, details, passed_reason, fail_reason=""):
    global total_score
    if condition:
        total_score += max_score
        details.append({
            "item": item_name,
            "score": max_score,
            "max_score": max_score,
            "passed": True,
            "reason": passed_reason
        })
    else:
        details.append({
            "item": item_name,
            "score": 0,
            "max_score": max_score,
            "passed": False,
            "reason": fail_reason
        })

# 1. Check ops/report.json exists
report_path = workspace / "ops" / "report.json"
check(report_path.is_file(), "ops/report.json exists", 5, score_details, "File present", "File not found")

# 2. Check JSON is valid
data = None
if report_path.is_file():
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        check(True, "JSON format valid", 5, score_details, "Valid JSON", "")
    except (json.JSONDecodeError, Exception) as e:
        check(False, "JSON format valid", 5, score_details, "", f"Invalid JSON: {e}")
else:
    check(False, "JSON format valid", 5, score_details, "", "File missing – cannot check JSON")

# Expected values
EXPECTED_TOTAL_SALES = 3600.0
EXPECTED_TOTAL_ORDERS = 8
EXPECTED_AVG_ORDER = 450.0
EXPECTED_REGION_SALES = {"North": 600.0, "South": 800.0, "East": 1000.0, "West": 1200.0}

if data is not None:
    # 3. total_sales
    ts = data.get("total_sales")
    if isinstance(ts, (int, float)):
        check(math.isclose(ts, EXPECTED_TOTAL_SALES, rel_tol=1e-9), "total_sales is correct", 20, score_details,
              f"Value {ts} equals expected {EXPECTED_TOTAL_SALES}",
              f"Value {ts} != expected {EXPECTED_TOTAL_SALES}")
    else:
        check(False, "total_sales is correct", 20, score_details, "", "Missing or not numeric")

    # 4. total_orders
    to_ = data.get("total_orders")
    if isinstance(to_, int):
        check(to_ == EXPECTED_TOTAL_ORDERS, "total_orders is correct", 20, score_details,
              f"Value {to_} equals expected {EXPECTED_TOTAL_ORDERS}",
              f"Value {to_} != expected {EXPECTED_TOTAL_ORDERS}")
    else:
        check(False, "total_orders is correct", 20, score_details, "", "Missing or not integer")

    # 5. average_order_value
    avg = data.get("average_order_value")
    if isinstance(avg, (int, float)):
        check(math.isclose(avg, EXPECTED_AVG_ORDER, rel_tol=1e-9), "average_order_value is correct", 20, score_details,
              f"Value {avg} equals expected {EXPECTED_AVG_ORDER}",
              f"Value {avg} != expected {EXPECTED_AVG_ORDER}")
    else:
        check(False, "average_order_value is correct", 20, score_details, "", "Missing or not numeric")

    # 6. region_sales (4 sub-items)
    rs = data.get("region_sales")
    if isinstance(rs, dict):
        for region, expected_val in EXPECTED_REGION_SALES.items():
            actual_val = rs.get(region)
            if isinstance(actual_val, (int, float)):
                check(math.isclose(actual_val, expected_val, rel_tol=1e-9),
                      f"region_sales['{region}'] is correct", 5, score_details,
                      f"Value {actual_val} equals expected {expected_val}",
                      f"Value {actual_val} != expected {expected_val}")
            else:
                check(False, f"region_sales['{region}'] is correct", 5, score_details, "",
                      f"Missing or not numeric for region {region}")
    else:
        check(False, "region_sales is a dict", 20, score_details, "", "Missing or not a dict")

    # 7. missing_category_handled
    mch = data.get("missing_category_handled")
    check(mch is True, "missing_category_handled is true", 10, score_details,
          "Field present and true",
          f"Missing or not true (got {mch})")
else:
    # If data is None, all subsequent checks fail
    check(False, "total_sales is correct", 20, score_details, "", "No data")
    check(False, "total_orders is correct", 20, score_details, "", "No data")
    check(False, "average_order_value is correct", 20, score_details, "", "No data")
    check(False, "region_sales is a dict", 20, score_details, "", "No data")
    check(False, "missing_category_handled is true", 10, score_details, "", "No data")

# Write result
result = {
    "total_score": total_score,
    "details": score_details
}
with open(workspace / "workplace_score.json", "w") as f:
    json.dump(result, f, indent=2)

print(f"Verification complete. Total score: {total_score}/100")
