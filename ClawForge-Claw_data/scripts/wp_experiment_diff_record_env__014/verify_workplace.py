import sys
import json
import csv
import os
import math

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

scores = []
total_score = 0

def add_score(item, score, max_score, passed, reason):
    scores.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })
    global total_score
    total_score += score

# 1. Check ops/ directory exists
ops_dir = os.path.join(workspace, "ops")
if os.path.isdir(ops_dir):
    add_score("ops/ directory exists", 10, 10, True, "Directory found")
else:
    add_score("ops/ directory exists", 0, 10, False, "Missing ops/ directory")

# 2. Check diff_record.json exists
result_path = os.path.join(ops_dir, "diff_record.json")
if os.path.isfile(result_path):
    add_score("diff_record.json exists", 10, 10, True, "File found")
else:
    add_score("diff_record.json exists", 0, 10, False, "File not found")
    # Cannot proceed to further checks, finalize
    final = {"total_score": total_score, "details": scores}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)
    sys.exit(0)

# 3. Parse JSON and validate structure
try:
    with open(result_path, "r") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        add_score("JSON is a dict object", 0, 10, False, "Root must be a dict")
        # can still try to parse if it's list?
        data = {}
    else:
        add_score("JSON is a dict object", 10, 10, True, "Valid JSON dict")
except Exception as e:
    add_score("Valid JSON", 0, 10, False, f"Parse error: {e}")
    data = {}

# 4. Validate that all expected groups are present and fields correct
# First, read the CSV and compute expected differences
csv_path = os.path.join(workspace, "data/experiments/experiment_results.csv")
expected_diff = {}
try:
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        rows_by_batch_group = {}
        for row in reader:
            batch = row["batch_id"].strip()
            group = row["group_id"].strip()
            # Filter invalid rows (missing cost_usd)
            if not row.get("cost_usd"):
                continue
            try:
                acc = float(row["accuracy"])
                lat = float(row["latency_ms"])
                cost = float(row["cost_usd"])
            except (ValueError, KeyError):
                continue
            key = (batch, group)
            # Take the last occurrence for each batch+group (handles duplicates)
            rows_by_batch_group[key] = (acc, lat, cost)
        
        # Compute differences for groups that exist in both batches
        groups_001 = set(k[1] for k in rows_by_batch_group if k[0] == "batch_001")
        groups_002 = set(k[1] for k in rows_by_batch_group if k[0] == "batch_002")
        common_groups = groups_001 & groups_002
        for g in common_groups:
            v1 = rows_by_batch_group[("batch_001", g)]
            v2 = rows_by_batch_group[("batch_002", g)]
            expected_diff[g] = {
                "accuracy_diff": round(v2[0] - v1[0], 2),
                "latency_diff": v2[1] - v1[1],
                "cost_diff": round(v2[2] - v1[2], 2)
            }
except Exception as e:
    add_score("CSV processing", 0, 10, False, f"Error reading CSV: {e}")
    expected_diff = {}

# 4a. Validate groups present
submitted_groups = set(data.keys())
expected_keys = set(expected_diff.keys())
if submitted_groups == expected_keys:
    add_score("Group keys match exactly", 10, 10, True, f"Keys: {sorted(expected_keys)}")
else:
    missing = expected_keys - submitted_groups
    extra = submitted_groups - expected_keys
    msg_parts = []
    if missing:
        msg_parts.append(f"Missing groups: {sorted(missing)}")
    if extra:
        msg_parts.append(f"Extra groups: {sorted(extra)}")
    add_score("Group keys match exactly", 0, 10, False, "; ".join(msg_parts))

# 5. Validate each group's diff fields and values
field_score_max = 30  # 10 per group, 3 groups
field_earned = 0
for group in expected_diff:
    if group not in data:
        continue
    entry = data[group]
    expected_entry = expected_diff[group]
    # Check required fields exist
    required_fields = ["accuracy_diff", "latency_diff", "cost_diff"]
    field_ok = all(f in entry for f in required_fields)
    if not field_ok:
        continue
    # Compare values with tolerance (for floats)
    val_ok = True
    for field in required_fields:
        expected_val = expected_entry[field]
        actual_val = entry[field]
        if isinstance(expected_val, float):
            if not math.isclose(actual_val, expected_val, abs_tol=0.005):
                val_ok = False
                break
        else:
            if actual_val != expected_val:
                val_ok = False
                break
    if field_ok and val_ok:
        field_earned += 10
    else:
        # partial credit possible
        pass

add_score("Group-level field and value correctness", field_earned, field_score_max, field_earned == field_score_max,
          f"Correct groups: {field_earned//10} out of 3")

# 6. Check no extra fields inside each group entry
extra_field_penalty = 0
for group, entry in data.items():
    if group not in expected_diff:
        continue
    allowed = {"accuracy_diff", "latency_diff", "cost_diff"}
    extra = set(entry.keys()) - allowed
    if extra:
        extra_field_penalty += 5  # per group with extra fields
        break  # only penalize once for simplicity? we'll sum
# Convert penalty to score: start at 10, deduct
base_clean = 10
clean_score = max(0, base_clean - extra_field_penalty)
add_score("No extra fields inside group entries", clean_score, 10, clean_score == 10,
          f"Extra field penalty: {extra_field_penalty}")

# 7. Summary validation (optional, we don't have summary field in expected)
# Not required, so no score

# Final score
add_score("Overall verification", 0, 0, True, "Completed")

final = {
    "total_score": total_score,
    "details": scores
}

output_path = os.path.join(workspace, "workplace_score.json")
with open(output_path, "w") as f:
    json.dump(final, f, indent=2)

print(f"Total score: {total_score}/100")
