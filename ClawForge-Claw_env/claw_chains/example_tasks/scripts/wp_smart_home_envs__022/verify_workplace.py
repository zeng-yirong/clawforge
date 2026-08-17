"""
Verify the agent's output for smart home climate conflict detection.
Checks that ops/conflicts.json contains correct list of devices whose current
settings (temperature/humidity) fall outside Jane Smith's health preferences.
Scoring based on completeness, correctness, and format.
"""
import sys
import os
import json
import math

def load_json_rel(path):
    full = os.path.join(workspace, path)
    if not os.path.exists(full):
        return None
    with open(full, 'r') as f:
        return json.load(f)

def read_file_rel(path):
    full = os.path.join(workspace, path)
    if not os.path.isfile(full):
        return None
    with open(full, 'r') as f:
        return f.read()

def main():
    global workspace
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total = 0

    # 1. Check ops/ directory exists (5 points)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        score_details.append({
            "item": "ops directory exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Directory ops/ found."
        })
        total += 5
    else:
        score_details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "Missing ops/ directory."
        })

    # 2. Check conflicts.json exists & is valid JSON (10 points)
    conflicts_path = os.path.join(workspace, "ops/conflicts.json")
    if os.path.isfile(conflicts_path):
        try:
            with open(conflicts_path, 'r') as f:
                agent_data = json.load(f)
            status = "valid"
        except json.JSONDecodeError:
            status = "invalid"
        if status == "valid":
            score_details.append({
                "item": "conflicts.json format",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "File is valid JSON."
            })
            total += 10
        else:
            score_details.append({
                "item": "conflicts.json format",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "File is not valid JSON."
            })
    else:
        score_details.append({
            "item": "conflicts.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/conflicts.json not found."
        })
        # Cannot proceed further
        final_score = total
        write_score(final_score, score_details)
        return

    # 3. Agent output must be a list (10 points)
    if not isinstance(agent_data, list):
        score_details.append({
            "item": "conflicts.json top-level structure",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Expected a JSON array (list) at root."
        })
        final_score = total
        write_score(final_score, score_details)
        return
    else:
        score_details.append({
            "item": "conflicts.json top-level structure",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Root is a list."
        })
        total += 10

    # 4. Load ground truth from env data (recalculate expected conflicts)
    health = load_json_rel("data/health/health.json")
    if health is None:
        score_details.append({
            "item": "Ground truth data",
            "score": 0,
            "max_score": 0,
            "passed": False,
            "reason": "Cannot read health.json for verification."
        })
        write_score(total, score_details)
        return

    # Find Jane
    jane = None
    for u in health.get("users", []):
        if u.get("name") == "Jane Smith":
            jane = u
            break
    if jane is None:
        score_details.append({
            "item": "Jane's health profile",
            "score": 0,
            "max_score": 0,
            "passed": False,
            "reason": "Jane Smith not found in health.json"
        })
        write_score(total, score_details)
        return

    temp_min = jane["temperature_preference"]["min"]
    temp_max = jane["temperature_preference"]["max"]
    hum_min = jane["humidity_preference"]["min"]
    hum_max = jane["humidity_preference"]["max"]

    # Load device statuses
    statuses = load_json_rel("data/status/device_status.json")
    if statuses is None:
        score_details.append({
            "item": "Ground truth data",
            "score": 0,
            "max_score": 0,
            "passed": False,
            "reason": "Cannot read device_status.json"
        })
        write_score(total, score_details)
        return

    # Load devices to map device_id to name & type
    devices_data = load_json_rel("data/devices/devices.json")
    if devices_data is None:
        score_details.append({
            "item": "Ground truth data",
            "score": 0,
            "max_score": 0,
            "passed": False,
            "reason": "Cannot read devices.json"
        })
        write_score(total, score_details)
        return
    device_dict = {}
    for d in devices_data.get("devices", []):
        device_dict[d["device_id"]] = d

    # Compute expected conflicts: only powered-on ACs and Humidifiers, check temp/humidity
    expected_conflicts = []
    for st in statuses.get("statuses", []):
        did = st["device_id"]
        if did not in device_dict:
            continue
        dev = device_dict[did]
        dev_type = dev["type"]
        if dev_type not in ("air_conditioner", "humidifier"):
            continue  # skip smart plugs
        if not st.get("power_on", False):
            continue  # device off, no conflict
        # Check temperature for AC
        if dev_type == "air_conditioner":
            current_temp = st.get("current_temperature")
            if current_temp is not None:
                if current_temp < temp_min or current_temp > temp_max:
                    expected_conflicts.append({
                        "device_id": did,
                        "device_name": dev["name"],
                        "parameter": "temperature",
                        "current_value": current_temp,
                        "expected_range": f"{temp_min}-{temp_max}°C"
                    })
        # Check humidity for humidifier
        if dev_type == "humidifier":
            current_hum = st.get("current_humidity")
            if current_hum is not None:
                if current_hum < hum_min or current_hum > hum_max:
                    expected_conflicts.append({
                        "device_id": did,
                        "device_name": dev["name"],
                        "parameter": "humidity",
                        "current_value": current_hum,
                        "expected_range": f"{hum_min}-{hum_max}%"
                    })

    # Now compare agent data with expected
    # For each expected conflict, check if it appears in agent list (ignoring order, extra fields ok)
    # We'll give 40 points for correct identification (each conflict ~20 points, there are 2)
    correct_found = 0
    wrong_extra = 0
    # Normalize agent output: we treat each entry as dict with at least device_id and parameter
    agent_entries = []
    for entry in agent_data:
        if isinstance(entry, dict) and "device_id" in entry and "parameter" in entry:
            agent_entries.append(entry)
        else:
            wrong_extra += 1  # malformed or missing required fields

    # Check each expected
    for exp in expected_conflicts:
        matched = False
        for ag in agent_entries:
            if ag.get("device_id") == exp["device_id"] and ag.get("parameter") == exp["parameter"]:
                # Also check current_value (allow floating point tolerance)
                cv_agent = ag.get("current_value")
                cv_exp = exp["current_value"]
                if cv_agent is not None and isinstance(cv_agent, (int, float)):
                    if math.isclose(cv_agent, cv_exp, rel_tol=1e-6):
                        matched = True
                        break
                # If not matching exactly, still consider if value is close enough? we require exact from builder
        if matched:
            correct_found += 1
        else:
            # Agent missed this conflict
            pass

    # Check for extra entries that are not in expected
    extra_entries = []
    for ag in agent_entries:
        found_in_exp = False
        for exp in expected_conflicts:
            if ag.get("device_id") == exp["device_id"] and ag.get("parameter") == exp["parameter"]:
                found_in_exp = True
                break
        if not found_in_exp:
            extra_entries.append(ag)

    # Scoring
    if not expected_conflicts:
        # No conflicts expected (should not happen in our scenario)
        conflict_score = 40
        reason = "No conflicts expected, agent correctly reported none."
    else:
        # 40 points for correct detection: each correct -> 40/len(expected)
        per_conflict = 40.0 / len(expected_conflicts)
        conflict_score = round(correct_found * per_conflict)

    # Deduct for extra entries (max 10 points penalty)
    extra_penalty = min(10, len(extra_entries) * 5)  # 5 per extra entry
    conflict_score = max(0, conflict_score - extra_penalty)

    if conflict_score >= 40:
        conflict_passed = True
    else:
        conflict_passed = False

    score_details.append({
        "item": "Conflict identification accuracy",
        "score": conflict_score,
        "max_score": 40,
        "passed": conflict_passed,
        "reason": f"Expected {len(expected_conflicts)} conflicts, detected {correct_found} correct, {len(extra_entries)} extra entries."
    })
    total += conflict_score

    # 5. Field completeness (15 points): each entry must have device_id, parameter, current_value, expected_range
    # Check all entries in agent list
    completeness_score = 0
    required_fields = ["device_id", "parameter", "current_value", "expected_range"]
    entries_checked = 0
    for entry in agent_data:
        if not isinstance(entry, dict):
            continue
        entries_checked += 1
        if all(field in entry for field in required_fields):
            completeness_score += 1
    max_completeness = max(len(agent_data), 1)  # at least 1
    completeness_pct = completeness_score / max(entries_checked, 1) * 100
    comp_score = round(15 * (completeness_pct / 100.0))
    if comp_score == 15:
        comp_passed = True
    else:
        comp_passed = False
    score_details.append({
        "item": "Field completeness (required: device_id, parameter, current_value, expected_range)",
        "score": comp_score,
        "max_score": 15,
        "passed": comp_passed,
        "reason": f"{completeness_score}/{max(entries_checked,1)} entries have all required fields."
    })
    total += comp_score

    # 6. No extra unrelated devices (10 points) – bonus for not including smart_plugs or off devices
    # We'll check that no entry has device_id of a smart_plug or a device that is off.
    penalty_extra_devices = 0
    for entry in agent_data:
        if isinstance(entry, dict):
            did = entry.get("device_id")
            if did and did in device_dict:
                dev_type = device_dict[did]["type"]
                if dev_type == "smart_plug":
                    penalty_extra_devices += 5
            # also check if device is powered off in status
            if did:
                for st in statuses.get("statuses", []):
                    if st["device_id"] == did and not st.get("power_on", False):
                        penalty_extra_devices += 5
                        break
    extra_dev_score = max(0, 10 - penalty_extra_devices)
    if extra_dev_score == 10:
        extra_dev_passed = True
    else:
        extra_dev_passed = False
    score_details.append({
        "item": "No irrelevant devices (smart plugs or powered-off devices)",
        "score": extra_dev_score,
        "max_score": 10,
        "passed": extra_dev_passed,
        "reason": f"Penalty deducted: {penalty_extra_devices} points for irrelevant entries."
    })
    total += extra_dev_score

    # Ensure total is 0-100
    final_score = min(100, max(0, total))
    write_score(final_score, score_details)

def write_score(total, details):
    output = {
        "total_score": int(total),
        "details": details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
