import sys
import os
import json
from datetime import datetime, timedelta

def verify(workspace):
    details = []
    total_score = 0
    max_total = 100

    # 1. schedule directory exists (10 pts)
    schedule_dir = os.path.join(workspace, "schedule")
    if os.path.isdir(schedule_dir):
        details.append({"item": "schedule directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "found schedule/"})
        total_score += 10
    else:
        details.append({"item": "schedule directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "schedule/ not found"})

    # 2. upcoming_interviews.json exists (10 pts)
    output_path = os.path.join(schedule_dir, "upcoming_interviews.json")
    if os.path.isfile(output_path):
        details.append({"item": "upcoming_interviews.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
        total_score += 10
    else:
        details.append({"item": "upcoming_interviews.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        _write_result(details, total_score, max_total, workspace)
        return

    # 3. Valid JSON (10 pts)
    try:
        with open(output_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON is valid", "score": 10, "max_score": 10, "passed": True, "reason": "valid JSON"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        _write_result(details, total_score, max_total, workspace)
        return

    # 4. Data is a list of records (10 pts)
    records = data if isinstance(data, list) else next((v for v in data.values() if isinstance(v, list)), [])
    if records:
        details.append({"item": "data contains a list of records", "score": 10, "max_score": 10, "passed": True, "reason": f"found {len(records)} record(s)"})
        total_score += 10
    else:
        details.append({"item": "data contains a list of records", "score": 0, "max_score": 10, "passed": False, "reason": "no list found"})

    # 5. Required fields present (20 pts)
    required_fields = ["candidate_id", "candidate_name", "job_id", "job_title", "scheduled_time", "status"]
    field_passed = True
    missing = []
    for i, rec in enumerate(records):
        for fld in required_fields:
            if fld not in rec:
                missing.append(f"Record {i} missing '{fld}'")
                field_passed = False
    if field_passed:
        details.append({"item": "required fields present", "score": 20, "max_score": 20, "passed": True, "reason": "all fields present"})
        total_score += 20
    else:
        details.append({"item": "required fields present", "score": 0, "max_score": 20, "passed": False, "reason": "; ".join(missing)})

    # 6. Correct candidate and job details (30 pts)
    # Read today's date
    today_path = os.path.join(workspace, "meta", "today.txt")
    try:
        with open(today_path) as f:
            today_str = f.read().strip()
        today = datetime.strptime(today_str, "%Y-%m-%d")
        tomorrow = today + timedelta(days=1)
        expected_time = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0).isoformat()
    except:
        expected_time = "2025-04-02T09:00:00"  # fallback

    correct = {"candidate_id": "cand_001", "candidate_name": "Alice Johnson",
               "job_id": "job_004", "job_title": "Backend Developer",
               "status": "scheduled", "scheduled_time": expected_time}

    matches = [rec for rec in records if rec.get("candidate_id") == correct["candidate_id"] and rec.get("job_id") == correct["job_id"]]
    if len(matches) == 1:
        rec = matches[0]
        all_ok = all(rec.get(k) == v for k, v in correct.items())
        if all_ok:
            details.append({"item": "correct candidate and job details", "score": 30, "max_score": 30, "passed": True, "reason": "exact match"})
            total_score += 30
        else:
            issues = [f"{k} expected {v}, got {rec.get(k)}" for k, v in correct.items() if rec.get(k) != v]
            details.append({"item": "correct candidate and job details", "score": 0, "max_score": 30, "passed": False, "reason": "; ".join(issues)})
    else:
        details.append({"item": "correct candidate and job details", "score": 0, "max_score": 30, "passed": False, "reason": f"expected 1 record for cand_001/job_004, found {len(matches)}"})

    # 7. No extra candidates (10 pts)
    extra = [rec for rec in records if rec.get("candidate_id") != "cand_001" or rec.get("job_id") != "job_004"]
    if not extra:
        details.append({"item": "no extra candidates", "score": 10, "max_score": 10, "passed": True, "reason": "only correct record"})
        total_score += 10
    else:
        details.append({"item": "no extra candidates", "score": 0, "max_score": 10, "passed": False, "reason": f"found {len(extra)} extra record(s)"})

    _write_result(details, total_score, max_total, workspace)


def _write_result(details, total_score, max_total, workspace):
    result = {"total_score": total_score, "details": details}
    path = os.path.join(workspace, "workplace_score.json")
    with open(path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total_score}/{max_total}")


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
