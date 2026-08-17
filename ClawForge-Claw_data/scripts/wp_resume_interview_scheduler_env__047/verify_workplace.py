import sys
import os
import json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
os.chdir(workspace)  # Ensure we operate in the correct workspace

score_items = []

# 1. Check directory structure (10 points)
expected_dirs = ["data/candidates", "data/jobs", "data/archive", "ops"]
dir_ok = all(os.path.isdir(d) for d in expected_dirs)
score_items.append({
    "item": "Directory structure",
    "score": 10 if dir_ok else 0,
    "max_score": 10,
    "passed": dir_ok,
    "reason": "All required directories exist" if dir_ok else f"Missing: {[d for d in expected_dirs if not os.path.isdir(d)]}"
})

# 2. Check output file exists (10 points)
output_path = "ops/interview_schedule.json"
file_exists = os.path.isfile(output_path)
score_items.append({
    "item": "Output file existence",
    "score": 10 if file_exists else 0,
    "max_score": 10,
    "passed": file_exists,
    "reason": "ops/interview_schedule.json exists" if file_exists else "File not found"
})

if not file_exists:
    # If file missing, all subsequent checks get 0
    for missing_item in ["JSON format valid", "Match count correct", "Each match correct"]:
        max_s = 10 if "count" not in missing_item else 20 if "count" in missing_item else 50
        score_items.append({
            "item": missing_item,
            "score": 0,
            "max_score": max_s,
            "passed": False,
            "reason": "Output file missing"
        })
    total = sum(item["score"] for item in score_items)
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total, "details": score_items}, f, indent=2)
    sys.exit(0)

# 3. JSON format valid (10 points)
try:
    with open(output_path, "r") as f:
        schedule = json.load(f)
    format_ok = isinstance(schedule, list)
    score_items.append({
        "item": "JSON format valid",
        "score": 10 if format_ok else 0,
        "max_score": 10,
        "passed": format_ok,
        "reason": "Valid JSON list" if format_ok else "Not a list"
    })
except Exception as e:
    score_items.append({
        "item": "JSON format valid",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": f"Parse error: {str(e)}"
    })
    format_ok = False

if not format_ok:
    for missing_item in ["Match count correct", "Each match correct"]:
        max_s = 20 if "count" in missing_item else 50
        score_items.append({
            "item": missing_item,
            "score": 0,
            "max_score": max_s,
            "passed": False,
            "reason": "Invalid JSON"
        })
    total = sum(item["score"] for item in score_items)
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total, "details": score_items}, f, indent=2)
    sys.exit(0)

# 4. Match count correct (20 points)
# Expected: two matches: C001-J001, C002-J002
expected_matches = {("C001", "J001"), ("C002", "J002")}
actual_matches = set()
for entry in schedule:
    cid = entry.get("candidate_id")
    jid = entry.get("job_id")
    if cid and jid:
        actual_matches.add((cid, jid))
count_correct = len(actual_matches) == 2
no_extra = actual_matches == expected_matches
match_ok = count_correct and no_extra
score_items.append({
    "item": "Match count correct",
    "score": 20 if match_ok else 0,
    "max_score": 20,
    "passed": match_ok,
    "reason": f"Found {len(actual_matches)} matches: {actual_matches}" if match_ok else f"Expected {expected_matches}, got {actual_matches}"
})

# 5. Each match correct (50 points) - check required fields and date
all_entries_have_fields = all(
    "candidate_id" in entry and "job_id" in entry and "interview_date" in entry
    for entry in schedule
)
date_ok = all(entry.get("interview_date") == "2025-03-24" for entry in schedule)
correct_matches_present = (("C001","J001") in actual_matches and ("C002","J002") in actual_matches)
field_ok = all_entries_have_fields and date_ok and correct_matches_present
score_items.append({
    "item": "Each match correct",
    "score": 50 if field_ok else 0,
    "max_score": 50,
    "passed": field_ok,
    "reason": "All entries have required fields, correct date, and correct matches" if field_ok else (
        "Missing fields" if not all_entries_have_fields else
        "Wrong date" if not date_ok else
        "Missing expected match")
})

total_score = sum(item["score"] for item in score_items)
with open("workplace_score.json", "w") as f:
    json.dump({"total_score": total_score, "details": score_items}, f, indent=2)
