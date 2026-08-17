import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def check_file_exists(path):
    return os.path.isfile(os.path.join(workspace, path))

def main():
    results = []
    total_score = 0

    # 1. ops/ directory existence (10 pts)
    ops_dir = os.path.join(workspace, "ops")
    ops_exists = os.path.isdir(ops_dir)
    results.append({
        "item": "ops/ directory exists",
        "score": 10 if ops_exists else 0,
        "max_score": 10,
        "passed": ops_exists,
        "reason": "Directory ops/ found" if ops_exists else "Directory ops/ missing"
    })
    total_score += 10 if ops_exists else 0

    # 2. ops/interviews.json exists and valid JSON (10 pts)
    interview_path = os.path.join(workspace, "ops", "interviews.json")
    interview_exists = check_file_exists("ops/interviews.json")
    interview_ok = False
    if interview_exists:
        try:
            interview_data = load_json(interview_path)
            interview_ok = True
        except:
            pass
    results.append({
        "item": "ops/interviews.json exists and valid JSON",
        "score": 10 if interview_ok else (0 if not interview_exists else 5),
        "max_score": 10,
        "passed": interview_ok,
        "reason": "Valid JSON" if interview_ok else ("File not found" if not interview_exists else "Invalid JSON")
    })
    total_score += 10 if interview_ok else (5 if interview_exists else 0)

    # 3. ops/reminders.json exists and valid JSON (10 pts)
    reminder_path = os.path.join(workspace, "ops", "reminders.json")
    reminder_exists = check_file_exists("ops/reminders.json")
    reminder_ok = False
    if reminder_exists:
        try:
            reminder_data = load_json(reminder_path)
            reminder_ok = True
        except:
            pass
    results.append({
        "item": "ops/reminders.json exists and valid JSON",
        "score": 10 if reminder_ok else (0 if not reminder_exists else 5),
        "max_score": 10,
        "passed": reminder_ok,
        "reason": "Valid JSON" if reminder_ok else ("File not found" if not reminder_exists else "Invalid JSON")
    })
    total_score += 10 if reminder_ok else (5 if reminder_exists else 0)

    # If interviews.json not valid, skip detailed checks
    if not interview_ok:
        results.append({"item": "interviews.json content checks", "score": 0, "max_score": 50, "passed": False, "reason": "Skipped due to invalid/missing file"})
        total_score += 0
    else:
        # 4. interview mandatory fields (20 pts)
        required_fields = ["candidate_id", "candidate_name", "job_id", "job_title", "interviewer", "interview_time", "location"]
        missing = [f for f in required_fields if f not in interview_data]
        field_ok = len(missing) == 0
        results.append({
            "item": "interviews.json contains all required fields",
            "score": 20 if field_ok else (0 if len(missing) > 2 else 10),
            "max_score": 20,
            "passed": field_ok,
            "reason": f"Missing: {', '.join(missing)}" if not field_ok else "All fields present"
        })
        total_score += 20 if field_ok else (10 if len(missing) <= 2 else 0)

        # 5. candidate_id correct (cand_004) (15 pts)
        cand_ok = interview_data.get("candidate_id") == "cand_004"
        results.append({
            "item": "Candidate ID is cand_004",
            "score": 15 if cand_ok else 0,
            "max_score": 15,
            "passed": cand_ok,
            "reason": f"Expected cand_004, got {interview_data.get('candidate_id')}" if not cand_ok else "Correct"
        })
        total_score += 15 if cand_ok else 0

        # 6. job_id correct (job_002) (10 pts)
        job_ok = interview_data.get("job_id") == "job_002"
        results.append({
            "item": "Job ID is job_002",
            "score": 10 if job_ok else 0,
            "max_score": 10,
            "passed": job_ok,
            "reason": f"Expected job_002, got {interview_data.get('job_id')}" if not job_ok else "Correct"
        })
        total_score += 10 if job_ok else 0

        # 7. interviewer name is Bob Smith (5 pts)
        interviewer_ok = interview_data.get("interviewer") == "Bob Smith"
        results.append({
            "item": "Interviewer is Bob Smith",
            "score": 5 if interviewer_ok else 0,
            "max_score": 5,
            "passed": interviewer_ok,
            "reason": f"Expected Bob Smith, got {interview_data.get('interviewer')}" if not interviewer_ok else "Correct"
        })
        total_score += 5 if interviewer_ok else 0

        # 8. interview_time is "2025-03-25 10:00" (5 pts)
        time_ok = interview_data.get("interview_time") == "2025-03-25 10:00"
        results.append({
            "item": "Interview time is 2025-03-25 10:00",
            "score": 5 if time_ok else 0,
            "max_score": 5,
            "passed": time_ok,
            "reason": f"Expected 2025-03-25 10:00, got {interview_data.get('interview_time')}" if not time_ok else "Correct"
        })
        total_score += 5 if time_ok else 0

        # 9. location is "Room 401" (5 pts)
        loc_ok = interview_data.get("location") == "Room 401"
        results.append({
            "item": "Location is Room 401",
            "score": 5 if loc_ok else 0,
            "max_score": 5,
            "passed": loc_ok,
            "reason": f"Expected Room 401, got {interview_data.get('location')}" if not loc_ok else "Correct"
        })
        total_score += 5 if loc_ok else 0

    # Check reminders content
    if not reminder_ok:
        results.append({"item": "reminders.json content checks", "score": 0, "max_score": 30, "passed": False, "reason": "Skipped due to invalid/missing file"})
        total_score += 0
    else:
        # 10. Reminder structure valid (10 pts)
        if isinstance(reminder_data, dict) and "reminders" in reminder_data and isinstance(reminder_data["reminders"], list):
            rem_list = reminder_data["reminders"]
            if len(rem_list) > 0:
                rem_item = rem_list[0]
                rem_fields = ["interview_id", "recipient", "remind_at"]
                rem_missing = [f for f in rem_fields if f not in rem_item]
                rem_ok = len(rem_missing) == 0 and len(rem_list) == 1
                results.append({
                    "item": "Reminders JSON has proper structure (list with one entry with interview_id, recipient, remind_at)",
                    "score": 10 if rem_ok else (5 if len(rem_list) >= 1 else 0),
                    "max_score": 10,
                    "passed": rem_ok,
                    "reason": f"Reminders structure issue: missing {rem_missing}" if not rem_ok else "Correct"
                })
                total_score += 10 if rem_ok else (5 if len(rem_list) >= 1 else 0)

                # 11. recipient is alice@company.com (10 pts)
                email_ok = rem_item.get("recipient") == "alice@company.com"
                results.append({
                    "item": "Reminder recipient is alice@company.com",
                    "score": 10 if email_ok else 0,
                    "max_score": 10,
                    "passed": email_ok,
                    "reason": f"Expected alice@company.com, got {rem_item.get('recipient')}" if not email_ok else "Correct"
                })
                total_score += 10 if email_ok else 0

                # 12. remind_at is one hour before interview: 2025-03-25 09:00 (10 pts)
                remind_ok = rem_item.get("remind_at") == "2025-03-25 09:00"
                results.append({
                    "item": "Remind at 2025-03-25 09:00",
                    "score": 10 if remind_ok else 0,
                    "max_score": 10,
                    "passed": remind_ok,
                    "reason": f"Expected 2025-03-25 09:00, got {rem_item.get('remind_at')}" if not remind_ok else "Correct"
                })
                total_score += 10 if remind_ok else 0
            else:
                results.append({"item": "Reminders list empty", "score": 0, "max_score": 30, "passed": False, "reason": "No reminders in list"})
                total_score += 0
        else:
            results.append({"item": "Reminders JSON structure invalid", "score": 0, "max_score": 30, "passed": False, "reason": "Expected dict with 'reminders' list"})
            total_score += 0

    # 13. Bonus: no extra files in ops (optional, but we subtract if extra)
    ops_files = [f for f in os.listdir(ops_dir) if os.path.isfile(os.path.join(ops_dir, f))] if ops_exists else []
    extra = [f for f in ops_files if f not in ("interviews.json", "reminders.json")]
    if extra:
        # Deduct 5 points (but not below 0)
        results.append({
            "item": "No extra files in ops/",
            "score": max(0, total_score - 5) - total_score,  # negative delta
            "max_score": 0,
            "passed": False,
            "reason": f"Extra files found: {', '.join(extra)}"
        })
        total_score = max(0, total_score - 5)
    else:
        results.append({
            "item": "No extra files in ops/",
            "score": 0,
            "max_score": 0,
            "passed": True,
            "reason": "Clean directory"
        })

    # Clamp to 100
    final_score = min(100, total_score)

    # Write result
    output = {
        "total_score": final_score,
        "details": results
    }
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Score written: {final_score}/100")

if __name__ == "__main__":
    main()
