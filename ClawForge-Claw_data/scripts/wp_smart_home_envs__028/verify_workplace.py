import sys
import os
import json

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def verify(workspace):
    details = []
    total_score = 0

    # 1. Check required directories and files exist (10 points)
    required_paths = [
        os.path.join(workspace, "data", "health.json"),
        os.path.join(workspace, "data", "devices.json"),
        os.path.join(workspace, "ops", "health_adjustments.json")
    ]
    all_exist = True
    for p in required_paths:
        if not os.path.exists(p):
            all_exist = False
            details.append({
                "item": f"File exists: {os.path.relpath(p, workspace)}",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Missing {os.path.relpath(p, workspace)}"
            })
        else:
            details.append({
                "item": f"File exists: {os.path.relpath(p, workspace)}",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "Found"
            })
    if all_exist:
        total_score += 10

    # If any required file missing, skip further checks
    if not all_exist:
        total_score = 0
        details.insert(0, {"item": "Total score", "score": 0, "max_score": 100, "passed": False, "reason": "Core files missing"})
        write_score(workspace, total_score, details)
        return

    # 2. Validate JSON parsing and structure (10 points)
    try:
        health_data = load_json(os.path.join(workspace, "data", "health.json"))
        devices_data = load_json(os.path.join(workspace, "data", "devices.json"))
        agent_result = load_json(os.path.join(workspace, "ops", "health_adjustments.json"))
        # Check top-level wrappers
        if "users" not in health_data or "devices" not in devices_data:
            raise ValueError("Missing wrapper keys")
        details.append({"item": "JSON parsing & wrappers", "score": 10, "max_score": 10, "passed": True, "reason": "All valid"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON parsing & wrappers", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        total_score = 10  # only got existence points
        write_score(workspace, total_score, details)
        return

    # 3. Verify that agent_output is a list (or dict with a list) – we expect a list of adjustments (20 points)
    if isinstance(agent_result, list):
        adjustments = agent_result
    elif isinstance(agent_result, dict):
        # try common wrapper key
        adjustments = agent_result.get("adjustments", agent_result.get("devices", None))
        if adjustments is None:
            details.append({"item": "Agent output format", "score": 0, "max_score": 20, "passed": False, "reason": "Not a list or dict containing 'adjustments' or 'devices' list"})
            total_score += 0
            write_score(workspace, total_score, details)
            return
    else:
        details.append({"item": "Agent output format", "score": 0, "max_score": 20, "passed": False, "reason": "Not a list or dict"})
        total_score += 0
        write_score(workspace, total_score, details)
        return

    format_ok = isinstance(adjustments, list) and all(
        isinstance(item, dict) and "device_id" in item and "recommended_temperature" in item
        for item in adjustments
    )
    if not format_ok:
        details.append({"item": "Agent output format", "score": 0, "max_score": 20, "passed": False, "reason": "Each item must have 'device_id' and 'recommended_temperature'"})
        write_score(workspace, total_score, details)
        return
    details.append({"item": "Agent output format", "score": 20, "max_score": 20, "passed": True, "reason": "Valid list structure"})
    total_score += 20

    # 4. Compute ground truth from health and devices (30 points – correctness)
    # Build location-to-user map
    user_by_location = {}
    for user in health_data["users"]:
        loc = user.get("location", None)
        if loc:
            user_by_location[loc] = user

    # Build list of AC devices that need adjustment
    expected_adjustments = []
    for dev in devices_data["devices"]:
        if dev["type"] != "air_conditioner":
            continue
        loc = dev.get("location", None)
        if not loc or loc not in user_by_location:
            continue
        user = user_by_location[loc]
        target_temp = user["temperature_preference"]["target"]
        current_temp = dev["default_settings"]["temperature"]
        if abs(current_temp - target_temp) > 0.01:  # consider float tolerance
            expected_adjustments.append({
                "device_id": dev["device_id"],
                "recommended_temperature": target_temp
            })

    # Sort both lists by device_id for comparison
    expected_sorted = sorted(expected_adjustments, key=lambda x: x["device_id"])
    agent_sorted = sorted(adjustments, key=lambda x: x["device_id"])

    if len(expected_sorted) != len(agent_sorted):
        details.append({"item": "Adjustment correctness (count)", "score": 0, "max_score": 30, "passed": False, "reason": f"Expected {len(expected_sorted)} adjustments, got {len(agent_sorted)}"})
        total_score += 0
        write_score(workspace, total_score, details)
        return

    match = True
    for e, a in zip(expected_sorted, agent_sorted):
        if e["device_id"] != a["device_id"] or abs(e["recommended_temperature"] - a["recommended_temperature"]) > 0.01:
            match = False
            break
    if match:
        details.append({"item": "Adjustment correctness", "score": 30, "max_score": 30, "passed": True, "reason": f"All {len(expected_sorted)} adjustments correct"})
        total_score += 30
    else:
        details.append({"item": "Adjustment correctness", "score": 0, "max_score": 30, "passed": False, "reason": "Mismatch with expected values"})
        total_score += 0

    # 5. Extra: no extra devices (20 points) – check that agent didn't include non-AC or irrelevant
    extra = [adj for adj in adjustments if adj["device_id"] not in {e["device_id"] for e in expected_sorted}]
    if extra:
        details.append({"item": "No extra adjustments", "score": 0, "max_score": 20, "passed": False, "reason": f"Found unexpected device(s): {[e['device_id'] for e in extra]}"})
        total_score += 0
    else:
        details.append({"item": "No extra adjustments", "score": 20, "max_score": 20, "passed": True, "reason": "Only expected devices"})
        total_score += 20

    write_score(workspace, total_score, details)

def write_score(workspace, total, details):
    result = {"total_score": total, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
