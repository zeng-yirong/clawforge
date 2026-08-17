import sys
import json
import os
from datetime import datetime, timedelta

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []
total_score = 0

# Helper to add item
def add_item(name, score, max_score, passed, reason):
    global total_score
    score_details.append({
        "item": name,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })
    total_score += score

# 1. Check ops directory exists
ops_path = os.path.join(workspace, "ops")
if os.path.isdir(ops_path):
    add_item("ops/ directory exists", 10, 10, True, "Found ops/")
else:
    add_item("ops/ directory exists", 0, 10, False, "Missing ops/ directory")
    # If missing, cannot continue
    final = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)
    sys.exit(0)

# 2. Check rescheduled_transport.json exists
result_path = os.path.join(workspace, "ops/rescheduled_transport.json")
if os.path.isfile(result_path):
    add_item("ops/rescheduled_transport.json exists", 10, 10, True, "File found")
else:
    add_item("ops/rescheduled_transport.json exists", 0, 10, False, "File not found")
    final = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)
    sys.exit(0)

# 3. Parse JSON
try:
    with open(result_path, "r") as f:
        data = json.load(f)
    add_item("JSON is valid", 10, 10, True, "Parsed successfully")
except (json.JSONDecodeError, Exception) as e:
    add_item("JSON is valid", 0, 10, False, f"Invalid JSON: {e}")
    final = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)
    sys.exit(0)

# 4. Check that data is a list (or dict?) – assume a list of one entry
if not isinstance(data, list):
    add_item("Data is a list", 0, 5, False, "Expected a list of rescheduled transports")
    # continue though
else:
    add_item("Data is a list", 5, 5, True, "Found list")

# 5. Check length – should be exactly 1 (only TR001 affected)
if len(data) != 1:
    add_item("Exactly one transport rescheduled", 0, 10, False, f"Found {len(data)} items, expected 1")
else:
    add_item("Exactly one transport rescheduled", 10, 10, True, "One item")

# 6. Validate fields and compute expected time
if len(data) >= 1:
    item = data[0]
    # Required fields: transport_id, new_pickup_time, status (optional but we check)
    if not isinstance(item, dict):
        add_item("Item is a dictionary", 0, 5, False, "Item is not a dict")
    else:
        add_item("Item is a dictionary", 5, 5, True, "Valid dict")
        # Check transport_id
        tid = item.get("transport_id")
        if tid == "TR001":
            add_item("transport_id is TR001", 5, 5, True, "Correct transport")
        else:
            add_item("transport_id is TR001", 0, 5, False, f"Got {tid}")
        # Check new_pickup_time
        new_time_str = item.get("new_pickup_time")
        if not new_time_str:
            add_item("new_pickup_time present", 0, 5, False, "Missing")
        else:
            add_item("new_pickup_time present", 5, 5, True, "Field exists")
            # Compute expected: original arrival of AA456 = 2025-08-15 11:00 + delay 120min -> 13:00, +30min = 13:30
            expected_time = "2025-08-15 13:30"
            if new_time_str == expected_time:
                add_item("new_pickup_time correct", 30, 30, True, f"Matches {expected_time}")
            else:
                add_item("new_pickup_time correct", 0, 30, False, f"Got {new_time_str}, expected {expected_time}")

# 7. Check that no extra fields that shouldn't be there (optional penalty if contains "hotel" etc.)
# Not required but we can give small bonus if clean
# (omitted for simplicity)

final = {"total_score": min(total_score, 100), "details": score_details}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(final, f, indent=2)
