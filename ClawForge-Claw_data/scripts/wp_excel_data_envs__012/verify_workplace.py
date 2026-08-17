import sys
import os
import csv
import json
import math

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def read_csv(path):
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)

details = []
total_score = 0

# 1. Check directory structure (ops folder exists)
ops_path = os.path.join(workspace, "ops")
if os.path.isdir(ops_path):
    details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found ops/ directory"})
    total_score += 10
else:
    details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ directory not found"})

# 2. Check output file exists
csv_path = os.path.join(ops_path, "category_summary.csv")
if os.path.isfile(csv_path):
    details.append({"item": "category_summary.csv exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
    total_score += 10
else:
    details.append({"item": "category_summary.csv exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
    # If file missing, skip remaining checks
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)

# 3. File format: valid CSV with expected columns
try:
    rows = read_csv(csv_path)
except Exception as e:
    details.append({"item": "CSV format validity", "score": 0, "max_score": 10, "passed": False, "reason": f"Failed to parse CSV: {e}"})
    total_score += 0
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)

required_columns = {"category", "total_sales", "total_orders", "avg_order_amount"}
actual_columns = set(rows[0].keys()) if rows else set()
if required_columns.issubset(actual_columns):
    details.append({"item": "CSV columns correct", "score": 10, "max_score": 10, "passed": True, "reason": f"Found columns: {actual_columns}"})
    total_score += 10
else:
    missing = required_columns - actual_columns
    details.append({"item": "CSV columns correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing columns: {missing}"})
    total_score += 0
    # Still continue to check numeric values for present columns

# 4. Numerical correctness – expected values (order-independent)
expected = {
    "Electronics": {"total_sales": 3100.0, "total_orders": 2, "avg_order_amount": 1550.0},
    "Clothing":    {"total_sales": 115.0,  "total_orders": 2, "avg_order_amount": 57.5},
    "Food":        {"total_sales": 12.0,   "total_orders": 1, "avg_order_amount": 12.0},
}

row_dict = {}
for row in rows:
    cat = row.get("category", "").strip()
    if cat:
        try:
            ts = float(row["total_sales"])
            to = int(float(row["total_orders"]))  # allow float but convert to int
            aoa = float(row["avg_order_amount"])
            row_dict[cat] = (ts, to, aoa)
        except (ValueError, KeyError):
            pass

correct_categories = 0
for cat, exp in expected.items():
    if cat in row_dict:
        ts, to, aoa = row_dict[cat]
        if (math.isclose(ts, exp["total_sales"], rel_tol=1e-6) and
            to == exp["total_orders"] and
            math.isclose(aoa, exp["avg_order_amount"], rel_tol=1e-6)):
            correct_categories += 1

# Scoring for cleaning + calculation (70 points total)
# 20 for dedup, 15 for fill missing, 15 for negative removal, 20 for correct aggregation
# But we combine into a single correctness score based on how many categories match.
# Since there are 3 categories, each correct category gives 20 points (60 total for aggregation)
# plus 10 for general cleaning correctness (if at least one category correct)
if correct_categories == 3:
    details.append({"item": "Clean & aggregate correctness", "score": 70, "max_score": 70, "passed": True, "reason": "All categories match expected values"})
    total_score += 70
elif correct_categories == 2:
    details.append({"item": "Clean & aggregate correctness", "score": 45, "max_score": 70, "passed": False, "reason": f"2 out of 3 categories correct"})
    total_score += 45
elif correct_categories == 1:
    details.append({"item": "Clean & aggregate correctness", "score": 20, "max_score": 70, "passed": False, "reason": f"1 out of 3 categories correct"})
    total_score += 20
else:
    details.append({"item": "Clean & aggregate correctness", "score": 0, "max_score": 70, "passed": False, "reason": "No categories match expected values"})

# Build final score (must be 0-100 integer)
final_score = min(int(round(total_score)), 100)
result = {"total_score": final_score, "details": details}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)
