#!/usr/bin/env python3
import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score = 0
details = []

# 1. Check ops directory exists (10 points)
ops_path = os.path.join(workspace, "ops")
if os.path.isdir(ops_path):
    details.append({
        "item": "ops directory exists",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "ops/ directory found"
    })
    score += 10
else:
    details.append({
        "item": "ops directory exists",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": "ops/ directory not found"
    })

# 2. Check plan.json exists (10 points)
plan_path = os.path.join(workspace, "ops", "plan.json")
if os.path.isfile(plan_path):
    details.append({
        "item": "plan.json exists",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "ops/plan.json found"
    })
    score += 10
else:
    details.append({
        "item": "plan.json exists",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": "ops/plan.json not found"
    })
    # If file doesn't exist, skip further checks
    details.append({
        "item": "JSON valid",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": "File missing"
    })
    details.append({
        "item": "devices_to_off list length",
        "score": 0,
        "max_score": 20,
        "passed": False,
        "reason": "File missing"
    })
    details.append({
        "item": "device IDs correct",
        "score": 0,
        "max_score": 45,
        "passed": False,
        "reason": "File missing"
    })
    details.append({
        "item": "reason present",
        "score": 0,
        "max_score": 5,
        "passed": False,
        "reason": "File missing"
    })
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": score, "details": details}, f)
    sys.exit(0)

# 3. Validate JSON is well-formed (10 points)
try:
    with open(plan_path, "r") as f:
        data = json.load(f)
    details.append({
        "item": "JSON valid",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Valid JSON"
    })
    score += 10
except json.JSONDecodeError as e:
    details.append({
        "item": "JSON valid",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": f"Invalid JSON: {e}"
    })
    # cannot proceed
    details.append({
        "item": "devices_to_off list length",
        "score": 0,
        "max_score": 20,
        "passed": False,
        "reason": "JSON parse failed"
    })
    details.append({
        "item": "device IDs correct",
        "score": 0,
        "max_score": 45,
        "passed": False,
        "reason": "JSON parse failed"
    })
    details.append({
        "item": "reason present",
        "score": 0,
        "max_score": 5,
        "passed": False,
        "reason": "JSON parse failed"
    })
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": score, "details": details}, f)
    sys.exit(0)

# 4. Expect the JSON to contain a list called "devices_to_off" (or we accept top-level list)
# We'll look for 'devices_to_off' first
if isinstance(data, dict) and "devices_to_off" in data:
    devices = data["devices_to_off"]
elif isinstance(data, list):
    devices = data
else:
    devices = None
    details.append({
        "item": "devices_to_off list length",
        "score": 0,
        "max_score": 20,
        "passed": False,
        "reason": "JSON does not contain 'devices_to_off' key nor a top-level list"
    })
    details.append({
        "item": "device IDs correct",
        "score": 0,
        "max_score": 45,
        "passed": False,
        "reason": "No list of devices"
    })
    details.append({
        "item": "reason present",
        "score": 0,
        "max_score": 5,
        "passed": False,
        "reason": "No list of devices"
    })
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": score, "details": details}, f)
    sys.exit(0)

# 5. Check device list length (20 points) - expected 3 devices (tv, floor lamp, desk)
expected_device_ids = {"tv_plug_01", "floor_lamp_plug_01", "desk_plug_01"}
actual_ids = set()
for item in devices:
    if isinstance(item, dict):
        did = item.get("device_id")
        if did:
            actual_ids.add(did)
    elif isinstance(item, str):
        actual_ids.add(item)

if len(actual_ids) == len(expected_device_ids):
    details.append({
        "item": "devices_to_off list length",
        "score": 20,
        "max_score": 20,
        "passed": True,
        "reason": f"Exactly {len(expected_device_ids)} devices found"
    })
    score += 20
else:
    details.append({
        "item": "devices_to_off list length",
        "score": 0,
        "max_score": 20,
        "passed": False,
        "reason": f"Expected {len(expected_device_ids)} devices, got {len(actual_ids)}"
    })

# 6. Check each expected device ID is present (15 each, total 45)
correct_id_score = 0
for did in expected_device_ids:
    if did in actual_ids:
        correct_id_score += 15
    else:
        # missing device – deduct full 15
        details.append({
            "item": f"device ID '{did}' present",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Missing device_id {did}"
        })
# Record aggregate
if correct_id_score == 45:
    details.append({
        "item": "device IDs correct",
        "score": 45,
        "max_score": 45,
        "passed": True,
        "reason": "All three expected device IDs present"
    })
    score += 45
else:
    # If we already added per-device details, just record aggregate as zero
    # But avoid duplicate entries – we handle by accumulating
    if correct_id_score == 0:
        # no per-device details added yet, add one aggregate
        details.append({
            "item": "device IDs correct",
            "score": 0,
            "max_score": 45,
            "passed": False,
            "reason": "None of the expected device IDs found"
        })
    else:
        # partial score: add an aggregate detail with partial
        details.append({
            "item": "device IDs correct",
            "score": correct_id_score,
            "max_score": 45,
            "passed": True if correct_id_score == 45 else False,
            "reason": f"Found {correct_id_score//15} out of 3 expected devices"
        })
        score += correct_id_score

# 7. Check each device entry has a non-empty reason (5 points)
all_have_reason = True
for item in devices:
    if isinstance(item, dict):
        reason = item.get("reason", "")
        if not reason:
            all_have_reason = False
            break
    else:
        all_have_reason = False
        break

if all_have_reason:
    details.append({
        "item": "reason present",
        "score": 5,
        "max_score": 5,
        "passed": True,
        "reason": "All device entries include a non-empty reason"
    })
    score += 5
else:
    details.append({
        "item": "reason present",
        "score": 0,
        "max_score": 5,
        "passed": False,
        "reason": "Missing or empty reason field in one or more entries"
    })

# Also penalize if there are extra device IDs not in expected set
extra_ids = actual_ids - expected_device_ids
if extra_ids:
    # Deduct 15 points per extra ID, but not negative overall score
    deduction = min(len(extra_ids) * 15, score)
    score -= deduction
    details.append({
        "item": "no extra devices",
        "score": -deduction,
        "max_score": 0,
        "passed": False,
        "reason": f"Extra device IDs found: {extra_ids}"
    })

# Write final score
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump({"total_score": max(score, 0), "details": details}, f)
