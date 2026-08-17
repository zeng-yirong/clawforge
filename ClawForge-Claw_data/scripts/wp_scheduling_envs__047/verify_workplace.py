import sys
import os
import json
import csv
import re

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    max_score = 100
    details = []

    # 1. Check required directories exist (5 pts)
    dirs_ok = True
    for d in ["data", "logs", "ops"]:
        if not os.path.isdir(os.path.join(workspace, d)):
            details.append({"item": f"Directory {d} exists", "score": 0, "max_score": 5, "passed": False, "reason": f"Missing directory {d}"})
            dirs_ok = False
            break
    if dirs_ok:
        details.append({"item": "Required directories exist", "score": 5, "max_score": 5, "passed": True, "reason": "data, logs, ops directories present"})
        score += 5

    # 2. Check ops/schedule_fix.json exists and is valid JSON (10 pts)
    fix_path = os.path.join(workspace, "ops", "schedule_fix.json")
    if not os.path.isfile(fix_path):
        details.append({"item": "ops/schedule_fix.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # Cannot continue
        total = sum(d["score"] for d in details)
        write_score(total, details)
        return total
    try:
        with open(fix_path, "r") as f:
            fix = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        details.append({"item": "Valid JSON in schedule_fix.json", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        total = sum(d["score"] for d in details)
        write_score(total, details)
        return total
    if not isinstance(fix, dict):
        details.append({"item": "schedule_fix.json root is object", "score": 0, "max_score": 10, "passed": False, "reason": "Root must be a JSON object"})
        total = sum(d["score"] for d in details)
        write_score(total, details)
        return total
    details.append({"item": "schedule_fix.json exists and valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "File exists and is valid JSON object"})
    score += 10

    # 3. Required fields present (10 pts)
    required = ["device_id", "action", "new_start_time", "new_end_time"]
    missing = [k for k in required if k not in fix]
    if missing:
        details.append({"item": "Required fields present", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing fields: {missing}"})
        total = sum(d["score"] for d in details)
        write_score(total, details)
        return total
    details.append({"item": "Required fields present", "score": 10, "max_score": 10, "passed": True, "reason": "All required fields present"})
    score += 10

    # 4. Device ID must be the bedroom humidifier (15 pts)
    expected_device = "hum_bed_01"
    actual_device = fix["device_id"]
    if actual_device != expected_device:
        details.append({"item": "Correct device_id", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected {expected_device}, got {actual_device}"})
        total = sum(d["score"] for d in details)
        write_score(total, details)
        return total
    details.append({"item": "Correct device_id", "score": 15, "max_score": 15, "passed": True, "reason": f"device_id is {expected_device}"})
    score += 15

    # 5. Action must be "reschedule" (10 pts)
    expected_action = "reschedule"
    actual_action = fix["action"]
    if actual_action != expected_action:
        details.append({"item": "Correct action", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {expected_action}, got {actual_action}"})
        total = sum(d["score"] for d in details)
        write_score(total, details)
        return total
    details.append({"item": "Correct action", "score": 10, "max_score": 10, "passed": True, "reason": f"action is {expected_action}"})
    score += 10

    # 6. New start and end times must avoid the AC dehumidify block (22:00-23:00)
    # The humidifier run duration is 30 minutes. A valid solution is to set start 21:30, end 22:00.
    # Accept any start that ends <= 22:00 or starts >= 23:00, but must remain within the same day.
    # The schedule days are Mon-Fri, but we ignore days for simplicity.
    # For uniqueness, we require new_start_time="21:30", new_end_time="22:00".
    expected_start = "21:30"
    expected_end = "22:00"
    actual_start = fix["new_start_time"]
    actual_end = fix["new_end_time"]

    # Validate time format HH:MM
    time_pattern = re.compile(r"^\d{2}:\d{2}$")
    if not (time_pattern.match(actual_start) and time_pattern.match(actual_end)):
        details.append({"item": "Valid time formats", "score": 0, "max_score": 10, "passed": False, "reason": f"Time format invalid: start={actual_start}, end={actual_end}"})
        total = sum(d["score"] for d in details)
        write_score(total, details)
        return total

    # Convert to minutes for comparison
    def to_min(t):
        h,m = map(int,t.split(":"))
        return h*60+m

    start_m = to_min(actual_start)
    end_m = to_min(actual_end)

    # Duration should be 30 minutes
    if end_m - start_m != 30:
        details.append({"item": "Correct duration (30 min)", "score": 0, "max_score": 10, "passed": False, "reason": f"Duration is {end_m-start_m} min, expected 30"})
        total = sum(d["score"] for d in details)
        write_score(total, details)
        return total

    # Must end at or before 22:00 (the time AC starts)
    if end_m > 22*60:
        details.append({"item": "End time <= 22:00", "score": 0, "max_score": 10, "passed": False, "reason": f"End time {actual_end} is after 22:00"})
        total = sum(d["score"] for d in details)
        write_score(total, details)
        return total

    # Must start after 20:00 (reasonable evening time) to avoid earlier scheduling issues
    if start_m < 20*60:
        details.append({"item": "Start time >= 20:00", "score": 0, "max_score": 10, "passed": False, "reason": f"Start time {actual_start} is too early"})
        total = sum(d["score"] for d in details)
        write_score(total, details)
        return total

    # Accept only exactly 21:30-22:00 (no other valid range that avoids the AC block)
    # Because AC runs 22:00-23:00, the only 30-min slot before that is 21:30-22:00.
    # (21:00-21:30 would end before the AC, but then it runs too early and may conflict with other schedules? We'll be strict)
    if actual_start != "21:30" or actual_end != "22:00":
        details.append({"item": "Exact correct times (21:30-22:00)", "score": 0, "max_score": 10, "passed": False, "reason": f"Got {actual_start}-{actual_end}, expected 21:30-22:00"})
        total = sum(d["score"] for d in details)
        write_score(total, details)
        return total

    details.append({"item": "New start and end times correct", "score": 10, "max_score": 10, "passed": True, "reason": f"Times {actual_start}-{actual_end} avoid conflict"})
    score += 10

    # All checks passed
    total = sum(d["score"] for d in details)
    write_score(total, details)
    return total

def write_score(total, details):
    result = {"total_score": total, "details": details}
    out_path = os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
