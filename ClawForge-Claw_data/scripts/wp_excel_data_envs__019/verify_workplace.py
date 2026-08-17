import sys
import os
import json
import csv
import math

def verify_workplace(workspace):
    details = []
    total_score = 0

    # Helper to add detail
    def add_item(name, score, max_score, passed, reason):
        details.append({
            "item": name,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        return score

    # 1. Directory structure: report/ exists
    report_dir = os.path.join(workspace, 'report')
    if os.path.isdir(report_dir):
        total_score += add_item("report directory exists", 5, 5, True, "Found report/")
    else:
        total_score += add_item("report directory exists", 0, 5, False, "Missing report/ directory")
        # If missing, skip further checks that depend on it
        missing_report = True
    # 2. File existence: report/clean_sales.csv and report/regional_avg.json
    clean_csv = os.path.join(report_dir, 'clean_sales.csv')
    avg_json = os.path.join(report_dir, 'regional_avg.json')
    if os.path.isfile(clean_csv):
        total_score += add_item("clean_sales.csv exists", 5, 5, True, "Found report/clean_sales.csv")
    else:
        total_score += add_item("clean_sales.csv exists", 0, 5, False, "Missing report/clean_sales.csv")
    if os.path.isfile(avg_json):
        total_score += add_item("regional_avg.json exists", 5, 5, True, "Found report/regional_avg.json")
    else:
        total_score += add_item("regional_avg.json exists", 0, 5, False, "Missing report/regional_avg.json")

    # 3. Validate CSV format and content
    csv_score = 0
    if os.path.isfile(clean_csv):
        try:
            with open(clean_csv, 'r', newline='') as f:
                reader = csv.reader(f)
                header = next(reader)
                expected_header = ['transaction_id','date','product_id','product_name','category','subcategory','region','city','customer_id','customer_name','sales_amount','quantity','discount','payment_method','salesperson_id','salesperson_name','channel']
                if header == expected_header:
                    csv_score += add_item("CSV header correct", 5, 5, True, "Header matches expected")
                else:
                    csv_score += add_item("CSV header correct", 0, 5, False, f"Header mismatch: {header}")
                rows = list(reader)
                # Check row count: after dedup we expect 9 rows (explain later)
                # Original rows (excluding header): 12 rows? Actually we wrote 13 rows (header + 12 data rows)
                # Data rows: 1+1+2+1+1+1+2+1+1 = 11? Let's recount: 
                # T001 duplicate (2), T002 two dates (2), T003 (1), T004 (1), T005 (1), T006 duplicate (2), T007 (1), T008 (1) => total 11 data rows.
                # After dedup: T001 -> 1 (remove exact dup), T002 -> keep latest (2024-02-12), T003, T004, T005, T006 -> 1, T007, T008 => 1+1+1+1+1+1+1+1 = 8? Wait we also have T002 latest, T001 one, T006 one, T003,T004,T005,T007,T008 = total 8.
                # But we also have T001 exact duplicate removed -> 1, T002 keep latest -> 1, T006 exact duplicate -> 1, others single -> 5, total 8.
                # Also T002 original two rows: dates 2024-02-10 and 2024-02-12 -> keep 2024-02-12. So 8 rows.
                # Check if any missing product_name/region: T003 missing product_name (filled), T004 missing region (filled), T007 missing both -> filled. So final 8 rows all filled.
                expected_rows = 8
                if len(rows) == expected_rows:
                    csv_score += add_item("CSV row count correct (after dedup)", 10, 10, True, f"Found {len(rows)} rows")
                else:
                    csv_score += add_item("CSV row count correct (after dedup)", 0, 10, False, f"Expected {expected_rows} rows, found {len(rows)}")
                # Check no duplicate transaction_id
                tids = [row[0] for row in rows]
                if len(tids) == len(set(tids)):
                    csv_score += add_item("No duplicate transaction_id", 5, 5, True, "All transaction IDs unique")
                else:
                    csv_score += add_item("No duplicate transaction_id", 0, 5, False, "Duplicate transaction IDs found")
                # Check no missing product_name or region
                missing_name = any(row[3].strip() == '' for row in rows)
                missing_region = any(row[6].strip() == '' for row in rows)
                if not missing_name and not missing_region:
                    csv_score += add_item("No missing product_name or region", 10, 10, True, "All fields filled")
                else:
                    csv_score += add_item("No missing product_name or region", 0, 10, False, f"Missing names: {missing_name}, missing regions: {missing_region}")
                # Check specific values: T002 should have sales_amount 235.00 (latest)
                for row in rows:
                    if row[0] == 'T002':
                        if float(row[9]) == 235.0:
                            csv_score += add_item("T002 uses latest row", 5, 5, True, f"T002 amount is {row[9]}")
                        else:
                            csv_score += add_item("T002 uses latest row", 0, 5, False, f"T002 amount is {row[9]}, expected 235.00")
        except Exception as e:
            csv_score += add_item("CSV parsing", 0, 10, False, f"Error reading CSV: {e}")
    else:
        csv_score += add_item("CSV validation skipped (file missing)", 0, 40, False, "File not found")
    total_score += csv_score

    # 4. Validate JSON
    json_score = 0
    if os.path.isfile(avg_json):
        try:
            with open(avg_json, 'r') as f:
                data = json.load(f)
            if isinstance(data, dict):
                json_score += add_item("JSON is a dict", 3, 3, True, "")
                # Expected regions and averages based on cleaned data:
                # Cleaned rows:
                # T001: East, 120.50
                # T002: West, 235.00
                # T003: South, 88.75
                # T004: Midwest, 450.00
                # T005: West, 320.00
                # T006: East, 140.00
                # T007: West, 275.50
                # T008: South, 190.00
                # East: (120.50+140.00)/2 = 130.25
                # West: (235.00+320.00+275.50)/3 = 830.50/3 = 276.83333333 -> 276.83
                # South: (88.75+190.00)/2 = 139.375 -> 139.38? (注意：88.75+190=278.75, /2=139.375, round 2->139.38)
                # Midwest: 450.00 -> 450.00
                expected = {
                    'East': round((120.50 + 140.00) / 2, 2),
                    'West': round((235.00 + 320.00 + 275.50) / 3, 2),
                    'South': round((88.75 + 190.00) / 2, 2),
                    'Midwest': 450.00
                }
                # Allow any numeric representation
                for region, exp_val in expected.items():
                    if region in data:
                        val = data[region]
                        if isinstance(val, (int, float)) and math.isclose(val, exp_val, rel_tol=1e-3):
                            json_score += add_item(f"Region {region} value", 5, 5, True, f"{region}: {val}")
                        else:
                            json_score += add_item(f"Region {region} value", 0, 5, False, f"Expected {exp_val}, got {val}")
                    else:
                        json_score += add_item(f"Region {region} exists", 0, 5, False, f"Missing region {region}")
                # Check no extra regions
                extra = [k for k in data if k not in expected]
                if extra:
                    json_score += add_item("No extra regions", 2, 2, False, f"Extra keys: {extra}")
                else:
                    json_score += add_item("No extra regions", 2, 2, True, "")
            else:
                json_score += add_item("JSON structure", 0, 3, False, "Root is not a dict")
        except Exception as e:
            json_score += add_item("JSON parsing", 0, 20, False, f"Error reading JSON: {e}")
    else:
        json_score += add_item("JSON validation skipped (file missing)", 0, 20, False, "File not found")
    total_score += json_score

    # Cap total
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, 'workplace_score.json'), 'w') as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total_score}/100")
    return total_score

if __name__ == '__main__':
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
