import sys
import os
import json

def check_file(ws):
    target = os.path.join(ws, "ops", "action_queue.json")
    if not os.path.isfile(target):
        return {"total_score": 0, "details": [{"item": "file_exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/action_queue.json not found"}]}
    return target

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total = 0

    # 1. file exists (10)
    target = check_file(workspace)
    if isinstance(target, dict):  # error
        score_obj = target
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_obj, f, indent=2)
        return

    details.append({"item": "file_exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/action_queue.json found"})
    total += 10

    # 2. valid JSON (10)
    try:
        with open(target, "r") as f:
            data = json.load(f)
        details.append({"item": "valid_json", "score": 10, "max_score": 10, "passed": True, "reason": "file is valid JSON"})
        total += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "valid_json", "score": 0, "max_score": 10, "passed": False, "reason": f"invalid JSON: {str(e)}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        return

    # 3. is a list (10)
    if not isinstance(data, list):
        details.append({"item": "is_list", "score": 0, "max_score": 10, "passed": False, "reason": "expected list, got " + type(data).__name__})
        total += 0
    else:
        details.append({"item": "is_list", "score": 10, "max_score": 10, "passed": True, "reason": "data is a list"})
        total += 10

    # 4. every element is string (10)
    if isinstance(data, list):
        all_str = all(isinstance(x, str) for x in data)
        if all_str:
            details.append({"item": "element_types", "score": 10, "max_score": 10, "passed": True, "reason": "all elements are strings"})
            total += 10
        else:
            details.append({"item": "element_types", "score": 0, "max_score": 10, "passed": False, "reason": "some elements are not strings"})
            total += 0

    # 5. length is 3 (10)
    if isinstance(data, list):
        if len(data) == 3:
            details.append({"item": "length", "score": 10, "max_score": 10, "passed": True, "reason": "exactly 3 IDs"})
            total += 10
        else:
            details.append({"item": "length", "score": 0, "max_score": 10, "passed": False, "reason": f"expected 3, got {len(data)}"})
            total += 0

    # 6. contains correct IDs (30, each 10)
    expected_ids = ["incident-003", "incident-001", "incident-002"]
    if isinstance(data, list):
        for i, exp in enumerate(expected_ids):
            if i < len(data) and data[i] == exp:
                details.append({"item": f"position_{i}_correct", "score": 10, "max_score": 10, "passed": True, "reason": f"expected {exp}, got {data[i]}"})
                total += 10
            else:
                actual = data[i] if i < len(data) else "MISSING"
                details.append({"item": f"position_{i}_correct", "score": 0, "max_score": 10, "passed": False, "reason": f"expected {exp}, got {actual}"})
                total += 0

    # 7. order correctness (20)
    if isinstance(data, list) and len(data) >= 3:
        order_ok = (data == expected_ids)
        if order_ok:
            details.append({"item": "order_correct", "score": 20, "max_score": 20, "passed": True, "reason": "IDs are in expected order"})
            total += 20
        else:
            details.append({"item": "order_correct", "score": 0, "max_score": 20, "passed": False, "reason": f"order mismatch: got {data}, expected {expected_ids}"})
            total += 0
    else:
        details.append({"item": "order_correct", "score": 0, "max_score": 20, "passed": False, "reason": "cannot check order due to earlier failures"})
        total += 0

    # final total capped at 100
    total = min(total, 100)
    score_obj = {"total_score": total, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score_obj, f, indent=2)

if __name__ == "__main__":
    verify()
