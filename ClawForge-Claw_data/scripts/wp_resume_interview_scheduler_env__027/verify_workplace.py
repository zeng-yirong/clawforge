import sys, os, json, csv, re
from datetime import datetime, timezone, timedelta

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def score():
    results = []
    total = 0
    max_total = 100

    # ---------- 1. Directory structure (10 points) ----------
    # Check ops exists, and the two output files exist
    ops_dir = os.path.join(workspace, "ops")
    schedule_path = os.path.join(ops_dir, "interview_schedule.json")
    reminder_path = os.path.join(ops_dir, "reminder_entries.csv")

    dir_check = os.path.isdir(ops_dir)
    sched_exists = os.path.isfile(schedule_path)
    rem_exists = os.path.isfile(reminder_path)
    if dir_check and sched_exists and rem_exists:
        results.append({"item": "Directory and output files exist", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ contains both required files."})
        total += 10
    else:
        missing = []
        if not dir_check: missing.append("ops directory")
        if not sched_exists: missing.append("interview_schedule.json")
        if not rem_exists: missing.append("reminder_entries.csv")
        results.append({"item": "Directory and output files exist", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing: {', '.join(missing)}"})

    # ---------- 2. Schema validity (15 points) ----------
    if sched_exists and rem_exists:
        try:
            with open(schedule_path, "r") as f:
                schedule = json.load(f)
            sched_valid = isinstance(schedule, dict)
            required_sched_keys = {"schedule_id", "job_id", "candidate_id", "interviewer_id", "interview_time", "status"}
            has_keys = sched_valid and required_sched_keys.issubset(schedule.keys())
            if has_keys:
                results.append({"item": "interview_schedule.json schema valid", "score": 8, "max_score": 8, "passed": True, "reason": "All required keys present."})
                total += 8
            else:
                results.append({"item": "interview_schedule.json schema valid", "score": 0, "max_score": 8, "passed": False, "reason": "Missing one or more required keys."})
        except Exception as e:
            results.append({"item": "interview_schedule.json schema valid", "score": 0, "max_score": 8, "passed": False, "reason": f"Not valid JSON: {str(e)}"})

        try:
            with open(reminder_path, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            rem_valid = len(rows) >= 1
            required_rem_keys = {"schedule_id", "remind_at", "recipient_email", "message"}
            if rows:
                headers_ok = required_rem_keys.issubset(rows[0].keys())
            else:
                headers_ok = False
            if rem_valid and headers_ok:
                results.append({"item": "reminder_entries.csv schema valid", "score": 7, "max_score": 7, "passed": True, "reason": "CSV has correct headers and at least 1 row."})
                total += 7
            else:
                results.append({"item": "reminder_entries.csv schema valid", "score": 0, "max_score": 7, "passed": False, "reason": "Missing headers or empty."})
        except Exception as e:
            results.append({"item": "reminder_entries.csv schema valid", "score": 0, "max_score": 7, "passed": False, "reason": f"Not valid CSV: {str(e)}"})
    else:
        # already failed, give 0 for these
        results.append({"item": "interview_schedule.json schema valid", "score": 0, "max_score": 8, "passed": False, "reason": "File missing"})
        results.append({"item": "reminder_entries.csv schema valid", "score": 0, "max_score": 7, "passed": False, "reason": "File missing"})

    # ---------- 3. Content correctness (75 points) ----------
    if sched_exists and rem_exists:
        try:
            with open(schedule_path, "r") as f:
                schedule = json.load(f)
        except:
            schedule = {}
        try:
            with open(reminder_path, "r") as f:
                reader = csv.DictReader(f)
                rem_rows = list(reader)
        except:
            rem_rows = []

        # 3a. Job ID must be J001 (Senior Software Engineer) (10 points)
        job_correct = schedule.get("job_id") == "J001"
        results.append({"item": "Job ID is the open Senior Software Engineer", "score": 10 if job_correct else 0, "max_score": 10, "passed": job_correct, "reason": f"Found job_id={schedule.get('job_id')}"})
        total += 10 if job_correct else 0

        # 3b. Candidate ID must be C003 (Alice Wang) (15 points)
        cand_correct = schedule.get("candidate_id") == "C003"
        results.append({"item": "Candidate ID is C003 (correct match)", "score": 15 if cand_correct else 0, "max_score": 15, "passed": cand_correct, "reason": f"Found candidate_id={schedule.get('candidate_id')}"})
        total += 15 if cand_correct else 0

        # 3c. Interviewer ID must be M001 (the hiring_manager from J001) (10 points)
        interviewer_correct = schedule.get("interviewer_id") == "M001"
        results.append({"item": "Interviewer ID is M001 (hiring manager)", "score": 10 if interviewer_correct else 0, "max_score": 10, "passed": interviewer_correct, "reason": f"Found interviewer_id={schedule.get('interviewer_id')}"})
        total += 10 if interviewer_correct else 0

        # 3d. Interview time: must be tomorrow at 10:00 UTC (20 points)
        try:
            interview_time_str = schedule.get("interview_time", "")
            # parse ISO format
            dt = datetime.fromisoformat(interview_time_str)
            utc_now = datetime.now(timezone.utc)
            tomorrow = utc_now.date() + timedelta(days=1)
            expected_hour = 10
            time_correct = (dt.year == tomorrow.year and dt.month == tomorrow.month and dt.day == tomorrow.day
                            and dt.hour == expected_hour and dt.minute == 0 and dt.tzinfo is not None)
            if time_correct:
                results.append({"item": "Interview time is tomorrow 10:00 UTC", "score": 20, "max_score": 20, "passed": True, "reason": "Time matches."})
                total += 20
            else:
                results.append({"item": "Interview time is tomorrow 10:00 UTC", "score": 0, "max_score": 20, "passed": False, "reason": f"Got {interview_time_str}, expected tomorrow 10:00 UTC"})
        except Exception as e:
            results.append({"item": "Interview time is tomorrow 10:00 UTC", "score": 0, "max_score": 20, "passed": False, "reason": f"Parse error: {str(e)}"})

        # 3e. Reminder content (20 points)
        # Must have exactly one row, schedule_id matching JSON, remind_at = interview_time - 15min, recipient_email = smith@company.com, message non-empty
        if rem_rows:
            row = rem_rows[0]
            sched_id = schedule.get("schedule_id", "")
            rem_id_match = row.get("schedule_id", "") == sched_id
            # remind_at should be 15 minutes before interview_time
            try:
                remind_dt = datetime.fromisoformat(row.get("remind_at", ""))
                interview_dt = datetime.fromisoformat(schedule.get("interview_time", ""))
                delta = interview_dt - remind_dt
                delta_correct = (delta.total_seconds() == 15 * 60)
            except:
                delta_correct = False
            recipient_correct = row.get("recipient_email", "") == "smith@company.com"
            message_present = bool(row.get("message", "").strip())
            reminder_score = 0
            reason_parts = []
            if rem_id_match:
                reminder_score += 5
            else:
                reason_parts.append("schedule_id mismatch")
            if delta_correct:
                reminder_score += 5
            else:
                reason_parts.append("remind_at not 15 min before interview")
            if recipient_correct:
                reminder_score += 5
            else:
                reason_parts.append("recipient_email not smith@company.com")
            if message_present:
                reminder_score += 5
            else:
                reason_parts.append("message empty")
            results.append({"item": "Reminder entry content correct", "score": reminder_score, "max_score": 20, "passed": reminder_score == 20, "reason": " ; ".join(reason_parts) if reason_parts else "All checks passed."})
            total += reminder_score
        else:
            results.append({"item": "Reminder entry content correct", "score": 0, "max_score": 20, "passed": False, "reason": "No rows found."})
    else:
        # fill zeros
        for i in range(5):
            results.append({"item": f"Content check {i+1}", "score": 0, "max_score": [10,15,10,20,20][i], "passed": False, "reason": "Required files missing."})

    # Ensure total_score integer between 0 and 100
    total_score = min(100, total)
    output = {"total_score": total_score, "details": results}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(output, f, indent=2)
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    score()
