import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total = 0

    # 1. ops directory exists
    ops_dir = os.path.join(workspace, "ops")
    dir_ok = os.path.isdir(ops_dir)
    score_details.append({
        "item": "ops directory exists",
        "score": 10 if dir_ok else 0,
        "max_score": 10,
        "passed": dir_ok,
        "reason": "ops directory found" if dir_ok else "ops directory not found"
    })
    if dir_ok:
        total += 10

    # 2. over_humidity.json exists
    target = os.path.join(ops_dir, "over_humidity.json")
    file_ok = os.path.isfile(target)
    score_details.append({
        "item": "over_humidity.json exists",
        "score": 10 if file_ok else 0,
        "max_score": 10,
        "passed": file_ok,
        "reason": "File exists" if file_ok else "File not found"
    })
    if file_ok:
        total += 10
    else:
        _write_score(workspace, total, score_details)
        return

    # 3. JSON valid and is a list
    try:
        with open(target, "r") as f:
            data = json.load(f)
        is_list = isinstance(data, list)
        score_details.append({
            "item": "valid JSON and root is a list",
            "score": 10 if is_list else 0,
            "max_score": 10,
            "passed": is_list,
            "reason": "Valid JSON list" if is_list else "Root is not a list"
        })
        if is_list:
            total += 10
        else:
            _write_score(workspace, total, score_details)
            return
    except Exception as e:
        score_details.append({
            "item": "valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        _write_score(workspace, total, score_details)
        return

    # 4. all items are strings
    all_str = all(isinstance(x, str) for x in data)
    score_details.append({
        "item": "all elements are strings",
        "score": 10 if all_str else 0,
        "max_score": 10,
        "passed": all_str,
        "reason": "All strings" if all_str else "Some non-string elements"
    })
    if all_str:
        total += 10

    # 5. set correctness (expected = {"d_003", "d_005"})
    expected = {"d_003", "d_005"}
    actual = set(data)
    missing = expected - actual
    extra = actual - expected
    if not missing and not extra:
        set_score = 60
        set_reason = "Exactly correct set: d_003, d_005"
        passed = True
    elif not missing and extra:
        set_score = 30
        set_reason = f"No missing items but has extra: {extra}"
        passed = False
    elif missing and not extra:
        set_score = 30
        set_reason = f"Missing items: {missing}, no extra"
        passed = False
    else:
        set_score = 0
        set_reason = f"Both missing: {missing} and extra: {extra}"
        passed = False
    score_details.append({
        "item": "correct device IDs set",
        "score": set_score,
        "max_score": 60,
        "passed": passed,
        "reason": set_reason
    })
    total += set_score

    _write_score(workspace, total, score_details)

def _write_score(workspace, total, details):
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump({"total_score": total, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
