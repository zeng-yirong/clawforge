import sys
import os
import json
import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

def get_workspace():
    if len(sys.argv) > 1:
        ws = sys.argv[1]
    else:
        ws = "."
    return Path(ws).resolve()

def load_csv(path, expected_fields=None):
    """Load CSV, return list of dicts. Returns None on error."""
    if not path.exists():
        return None
    try:
        with open(path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if expected_fields:
                if not all(f in reader.fieldnames for f in expected_fields):
                    return None
            return rows
    except Exception:
        return None

def parse_amount(s):
    """Parse sales_amount string to Decimal or None if invalid."""
    if s is None or s.strip() == "":
        return None
    try:
        val = Decimal(s.strip())
        # negative or zero -> invalid
        if val <= 0:
            return None
        return val
    except Exception:
        return None

def parse_date(s):
    """Check if date is valid YYYY-MM-DD format and reasonable year."""
    if not s or not isinstance(s, str):
        return False
    parts = s.split("-")
    if len(parts) != 3:
        return False
    try:
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        if y < 2024 or y > 2025:
            return False
        if m < 1 or m > 12:
            return False
        if d < 1 or d > 31:
            return False
        # quick check for month-day validity (not exhaustive)
        if m == 2 and d > 29:
            return False
        if m in [4,6,9,11] and d > 30:
            return False
        return True
    except:
        return False

def verify():
    ws = get_workspace()
    details = []
    total_score = 0

    # ---- 1. Check output file exists (10 pts) ----
    out_path = ws / "ops" / "cleaned_summary.json"
    if not out_path.exists():
        details.append({"item": "output file exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/cleaned_summary.json not found"})
    else:
        details.append({"item": "output file exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
    total_score += details[-1]["score"]

    # ---- 2. JSON validity and structure (15 pts) ----
    if out_path.exists():
        try:
            with open(out_path, "r") as f:
                data = json.load(f)
        except Exception as e:
            data = None
            details.append({"item": "JSON parseable", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON parse error: {e}"})
        else:
            required_keys = ["total_revenue", "average_order_value", "clean_order_count"]
            if all(k in data for k in required_keys):
                if isinstance(data["total_revenue"], (int, float)) and \
                   isinstance(data["average_order_value"], (int, float)) and \
                   isinstance(data["clean_order_count"], int):
                    details.append({"item": "JSON structure correct", "score": 15, "max_score": 15, "passed": True, "reason": "All required fields present with correct types"})
                else:
                    details.append({"item": "JSON structure correct", "score": 5, "max_score": 15, "passed": False, "reason": "Fields exist but type mismatch"})
            else:
                missing = [k for k in required_keys if k not in data]
                details.append({"item": "JSON structure correct", "score": 0, "max_score": 15, "passed": False, "reason": f"Missing keys: {missing}"})
    else:
        details.append({"item": "JSON parseable", "score": 0, "max_score": 15, "passed": False, "reason": "No file to parse"})
    total_score += details[-1]["score"]

    # ---- 3. Recompute ground truth from raw data (60 pts) ----
    # We'll load all CSVs under raw_data/ (excluding backup folder)
    raw_dir = ws / "raw_data"
    csv_files = []
    if raw_dir.exists():
        for f in raw_dir.iterdir():
            if f.suffix == ".csv" and "backup" not in str(f):
                csv_files.append(f)
    else:
        csv_files = []

    # Collect all rows from non-backup CSVs
    all_rows = []
    for f in csv_files:
        rows = load_csv(f, expected_fields=["transaction_id", "sales_amount", "date"])
        if rows is not None:
            all_rows.extend(rows)

    # Define cleaning rules:
    # 1. Keep only rows with valid date (YYYY-MM-DD, 2024-2025)
    # 2. Keep only rows with positive sales_amount (parseable)
    # 3. Deduplicate: for each transaction_id, keep the first occurrence encountered
    #    (order: file order as loaded, but we'll preserve order from CSV scan)
    #    Note: We will process rows in the order they appear in the files (2024 first, then 2025)
    valid_rows = []
    seen_tids = set()
    for row in all_rows:
        tid = row.get("transaction_id", "")
        if not tid:
            continue
        # check date
        if not parse_date(row.get("date", "")):
            continue
        # check amount
        amount = parse_amount(row.get("sales_amount", ""))
        if amount is None:
            continue
        # dedup
        if tid in seen_tids:
            continue
        seen_tids.add(tid)
        valid_rows.append({"tid": tid, "amount": amount})

    # Compute ground truth
    total_revenue = sum(r["amount"] for r in valid_rows)
    clean_count = len(valid_rows)
    if clean_count > 0:
        avg_val = total_revenue / clean_count
    else:
        avg_val = 0

    # Round to 2 decimal places (standard rounding)
    total_revenue_round = float(total_revenue.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    avg_val_round = float(Decimal(str(avg_val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    # Compare with agent output
    if out_path.exists() and data is not None:
        agent_total = data.get("total_revenue")
        agent_avg = data.get("average_order_value")
        agent_count = data.get("clean_order_count")

        # total_revenue: exact match within 0.01
        rev_match = False
        if isinstance(agent_total, (int, float)):
            if abs(agent_total - total_revenue_round) < 0.005:
                rev_match = True

        avg_match = False
        if isinstance(agent_avg, (int, float)):
            if abs(agent_avg - avg_val_round) < 0.005:
                avg_match = True

        count_match = (agent_count == clean_count)

        # Score weights: total_revenue 20, average 20, count 20
        rev_score = 20 if rev_match else 0
        avg_score = 20 if avg_match else 0
        count_score = 20 if count_match else 0

        details.append({"item": "total_revenue correct", "score": rev_score, "max_score": 20, "passed": rev_match, "reason": f"Agent: {agent_total}, Expected: {total_revenue_round}"})
        details.append({"item": "average_order_value correct", "score": avg_score, "max_score": 20, "passed": avg_match, "reason": f"Agent: {agent_avg}, Expected: {avg_val_round}"})
        details.append({"item": "clean_order_count correct", "score": count_score, "max_score": 20, "passed": count_match, "reason": f"Agent: {agent_count}, Expected: {clean_count}"})
        total_score += rev_score + avg_score + count_score
    else:
        details.append({"item": "total_revenue correct", "score": 0, "max_score": 20, "passed": False, "reason": "No output data"})
        details.append({"item": "average_order_value correct", "score": 0, "max_score": 20, "passed": False, "reason": "No output data"})
        details.append({"item": "clean_order_count correct", "score": 0, "max_score": 20, "passed": False, "reason": "No output data"})
        total_score += 0

    # ---- 4. No extra fields in output (5 pts) ----
    extra_penalty = 0
    if out_path.exists() and data is not None:
        allowed = {"total_revenue", "average_order_value", "clean_order_count"}
        extras = set(data.keys()) - allowed
        if extras:
            extra_penalty = 5  # full deduction for extra fields
            details.append({"item": "no extra fields", "score": 0, "max_score": 5, "passed": False, "reason": f"Extra fields: {extras}"})
        else:
            details.append({"item": "no extra fields", "score": 5, "max_score": 5, "passed": True, "reason": "Only expected fields"})
    else:
        details.append({"item": "no extra fields", "score": 0, "max_score": 5, "passed": False, "reason": "No file"})
    total_score += details[-1]["score"] - extra_penalty  # already added

    # ---- 5. Filename exactly as required (10 pts) ----
    # Check that the file is exactly ops/cleaned_summary.json (case-sensitive)
    expected_path = ws / "ops" / "cleaned_summary.json"
    if out_path.exists() and out_path == expected_path:
        details.append({"item": "correct file path", "score": 10, "max_score": 10, "passed": True, "reason": "ops/cleaned_summary.json"})
    else:
        details.append({"item": "correct file path", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected ops/cleaned_summary.json, got {out_path.relative_to(ws) if out_path.exists() else 'none'}"})
    total_score += details[-1]["score"]

    # Cap score to 100
    final_score = min(total_score, 100)

    # Write score
    score_data = {
        "total_score": final_score,
        "details": details
    }
    score_path = ws / "workplace_score.json"
    with open(score_path, "w") as f:
        json.dump(score_data, f, indent=2)

    print(f"Verification complete. Score: {final_score}/100")

if __name__ == "__main__":
    verify()
