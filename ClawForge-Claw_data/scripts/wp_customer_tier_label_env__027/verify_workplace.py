import sys
import json
import os
import re

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []

def add_score(item, score, max_score, passed, reason):
    score_details.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })

total_score = 0

# ---------- 1. File existence (10 pts) ----------
target_path = os.path.join(workspace, "ops", "customer_tier_updates.json")
if os.path.isfile(target_path):
    add_score("ops/customer_tier_updates.json exists", 10, 10, True, "File found")
    total_score += 10
else:
    add_score("ops/customer_tier_updates.json exists", 0, 10, False, "File not found")
    print(json.dumps({"total_score": 0, "details": score_details}))
    sys.exit(0)

# ---------- 2. Valid JSON (10 pts) ----------
try:
    with open(target_path, "r") as f:
        data = json.load(f)
    if not isinstance(data, list):
        add_score("Valid JSON + list", 0, 10, False, "Root element is not a list")
        print(json.dumps({"total_score": 0, "details": score_details}))
        sys.exit(0)
    add_score("Valid JSON + list", 10, 10, True, "Root is a list")
    total_score += 10
except Exception as e:
    add_score("Valid JSON", 0, 10, False, f"JSON parse error: {e}")
    print(json.dumps({"total_score": 0, "details": score_details}))
    sys.exit(0)

# ---------- Load reference data (customers, logs) ----------
def load_json(rel_path):
    full = os.path.join(workspace, rel_path)
    if not os.path.isfile(full):
        return None
    with open(full, "r") as f:
        return json.load(f)

customers = load_json("customers/customers.json")
consumption = load_json("raw_data/consumption_logs.json")
activity = load_json("raw_data/activity_logs.json")
if not all([customers, consumption, activity]):
    add_score("Reference data loading", 0, 0, False, "Missing required reference files (customers.json, consumption_logs.json, activity_logs.json)")
    # We give 0 but continue? better to abort.
    print(json.dumps({"total_score": total_score, "details": score_details}))
    sys.exit(0)

# Build lookup maps
cust_map = {c["customer_id"]: c for c in customers["customers"]}
cons_map = {}
for rec in consumption["consumption_logs"]:
    # skip invalid spend
    if not isinstance(rec.get("quarter_spend_usd"), int) or rec["quarter_spend_usd"] < 0:
        continue
    cons_map[rec["customer_id"]] = rec

act_map = {}
for rec in activity["activity_logs"]:
    act_map[rec["customer_id"]] = rec

# Determine expected customers to process (must have both valid consumption and activity)
expected_ids = set(cons_map.keys()) & set(act_map.keys()) & set(cust_map.keys())
# Dummy has no activity, healthplus has both, etc.
expected_records = []
for cid in sorted(expected_ids):
    c = cust_map[cid]
    con = cons_map[cid]
    act = act_map[cid]
    spend = con["quarter_spend_usd"]
    days = act["last_active_days"]
    risk = act["risk_level"]

    # Determine tier
    if spend >= 50000 and days <= 7 and risk == "low":
        tier = "platinum"
    elif 20000 <= spend < 50000 and days <= 30:
        tier = "gold"
    elif 5000 <= spend < 20000:
        tier = "silver"
    else:
        tier = "bronze"

    # Build new_labels: keep non-tier labels, replace tier:xxx
    old_labels = c.get("labels", [])
    new_labels = [lab for lab in old_labels if not lab.startswith("tier:")]
    new_labels.append(f"tier:{tier}")
    expected_records.append({
        "customer_id": cid,
        "new_labels": new_labels
    })

# Expected output (sorted by customer_id)
expected_output = sorted(expected_records, key=lambda x: x["customer_id"])

# ---------- 3. Check number of entries (10 pts) ----------
actual_sorted = sorted(data, key=lambda x: x.get("customer_id", ""))
if len(actual_sorted) == len(expected_output):
    add_score("Number of entries correct", 10, 10, True, f"Found {len(actual_sorted)} entries, expected {len(expected_output)}")
    total_score += 10
else:
    add_score("Number of entries correct", 0, 10, False, f"Found {len(actual_sorted)} entries, expected {len(expected_output)}")
    # still continue to grade individual ones

# ---------- 4. Entry-by-entry correctness (20 pts each, 3 entries = 60) ----------
max_per_entry = 20
for exp in expected_output:
    cid = exp["customer_id"]
    # find matching actual
    matches = [a for a in actual_sorted if a.get("customer_id") == cid]
    if not matches:
        add_score(f"Entry {cid}", 0, max_per_entry, False, "Missing customer entry")
        continue
    act_entry = matches[0]
    act_labels = act_entry.get("new_labels", [])
    exp_labels = exp["new_labels"]
    # compare as sets (order doesn't matter)
    if set(act_labels) == set(exp_labels):
        add_score(f"Entry {cid} labels correct", max_per_entry, max_per_entry, True, f"Labels: {act_labels}")
        total_score += max_per_entry
    else:
        add_score(f"Entry {cid} labels correct", 0, max_per_entry, False, f"Expected {exp_labels}, got {act_labels}")

# ---------- 5. Check no extra / unexpected entries (10 pts) ----------
expected_ids_set = set(e["customer_id"] for e in expected_output)
actual_ids = set(a.get("customer_id","") for a in actual_sorted)
unexpected = actual_ids - expected_ids_set
if len(unexpected) == 0:
    add_score("No unexpected customer entries", 10, 10, True, "All entries correspond to valid customers")
    total_score += 10
else:
    add_score("No unexpected customer entries", 0, 10, False, f"Unexpected customer(s): {unexpected}")

# ---------- Write score ----------
total_score = min(total_score, 100)  # cap
result = {
    "total_score": total_score,
    "details": score_details
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
