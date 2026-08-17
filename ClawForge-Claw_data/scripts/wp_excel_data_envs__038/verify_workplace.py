#!/usr/bin/env python3
import sys
import json
import csv
import os

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []
total_score = 0

# ---------- 1. Check output file exists ----------
file_path = os.path.join(workspace, "ops/duplicates.json")
file_exists = os.path.isfile(file_path)
score_details.append({
    "item": "Output file ops/duplicates.json exists",
    "max_score": 10,
    "score": 10 if file_exists else 0,
    "passed": file_exists,
    "reason": "File found" if file_exists else "File not found"
})
if file_exists:
    total_score += 10

# ---------- 2. JSON validity ----------
valid_json = False
parsed = None
if file_exists:
    try:
        with open(file_path, "r") as f:
            parsed = json.load(f)
        valid_json = True
    except Exception:
        pass
score_details.append({
    "item": "Output file is valid JSON",
    "max_score": 10,
    "score": 10 if valid_json else 0,
    "passed": valid_json,
    "reason": "Valid JSON" if valid_json else "Invalid JSON"
})
if valid_json:
    total_score += 10

# ---------- 3. Contains key "duplicate_ids" ----------
has_key = False
if valid_json and isinstance(parsed, dict):
    has_key = "duplicate_ids" in parsed
score_details.append({
    "item": "JSON contains key 'duplicate_ids'",
    "max_score": 10,
    "score": 10 if has_key else 0,
    "passed": has_key,
    "reason": "Key present" if has_key else "Key missing"
})
if has_key:
    total_score += 10

# ---------- 4. Compute ground truth from csv ----------
expected_ids = []
if os.path.isfile(os.path.join(workspace, "data/raw_data/sales_raw.csv")):
    with open(os.path.join(workspace, "data/raw_data/sales_raw.csv"), newline="") as f:
        reader = csv.DictReader(f)
        counts = {}
        for row in reader:
            tid = row["transaction_id"]
            counts[tid] = counts.get(tid, 0) + 1
        expected_ids = sorted([tid for tid, cnt in counts.items() if cnt > 1])
else:
    score_details.append({
        "item": "Source CSV exists",
        "max_score": 0,
        "score": 0,
        "passed": False,
        "reason": "Cannot compute ground truth – source file missing"
    })

# ---------- 5. Compare actual duplicate IDs ----------
ids_match = False
actual_ids = []
if has_key:
    actual_ids = parsed["duplicate_ids"]
    # Normalize: ensure sorted list
    if isinstance(actual_ids, list) and all(isinstance(x, str) for x in actual_ids):
        sorted_actual = sorted(actual_ids)
        if sorted_actual == expected_ids:
            ids_match = True

id_score = 30 if ids_match else 0
score_details.append({
    "item": "Duplicate IDs exactly match ground truth",
    "max_score": 30,
    "score": id_score,
    "passed": ids_match,
    "reason": f"Expected {expected_ids}, got {actual_ids}" if not ids_match else "Perfect match"
})
if ids_match:
    total_score += 30

# ---------- 6. Partial credit if any correct IDs, but not all -------------
# We'll give up to 30 points if at least some correct (but we already awarded full if all correct)
# To avoid double-count, we only add if not full match.
if not ids_match and has_key and isinstance(actual_ids, list):
    set_expected = set(expected_ids)
    set_actual = set(actual_ids)
    correct_ids = set_actual & set_expected
    false_positives = set_actual - set_expected
    missing = set_expected - set_actual
    if len(correct_ids) > 0 and (len(false_positives) == 0 or len(missing) == 0):
        # partial but no false positives or no missing – still something
        # We'll give proportional score
        proportion = len(correct_ids) / max(len(expected_ids), 1)
        partial_score = int(proportion * 30)
        total_score -= id_score  # remove the 0 we added earlier
        total_score += partial_score
        # update the detail entry
        score_details[-1]["score"] = partial_score
        score_details[-1]["passed"] = False
        score_details[-1]["reason"] = f"Partial match: correct {sorted(correct_ids)}, false positives {sorted(false_positives)}, missing {sorted(missing)}"
    # else no points

# Ensure total_score is integer between 0 and 100
total_score = min(100, max(0, total_score))

# Write result
result = {
    "total_score": total_score,
    "details": score_details
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)

print(f"Verification complete. Total score: {total_score}/100")
