import os
import sys
import json
import math

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."
SCORE_FILE = os.path.join(WORKSPACE, "workplace_score.json")

REQUIRED_FILE = os.path.join(WORKSPACE, "ops/top_beat_candidate.json")

EXPECTED_TICKER = "TECH"
EXPECTED_COMPANY = "TechVentures Inc"
EXPECTED_QUARTERS = ["Q1 2026", "Q2 2026"]
EXPECTED_TOTAL = round(5.634 + 6.508, 2)   # 12.14

results = []

def check(description, score, max_score, passed, reason=""):
    results.append({
        "item": description,
        "score": score if passed else 0,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })

# --- 1. Directory structure (ops/) ---
if os.path.isdir(os.path.join(WORKSPACE, "ops")):
    check("ops/ directory exists", 5, 5, True)
else:
    check("ops/ directory exists", 0, 5, False, "Missing ops/ directory")

# --- 2. File exists ---
if os.path.isfile(REQUIRED_FILE):
    check("ops/top_beat_candidate.json exists", 10, 10, True)
else:
    check("ops/top_beat_candidate.json exists", 0, 10, False, "File not found")
    # Skip further checks if file missing
    details_list = results
    total = sum(d["score"] for d in details_list)
    with open(SCORE_FILE, "w") as f:
        json.dump({"total_score": total, "details": details_list}, f, indent=2)
    sys.exit(0)

# --- 3. JSON validity ---
try:
    with open(REQUIRED_FILE, "r") as f:
        data = json.load(f)
    check("File is valid JSON", 10, 10, True)
except Exception as e:
    check("File is valid JSON", 0, 10, False, str(e))
    # Stop checking
    details_list = results
    total = sum(d["score"] for d in details_list)
    with open(SCORE_FILE, "w") as f:
        json.dump({"total_score": total, "details": details_list}, f, indent=2)
    sys.exit(0)

# --- 4. Required fields ---
required_fields = ["ticker", "company_name", "total_eps_beat_pct", "quarters"]
missing_fields = [f for f in required_fields if f not in data]
if not missing_fields:
    check("All required fields present", 15, 15, True)
else:
    check("All required fields present", 0, 15, False, f"Missing: {missing_fields}")

# --- 5. Quarters field content ---
quarters = data.get("quarters", [])
if isinstance(quarters, list) and sorted(quarters) == sorted(EXPECTED_QUARTERS):
    check("quarters list matches exactly", 10, 10, True)
else:
    check("quarters list matches exactly", 0, 10, False, f"Got {quarters}")

# --- 6. ticker and company_name ---
ticker_ok = data.get("ticker") == EXPECTED_TICKER
company_ok = data.get("company_name") == EXPECTED_COMPANY
if ticker_ok and company_ok:
    check("ticker and company_name correct", 15, 15, True)
else:
    errs = []
    if not ticker_ok:
        errs.append(f"ticker expected {EXPECTED_TICKER}, got {data.get('ticker')}")
    if not company_ok:
        errs.append(f"company_name expected {EXPECTED_COMPANY}, got {data.get('company_name')}")
    check("ticker and company_name correct", 0, 15, False, "; ".join(errs))

# --- 7. total_eps_beat_pct numeric and accurate ---
total_pct = data.get("total_eps_beat_pct")
if isinstance(total_pct, (int, float)):
    diff = abs(total_pct - EXPECTED_TOTAL)
    if diff <= 0.02:
        check("total_eps_beat_pct correct (within 0.02)", 35, 35, True)
    else:
        check("total_eps_beat_pct correct (within 0.02)", 0, 35, False,
              f"Expected {EXPECTED_TOTAL}, got {total_pct}, diff {diff:.4f}")
else:
    check("total_eps_beat_pct correct (within 0.02)", 0, 35, False,
          f"Not a number: {total_pct}")

# --- Summary ---
total_score = sum(d["score"] for d in results)
final = {
    "total_score": total_score,
    "details": results
}
with open(SCORE_FILE, "w") as f:
    json.dump(final, f, indent=2)

print(f"Score written: {total_score}/100")
