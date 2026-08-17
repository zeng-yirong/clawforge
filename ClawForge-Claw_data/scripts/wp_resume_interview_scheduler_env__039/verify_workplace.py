import sys
import os
import json
from datetime import datetime, timedelta

def verify(workspace):
    score = 0
    details = []

    # 1. Check file exists (10 points)
    target_path = os.path.join(workspace, "ops/interviews.json")
    if not os.path.isfile(target_path):
        details.append({"item": "ops/interviews.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # early exit because rest can't be checked
        total = sum(d["score"] for d in details)
        return {"total_score": total, "details": details}
    else:
        details.append({"item": "ops/interviews.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File present"})
        score += 10

    # 2. JSON is valid (10 points)
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Root not a list")
        details.append({"item": "Valid JSON array", "score": 10, "max_score": 10, "passed": True, "reason": "Parsed successfully"})
        score += 10
    except Exception as e:
        details.append({"item": "Valid JSON array", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})

    # 3. Each entry has required fields (10 points)
    required_fields = ["candidate_id", "job_id", "interview_date", "interview_time"]
    field_ok = True
    for entry in data:
        for f in required_fields:
            if f not in entry:
                field_ok = False
                break
        if not field_ok:
            break
    if field_ok:
        details.append({"item": "All entries contain required fields", "score": 10, "max_score": 10, "passed": True, "reason": "Fields present"})
        score += 10
    else:
        details.append({"item": "All entries contain required fields", "score": 0, "max_score": 10, "passed": False, "reason": "Missing fields"})

    # 4. Correct job_id (J001) (10 points) – no extra jobs
    job_ids = [e["job_id"] for e in data]
    if all(j == "J001" for j in job_ids):
        details.append({"item": "All interviews for correct job J001", "score": 10, "max_score": 10, "passed": True, "reason": "Job ID consistent"})
        score += 10
    else:
        details.append({"item": "All interviews for correct job J001", "score": 0, "max_score": 10, "passed": False, "reason": "Other job IDs found"})

    # 5. Correct candidates list (full skills match) (30 points)
    # Expected candidates: C001 (first occurrence), C003, C004, C007 (total 4)
    # Note: C001 duplicate with different skills is ignored; C006 lowercase not exact match.
    expected_candidates = {"C001", "C003", "C004", "C007"}
    actual_candidates = set(e["candidate_id"] for e in data)
    if actual_candidates == expected_candidates:
        details.append({"item": "Correct candidate selection", "score": 30, "max_score": 30, "passed": True, "reason": "All and only correct candidates"})
        score += 30
    else:
        missing = expected_candidates - actual_candidates
        extra = actual_candidates - expected_candidates
        reason = f"Missing: {missing}, Extra: {extra}" if missing or extra else "Unknown"
        details.append({"item": "Correct candidate selection", "score": 0, "max_score": 30, "passed": False, "reason": reason})

    # 6. Interview times valid (20 points)
    today = datetime(2025, 3, 10)  # Monday
    next_working_day1 = today + timedelta(days=1)  # Tuesday 2025-03-11
    next_working_day2 = today + timedelta(days=2)  # Wednesday 2025-03-12
    expected_dates = [next_working_day1.strftime("%Y-%m-%d"), next_working_day2.strftime("%Y-%m-%d")]

    time_ok = True
    # Sort entries by candidate_id to ensure consistent order? Actually we need to check order: 4 candidates, 30 min each => first two on day1, last two on day2.
    # But order not specified; we only verify dates and times are within allowed range and consecutive.
    # Simpler: ensure each interview date is one of the two working days, and time is 09:00, 09:30, 10:00, 10:30 (for first two) etc.
    valid_times_day1 = ["09:00", "09:30", "10:00", "10:30"]
    valid_times_day2 = ["09:00", "09:30", "10:00", "10:30"]  # but only first two might be used
    # Check if there are at most 4 entries.
    if len(data) != 4:
        details.append({"item": "Interview time constraints", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected 4 interviews, got {len(data)}"})
        time_ok = False
    else:
        # We need to verify that each interview has a valid date and time slot.
        # Also ensure no duplicate time slots.
        slots_used = set()
        for entry in data:
            d = entry["interview_date"]
            t = entry["interview_time"]
            slot = (d, t)
            if d not in expected_dates:
                time_ok = False
                break
            # time must be one of the valid half-hour slots
            # In a real scenario, the agent should follow first-come-first-serve consecutive.
            # We'll accept any set of 4 slots that are all within business hours (09:00-10:30) and no duplicates.
            valid_times = valid_times_day1 if d == expected_dates[0] else valid_times_day2
            if t not in valid_times:
                time_ok = False
                break
            if slot in slots_used:
                time_ok = False
                break
            slots_used.add(slot)
        if time_ok:
            details.append({"item": "Interview time constraints", "score": 20, "max_score": 20, "passed": True, "reason": "All dates and times valid, no overlap"})
            score += 20
        else:
            details.append({"item": "Interview time constraints", "score": 0, "max_score": 20, "passed": False, "reason": "Invalid date/time or duplicate"})

    # 7. No extra fields (10 points)
    extra_fields_ok = True
    for entry in data:
        if set(entry.keys()) != set(required_fields):
            extra_fields_ok = False
            break
    if extra_fields_ok:
        details.append({"item": "No extra fields", "score": 10, "max_score": 10, "passed": True, "reason": "Only expected fields"})
        score += 10
    else:
        details.append({"item": "No extra fields", "score": 0, "max_score": 10, "passed": False, "reason": "Extra or missing fields"})

    total = min(score, 100)
    return {"total_score": total, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
