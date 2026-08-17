import json
import os
import sys

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(relative_path):
    path = os.path.join(WORKSPACE, relative_path)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return "INVALID_JSON"

def main():
    details = []
    total = 0

    # ── 1. Directory structure (10 pts) ─────────────────────────
    dir_ops = os.path.isdir(os.path.join(WORKSPACE, "ops"))
    dir_reminders = os.path.isdir(os.path.join(WORKSPACE, "reminders"))
    passed_dirs = dir_ops and dir_reminders
    score_dirs = 10 if passed_dirs else 0
    details.append({
        "item": "Directories ops/ and reminders/ exist",
        "score": score_dirs,
        "max_score": 10,
        "passed": passed_dirs,
        "reason": "Both directories found" if passed_dirs else "Missing one or both directories"
    })
    total += score_dirs

    # ── 2. Interview file existence (10 pts) ────────────────────
    interview_data = load_json("ops/interviews.json")
    interview_file_ok = interview_data is not None and interview_data != "INVALID_JSON"
    score_interview_file = 10 if interview_file_ok else 0
    details.append({
        "item": "ops/interviews.json exists and is valid JSON",
        "score": score_interview_file,
        "max_score": 10,
        "passed": interview_file_ok,
        "reason": "File valid" if interview_file_ok else "File missing or invalid JSON"
    })
    total += score_interview_file

    # ── 3. Reminder file existence (10 pts) ─────────────────────
    reminder_data = load_json("reminders/reminders.json")
    reminder_file_ok = reminder_data is not None and reminder_data != "INVALID_JSON"
    score_reminder_file = 10 if reminder_file_ok else 0
    details.append({
        "item": "reminders/reminders.json exists and is valid JSON",
        "score": score_reminder_file,
        "max_score": 10,
        "passed": reminder_file_ok,
        "reason": "File valid" if reminder_file_ok else "File missing or invalid JSON"
    })
    total += score_reminder_file

    # ── 4. Interview record fields (20 pts) ─────────────────────
    fields_ok = False
    if interview_file_ok and isinstance(interview_data, dict):
        # Expect a single interview object, not a list. Allow wrapper {"interviews": [...]} or direct object.
        rec = None
        if "interviews" in interview_data and isinstance(interview_data["interviews"], list):
            if len(interview_data["interviews"]) == 1:
                rec = interview_data["interviews"][0]
        elif isinstance(interview_data, dict) and "candidate_id" in interview_data:
            rec = interview_data

        if rec:
            required_fields = {"candidate_id", "job_id", "interview_time", "status"}
            present = {f for f in required_fields if f in rec}
            fields_ok = (present == required_fields)

    score_fields = 20 if fields_ok else 0
    details.append({
        "item": "Interview record contains all required fields (candidate_id, job_id, interview_time, status)",
        "score": score_fields,
        "max_score": 20,
        "passed": fields_ok,
        "reason": "All fields present" if fields_ok else "Missing or malformed fields"
    })
    total += score_fields

    # ── 5. Reminder record fields (20 pts) ─────────────────────
    reminder_fields_ok = False
    if reminder_file_ok and isinstance(reminder_data, dict):
        rec = None
        if "reminders" in reminder_data and isinstance(reminder_data["reminders"], list):
            if len(reminder_data["reminders"]) == 1:
                rec = reminder_data["reminders"][0]
        elif isinstance(reminder_data, dict) and "candidate_id" in reminder_data:
            rec = reminder_data

        if rec:
            # Acceptable fields: candidate_id, remind_at or offset; we check for at least candidate_id and time related.
            has_candidate = "candidate_id" in rec
            has_time_info = any(k in rec for k in ["remind_at", "reminder_offset", "time"])
            reminder_fields_ok = has_candidate and has_time_info

    score_rem_fields = 20 if reminder_fields_ok else 0
    details.append({
        "item": "Reminder record contains candidate_id and time/offset information",
        "score": score_rem_fields,
        "max_score": 20,
        "passed": reminder_fields_ok,
        "reason": "Required fields present" if reminder_fields_ok else "Missing candidate_id or time info"
    })
    total += score_rem_fields

    # ── 6. Exact values (30 pts) ────────────────────────────────
    exact_correct = False
    if fields_ok and interview_file_ok:
        rec = None
        if "interviews" in interview_data:
            rec = interview_data["interviews"][0]
        else:
            rec = interview_data
        if rec:
            expected = {
                "candidate_id": "candidate_003",
                "job_id": "job_001",
                "interview_time": "2025-04-16T10:00:00",
                "status": "scheduled"
            }
            exact_correct = all(rec.get(k) == v for k, v in expected.items())

    score_exact = 30 if exact_correct else 0
    details.append({
        "item": "Exact interview values match: candidate_003, job_001, 2025-04-16T10:00:00, scheduled",
        "score": score_exact,
        "max_score": 30,
        "passed": exact_correct,
        "reason": "All values correct" if exact_correct else "One or more values differ"
    })
    total += score_exact

    # ── Output ──────────────────────────────────────────────────
    result = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
