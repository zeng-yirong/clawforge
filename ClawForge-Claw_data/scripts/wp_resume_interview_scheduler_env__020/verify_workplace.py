import json
import os
import sys
import re
from pathlib import Path

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    score = 0
    details = []

    # --- Check required directories exist (10 points) ---
    required_dirs = ["schedules", "reminders", "data/candidates", "data/jobs"]
    for d in required_dirs:
        p = ws / d
        exists = p.is_dir()
        if exists:
            score += 2.5
            details.append({
                "item": f"Directory '{d}' exists",
                "score": 2.5,
                "max_score": 2.5,
                "passed": True,
                "reason": "Found"
            })
        else:
            details.append({
                "item": f"Directory '{d}' exists",
                "score": 0,
                "max_score": 2.5,
                "passed": False,
                "reason": f"Missing directory: {p}"
            })

    # --- Check schedule file existence and format (20 points) ---
    schedule_path = ws / "schedules" / "interview_C-002_JOB-2024-007.json"
    schedule_ok = False
    schedule_data = None
    try:
        schedule_data = load_json(schedule_path)
        schedule_ok = True
    except Exception as e:
        details.append({
            "item": "Schedule file for C-002 & JOB-2024-007 exists and is valid JSON",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"File not found or invalid JSON: {e}"
        })

    if schedule_ok:
        # Check required fields
        required_fields = ["candidate_id", "job_id", "interview_date", "interview_time", "duration_minutes"]
        missing_fields = [f for f in required_fields if f not in schedule_data]
        extra_fields = [k for k in schedule_data if k not in required_fields]

        field_score = 0
        field_reasons = []
        if not missing_fields:
            field_score += 8
            field_reasons.append("All required fields present")
        else:
            field_reasons.append(f"Missing fields: {missing_fields}")

        # Check exact values
        exact_checks = {
            "candidate_id": "C-002",
            "job_id": "JOB-2024-007",
            "interview_date": "2025-06-15",
            "interview_time": "14:00",
            "duration_minutes": 60
        }
        all_correct = True
        for field, expected in exact_checks.items():
            actual = schedule_data.get(field)
            if actual != expected:
                all_correct = False
                field_reasons.append(f"Field '{field}' expected '{expected}', got '{actual}'")
            else:
                field_reasons.append(f"Field '{field}' correct")
        if all_correct:
            field_score += 12
            field_reasons.append("All field values correct")
        else:
            field_score += 0
            # partial credit? we'll give 0 for any mismatch to keep strict

        details.append({
            "item": "Schedule file content fields and values",
            "score": field_score,
            "max_score": 20,
            "passed": field_score == 20,
            "reason": "; ".join(field_reasons)
        })
        score += field_score
    else:
        score += 0
        details[-1]["max_score"] = 20

    # --- Check reminder file existence and format (20 points) ---
    reminder_path = ws / "reminders" / "reminder_C-002_JOB-2024-007.json"
    reminder_ok = False
    reminder_data = None
    try:
        reminder_data = load_json(reminder_path)
        reminder_ok = True
    except Exception as e:
        details.append({
            "item": "Reminder file for C-002 & JOB-2024-007 exists and is valid JSON",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"File not found or invalid JSON: {e}"
        })

    if reminder_ok:
        required_reminder_fields = ["candidate_id", "job_id", "reminder_date", "reminder_time"]
        missing_rem = [f for f in required_reminder_fields if f not in reminder_data]
        extra_rem = [k for k in reminder_data if k not in required_reminder_fields]

        rem_field_score = 0
        rem_reasons = []
        if not missing_rem:
            rem_field_score += 8
            rem_reasons.append("All required fields present")
        else:
            rem_reasons.append(f"Missing fields: {missing_rem}")

        # Check exact values: reminder should be 30 minutes before 14:00 => 13:30 on same day
        rem_exact = {
            "candidate_id": "C-002",
            "job_id": "JOB-2024-007",
            "reminder_date": "2025-06-15",
            "reminder_time": "13:30"
        }
        rem_all_correct = True
        for field, expected in rem_exact.items():
            actual = reminder_data.get(field)
            if actual != expected:
                rem_all_correct = False
                rem_reasons.append(f"Field '{field}' expected '{expected}', got '{actual}'")
            else:
                rem_reasons.append(f"Field '{field}' correct")
        if rem_all_correct:
            rem_field_score += 12
            rem_reasons.append("All field values correct")
        else:
            rem_field_score += 0

        details.append({
            "item": "Reminder file content fields and values",
            "score": rem_field_score,
            "max_score": 20,
            "passed": rem_field_score == 20,
            "reason": "; ".join(rem_reasons)
        })
        score += rem_field_score
    else:
        score += 0
        details[-1]["max_score"] = 20

    # --- Check that no other interview schedule files were created for other candidates (30 points) ---
    # The only valid schedule should be for C-002 + JOB-2024-007. If extra files exist, deduct.
    schedule_dir = ws / "schedules"
    valid_schedule_files = {"interview_C-002_JOB-2024-007.json"}
    extra_schedule_files = set()
    if schedule_dir.is_dir():
        for f in schedule_dir.iterdir():
            if f.is_file() and f.name not in valid_schedule_files and f.suffix == ".json":
                extra_schedule_files.add(f.name)
    if extra_schedule_files:
        details.append({
            "item": "No extra schedule files for other candidates",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"Found extra schedule files: {extra_schedule_files}"
        })
        score += 0
    else:
        details.append({
            "item": "No extra schedule files for other candidates",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": "Only expected schedule file present"
        })
        score += 30

    # --- Check that no other reminder files for other candidates (10 points) ---
    reminder_dir = ws / "reminders"
    valid_reminder_files = {"reminder_C-002_JOB-2024-007.json"}
    extra_reminder_files = set()
    if reminder_dir.is_dir():
        for f in reminder_dir.iterdir():
            if f.is_file() and f.name not in valid_reminder_files and f.suffix == ".json":
                extra_reminder_files.add(f.name)
    if extra_reminder_files:
        details.append({
            "item": "No extra reminder files for other candidates",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Found extra reminder files: {extra_reminder_files}"
        })
        score += 0
    else:
        details.append({
            "item": "No extra reminder files for other candidates",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Only expected reminder file present"
        })
        score += 10

    # --- Additional checks: candidate skills correctly matched (10 points) ---
    # Verify that candidate C-002 indeed has the required skills for job JOB-2024-007
    # This tests if the agent did the right reasoning (though we can't fully test, but we can cross-check)
    try:
        candidates_path = ws / "data" / "candidates" / "candidates.json"
        jobs_path = ws / "data" / "jobs" / "jobs.json"
        candidates_data = load_json(candidates_path)["candidates"]
        jobs_data = load_json(jobs_path)["jobs"]
        job = None
        for j in jobs_data:
            if j["job_id"] == "JOB-2024-007":
                job = j
                break
        candidate = None
        for c in candidates_data:
            if c["candidate_id"] == "C-002":
                candidate = c
                break
        if job and candidate:
            required = set(job["required_skills"])
            actual = set(candidate["skills"])
            if required.issubset(actual):
                details.append({
                    "item": "Candidate C-002 skills cover all required skills of JOB-2024-007",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": "Skills match"
                })
                score += 10
            else:
                details.append({
                    "item": "Candidate C-002 skills cover all required skills of JOB-2024-007",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": f"Missing skills: {required - actual}"
                })
        else:
            details.append({
                "item": "Candidate C-002 skills cover all required skills of JOB-2024-007",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "Could not load candidate or job data"
            })
    except Exception as e:
        details.append({
            "item": "Candidate C-002 skills cover all required skills of JOB-2024-007",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Error reading data files: {e}"
        })

    total_score = min(100, int(score))  # cap at 100
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total_score}/100")

if __name__ == "__main__":
    verify()
