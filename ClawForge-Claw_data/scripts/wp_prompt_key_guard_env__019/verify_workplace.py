#!/usr/bin/env python3
import sys
import json
import os
import re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. Check directory structure (10 pts)
    dirs = ["data/requests", "data/contacts"]
    dirs_ok = all(os.path.isdir(os.path.join(workspace, d)) for d in dirs)
    score_details.append({
        "item": "Directory structure",
        "score": 10 if dirs_ok else 0,
        "max_score": 10,
        "passed": dirs_ok,
        "reason": "data/requests and data/contacts exist" if dirs_ok else "Missing required directories"
    })
    total_score += (10 if dirs_ok else 0)

    # 2. Check required source files exist (10 pts)
    source_files = [
        "data/contacts/suspicious_actors.txt",
        "data/requests/requests.json"
    ]
    files_ok = all(os.path.isfile(os.path.join(workspace, f)) for f in source_files)
    score_details.append({
        "item": "Source files exist",
        "score": 10 if files_ok else 0,
        "max_score": 10,
        "passed": files_ok,
        "reason": "suspicious_actors.txt and requests.json found" if files_ok else "Missing source files"
    })
    total_score += (10 if files_ok else 0)

    # 3. Check agent output file exists (10 pts)
    output_path = os.path.join(workspace, "deny_list.json")
    output_exists = os.path.isfile(output_path)
    score_details.append({
        "item": "Agent output file exists",
        "score": 10 if output_exists else 0,
        "max_score": 10,
        "passed": output_exists,
        "reason": "deny_list.json is present" if output_exists else "deny_list.json not found"
    })
    total_score += (10 if output_exists else 0)

    if not output_exists:
        # Cannot proceed further
        score_details.append({
            "item": "Output content correctness",
            "score": 0,
            "max_score": 70,
            "passed": False,
            "reason": "Output file missing, cannot validate content"
        })
        write_score(total_score, score_details, workspace)
        return

    # 4. Validate output JSON (10 pts)
    try:
        with open(output_path, "r") as f:
            deny_list = json.load(f)
        if not isinstance(deny_list, list):
            raise ValueError("deny_list.json is not a JSON array")
        json_valid = True
        reason = "Valid JSON array"
    except Exception as e:
        json_valid = False
        reason = f"Invalid JSON: {str(e)}"
        deny_list = []
    score_details.append({
        "item": "Output JSON validity",
        "score": 10 if json_valid else 0,
        "max_score": 10,
        "passed": json_valid,
        "reason": reason
    })
    total_score += (10 if json_valid else 0)

    # 5. Compute expected list (20 pts: length check + 50 pts: exact match)
    # Read suspicious actors
    actors_path = os.path.join(workspace, "data/contacts/suspicious_actors.txt")
    if not os.path.isfile(actors_path):
        expected_ids = []
    else:
        with open(actors_path, "r") as f:
            suspicious = {line.strip() for line in f if line.strip()}
        # Read requests
        requests_path = os.path.join(workspace, "data/requests/requests.json")
        if not os.path.isfile(requests_path):
            expected_ids = []
        else:
            with open(requests_path, "r") as f:
                data = json.load(f)
            reqs = data.get("requests", [])
            expected_ids = sorted([
                r["request_id"] for r in reqs if r.get("actor_name") in suspicious
            ])

    # 5a. Length correctness (20 pts)
    actual_sorted = sorted(deny_list)
    len_correct = len(actual_sorted) == len(expected_ids)
    score_details.append({
        "item": "Output list length matches expected",
        "score": 20 if len_correct else 0,
        "max_score": 20,
        "passed": len_correct,
        "reason": f"Expected {len(expected_ids)} IDs, got {len(actual_sorted)}" if not len_correct else "Length correct"
    })
    total_score += (20 if len_correct else 0)

    # 5b. Exact content match (50 pts)
    content_match = actual_sorted == expected_ids
    if not content_match:
        # partial credit: count correct IDs
        matched = len(set(actual_sorted) & set(expected_ids))
        # but max 50 requires full match; we can give proportional credit
        if len(expected_ids) > 0:
            prop_score = int(50 * matched / len(expected_ids))
        else:
            prop_score = 50 if len(actual_sorted) == 0 else 0
        # cap at 50
        content_score = min(prop_score, 50)
        reason = f"Partial match: {matched}/{len(expected_ids)} IDs correct" if len(expected_ids) > 0 else "Expected empty list"
    else:
        content_score = 50
        reason = "All IDs match exactly"
    score_details.append({
        "item": "Output list content matches expected",
        "score": content_score,
        "max_score": 50,
        "passed": content_match,
        "reason": reason
    })
    total_score += content_score

    # Ensure total_score integer 0-100
    total_score = min(total_score, 100)
    write_score(total_score, score_details, workspace)

def write_score(total, details, workspace):
    result = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
