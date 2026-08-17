import sys
import os
import json
import csv
import math

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
os.chdir(workspace)

score_details = []
total_score = 0

def check(condition, item, score, max_score, reason=""):
    passed = bool(condition)
    score_details.append({
        "item": item,
        "score": score if passed else 0,
        "max_score": max_score,
        "passed": passed,
        "reason": reason if not passed else ""
    })
    return passed

# 1. Check reports directory exists (10 points)
dir_ok = check(os.path.isdir("reports"), "Directory 'reports' exists", 10, 10, "Missing reports/ directory")

# 2. Check files exist (15 each = 30)
region_file = "reports/region_summary.json"
susp_file = "reports/suspicious.json"
region_exists = check(os.path.isfile(region_file), "File 'reports/region_summary.json' exists", 15, 15, "File not found")
susp_exists = check(os.path.isfile(susp_file), "File 'reports/suspicious.json' exists", 15, 15, "File not found")

# 3. Parse JSONs (10 each = 20)
region_data = None
susp_data = None
if region_exists:
    try:
        with open(region_file) as f:
            region_data = json.load(f)
        region_valid = check(True, "region_summary.json is valid JSON", 10, 10, "")
    except:
        region_valid = check(False, "region_summary.json is valid JSON", 0, 10, "Invalid JSON")
else:
    region_valid = check(False, "region_summary.json is valid JSON", 0, 10, "File missing")

if susp_exists:
    try:
        with open(susp_file) as f:
            susp_data = json.load(f)
        susp_valid = check(True, "suspicious.json is valid JSON", 10, 10, "")
    except:
        susp_valid = check(False, "suspicious.json is valid JSON", 0, 10, "Invalid JSON")
else:
    susp_valid = check(False, "suspicious.json is valid JSON", 0, 10, "File missing")

# 4. Load original raw data to compute expected values (only if files exist, but we have them by design)
#    We'll compute expected region summary based on ground truth logic.
def compute_expected():
    # Read original CSV (must be present)
    orig_rows = []
    with open("data/raw/sales_raw.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            orig_rows.append(row)
    
    # Step 1: remove exact duplicates (same all fields)
    seen = set()
    deduped = []
    for row in orig_rows:
        key = tuple(row.values())
        if key not in seen:
            seen.add(key)
            deduped.append(row)
    
    # Step 2: fill missing sales_amount with 0
    for row in deduped:
        if row["sales_amount"] == "" or row["sales_amount"] is None:
            row["sales_amount"] = "0"
    
    # Step 3: remove suspicious record TXN-000999
    cleaned = [row for row in deduped if row["transaction_id"] != "TXN-000999"]
    # Also capture suspicious record
    susp_record = None
    for row in deduped:
        if row["transaction_id"] == "TXN-000999":
            susp_record = row
            break
    
    # Step 4: group by region, sum sales_amount
    region_sum = {}
    for row in cleaned:
        amount = float(row["sales_amount"])
        region = row["region"]
        region_sum[region] = region_sum.get(region, 0) + amount
    
    return region_sum, susp_record

expected_region_sum, expected_susp = compute_expected()

# 5. Compare region_summary content (50 points total)
region_content_ok = False
if region_valid and region_data is not None:
    # Check that keys match exactly
    if set(region_data.keys()) == set(expected_region_sum.keys()):
        # Check each value with tolerance
        values_match = True
        for k in expected_region_sum:
            exp_val = expected_region_sum[k]
            got_val = region_data.get(k)
            if not isinstance(got_val, (int, float)):
                values_match = False
                break
            if abs(got_val - exp_val) > 1e-6:
                values_match = False
                break
        if values_match:
            region_content_ok = True
            check(True, "region_summary values correct", 50, 50, "")
        else:
            check(False, "region_summary values correct", 0, 50, f"Expected {expected_region_sum}, got {region_data}")
    else:
        check(False, "region_summary values correct", 0, 50, f"Key mismatch: expected {set(expected_region_sum.keys())}, got {set(region_data.keys())}")
else:
    check(False, "region_summary values correct", 0, 50, "region_data not available")

# 6. Compare suspicious.json content (20 points)
susp_content_ok = False
if susp_valid and susp_data is not None:
    # susp_data can be a dict or list? Prompt says "完整字段保存", we expect a dict.
    if isinstance(susp_data, dict):
        # Check transaction_id
        if susp_data.get("transaction_id") == "TXN-000999":
            # Check sales_amount
            try:
                sales = float(susp_data.get("sales_amount", 0))
                if abs(sales - 1500.0) < 1e-6:
                    # Check region
                    if susp_data.get("region") == "East":
                        susp_content_ok = True
                        check(True, "suspicious.json contains correct record", 20, 20, "")
                    else:
                        check(False, "suspicious.json field 'region' wrong", 0, 20, f"Expected 'East', got {susp_data.get('region')}")
                else:
                    check(False, "suspicious.json field 'sales_amount' wrong", 0, 20, f"Expected 1500.0, got {sales}")
            except:
                check(False, "suspicious.json field 'sales_amount' not numeric", 0, 20, "")
        else:
            check(False, "suspicious.json missing or wrong transaction_id", 0, 20, f"Expected TXN-000999, got {susp_data.get('transaction_id')}")
    else:
        check(False, "suspicious.json should be a JSON object", 0, 20, f"Got type {type(susp_data).__name__}")
else:
    check(False, "suspicious.json content check", 0, 20, "susp_data not available")

# Compute total
total_score = sum(d["score"] for d in score_details)
# Round to integer
total_score = int(round(total_score))

result = {
    "total_score": total_score,
    "details": score_details
}
with open("workplace_score.json", "w") as f:
    json.dump(result, f, indent=2)

if __name__ == "__main__":
    pass
