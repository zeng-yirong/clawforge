#!/usr/bin/env python3
import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score = 0
details = []
max_total = 100

# ------------------------------------------------------------
# 1. Check ops directory exists
# ------------------------------------------------------------
ops_path = os.path.join(workspace, "ops")
if os.path.isdir(ops_path):
    details.append({
        "item": "ops directory exists",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Found ops/ directory."
    })
    score += 10
else:
    details.append({
        "item": "ops directory exists",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": "ops/ directory not found."
    })
    # cannot proceed further
    _write_and_exit(score, details, workspace)
    sys.exit(0)

# ------------------------------------------------------------
# 2. Check denied_requests.json exists
# ------------------------------------------------------------
result_path = os.path.join(ops_path, "denied_requests.json")
if not os.path.isfile(result_path):
    details.append({
        "item": "denied_requests.json exists",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": "File ops/denied_requests.json not found."
    })
    _write_and_exit(score, details, workspace)
    sys.exit(0)
else:
    details.append({
        "item": "denied_requests.json exists",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "File exists."
    })
    score += 10

# ------------------------------------------------------------
# 3. JSON parse validity
# ------------------------------------------------------------
try:
    with open(result_path, "r") as f:
        data = json.load(f)
except (json.JSONDecodeError, ValueError) as e:
    details.append({
        "item": "valid JSON",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": f"Invalid JSON: {e}"
    })
    _write_and_exit(score, details, workspace)
    sys.exit(0)

details.append({
    "item": "valid JSON",
    "score": 10,
    "max_score": 10,
    "passed": True,
    "reason": "JSON parsed successfully."
})
score += 10

# ------------------------------------------------------------
# 4. Required field 'denied_ids' exists and is a list
# ------------------------------------------------------------
if not isinstance(data, dict):
    details.append({
        "item": "top-level object with denied_ids",
        "score": 0,
        "max_score": 20,
        "passed": False,
        "reason": "Top-level is not a JSON object."
    })
    _write_and_exit(score, details, workspace)
    sys.exit(0)

if "denied_ids" not in data:
    details.append({
        "item": "top-level object with denied_ids",
        "score": 0,
        "max_score": 20,
        "passed": False,
        "reason": "Missing key 'denied_ids'."
    })
    _write_and_exit(score, details, workspace)
    sys.exit(0)

denied = data["denied_ids"]
if not isinstance(denied, list):
    details.append({
        "item": "denied_ids is a list",
        "score": 0,
        "max_score": 20,
        "passed": False,
        "reason": f"denied_ids is type {type(denied).__name__}, expected list."
    })
    _write_and_exit(score, details, workspace)
    sys.exit(0)

details.append({
    "item": "denied_ids is a list",
    "score": 20,
    "max_score": 20,
    "passed": True,
    "reason": "Key exists and value is a list."
})
score += 20

# ------------------------------------------------------------
# 5. Correct length (exactly 2)
# ------------------------------------------------------------
expected_ids = {"req_023", "req_047"}
actual_set = set(denied)
if len(denied) != 2:
    details.append({
        "item": "list length = 2",
        "score": 0,
        "max_score": 20,
        "passed": False,
        "reason": f"List has {len(denied)} items, expected 2."
    })
    # continue to check content anyway
else:
    details.append({
        "item": "list length = 2",
        "score": 20,
        "max_score": 20,
        "passed": True,
        "reason": "Length is exactly 2."
    })
    score += 20

# ------------------------------------------------------------
# 6. Content matches expected IDs exactly (order irrelevant)
# ------------------------------------------------------------
if actual_set == expected_ids:
    details.append({
        "item": "denied_ids content matches expected (req_023, req_047)",
        "score": 30,
        "max_score": 30,
        "passed": True,
        "reason": "All expected IDs present, no extra IDs."
    })
    score += 30
else:
    # Partial match? Give partial credit only if no extra and missing one.
    missing = expected_ids - actual_set
    extra = actual_set - expected_ids
    if len(missing) == 0 and len(extra) > 0:
        reason = f"Contains all expected IDs but also extra: {extra}."
        passed = False
        pts = 15  # half credit for having correct ones but extra
    elif len(missing) == 1 and len(extra) == 0:
        reason = f"Missing {missing}, no extra."
        passed = False
        pts = 15
    elif len(missing) == 0 and len(extra) == 0:
        reason = "Lists are identical (should not happen here)."
        passed = True
        pts = 30
    else:
        reason = f"Missing: {missing}, Extra: {extra}."
        passed = False
        pts = 0
    details.append({
        "item": "denied_ids content matches expected (req_023, req_047)",
        "score": pts,
        "max_score": 30,
        "passed": passed,
        "reason": reason
    })
    score += pts

# ------------------------------------------------------------
# Write final score
# ------------------------------------------------------------
total_score = round(score)
if total_score > 100:
    total_score = 100

output = {
    "total_score": total_score,
    "details": details
}
output_path = os.path.join(workspace, "workplace_score.json")
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)
print(f"Score written: {total_score}/100")
