import sys
import json
import os
from pathlib import Path

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
ws = Path(workspace)

total_score = 0
details = []

# ---------- 1. ops directory exists (10) ----------
ops_dir = ws / "ops"
if ops_dir.is_dir():
    total_score += 10
    details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found ops/ directory."})
else:
    details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ directory not found."})

# ---------- 2. priority_incidents.json exists (10) ----------
result_file = ops_dir / "priority_incidents.json"
if result_file.is_file():
    total_score += 10
    details.append({"item": "priority_incidents.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found."})
else:
    details.append({"item": "priority_incidents.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File missing."})
    # cannot proceed; write score and exit
    with open(ws / "workplace_score.json", "w") as sf:
        json.dump({"total_score": total_score, "details": details}, sf, indent=2)
    sys.exit(0)

# ---------- 3. JSON is valid (10) ----------
try:
    with open(result_file, "r") as f:
        data = json.load(f)
    total_score += 10
    details.append({"item": "JSON parseable", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON."})
except Exception as e:
    details.append({"item": "JSON parseable", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
    with open(ws / "workplace_score.json", "w") as sf:
        json.dump({"total_score": total_score, "details": details}, sf, indent=2)
    sys.exit(0)

# ---------- 4. Structure: list of incidents (10) ----------
if isinstance(data, dict) and "incidents" in data:
    incidents = data["incidents"]
    if isinstance(incidents, list):
        total_score += 10
        details.append({"item": "Structure: incidents list", "score": 10, "max_score": 10, "passed": True, "reason": "Top-level key 'incidents' with list."})
    else:
        details.append({"item": "Structure: incidents list", "score": 0, "max_score": 10, "passed": False, "reason": "'incidents' is not a list."})
        with open(ws / "workplace_score.json", "w") as sf:
            json.dump({"total_score": total_score, "details": details}, sf, indent=2)
        sys.exit(0)
else:
    details.append({"item": "Structure: incidents list", "score": 0, "max_score": 10, "passed": False, "reason": "Top-level key 'incidents' missing or not dict."})
    with open(ws / "workplace_score.json", "w") as sf:
        json.dump({"total_score": total_score, "details": details}, sf, indent=2)
    sys.exit(0)

# ---------- 5. Each element has id & action (10) ----------
bad_elements = []
for i, inc in enumerate(incidents):
    if not isinstance(inc, dict):
        bad_elements.append(i)
        continue
    if "id" not in inc or "action" not in inc:
        bad_elements.append(i)
if not bad_elements:
    total_score += 10
    details.append({"item": "Each incident has id and action", "score": 10, "max_score": 10, "passed": True, "reason": "All elements have required keys."})
else:
    details.append({"item": "Each incident has id and action", "score": 0, "max_score": 10, "passed": False, "reason": f"Element(s) {bad_elements} missing keys."})
    with open(ws / "workplace_score.json", "w") as sf:
        json.dump({"total_score": total_score, "details": details}, sf, indent=2)
    sys.exit(0)

# ---------- 6. Correct incidents selected (set + order) (30) ----------
# Expected: INC-001, INC-002, INC-003, INC-007 sorted by opened_at
# opened_at from env_builder:
# INC-001: 2025-06-01T10:00:00
# INC-002: 2025-06-01T11:00:00
# INC-003: 2025-06-01T12:00:00
# INC-007: 2025-06-01T15:00:00
expected_ids = ["INC-001", "INC-002", "INC-003", "INC-007"]
actual_ids = [inc["id"] for inc in incidents]
if actual_ids == expected_ids:
    total_score += 30
    details.append({"item": "Correct incident set and order", "score": 30, "max_score": 30, "passed": True, "reason": f"IDs match expected: {expected_ids}"})
else:
    # partial credit if set correct but order wrong (15), or if set wrong (0)
    if set(actual_ids) == set(expected_ids):
        total_score += 15
        details.append({"item": "Correct incident set and order", "score": 15, "max_score": 30, "passed": False, "reason": f"Set correct but order wrong. Got {actual_ids}, expected {expected_ids}."})
    else:
        total_score += 0
        details.append({"item": "Correct incident set and order", "score": 0, "max_score": 30, "passed": False, "reason": f"Set mismatch. Got {actual_ids}, expected {expected_ids}."})

# ---------- 7. Actions match runbook (20) ----------
# runbook mapping:
# ups_outage -> "Power cycle the UPS and verify"
# service_down -> "Roll back last deployment"
incident_details = {
    "INC-001": "Power cycle the UPS and verify",
    "INC-002": "Roll back last deployment",
    "INC-003": "Power cycle the UPS and verify",
    "INC-007": "Roll back last deployment"
}
all_actions_correct = True
for inc in incidents:
    expected_action = incident_details.get(inc["id"])
    if expected_action is None:
        all_actions_correct = False
        break
    if inc["action"] != expected_action:
        all_actions_correct = False
        break
if all_actions_correct:
    total_score += 20
    details.append({"item": "Actions match runbook", "score": 20, "max_score": 20, "passed": True, "reason": "All actions correct."})
else:
    # count correct
    correct_count = 0
    for inc in incidents:
        expected_action = incident_details.get(inc["id"])
        if expected_action and inc["action"] == expected_action:
            correct_count += 1
    # proportional (max 20)
    action_score = int(20 * correct_count / len(expected_ids))
    total_score += action_score
    details.append({"item": "Actions match runbook", "score": action_score, "max_score": 20, "passed": False, "reason": f"Correct actions: {correct_count}/{len(expected_ids)}."})

# ---------- final ----------
if total_score > 100:
    total_score = 100
final_result = {
    "total_score": total_score,
    "details": details
}
with open(ws / "workplace_score.json", "w") as f:
    json.dump(final_result, f, indent=2)
