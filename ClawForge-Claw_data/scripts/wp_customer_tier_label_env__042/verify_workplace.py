import os
import sys
import json
import math

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []
total_score = 0

def add_item(item, score, max_score, passed, reason):
    global total_score
    total_score += score
    score_details.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })

# 1. Check ops directory exists
if os.path.isdir(os.path.join(workspace, "ops")):
    add_item("ops directory exists", 5, 5, True, "ops directory present")
else:
    add_item("ops directory exists", 0, 5, False, "ops directory missing")

# 2. Check label_update.json exists
label_path = os.path.join(workspace, "ops", "label_update.json")
if os.path.isfile(label_path):
    add_item("label_update.json exists", 10, 10, True, "file found")
else:
    add_item("label_update.json exists", 0, 10, False, "file not found")
    # can't proceed further
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
    sys.exit(0)

# 3. Check JSON validity
try:
    with open(label_path, "r") as f:
        data = json.load(f)
    add_item("label_update.json is valid JSON", 10, 10, True, "valid JSON")
except Exception as e:
    add_item("label_update.json is valid JSON", 0, 10, False, f"invalid JSON: {e}")
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
    sys.exit(0)

# 4. Check data structure: must contain "labels" list
if isinstance(data, dict) and "labels" in data:
    labels_list = data["labels"]
    add_item("JSON contains 'labels' array", 10, 10, True, "structure OK")
else:
    add_item("JSON contains 'labels' array", 0, 10, False, "missing 'labels' key or not a dict")
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
    sys.exit(0)

# 5. Read source data to compute expected labels
def read_json(path):
    with open(os.path.join(workspace, path), "r") as f:
        return json.load(f)

try:
    cons_data = read_json("data/logs/consumption_logs.json").get("consumption_logs", [])
    act_data = read_json("data/logs/activity_logs.json").get("activity_logs", [])
except Exception as e:
    add_item("Read source data", 0, 5, False, f"Cannot read source files: {e}")
    total_score = total_score  # keep previous
    # still compute partial
    cons_data = []
    act_data = []

# Build lookup dicts
cons_dict = {}
for c in cons_data:
    cid = c["customer_id"]
    spend = c["quarter_spend_usd"]
    # treat non-numeric as 0
    if isinstance(spend, str) or not isinstance(spend, (int, float)):
        spend = 0
    cons_dict[cid] = spend

act_dict = {}
for a in act_data:
    cid = a["customer_id"]
    act_dict[cid] = a

# Expected tiers based on rules
def compute_expected(cid):
    spend = cons_dict.get(cid, 0)
    act = act_dict.get(cid, {})
    risk = act.get("risk_level", "low")
    days = act.get("last_active_days", 999)
    trend = act.get("usage_trend", "up")

    # check gold
    if spend >= 20000 and days <= 30:
        return "gold"
    # check silver
    if spend >= 10000 and days <= 60:
        return "silver"
    # check churn conditions: risk high OR trend down
    if risk == "high" or trend == "down":
        return "churn_risk"
    return "bronze"

expected = {
    "C001": "gold",
    "C002": "silver",
    "C003": "churn_risk",
    "C004": "bronze",
    "C005": "churn_risk"
}

# Check each entry in labels_list
labels_dict = {}
for entry in labels_list:
    if isinstance(entry, dict) and "customer_id" in entry and "tier_label" in entry:
        cid = entry["customer_id"]
        label = entry["tier_label"]
        labels_dict[cid] = label

# Check all 5 customers
customer_ids = ["C001","C002","C003","C004","C005"]
correct_count = 0
for cid in customer_ids:
    if cid in labels_dict:
        if labels_dict[cid] == expected[cid]:
            correct_count += 1
            add_item(f"Customer {cid} label correct", 12, 12, True, f"expected {expected[cid]}, got {labels_dict[cid]}")
        else:
            add_item(f"Customer {cid} label correct", 0, 12, False, f"expected {expected[cid]}, got {labels_dict[cid]}")
    else:
        add_item(f"Customer {cid} label correct", 0, 12, False, f"missing customer {cid} in labels")

# Check no extra customers (optional, but penalize if any unexpected)
# We can add a small penalty for extra customers not in expected set
extra = set(labels_dict.keys()) - set(customer_ids)
if extra:
    add_item("No extra customers", 0, 5, False, f"unexpected customers: {extra}")
else:
    add_item("No extra customers", 5, 5, True, "no extra customers")

# Final score
final_total = sum(item["score"] for item in score_details)
# ensure 0-100
final_total = max(0, min(100, final_total))

result = {
    "total_score": final_total,
    "details": score_details
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)
