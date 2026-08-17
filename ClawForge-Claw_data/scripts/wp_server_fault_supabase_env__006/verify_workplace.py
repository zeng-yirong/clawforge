import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)
    score_details = []
    total_score = 0

    # 1. Check ops directory exists (10)
    ops_dir = "ops"
    dir_exists = os.path.isdir(ops_dir)
    score_details.append({
        "item": "ops directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops directory found" if dir_exists else "ops directory missing"
    })
    if dir_exists:
        total_score += 10

    # 2. Check critical_incidents.json exists and is valid JSON (10)
    result_path = os.path.join(ops_dir, "critical_incidents.json")
    file_exists = os.path.isfile(result_path)
    valid_json = False
    data = None
    if file_exists:
        try:
            with open(result_path) as f:
                data = json.load(f)
            valid_json = True
        except (json.JSONDecodeError, Exception):
            valid_json = False
    score_details.append({
        "item": "critical_incidents.json exists and valid JSON",
        "score": 10 if (file_exists and valid_json) else 0,
        "max_score": 10,
        "passed": file_exists and valid_json,
        "reason": "File valid" if (file_exists and valid_json) else ("File missing" if not file_exists else "Invalid JSON")
    })
    if file_exists and valid_json:
        total_score += 10

    # 3. Check structure: must have incident_ids key, value must be list (10)
    has_key = False
    is_list = False
    if data is not None:
        has_key = "incident_ids" in data
        if has_key:
            is_list = isinstance(data["incident_ids"], list)
    key_ok = has_key and is_list
    score_details.append({
        "item": "JSON contains 'incident_ids' list",
        "score": 10 if key_ok else 0,
        "max_score": 10,
        "passed": key_ok,
        "reason": "Structure correct" if key_ok else ("Missing key" if not has_key else "incident_ids is not a list")
    })
    if key_ok:
        total_score += 10

    # 4. Check no extra keys (10)
    extra = False
    if data is not None:
        extra = len(data.keys()) > 1
    score_details.append({
        "item": "No extra fields in JSON",
        "score": 10 if (data is not None and not extra) else 0,
        "max_score": 10,
        "passed": data is not None and not extra,
        "reason": "Only incident_ids present" if (data is not None and not extra) else ("Extra keys found" if extra else "No data")
    })
    if data is not None and not extra:
        total_score += 10

    # 5. Check incident IDs correctness (50)
    # Expected: INC-001, INC-003, INC-005 (service_down, critical, status not closed)
    # INC-008 is also service_down critical open -> it should be included based on criteria.
    # Re-evaluate: prompt says "服务完全不可用 且 严重等级最高 的工单，注意那些还没关闭的才算"
    # INC-008 is service_down critical open -> include. So expected 4 IDs: INC-001, INC-003, INC-005, INC-008
    expected_ids = {"INC-001", "INC-003", "INC-005", "INC-008"}
    if key_ok:
        actual_ids = set(data["incident_ids"])
        correct = actual_ids == expected_ids
        # Count matches
        common = actual_ids & expected_ids
        missing = expected_ids - actual_ids
        extra_ids = actual_ids - expected_ids
        points = 0
        if correct:
            points = 50
        else:
            # partial: each correct ID 10 points, each incorrect ID -5 (min 0)
            correct_count = len(common)
            incorrect_count = len(extra_ids) + len(missing)
            points = max(0, correct_count * 12.5 - incorrect_count * 5)  # max 50, min 0
        score_details.append({
            "item": "Incident IDs match expected set",
            "score": int(points),
            "max_score": 50,
            "passed": correct,
            "reason": f"Expected {sorted(expected_ids)}, got {sorted(actual_ids)}" if not correct else "All IDs correct"
        })
        total_score += int(points)
    else:
        score_details.append({
            "item": "Incident IDs match expected set",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": "Could not read incident_ids"
        })

    # Write score file
    final_score = min(total_score, 100)
    result = {
        "total_score": final_score,
        "details": score_details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
