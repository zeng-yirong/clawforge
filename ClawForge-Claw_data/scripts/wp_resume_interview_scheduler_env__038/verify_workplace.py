import json
import os
import sys

def verify(workspace: str) -> dict:
    details = []
    total_score = 0
    max_total = 100

    # Item 1: Check that ops directory exists (10 points)
    ops_dir = os.path.join(workspace, "ops")
    item = {
        "item": "ops directory exists",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": ""
    }
    if os.path.isdir(ops_dir):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "Directory ops/ found."
    else:
        item["reason"] = "Missing ops/ directory."
    details.append(item)
    total_score += item["score"]

    # Item 2: Check that interview_schedule.json exists and is valid JSON (10 points)
    target_file = os.path.join(ops_dir, "interview_schedule.json")
    item = {
        "item": "interview_schedule.json exists and valid JSON",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": ""
    }
    if not os.path.isfile(target_file):
        item["reason"] = "File ops/interview_schedule.json not found."
    else:
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                item["score"] = 10
                item["passed"] = True
                item["reason"] = "File exists and contains a valid JSON array."
            else:
                item["reason"] = "File content is not a JSON array."
        except (json.JSONDecodeError, ValueError):
            item["reason"] = "File does not contain valid JSON."
    details.append(item)
    total_score += item["score"]

    # If the file was not valid, we still try to load it for further checks (skip if absent)
    if item["passed"]:
        # Item 3: Correct number of candidates (exactly 2) (30 points)
        item3 = {
            "item": "candidate count matches expected (2)",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": ""
        }
        if len(data) == 2:
            item3["score"] = 30
            item3["passed"] = True
            item3["reason"] = f"Found exactly {len(data)} interview entries."
        else:
            item3["reason"] = f"Expected 2 entries, got {len(data)}."
        details.append(item3)
        total_score += item3["score"]

        # Item 4: Validate each entry's required fields (40 points, 20 per entry)
        expected_keys = {"candidate_id", "candidate_name", "job_id", "job_title", "scheduled_time", "reminder"}
        required_candidates_ids = {"C001", "C002"}
        found_ids = set()
        entry_score = 0
        max_entry = 40
        for i, entry in enumerate(data):
            if not isinstance(entry, dict):
                continue
            keys = set(entry.keys())
            if expected_keys.issubset(keys):
                # Check required values
                cid = entry.get("candidate_id", "")
                if cid in required_candidates_ids:
                    found_ids.add(cid)
                    # Check job_id and job_title
                    if entry.get("job_id") == "J001" and entry.get("job_title") == "Backend Developer":
                        entry_score += 10
                    # Check scheduled_time
                    if entry.get("scheduled_time") == "2025-06-10T10:00:00":
                        entry_score += 5
                    # Check reminder flag
                    if entry.get("reminder") is True:
                        entry_score += 5
        # Full mark if both required candidates present and all value checks pass
        if found_ids == required_candidates_ids and entry_score == 40:
            item4 = {
                "item": "field correctness for all entries",
                "score": 40,
                "max_score": 40,
                "passed": True,
                "reason": "All required fields and values match expectations."
            }
        else:
            # Partial scoring per entry may be complex; use percentage of achieved score
            achieved = entry_score
            possible = 40
            item4 = {
                "item": "field correctness for all entries",
                "score": achieved,
                "max_score": 40,
                "passed": achieved >= 20,
                "reason": f"Achieved {achieved}/{possible} field checks."
            }
        details.append(item4)
        total_score += item4["score"]

        # Item 5: No extra unexpected files in ops/ (10 points) – optional strictness
        item5 = {
            "item": "ops directory contains only interview_schedule.json",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": ""
        }
        contents = os.listdir(ops_dir)
        allowed = {"interview_schedule.json"}
        extra = [f for f in contents if f not in allowed]
        if not extra:
            item5["score"] = 10
            item5["passed"] = True
            item5["reason"] = "No extra files found in ops/."
        else:
            item5["reason"] = f"Extra files found: {extra}"
        details.append(item5)
        total_score += item5["score"]
    else:
        # If main file is invalid, give 0 for remaining items
        for name, max_score in [("candidate count", 30), ("field correctness", 40), ("no extra files", 10)]:
            details.append({
                "item": name,
                "score": 0,
                "max_score": max_score,
                "passed": False,
                "reason": "Skipped due to missing or invalid interview_schedule.json"
            })

    # Clamp total scores to max
    total_score = min(total_score, max_total)

    result = {
        "total_score": total_score,
        "details": details
    }
    return result

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {result['total_score']}/100")
