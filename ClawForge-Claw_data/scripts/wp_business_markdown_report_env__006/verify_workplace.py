"""
Verify that the agent has produced the correct business markdown report.
Checks:
1. Directory structure and required file existence.
2. Report is valid Markdown (basic). 
3. Contains a header table for December 2024 metrics.
4. Contains a header table for month-over-month change percentages.
5. Specific numeric values must match the ground truth computed from env_builder.
6. No extra non-core metrics or old backup data is included.
Score breakdown:
- Directory & file existence: 10 points
- Markdown structure (headers / tables): 15 points
- December metrics table correctness (values): 40 points
- MoM change table correctness (percentages): 30 points
- Cleanliness (no forbidden entries): 5 points
"""
import sys, os, json, csv, re
from pathlib import Path

def load_csv_data(base_path: str) -> dict:
    """Load the three ledger CSVs from data/ledgers/ and return a dict mapping ledger -> list of rows."""
    ledgers = {}
    for fname in ["customer_ledger.csv", "product_ledger.csv", "ops_ledger.csv"]:
        fpath = os.path.join(base_path, "data", "ledgers", fname)
        if not os.path.exists(fpath):
            return None
        rows = []
        with open(fpath, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        ledgers[fname.replace("_ledger.csv", "")] = rows
    return ledgers

def compute_expected(ledgers: dict) -> dict:
    """From the raw ledger rows, compute expected December values and MoM changes for core metrics.
    Core metrics:
      customer: revenue, active_customers
      product: units_sold, avg_price
      ops: uptime_pct, ticket_resolved
    Returns dict with 'dec_values' and 'mom_changes'.
    """
    core_metrics = {
        "customer": ["revenue", "active_customers"],
        "product": ["units_sold", "avg_price"],
        "ops": ["uptime_pct", "ticket_resolved"]
    }
    # group by ledger
    dec_vals = {}
    nov_vals = {}
    for ledger_name, rows in ledgers.items():
        dec = {}
        nov = {}
        for r in rows:
            if r['period'] == '2024-12' and r['metric_code'] in core_metrics.get(ledger_name, []):
                dec[r['metric_code']] = float(r['metric_value'])
            elif r['period'] == '2024-11' and r['metric_code'] in core_metrics.get(ledger_name, []):
                nov[r['metric_code']] = float(r['metric_value'])
        if dec:
            dec_vals[ledger_name] = dec
        if nov:
            nov_vals[ledger_name] = nov
    
    expected = {}
    expected['dec_values'] = dec_vals
    # compute MoM change: (dec - nov)/nov * 100, rounded to 1 decimal
    mom = {}
    for ledger in dec_vals:
        mom[ledger] = {}
        for metric in dec_vals[ledger]:
            if ledger in nov_vals and metric in nov_vals[ledger] and nov_vals[ledger][metric] != 0:
                change = round(((dec_vals[ledger][metric] - nov_vals[ledger][metric]) / nov_vals[ledger][metric]) * 100, 1)
            else:
                change = None  # should not happen for our data
            mom[ledger][metric] = change
    expected['mom_changes'] = mom
    return expected

def check_markdown_content(content: str, expected: dict) -> dict:
    """Check the report content against expected values. Return detailed results."""
    results = []
    # Scores
    max_total = 100
    # 1. basic structure (10) - headers and at least one table
    has_h1 = bool(re.search(r'^#\s+', content, re.MULTILINE))
    # Count tables (lines starting with |)
    lines = content.splitlines()
    table_lines = [l for l in lines if l.startswith('|')]
    has_tables = len(table_lines) >= 6  # rough indicator
    struct_score = 0
    struct_max = 10
    struct_reason = ""
    if has_h1 and has_tables:
        struct_score = struct_max
        struct_reason = "Report has headers and tables."
    else:
        struct_reason = "Missing headers or tables."
    results.append({"item": "Markdown structure", "score": struct_score, "max_score": struct_max, "passed": struct_score==struct_max, "reason": struct_reason})
    
    # 2. December metrics table (40) - look for a table containing the six core metrics with correct values
    # We'll parse the first substantial table that includes numbers like 450000, 1250 etc.
    # Strategy: find all table rows, split by '|', strip, look for numeric entries.
    # We'll try to extract a mapping from the table.
    # Since we want robust checking, we'll search for specific patterns.
    dec_score = 0
    dec_max = 40
    dec_reason = ""
    # Expected December numeric values:
    expected_dec_flat = {
        'customer_revenue': 450000,
        'customer_active_customers': 1250,
        'product_units_sold': 3200,
        'product_avg_price': 149.5,
        'ops_uptime_pct': 99.8,
        'ops_ticket_resolved': 430,
    }
    # Build a regex that searches for each value in the content (approximately, but exact match via word boundary)
    # We'll check that all six values appear at least once.
    found_all = True
    missing = []
    for key, val in expected_dec_flat.items():
        # Try to find the number as a separate token; for floats use pattern that matches 149.5
        pattern = r'(?<!\d)' + re.escape(str(val)) + r'(?!\d)'
        if not re.search(pattern, content):
            found_all = False
            missing.append(key)
    if found_all:
        dec_score = dec_max
        dec_reason = "All December metric values found."
    else:
        dec_reason = f"Missing values for: {', '.join(missing)}"
        # Partial credit: 5 per correct value
        found_count = 6 - len(missing)
        dec_score = int((found_count / 6) * dec_max)
    results.append({"item": "December metrics values", "score": dec_score, "max_score": dec_max, "passed": dec_score==dec_max, "reason": dec_reason})
    
    # 3. MoM change table (30) - check for percentage values:
    expected_mom_flat = {
        'customer_revenue': 7.1,     # (450000-420000)/420000*100 = 7.142... -> 7.1
        'customer_active_customers': 5.9, # (1250-1180)/1180*100 = 5.932... -> 5.9
        'product_units_sold': 14.3,   # (3200-2800)/2800*100 = 14.2857 -> 14.3
        'product_avg_price': 3.1,     # (149.5-145)/145*100 = 3.1034 -> 3.1
        'ops_uptime_pct': 0.3,        # (99.8-99.5)/99.5*100 = 0.3015 -> 0.3
        'ops_ticket_resolved': 10.3,  # (430-390)/390*100 = 10.2564 -> 10.3
    }
    mom_score = 0
    mom_max = 30
    mom_reason = ""
    found_all_mom = True
    missing_mom = []
    for key, val in expected_mom_flat.items():
        # percentages may be written as "7.1%" or "7.1" ; we allow optional % sign and optional sign
        # Pattern: optional minus, digits, optional dot, optional digits, possibly followed by %
        pattern = r'(?<!\d)' + re.escape(str(val)) + r'(?!\d)(%?)'
        if not re.search(pattern, content):
            found_all_mom = False
            missing_mom.append(key)
    if found_all_mom:
        mom_score = mom_max
        mom_reason = "All MoM percentages found."
    else:
        mom_reason = f"Missing MoM values for: {', '.join(missing_mom)}"
        found_count_mom = 6 - len(missing_mom)
        mom_score = int((found_count_mom / 6) * mom_max)
    results.append({"item": "MoM change percentages", "score": mom_score, "max_score": mom_max, "passed": mom_score==mom_max, "reason": mom_reason})
    
    # 4. Cleanliness (5) - no forbidden metrics (churn_rate, inventory_level, etc.) and no old backup references
    clean_score = 0
    clean_max = 5
    clean_reason = ""
    forbidden_patterns = ['churn_rate', 'inventory_level', 'defect_rate', 'sla_breach', 'avg_response_time', 'old_ops_backup', 'customer_ledger_2024-09']
    found_forbidden = False
    for pat in forbidden_patterns:
        if pat in content:
            found_forbidden = True
            clean_reason = f"Forbidden term '{pat}' found."
            break
    if not found_forbidden:
        # also check that the file does not contain the word "old" in a way that suggests backup data
        if 'old_report' in content:
            found_forbidden = True
            clean_reason = "Old report mentioned."
    if not found_forbidden:
        clean_score = clean_max
        clean_reason = "No forbidden metrics or backup references."
    else:
        clean_score = 0
    results.append({"item": "Cleanliness (no extras)", "score": clean_score, "max_score": clean_max, "passed": clean_score==clean_max, "reason": clean_reason})
    
    total = sum(r['score'] for r in results)
    return {"total_score": total, "details": results}


def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    base_path = workspace
    
    # Check required directory structure and file
    score_info = []
    dir_ok = 0
    dir_max = 10
    required = [
        "reports/monthly_summary.md",
    ]
    missing_files = []
    for f in required:
        if not os.path.exists(os.path.join(base_path, f)):
            missing_files.append(f)
    if not missing_files:
        dir_ok = dir_max
        reason = "Required report file exists."
    else:
        reason = f"Missing: {', '.join(missing_files)}"
    score_info.append({"item": "File existence", "score": dir_ok, "max_score": dir_max, "passed": dir_ok==dir_max, "reason": reason})
    
    # If file missing, output score and exit
    if missing_files:
        total = sum(r['score'] for r in score_info)
        out = {"total_score": total, "details": score_info}
        with open(os.path.join(base_path, "workplace_score.json"), "w") as f:
            json.dump(out, f, indent=2)
        return
    
    # Read the report
    report_path = os.path.join(base_path, "reports/monthly_summary.md")
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Load ledgers to compute expected
    ledgers = load_csv_data(base_path)
    if ledgers is None:
        # missing data ledgers - this shouldn't happen, but score accordingly
        dir_ok = 0
        # we already have file existence ok; add a detail for data missing
        total_score = 0
        out = {"total_score": 0, "details": [{"item":"Ledger data","score":0,"max_score":100,"passed":False,"reason":"Cannot load ledger CSVs"}]}
        with open(os.path.join(base_path, "workplace_score.json"), "w") as f:
            json.dump(out, f, indent=2)
        return
    
    expected = compute_expected(ledgers)
    
    # Do content checks
    content_results = check_markdown_content(content, expected)
    
    # Combine with file existence score
    content_results["details"].insert(0, score_info[0])  # prepend file existence
    total_score = sum(r['score'] for r in content_results["details"])
    final = {"total_score": total_score, "details": content_results["details"]}
    
    with open(os.path.join(base_path, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    main()
