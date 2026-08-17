import sys
import json
import os
from pathlib import Path

def verify(workspace: str):
    score_details = []
    total_score = 0

    # 1. Check directory structure
    dirs_to_check = ["data", "data/requests", "data/assets", "data/attachments", "ops"]
    dirs_ok = True
    for d in dirs_to_check:
        if not os.path.isdir(os.path.join(workspace, d)):
            dirs_ok = False
            score_details.append({"item": f"Directory {d} exists", "score": 0, "max_score": 5, "passed": False, "reason": f"Missing directory: {d}"})
            break
    if dirs_ok:
        score_details.append({"item": "Required directories exist", "score": 5, "max_score": 5, "passed": True, "reason": "All core directories found"})

    # 2. Check deny_list.json exists
    deny_path = os.path.join(workspace, "ops/deny_list.json")
    if not os.path.isfile(deny_path):
        score_details.append({"item": "ops/deny_list.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # Since file missing, we can't check content
        total_score = sum(s["score"] for s in score_details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    score_details.append({"item": "ops/deny_list.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File present"})

    # 3. Validate JSON syntax and top-level structure
    try:
        with open(deny_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        score_details.append({"item": "JSON syntax & structure", "score": 0, "max_score": 15, "passed": False, "reason": f"Invalid JSON: {e}"})
        total_score = sum(s["score"] for s in score_details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    if not isinstance(data, dict) or "requests" not in data:
        score_details.append({"item": "JSON structure", "score": 0, "max_score": 15, "passed": False, "reason": "Missing 'requests' key or not an object"})
        total_score = sum(s["score"] for s in score_details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    if not isinstance(data["requests"], list):
        score_details.append({"item": "JSON structure", "score": 0, "max_score": 15, "passed": False, "reason": "'requests' is not a list"})
        total_score = sum(s["score"] for s in score_details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # Check for extra keys
    allowed_keys = {"requests"}
    extra_keys = set(data.keys()) - allowed_keys
    if extra_keys:
        score_details.append({"item": "JSON structure (no extra keys)", "score": 5, "max_score": 15, "passed": False, "reason": f"Unexpected keys: {extra_keys}"})
    else:
        score_details.append({"item": "JSON structure valid", "score": 15, "max_score": 15, "passed": True, "reason": "Valid JSON with correct structure"})

    # 4. Content correctness (the core)
    # Expected list of request IDs: req_003 and req_007
    expected_ids = {"req_003", "req_007"}
    actual_ids = set(data["requests"])

    # Check each entry is a string
    if not all(isinstance(x, str) for x in data["requests"]):
        score_details.append({"item": "All IDs are strings", "score": 0, "max_score": 10, "passed": False, "reason": "Some entries are not strings"})
    
    missing = expected_ids - actual_ids
    extra = actual_ids - expected_ids

    content_score = 70
    reasons = []
    if missing:
        content_score -= 20 * len(missing)
        reasons.append(f"Missing expected IDs: {sorted(missing)}")
    if extra:
        content_score -= 20 * len(extra)
        reasons.append(f"Unexpected extra IDs: {sorted(extra)}")
    content_score = max(0, content_score)
    content_passed = content_score == 70
    reason_str = "; ".join(reasons) if reasons else "Exactly correct set"

    score_details.append({"item": "Content correctness", "score": content_score, "max_score": 70, "passed": content_passed, "reason": reason_str})

    total_score = sum(s["score"] for s in score_details)
    # Write output
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
