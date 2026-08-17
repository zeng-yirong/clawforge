import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def check_result():
    details = []
    total_score = 0

    # ---------- 1. ops directory exists (10 points) ----------
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    details.append({
        "item": "ops directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops directory found" if dir_exists else "ops directory missing"
    })
    if dir_exists:
        total_score += 10

    # ---------- 2. denied_requests.json exists and is valid JSON (10 points) ----------
    result_path = os.path.join(workspace, "ops", "denied_requests.json")
    file_exists = os.path.isfile(result_path)
    valid_json = False
    data = None
    if file_exists:
        try:
            with open(result_path, "r") as f:
                data = json.load(f)
            valid_json = True
        except (json.JSONDecodeError, ValueError):
            pass
    details.append({
        "item": "denied_requests.json exists and valid JSON",
        "score": 10 if (file_exists and valid_json) else 0,
        "max_score": 10,
        "passed": file_exists and valid_json,
        "reason": "File exists and valid" if (file_exists and valid_json) else (
            "File missing" if not file_exists else "Invalid JSON content"
        )
    })
    if file_exists and valid_json:
        total_score += 10

    # ---------- 3. Correct list of IDs (60 points, 30 each) ----------
    # Expected IDs: req-101 and req-103 (the two impersonators whose actor_name is not in Security Engineering)
    # req-101: Fake Auditor 1 (Marketing) claimed Security Auditor → should deny
    # req-103: Fake Auditor 2 (Finance) claimed Security Auditor → should deny
    # req-105: Charlie Li is real Security Engineering, so NOT impersonation → should not be denied
    # req-106: Alice Wong is real Security Engineering, also not impersonation
    # req-107: Evan Park is real Security Engineering, also not impersonation
    # req-108: completed, should be ignored even if impersonator
    expected_ids = {"req-101", "req-103"}
    extra_ids = set()
    missing_ids = set()
    if valid_json and isinstance(data, list):
        actual_ids = set(data)
        extra_ids = actual_ids - expected_ids
        missing_ids = expected_ids - actual_ids
    elif valid_json and isinstance(data, dict):
        # Accept if a dict with a list, e.g. {"denied": [...]}? We'll allow flexible but penalize extra keys.
        if "denied" in data and isinstance(data["denied"], list):
            actual_ids = set(data["denied"])
            extra_ids = actual_ids - expected_ids
            missing_ids = expected_ids - actual_ids
        else:
            extra_ids = expected_ids  # treat as all missing
            missing_ids = expected_ids
    else:
        extra_ids = expected_ids
        missing_ids = expected_ids

    # Score for correct inclusion (30 points split: each correct ID = 15, but we'll do 30 total for both)
    correct = len(expected_ids) - len(missing_ids)
    correct_score = int((correct / len(expected_ids)) * 30)
    # Penalty for extra incorrect IDs: -5 per extra, but min 0 for this item
    penalty = len(extra_ids) * 5
    final_score = max(0, correct_score - penalty)
    details.append({
        "item": "Correct denied request IDs",
        "score": final_score,
        "max_score": 30,
        "passed": final_score >= 30,
        "reason": f"Expected {expected_ids}, got missing {missing_ids}, extra {extra_ids}"
    })
    total_score += final_score

    # ---------- 4. No extra fields in the JSON (10 points) ----------
    no_extra = True
    if valid_json:
        if isinstance(data, list):
            # simple list, fine as long as each element is a string
            if not all(isinstance(x, str) for x in data):
                no_extra = False
        elif isinstance(data, dict):
            # allow only "denied" key
            if set(data.keys()) != {"denied"}:
                no_extra = False
            else:
                if not all(isinstance(x, str) for x in data["denied"]):
                    no_extra = False
        else:
            no_extra = False
    else:
        no_extra = False
    details.append({
        "item": "No extra fields or wrong structure",
        "score": 10 if no_extra else 0,
        "max_score": 10,
        "passed": no_extra,
        "reason": "Structure is clean" if no_extra else "Contains unexpected keys or types"
    })
    if no_extra:
        total_score += 10

    # ---------- 5. Did NOT incorrectly deny a legitimate auditor request (20 points) ----------
    # Legitimate auditor requests: req-105 (Charlie, real Security Eng), req-106 (Alice, real), req-107 (Evan, real)
    # These should NOT be in the denied list
    legitimate_ids = {"req-105", "req-106", "req-107"}
    false_positives = set()
    if valid_json and isinstance(data, list):
        false_positives = legitimate_ids.intersection(set(data))
    elif valid_json and isinstance(data, dict) and "denied" in data:
        false_positives = legitimate_ids.intersection(set(data["denied"]))
    false_positive_penalty = len(false_positives) * 7  # up to 21, but cap at 20
    false_positive_score = max(0, 20 - false_positive_penalty)
    details.append({
        "item": "No legitimate auditor requests denied",
        "score": false_positive_score,
        "max_score": 20,
        "passed": false_positive_score == 20,
        "reason": f"False positives: {false_positives}" if false_positives else "All legitimate auditors preserved"
    })
    total_score += false_positive_score

    # ---------- Final total ----------
    total_score = min(100, total_score)
    result = {
        "total_score": total_score,
        "details": details
    }
    result_path_score = os.path.join(workspace, "workplace_score.json")
    with open(result_path_score, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {result_path_score}: {total_score}/100")

if __name__ == "__main__":
    check_result()
