"""
Verifier for task wp_flight_delay_envs__047.
Checks that the agent has produced output/affected_schedule.json with the
correct structure and exact time adjustments for affected bookings.
Scoring:
  - Directory existence               10 pts
  - File is valid JSON                10 pts
  - Schema (fields present)           20 pts
  - Correct affected records (IDs)    30 pts
  - Exact time calculations           30 pts
"""
import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    output_path = os.path.join(workspace, "output", "affected_schedule.json")

    details = []
    total = 0

    # 1. Directory existence (10)
    dir_ok = os.path.isdir(os.path.join(workspace, "output"))
    details.append({
        "item": "output directory exists",
        "score": 10 if dir_ok else 0,
        "max_score": 10,
        "passed": dir_ok,
        "reason": "Directory output/ found" if dir_ok else "Directory output/ missing"
    })
    if dir_ok:
        total += 10

    # 2. File exists and valid JSON (10)
    file_ok = False
    data = None
    if os.path.isfile(output_path):
        try:
            with open(output_path, "r") as f:
                data = json.load(f)
            file_ok = True
            reason = "File is valid JSON"
        except (json.JSONDecodeError, Exception) as e:
            reason = f"Invalid JSON: {e}"
    else:
        reason = "File output/affected_schedule.json not found"
    details.append({
        "item": "affected_schedule.json valid JSON",
        "score": 10 if file_ok else 0,
        "max_score": 10,
        "passed": file_ok,
        "reason": reason
    })
    if file_ok:
        total += 10

    if not file_ok:
        # cannot proceed further
        final = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    # 3. Schema – each record must have booking_id, type, original_time, adjusted_time (20)
    records = data if isinstance(data, list) else data.get("affected_schedule", data)
    if not isinstance(records, list):
        records = []
    schema_ok = True
    required_fields = {"booking_id", "type", "original_time", "adjusted_time"}
    schema_reason = ""
    bad_record_indices = []
    for idx, rec in enumerate(records):
        if not isinstance(rec, dict):
            schema_ok = False
            bad_record_indices.append(idx)
            continue
        missing = required_fields - set(rec.keys())
        if missing:
            schema_ok = False
            bad_record_indices.append(idx)
    if schema_ok:
        schema_score = 20
        schema_reason = "All records have required fields"
    else:
        schema_score = 0
        schema_reason = f"Records at indices {bad_record_indices} missing fields {required_fields}"
    details.append({
        "item": "Schema fields (booking_id, type, original_time, adjusted_time)",
        "score": schema_score,
        "max_score": 20,
        "passed": schema_ok,
        "reason": schema_reason
    })
    total += schema_score

    # 4. Correct affected bookings (30)
    # Expected affected: HB001, TB001, HB002, TB002 (only confirmed, linked to delayed flights)
    expected_ids = {"HB001", "TB001", "HB002", "TB002"}
    found_ids = {r.get("booking_id") for r in records if isinstance(r, dict)}
    correct_ids = found_ids & expected_ids
    extra_ids = found_ids - expected_ids
    missing_ids = expected_ids - found_ids
    id_penalty = len(extra_ids) + len(missing_ids)
    id_score = max(0, 30 - id_penalty * 10)  # each wrong missing/extra costs 10 pts
    id_passed = id_score == 30
    id_reason_parts = []
    if missing_ids:
        id_reason_parts.append(f"missing: {missing_ids}")
    if extra_ids:
        id_reason_parts.append(f"extra: {extra_ids}")
    id_reason = "; ".join(id_reason_parts) if id_reason_parts else "all correct"
    details.append({
        "item": "Correct booking IDs identified",
        "score": id_score,
        "max_score": 30,
        "passed": id_passed,
        "reason": id_reason
    })
    total += id_score

    # 5. Exact time calculations (30)
    # Build lookup by booking_id
    record_map = {r.get("booking_id"): r for r in records if isinstance(r, dict)}
    # Expected adjusted times (HH:MM, in same day, no wrap)
    expected_adjustments = {
        "HB001": {"original_time": "15:00", "adjusted_time": "17:00"},
        "TB001": {"original_time": "18:30", "adjusted_time": "20:30"},
        "HB002": {"original_time": "16:00", "adjusted_time": "16:30"},
        "TB002": {"original_time": "16:30", "adjusted_time": "17:00"},
    }
    time_score = 0
    time_errors = []
    for bkid, exp in expected_adjustments.items():
        rec = record_map.get(bkid)
        if not rec:
            time_errors.append(f"{bkid} missing")
            continue
        orig = rec.get("original_time")
        adj = rec.get("adjusted_time")
        if orig != exp["original_time"]:
            time_errors.append(f"{bkid} original_time expected {exp['original_time']}, got {orig}")
        if adj != exp["adjusted_time"]:
            time_errors.append(f"{bkid} adjusted_time expected {exp['adjusted_time']}, got {adj}")
    if not time_errors:
        time_score = 30
        time_reason = "All time calculations correct"
    else:
        time_score = max(0, 30 - len(time_errors) * 10)
        time_reason = "; ".join(time_errors)
    details.append({
        "item": "Exact time adjustments",
        "score": time_score,
        "max_score": 30,
        "passed": time_score == 30,
        "reason": time_reason
    })
    total += time_score

    final = {"total_score": total, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    main()
