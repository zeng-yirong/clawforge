import sys
import json
import os
import math
from pathlib import Path

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def verify():
    # cwd: workspace root (assets/wp_smart_home_envs__016/)
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)
    
    score_details = []
    total_score = 0

    # 1. Check output directory exists (5 points)
    out_dir = Path("output")
    if out_dir.exists() and out_dir.is_dir():
        score_details.append({"item": "output directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "Found output/ directory"})
        total_score += 5
    else:
        score_details.append({"item": "output directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "output/ directory not found"})

    # 2. Check report file exists (10 points)
    report_path = out_dir / "health_conflicts_report.json"
    if report_path.exists() and report_path.is_file():
        score_details.append({"item": "report file exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found output/health_conflicts_report.json"})
        total_score += 10
    else:
        score_details.append({"item": "report file exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # skip further checks if file missing
        write_results(score_details, total_score)
        return

    # 3. JSON valid and has top-level structure (10 points)
    try:
        report = load_json(report_path)
        score_details.append({"item": "report JSON valid", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON"})
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        score_details.append({"item": "report JSON valid", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {str(e)}"})
        write_results(score_details, total_score)
        return

    # Check that report is a list or contains a list under some key? Expect a list of conflicts.
    # We'll accept either a top-level list or an object with a 'conflicts' key.
    conflicts = None
    if isinstance(report, list):
        conflicts = report
    elif isinstance(report, dict):
        conflicts = report.get("conflicts", None)
        if not isinstance(conflicts, list):
            conflicts = None

    if conflicts is None:
        score_details.append({"item": "report structure", "score": 0, "max_score": 10, "passed": False, "reason": "Report should be a list or contain a 'conflicts' list"})
        write_results(score_details, total_score)
        return
    else:
        score_details.append({"item": "report structure", "score": 10, "max_score": 10, "passed": True, "reason": "Conflicts list found"})
        total_score += 10

    # 4. Count and identify conflicts (60 points total)
    # Expected conflicts based on builder data:
    #   - hum_bedroom_01: target_humidity=60, John's max=50 -> conflict type humidity, recommended 50
    #   - ac_living_01: target_temp_c=26, Jane's temp max=24 -> conflict type temperature, recommended 24
    # (Note: ac_bedroom_01 target 23, John's range 20-22 -> conflict temperature, recommended 22? 
    #   Let's also include that one for richer scoring.)
    # Builder sets John's temp_pref min=20 max=22, current 23 -> conflict.
    # So three conflicts expected.
    
    expected_conflicts = {
        "hum_bedroom_01": {"type": "humidity", "current": 60, "recommended": 50},
        "ac_living_01": {"type": "temperature", "current": 26, "recommended": 24},
        "ac_bedroom_01": {"type": "temperature", "current": 23, "recommended": 22}
    }

    found_device_ids = set()
    partial_score = 0
    max_partial = 60  # 20 per conflict

    for conflict in conflicts:
        if not isinstance(conflict, dict):
            continue
        device_id = conflict.get("device_id")
        if not device_id or device_id not in expected_conflicts:
            continue
        found_device_ids.add(device_id)
        exp = expected_conflicts[device_id]
        # Score each recognized conflict: check type, current, recommended
        conflict_type = conflict.get("type")
        current_val = conflict.get("current_value")
        recommended_val = conflict.get("recommended_value")
        if (conflict_type == exp["type"] and
            current_val == exp["current"] and
            recommended_val == exp["recommended"]):
            partial_score += 20
            reason = f"Conflict for {device_id} perfectly matches"
        elif (conflict_type == exp["type"] and current_val == exp["current"] and recommended_val is not None and abs(recommended_val - exp["recommended"]) <= 1):
            # Accept slight rounding differences
            partial_score += 15
            reason = f"Conflict for {device_id} matched type/current but recommended slightly off"
        else:
            partial_score += 10 if conflict_type == exp["type"] else 0
            reason = f"Conflict for {device_id} partially correct"

        score_details.append({"item": f"Conflict: {device_id}", "score": 20 if (conflict_type == exp["type"] and current_val == exp["current"] and recommended_val == exp["recommended"]) else (15 if (conflict_type == exp["type"] and current_val == exp["current"]) else 10 if conflict_type == exp["type"] else 0), "max_score": 20, "passed": True, "reason": reason})
        # we'll adjust later

    # If some expected conflicts missing, deduct
    missing = set(expected_conflicts.keys()) - found_device_ids
    for missing_id in missing:
        score_details.append({"item": f"Missing conflict: {missing_id}", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected conflict for {missing_id} not found"})

    total_score += partial_score

    # 5. No extra incorrect conflicts (penalize if extra wrong device reported as conflict)
    extra_devices = [c.get("device_id") for c in conflicts if isinstance(c, dict) and c.get("device_id") not in expected_conflicts]
    if extra_devices:
        penalty = min(5 * len(extra_devices), 10)
        total_score -= penalty
        score_details.append({"item": "No spurious conflicts", "score": -penalty, "max_score": 0, "passed": True, "reason": f"Found extra device(s): {extra_devices}"})
    else:
        score_details.append({"item": "No spurious conflicts", "score": 0, "max_score": 0, "passed": True, "reason": "No extra devices reported"})

    # Clamp total to 0-100
    total_score = max(0, min(100, total_score))

    # Add penalty details if any (already done)

    write_results(score_details, total_score)

def write_results(details, total):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {total}/100")

if __name__ == "__main__":
    verify()
