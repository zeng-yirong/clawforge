import sys
import json
import os
import pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0

    # 1. Check ops/ directory exists (10 points)
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    score = 10 if dir_exists else 0
    total_score += score
    results.append({
        "item": "ops/ directory exists",
        "score": score,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "Directory ops/ found" if dir_exists else "ops/ not found"
    })

    # 2. Check ops/final_action_list.json exists (10 points)
    target_file = os.path.join(ops_dir, "final_action_list.json")
    file_exists = os.path.isfile(target_file) if dir_exists else False
    score = 10 if file_exists else 0
    total_score += score
    results.append({
        "item": "ops/final_action_list.json exists",
        "score": score,
        "max_score": 10,
        "passed": file_exists,
        "reason": "File found" if file_exists else "File missing"
    })

    if not file_exists:
        # Cannot proceed further, write partial score
        _write_score(total_score, results, workspace)
        return

    # 3. JSON validity (10 points)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        json_valid = True
        score = 10
        reason = "Valid JSON"
    except (json.JSONDecodeError, Exception) as e:
        json_valid = False
        score = 0
        reason = f"Invalid JSON: {e}"
    total_score += score
    results.append({
        "item": "JSON is valid",
        "score": score,
        "max_score": 10,
        "passed": json_valid,
        "reason": reason
    })

    if not json_valid:
        _write_score(total_score, results, workspace)
        return

    # Ensure data is a list
    if not isinstance(data, list):
        total_score += 0
        results.append({
            "item": "Root element is a list",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "Expected a JSON array, got " + str(type(data).__name__)
        })
        _write_score(total_score, results, workspace)
        return

    correct_items = [
        {"incident_id": "INC-001", "action": "Shutdown main power feed"},
        {"incident_id": "INC-003", "action": "Restart service via failover"}
    ]

    # 4. Length check (20 points)
    expected_len = 2
    actual_len = len(data)
    len_ok = actual_len == expected_len
    score = 20 if len_ok else 0
    total_score += score
    results.append({
        "item": f"Array has exactly {expected_len} items",
        "score": score,
        "max_score": 20,
        "passed": len_ok,
        "reason": f"Found {actual_len} items" if len_ok else f"Expected {expected_len}, got {actual_len}"
    })

    # 5. Each item has required fields (10 points)
    fields_ok = True
    for item in data:
        if not isinstance(item, dict):
            fields_ok = False
            break
        if "incident_id" not in item or "action" not in item:
            fields_ok = False
            break
    score = 10 if fields_ok else 0
    total_score += score
    results.append({
        "item": "All items have 'incident_id' and 'action' fields",
        "score": score,
        "max_score": 10,
        "passed": fields_ok,
        "reason": "Fields present" if fields_ok else "Missing or invalid fields"
    })

    if not fields_ok:
        _write_score(total_score, results, workspace)
        return

    # Build lookup from agent output
    agent_map = {item["incident_id"]: item["action"] for item in data}

    # 6. Check INC-001 present and action correct (15 points)
    inc1_present = "INC-001" in agent_map
    inc1_action_ok = agent_map.get("INC-001") == "Shutdown main power feed"
    inc1_passed = inc1_present and inc1_action_ok
    score = 15 if inc1_passed else 0
    total_score += score
    results.append({
        "item": "INC-001 present with correct action",
        "score": score,
        "max_score": 15,
        "passed": inc1_passed,
        "reason": "OK" if inc1_passed else f"Present={inc1_present}, ActionCorrect={inc1_action_ok}"
    })

    # 7. Check INC-003 present and action correct (15 points)
    inc3_present = "INC-003" in agent_map
    inc3_action_ok = agent_map.get("INC-003") == "Restart service via failover"
    inc3_passed = inc3_present and inc3_action_ok
    score = 15 if inc3_passed else 0
    total_score += score
    results.append({
        "item": "INC-003 present with correct action",
        "score": score,
        "max_score": 15,
        "passed": inc3_passed,
        "reason": "OK" if inc3_passed else f"Present={inc3_present}, ActionCorrect={inc3_action_ok}"
    })

    # 8. No extra items beyond the two required (10 points)
    allowed_ids = {"INC-001", "INC-003"}
    extra_ids = [item["incident_id"] for item in data if item["incident_id"] not in allowed_ids]
    no_extra = len(extra_ids) == 0
    score = 10 if no_extra else 0
    total_score += score
    results.append({
        "item": "No unexpected incident_ids",
        "score": score,
        "max_score": 10,
        "passed": no_extra,
        "reason": "Clean" if no_extra else f"Unexpected IDs: {extra_ids}"
    })

    # Final total capped at 100
    total_score = min(total_score, 100)
    _write_score(total_score, results, workspace)

def _write_score(total_score, details, workspace):
    result = {
        "total_score": total_score,
        "details": details
    }
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {output_path}: {total_score}/100")

if __name__ == "__main__":
    main()
