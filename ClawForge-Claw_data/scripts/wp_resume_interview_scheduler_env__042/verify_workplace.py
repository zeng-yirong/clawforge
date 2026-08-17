import os
import sys
import json
from datetime import datetime

def verify(workspace: str):
    details = []
    total_score = 0
    max_total = 100

    # Helper to add score item
    def add(item, score, max_score, passed, reason):
        details.append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        return score

    # 1. Check that 'ops' directory exists (10 pts)
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        total_score += add("ops directory exists", 10, 10, True, "Found 'ops/' directory")
    else:
        total_score += add("ops directory exists", 0, 10, False, "Missing 'ops/' directory")

    # 2. Check that scheduled_interviews.json exists (10 pts)
    result_file = os.path.join(ops_path, "scheduled_interviews.json")
    if os.path.isfile(result_file):
        total_score += add("scheduled_interviews.json exists", 10, 10, True, "File found")
    else:
        total_score += add("scheduled_interviews.json exists", 0, 10, False, "File not found")
        # no need to continue if file missing
        finalize(total_score, max_total, details)
        return

    # 3. Validate JSON structure (10 pts)
    try:
        with open(result_file, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Expected a list")
        total_score += add("JSON is valid and a list", 10, 10, True, "Parsed successfully as list")
    except Exception as e:
        total_score += add("JSON is valid and a list", 0, 10, False, f"JSON parse error: {e}")
        finalize(total_score, max_total, details)
        return

    # 4. Check required fields in each interview entry (20 pts)
    required_fields = {"candidate_id": str, "job_id": str, "datetime": str}
    field_ok = True
    for i, entry in enumerate(data):
        for field, ftype in required_fields.items():
            if field not in entry or not isinstance(entry[field], ftype):
                field_ok = False
                reason = f"Entry {i} missing or wrong type for field '{field}'"
                break
        if not field_ok:
            break
    if field_ok and len(data) > 0:
        total_score += add("All entries have candidate_id, job_id, datetime (string)", 20, 20, True, "Fields valid")
    else:
        total_score += add("All entries have candidate_id, job_id, datetime (string)", 0, 20, False,
                           "Missing or invalid fields")

    # 5. Verify the exact number of interviews (30 pts)
    # Expected: two pairs (c001,j001) and (c003,j001), after exclusion
    expected_count = 2
    if len(data) == expected_count:
        total_score += add("Correct number of interviews (2)", 30, 30, True, f"Found {len(data)} entries")
    else:
        total_score += add("Correct number of interviews (2)", 0, 30, False,
                           f"Expected {expected_count}, got {len(data)}")

    # 6. Verify content – exact pairs and datetimes (20 pts)
    # Expected pairs sorted by (job_id, candidate_id):
    # First: (c001, j001) -> datetime 2025-04-21T10:00:00
    # Second: (c003, j001) -> datetime 2025-04-22T10:00:00
    expected_pairs = [
        {"candidate_id": "c001", "job_id": "j001", "datetime": "2025-04-21T10:00:00"},
        {"candidate_id": "c003", "job_id": "j001", "datetime": "2025-04-22T10:00:00"},
    ]
    content_ok = True
    if len(data) == expected_count:
        # Check that both expected pairs exist in the list (order matters per spec)
        for i, (entry, exp) in enumerate(zip(data, expected_pairs)):
            if entry.get("candidate_id") != exp["candidate_id"] or \
               entry.get("job_id") != exp["job_id"] or \
               entry.get("datetime") != exp["datetime"]:
                content_ok = False
                break
    else:
        content_ok = False

    if content_ok:
        total_score += add("Interview entries match expected pairs and datetimes", 20, 20, True, "All correct")
    else:
        total_score += add("Interview entries match expected pairs and datetimes", 0, 20, False,
                           "Mismatch in pairs or datetimes")

    finalize(total_score, max_total, details)

def finalize(total, max_total, details):
    score_data = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(score_data, f, indent=2)
    # Also print summary to stdout
    print(f"Total score: {total}/{max_total}")
    for d in details:
        status = "PASS" if d["passed"] else "FAIL"
        print(f"  [{status}] {d['item']}: {d['score']}/{d['max_score']} - {d['reason']}")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
