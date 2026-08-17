import sys
import json
import os
from datetime import datetime, timedelta, timezone

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

details = []
total_score = 0

def grade(item, score, max_score, passed, reason):
    global total_score
    total_score += score
    details.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })

# 1. Directory & file existence (10 points)
ops_dir = os.path.join(workspace, "ops")
if os.path.isdir(ops_dir):
    grade("ops/ directory exists", 5, 5, True, "")
else:
    grade("ops/ directory exists", 0, 5, False, "Missing ops/ directory")

schedule_path = os.path.join(ops_dir, "scheduled_interviews.json")
reminder_path = os.path.join(ops_dir, "reminders.json")

schedule_exists = os.path.isfile(schedule_path)
reminder_exists = os.path.isfile(reminder_path)

if schedule_exists:
    grade("scheduled_interviews.json exists", 5, 5, True, "")
else:
    grade("scheduled_interviews.json exists", 0, 5, False, "File not found")

if reminder_exists:
    grade("reminders.json exists", 5, 5, True, "")
else:
    grade("reminders.json exists", 0, 5, False, "File not found")

# Early exit if files missing
if not schedule_exists or not reminder_exists:
    # still allow partial scores
    pass
else:
    # 2. File validity (10 points)
    try:
        with open(schedule_path, "r") as f:
            schedule_data = json.load(f)
        if not isinstance(schedule_data, list):
            grade("scheduled_interviews.json is a JSON array", 0, 5, False, "Root element is not a list")
        else:
            grade("scheduled_interviews.json is a JSON array", 5, 5, True, "")
    except (json.JSONDecodeError, IOError) as e:
        grade("scheduled_interviews.json is valid JSON", 0, 5, False, str(e))

    try:
        with open(reminder_path, "r") as f:
            reminder_data = json.load(f)
        if not isinstance(reminder_data, list):
            grade("reminders.json is a JSON array", 0, 5, False, "Root element is not a list")
        else:
            grade("reminders.json is a JSON array", 5, 5, True, "")
    except (json.JSONDecodeError, IOError) as e:
        grade("reminders.json is valid JSON", 0, 5, False, str(e))

    # 3. Field completeness for each interview (21 points)
    required_interview_fields = ["interview_id", "candidate_id", "job_id", "interviewer", "scheduled_time", "location", "status"]
    if isinstance(schedule_data, list):
        missing_field_count = 0
        for idx, inv in enumerate(schedule_data):
            for field in required_interview_fields:
                if field not in inv:
                    missing_field_count += 1
        if missing_field_count == 0:
            grade("All interview records have every required field", 21, 21, True, "")
        else:
            grade("All interview records have every required field", 0, 21, False, f"{missing_field_count} missing field(s) across records")
    else:
        grade("All interview records have every required field", 0, 21, False, "Could not validate because schedule is not a list")

    # 4. Number of interviews (10 points)
    if isinstance(schedule_data, list):
        num_interviews = len(schedule_data)
        if num_interviews == 3:
            grade("Correct number of interviews (3)", 10, 10, True, "")
        else:
            grade("Correct number of interviews (3)", 0, 10, False, f"Found {num_interviews}, expected 3")
    else:
        grade("Correct number of interviews (3)", 0, 10, False, "Not a list")

    # 5. Number of reminders (10 points)
    if isinstance(reminder_data, list):
        num_reminders = len(reminder_data)
        if num_reminders == 3:
            grade("Correct number of reminders (3)", 10, 10, True, "")
        else:
            grade("Correct number of reminders (3)", 0, 10, False, f"Found {num_reminders}, expected 3")
    else:
        grade("Correct number of reminders (3)", 0, 10, False, "Not a list")

    # 6. Exact content of scheduled interviews (36 points total = 12 per interview)
    # Expected interviews (order by job_id ascending):
    expected_interviews = [
        {
            "job_id": "J001",
            "candidate_id": "C001",
            "scheduled_time": "2025-06-01T10:00:00",
            "location": "Room 101",
            "status": "confirmed",
            "interviewer": "smith@example.com"
        },
        {
            "job_id": "J002",
            "candidate_id": "C002",
            "scheduled_time": "2025-06-01T11:00:00",
            "location": "Room 101",
            "status": "confirmed",
            "interviewer": "smith@example.com"
        },
        {
            "job_id": "J004",
            "candidate_id": "C001",
            "scheduled_time": "2025-06-01T12:00:00",
            "location": "Room 101",
            "status": "confirmed",
            "interviewer": "smith@example.com"
        }
    ]

    if isinstance(schedule_data, list):
        # Sort schedule by scheduled_time to match expected order
        try:
            sorted_schedule = sorted(schedule_data, key=lambda x: x.get("scheduled_time", ""))
        except Exception:
            sorted_schedule = schedule_data

        for idx, exp in enumerate(expected_interviews):
            item_prefix = f"Interview {idx+1} (job {exp['job_id']})"
            if idx >= len(sorted_schedule):
                grade(f"{item_prefix} - all fields correct", 0, 12, False, "Missing interview record")
                continue
            actual = sorted_schedule[idx]
            score_this = 0
            reasons = []
            # Check each field
            for field, expected_val in exp.items():
                actual_val = actual.get(field)
                if actual_val == expected_val:
                    score_this += 2
                else:
                    reasons.append(f"field {field}: expected '{expected_val}', got '{actual_val}'")
            if score_this == 12:
                grade(f"{item_prefix} - all fields correct", 12, 12, True, "")
            else:
                grade(f"{item_prefix} - all fields correct", score_this, 12, False, "; ".join(reasons))
    else:
        grade("Interviews content validation", 0, 36, False, "Not a list")

    # 7. Reminder content (15 points)
    # For each interview, expected reminder_time = scheduled_time - 15min, and matching interview_id
    if isinstance(reminder_data, list) and isinstance(schedule_data, list):
        # Build map from interview_id to scheduled_time
        inv_time_map = {}
        for inv in schedule_data:
            inv_id = inv.get("interview_id")
            st = inv.get("scheduled_time")
            if inv_id and st:
                inv_time_map[inv_id] = st

        correct_reminders = 0
        total_reminder_checks = len(expected_interviews) * 2  # 2 checks per reminder
        errors = []
        # We'll iterate over expected interviews and find matching reminder by interview_id
        for exp in expected_interviews:
            # Find which interview_id corresponds to this job (from schedule)
            matched_inv = None
            for inv in schedule_data:
                if inv.get("job_id") == exp["job_id"]:
                    matched_inv = inv
                    break
            if matched_inv is None:
                errors.append(f"No interview record found for job {exp['job_id']}")
                continue
            inv_id = matched_inv.get("interview_id")
            # Find reminder with that interview_id
            found_reminder = None
            for rem in reminder_data:
                if rem.get("interview_id") == inv_id:
                    found_reminder = rem
                    break
            if found_reminder is None:
                errors.append(f"No reminder for interview_id {inv_id}")
                continue
            # Check reminder_time
            expected_rem_time = (datetime.fromisoformat(exp["scheduled_time"]) - timedelta(minutes=15)).isoformat()
            # Ensure we use same timezone suffix (Z)
            expected_rem_time += "Z"  # because scheduled_time ends with Z
            actual_rem_time = found_reminder.get("reminder_time")
            if actual_rem_time == expected_rem_time:
                correct_reminders += 1
            else:
                errors.append(f"Reminder for {inv_id}: expected time {expected_rem_time}, got {actual_rem_time}")
        if errors:
            grade("All reminders have correct time and matching interview_id", correct_reminders * 5, 15, False, "; ".join(errors))
        else:
            grade("All reminders have correct time and matching interview_id", 15, 15, True, "")
    else:
        grade("Reminders content validation", 0, 15, False, "Could not validate")

# Write score file
score_obj = {
    "total_score": min(total_score, 100),  # cap at 100
    "details": details
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(score_obj, f, indent=2)

print(f"Score: {score_obj['total_score']}/100")
