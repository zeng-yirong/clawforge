import sys
import json
import os

def verify(workspace: str) -> dict:
    details = []
    total_score = 0

    # -- 1. Check ops directory exists  (5 points)
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    details.append({
        "item": "ops directory exists",
        "score": 5 if dir_exists else 0,
        "max_score": 5,
        "passed": dir_exists,
        "reason": "Found" if dir_exists else "Missing"
    })
    if dir_exists:
        total_score += 5

    # -- 2. Check ops/ups_resolutions.json exists  (5 points)
    result_path = os.path.join(workspace, "ops", "ups_resolutions.json")
    file_exists = os.path.isfile(result_path)
    details.append({
        "item": "ops/ups_resolutions.json exists",
        "score": 5 if file_exists else 0,
        "max_score": 5,
        "passed": file_exists,
        "reason": "Found" if file_exists else "Missing"
    })
    if file_exists:
        total_score += 5

    if not file_exists:
        # cannot continue
        return {"total_score": total_score, "details": details}

    # -- 3. Parse JSON  (10 points)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        parsed_ok = True
        reason = "Valid JSON"
    except Exception as e:
        parsed_ok = False
        reason = f"Invalid JSON: {e}"
    details.append({
        "item": "JSON validity",
        "score": 10 if parsed_ok else 0,
        "max_score": 10,
        "passed": parsed_ok,
        "reason": reason
    })
    if parsed_ok:
        total_score += 10
    else:
        return {"total_score": total_score, "details": details}

    # -- 4. Check it is a list  (5 points)
    is_list = isinstance(data, list)
    details.append({
        "item": "Root is a list",
        "score": 5 if is_list else 0,
        "max_score": 5,
        "passed": is_list,
        "reason": "Is list" if is_list else "Not a list"
    })
    if is_list:
        total_score += 5
    else:
        return {"total_score": total_score, "details": details}

    # -- 5. List length must be exactly 2 (the two valid UPS tickets)  (20 points)
    correct_count = (len(data) == 2)
    details.append({
        "item": "Exactly 2 resolution records (INC-001 & INC-003)",
        "score": 20 if correct_count else 0,
        "max_score": 20,
        "passed": correct_count,
        "reason": f"Found {len(data)} records" if not correct_count else "Correct count"
    })
    if correct_count:
        total_score += 20

    # -- 6. Sort records by incident_id for deterministic check  (agent should have done it)
    sorted_data = sorted(data, key=lambda x: x.get("incident_id", ""))
    # expected records
    expected = [
        {"incident_id": "INC-001", "action": "power_cycle_ups"},
        {"incident_id": "INC-003", "action": "transfer_to_backup"}
    ]

    # 6a. Check first record  (20 points)
    first_ok = False
    if len(sorted_data) >= 1:
        rec = sorted_data[0]
        if rec.get("incident_id") == "INC-001" and rec.get("action") == "power_cycle_ups":
            first_ok = True
    details.append({
        "item": "INC-001 action is 'power_cycle_ups'",
        "score": 20 if first_ok else 0,
        "max_score": 20,
        "passed": first_ok,
        "reason": "Match" if first_ok else f"Got {sorted_data[0] if len(sorted_data)>0 else 'missing'}"
    })
    if first_ok:
        total_score += 20

    # 6b. Check second record  (20 points)
    second_ok = False
    if len(sorted_data) >= 2:
        rec = sorted_data[1]
        if rec.get("incident_id") == "INC-003" and rec.get("action") == "transfer_to_backup":
            second_ok = True
    details.append({
        "item": "INC-003 action is 'transfer_to_backup'",
        "score": 20 if second_ok else 0,
        "max_score": 20,
        "passed": second_ok,
        "reason": "Match" if second_ok else f"Got {sorted_data[1] if len(sorted_data)>1 else 'missing'}"
    })
    if second_ok:
        total_score += 20

    # -- 7. No extra fields besides incident_id and action  (10 points)
    extra_fields_penalty = 0
    extra_reason = ""
    for i, rec in enumerate(sorted_data):
        keys = set(rec.keys())
        allowed = {"incident_id", "action"}
        extra = keys - allowed
        if extra:
            extra_fields_penalty += 5  # 5 per offending record
            extra_reason = f"Record {i} has extra keys: {extra}"
    if extra_fields_penalty > 10:
        extra_fields_penalty = 10
    no_extra_score = 10 - extra_fields_penalty
    if no_extra_score < 0:
        no_extra_score = 0
    passed_extra = (extra_fields_penalty == 0)
    details.append({
        "item": "No extra fields beyond incident_id and action",
        "score": no_extra_score,
        "max_score": 10,
        "passed": passed_extra,
        "reason": "Clean" if passed_extra else extra_reason
    })
    total_score += no_extra_score

    # ensure total_score not exceed 100
    total_score = min(total_score, 100)
    return {"total_score": total_score, "details": details}


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
