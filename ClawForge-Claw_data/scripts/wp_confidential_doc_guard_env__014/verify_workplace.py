import json
import os
import sys

def verify(workspace: str):
    details = []
    total_score = 0
    max_total = 100

    # 1. ops directory exists (5 points)
    ops_path = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_path)
    details.append({
        "item": "ops directory exists",
        "score": 5 if dir_exists else 0,
        "max_score": 5,
        "passed": dir_exists,
        "reason": "Found ops/" if dir_exists else "Missing ops/ directory"
    })
    total_score += details[-1]["score"]

    # 2. denied_requests.json exists (10 points)
    file_path = os.path.join(ops_path, "denied_requests.json")
    file_exists = os.path.isfile(file_path)
    details.append({
        "item": "denied_requests.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "File present" if file_exists else "File not found"
    })
    if not file_exists:
        total_score += details[-1]["score"]
        # Write result and exit early
        final = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    total_score += details[-1]["score"]

    # 3. JSON parseable (10 points)
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        parse_ok = True
    except Exception as e:
        parse_ok = False
        reason = f"JSON parse error: {str(e)}"
    details.append({
        "item": "JSON format valid",
        "score": 10 if parse_ok else 0,
        "max_score": 10,
        "passed": parse_ok,
        "reason": "Valid JSON" if parse_ok else reason
    })
    total_score += details[-1]["score"]
    if not parse_ok:
        final = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    # 4. Has "denied" field (5 points)
    has_denied = isinstance(data, dict) and "denied" in data
    details.append({
        "item": "Has 'denied' field",
        "score": 5 if has_denied else 0,
        "max_score": 5,
        "passed": has_denied,
        "reason": "Field present" if has_denied else "Missing 'denied' key"
    })
    total_score += details[-1]["score"]

    # 5. "denied" is a list (10 points)
    if has_denied:
        is_list = isinstance(data["denied"], list)
    else:
        is_list = False
    details.append({
        "item": "'denied' is a list",
        "score": 10 if is_list else 0,
        "max_score": 10,
        "passed": is_list,
        "reason": "Is list" if is_list else "Not a list"
    })
    total_score += details[-1]["score"]

    # 6. List length correct (10 points)
    expected_ids = {"req-02", "req-04", "req-07", "req-08"}
    if is_list:
        actual_ids = set(data["denied"])
        length_ok = len(actual_ids) == len(expected_ids)
    else:
        actual_ids = set()
        length_ok = False
    details.append({
        "item": "List length matches expected (4)",
        "score": 10 if length_ok else 0,
        "max_score": 10,
        "passed": length_ok,
        "reason": f"Length {len(actual_ids)} correct" if length_ok else f"Length {len(actual_ids)} != 4"
    })
    total_score += details[-1]["score"]

    # 7. Each expected ID present (10 each, total 40)
    correct_count = 0
    extra_ids = set()
    if is_list:
        for rid in expected_ids:
            if rid in actual_ids:
                correct_count += 1
        extra_ids = actual_ids - expected_ids
    expected_score_each = 10  # per correct ID
    correct_score = correct_count * expected_score_each
    # Penalty for extra IDs: -10 each
    penalty = len(extra_ids) * 10
    final_correct_score = max(0, correct_score - penalty)
    details.append({
        "item": "Correct denied IDs (exact match, no extras)",
        "score": final_correct_score,
        "max_score": 40,
        "passed": correct_count == len(expected_ids) and len(extra_ids) == 0,
        "reason": f"Correct: {correct_count}/{len(expected_ids)}, extras: {len(extra_ids)} => score {final_correct_score}"
    })
    total_score += details[-1]["score"]

    # Final score within 0-100
    total_score = min(100, max(0, total_score))
    final = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
