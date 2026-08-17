import os
import sys
import json
from datetime import datetime, timedelta

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return None

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_detail = []
    total = 0
    max_total = 100

    # 1. Check that ops/interview_schedule.json exists (10 points)
    schedule_path = os.path.join(workspace, "ops/interview_schedule.json")
    exists = os.path.isfile(schedule_path)
    score_detail.append({
        "item": "ops/interview_schedule.json existence",
        "score": 10 if exists else 0,
        "max_score": 10,
        "passed": exists,
        "reason": "File found" if exists else "File not found at ops/interview_schedule.json"
    })
    if exists:
        total += 10
    else:
        total += 0

    # If file doesn't exist, we can't check further, but still need to return score
    if not exists:
        score_detail.append({"item": "JSON valid & structure", "score": 0, "max_score": 10, "passed": False, "reason": "File missing"})
        score_detail.append({"item": "Record count (expected 2)", "score": 0, "max_score": 20, "passed": False, "reason": "N/A"})
        score_detail.append({"item": "Candidate-Job matching correctness", "score": 0, "max_score": 40, "passed": False, "reason": "N/A"})
        score_detail.append({"item": "Time calculation", "score": 0, "max_score": 20, "passed": False, "reason": "N/A"})
        final = {"total_score": total, "details": score_detail}
        with open("workplace_score.json", "w") as f:
            json.dump(final, f, indent=2)
        return

    # 2. Parse schedule file (10 points for valid JSON and correct structure)
    schedule = load_json(schedule_path)
    if schedule is None:
        score_detail.append({
            "item": "JSON valid & structure",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Invalid or unparseable JSON"
        })
        score_detail.append({"item": "Record count", "score": 0, "max_score": 20, "passed": False, "reason": "N/A"})
        score_detail.append({"item": "Candidate-Job matching", "score": 0, "max_score": 40, "passed": False, "reason": "N/A"})
        score_detail.append({"item": "Time calculation", "score": 0, "max_score": 20, "passed": False, "reason": "N/A"})
        final = {"total_score": total, "details": score_detail}
        with open("workplace_score.json", "w") as f:
            json.dump(final, f, indent=2)
        return

    # Expect the top-level to be a list (each entry is an interview)
    if not isinstance(schedule, list):
        # maybe it's wrapped like {"interviews": [...]}? We'll be flexible but penalize
        if isinstance(schedule, dict):
            # try common wrappers
            for key in ["interviews", "schedule", "interview_schedule"]:
                if key in schedule and isinstance(schedule[key], list):
                    schedule = schedule[key]
                    break
            else:
                score_detail.append({
                    "item": "JSON valid & structure",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": "Top-level is dict without known wrapper key; expected list"
                })
                score_detail.append({"item": "Record count", "score": 0, "max_score": 20, "passed": False, "reason": "N/A"})
                score_detail.append({"item": "Matching", "score": 0, "max_score": 40, "passed": False, "reason": "N/A"})
                score_detail.append({"item": "Times", "score": 0, "max_score": 20, "passed": False, "reason": "N/A"})
                final = {"total_score": total, "details": score_detail}
                with open("workplace_score.json", "w") as f:
                    json.dump(final, f, indent=2)
                return
        else:
            score_detail.append({
                "item": "JSON valid & structure",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "Top-level is not a list or dict"
            })
            # fill rest
            score_detail.append({"item": "Record count", "score": 0, "max_score": 20, "passed": False, "reason": "N/A"})
            score_detail.append({"item": "Matching", "score": 0, "max_score": 40, "passed": False, "reason": "N/A"})
            score_detail.append({"item": "Times", "score": 0, "max_score": 20, "passed": False, "reason": "N/A"})
            final = {"total_score": total, "details": score_detail}
            with open("workplace_score.json", "w") as f:
                json.dump(final, f, indent=2)
            return

    # Structure is OK – award 10 points
    score_detail.append({
        "item": "JSON valid & structure",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Valid JSON and top-level list"
    })
    total += 10

    # 3. Record count (20 points) – expect exactly 2
    expected_count = 2
    record_count = len(schedule)
    count_ok = record_count == expected_count
    score_detail.append({
        "item": "Record count (expected 2)",
        "score": 20 if count_ok else max(0, 20 - abs(record_count - expected_count) * 10),
        "max_score": 20,
        "passed": count_ok,
        "reason": f"Got {record_count} records, expected {expected_count}" if not count_ok else "Correct count"
    })
    total += 20 if count_ok else max(0, 20 - abs(record_count - expected_count) * 10)

    # 4. Matching correctness (40 points, 20 per correct pair)
    # Load the original data to know the true matches
    data_path = os.path.join(workspace, "data")
    candidates_path = os.path.join(data_path, "candidates/candidates.json")
    jobs_path = os.path.join(data_path, "jobs/jobs.json")
    config_path = os.path.join(workspace, "config/settings.json")

    candidates_data = load_json(candidates_path)
    jobs_data = load_json(jobs_path)
    config_data = load_json(config_path)

    # Compute expected matches: candidate's skills must be superset of job's required_skills
    true_matches = []
    if candidates_data and "candidates" in candidates_data and jobs_data and "jobs" in jobs_data:
        cand_list = candidates_data["candidates"]
        job_list = jobs_data["jobs"]
        for cand in cand_list:
            for job in job_list:
                if set(cand["skills"]).issuperset(set(job["required_skills"])):
                    true_matches.append((cand["candidate_id"], job["job_id"]))

    # Sort true_matches by candidate_id (to get deterministic ordering)
    true_matches_sorted = sorted(true_matches, key=lambda x: x[0])

    # Also we need time base
    base_time = None
    if config_data and "interview_start_time" in config_data:
        try:
            base_time = datetime.fromisoformat(config_data["interview_start_time"])
        except:
            pass
    duration = config_data.get("interview_duration_minutes", 30) if config_data else 30
    reminder = config_data.get("reminder_before_minutes", 15) if config_data else 15

    match_score = 0
    # For each expected match, try to find a corresponding record in schedule
    # We'll require that the schedule records have fields candidate_id and job_id
    # Also check that the times are correct (using order of appearance in schedule)
    # We'll sort schedule by candidate_id as well for comparison
    # But we can allow any order, as long as each pair exists with correct times
    # However times must correspond to the assigned slots: first slot = base, second = base+30min, etc.
    # We'll assume the schedule list order determines the slot index.

    # First, extract fields from schedule records – we allow flexible field names
    def extract_id(rec, field_candidates):
        for f in field_candidates:
            if f in rec:
                return rec[f]
        return None

    schedule_pairs = []
    for rec in schedule:
        cid = extract_id(rec, ["candidate_id", "candidateId", "candidate"])
        jid = extract_id(rec, ["job_id", "jobId", "job"])
        if cid and jid:
            schedule_pairs.append((cid, jid))

    # Check that each true match appears in schedule_pairs
    true_set = set(true_matches_sorted)
    schedule_set = set(schedule_pairs)
    correct_pairs = true_set.intersection(schedule_set)
    incorrect_pairs = schedule_set - true_set

    match_score = len(correct_pairs) * 20  # each correct pair gives 20
    if match_score > 40:
        match_score = 40  # cap
    if incorrect_pairs:
        match_score = max(0, match_score - len(incorrect_pairs) * 10)  # penalty for extra pairs

    match_passed = len(correct_pairs) == len(true_matches_sorted) and len(incorrect_pairs) == 0
    score_detail.append({
        "item": "Candidate-Job matching correctness",
        "score": match_score,
        "max_score": 40,
        "passed": match_passed,
        "reason": f"True matches: {true_matches_sorted}, schedule pairs: {schedule_pairs}, correct: {correct_pairs}, extra: {incorrect_pairs}"
    })
    total += match_score

    # 5. Time calculation (20 points)
    # Verify that for each record, the interview times and reminder are correct
    # We need to map the order in schedule to slot indices.
    # We'll sort schedule by a start_time field if available, otherwise by candidate_id.
    # For simplicity, we sort schedule list by candidate_id (assuming agent used that order)
    # Then compute expected times.
    time_score = 0
    if base_time and len(schedule_pairs) > 0:
        # Build mapping from candidate_id to record
        rec_by_cid = {}
        for rec in schedule:
            cid = extract_id(rec, ["candidate_id", "candidateId", "candidate"])
            if cid:
                rec_by_cid[cid] = rec

        # Reconstruct the order we expect: sort true_matches_sorted by candidate_id
        expected_order_cids = [cid for cid, _ in true_matches_sorted]

        # Now check each record in that order
        all_times_correct = True
        for idx, cid in enumerate(expected_order_cids):
            if cid not in rec_by_cid:
                all_times_correct = False
                continue
            rec = rec_by_cid[cid]
            start_expected = base_time + timedelta(minutes=idx * duration)
            end_expected = start_expected + timedelta(minutes=duration)
            reminder_expected = start_expected - timedelta(minutes=reminder)

            # Allow flexible field names for times
            start_field = extract_id(rec, ["interview_start", "start_time", "interview_start_time"])
            end_field = extract_id(rec, ["interview_end", "end_time", "interview_end_time"])
            reminder_field = extract_id(rec, ["reminder_at", "reminder_time", "reminder"])

            if start_field is None or end_field is None or reminder_field is None:
                all_times_correct = False
                continue

            # Try to parse fields – they may be string or datetime object
            try:
                start_val = datetime.fromisoformat(start_field) if isinstance(start_field, str) else start_field
                end_val = datetime.fromisoformat(end_field) if isinstance(end_field, str) else end_field
                reminder_val = datetime.fromisoformat(reminder_field) if isinstance(reminder_field, str) else reminder_field
            except:
                all_times_correct = False
                continue

            if start_val != start_expected or end_val != end_expected or reminder_val != reminder_expected:
                all_times_correct = False

        if all_times_correct:
            time_score = 20
        else:
            # partial credit: check each record individually
            correct_count = 0
            for idx, cid in enumerate(expected_order_cids):
                if cid not in rec_by_cid:
                    continue
                rec = rec_by_cid[cid]
                start_expected = base_time + timedelta(minutes=idx * duration)
                end_expected = start_expected + timedelta(minutes=duration)
                reminder_expected = start_expected - timedelta(minutes=reminder)
                try:
                    start_val = datetime.fromisoformat(rec.get("interview_start", "")) if isinstance(rec.get("interview_start", ""), str) else rec.get("start_time")
                    end_val = datetime.fromisoformat(rec.get("interview_end", "")) if isinstance(rec.get("interview_end", ""), str) else rec.get("end_time")
                    reminder_val = datetime.fromisoformat(rec.get("reminder_at", "")) if isinstance(rec.get("reminder_at", ""), str) else rec.get("reminder_time")
                except:
                    continue
                if start_val == start_expected and end_val == end_expected and reminder_val == reminder_expected:
                    correct_count += 1
            time_score = (correct_count / len(expected_order_cids)) * 20
    else:
        all_times_correct = False

    time_passed = time_score == 20
    score_detail.append({
        "item": "Time calculation (start/end/reminder)",
        "score": round(time_score),
        "max_score": 20,
        "passed": time_passed,
        "reason": f"Base: {base_time}, duration: {duration}, reminder: {reminder}. Computed score: {time_score}"
    })
    total += round(time_score)

    # Final score clamped to 100
    final_total = min(total, 100)
    final = {"total_score": final_total, "details": score_detail}
    with open("workplace_score.json", "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    verify()
