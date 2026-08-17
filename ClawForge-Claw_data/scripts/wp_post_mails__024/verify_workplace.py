import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. ops 目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        score += 10
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ found"})
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ not found"})
        _write_score(workspace, score, details)
        return

    # 2. finance_summary.json 是否存在 (10分)
    result_path = os.path.join(ops_dir, "finance_summary.json")
    if os.path.isfile(result_path):
        score += 10
        details.append({"item": "finance_summary.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
    else:
        details.append({"item": "finance_summary.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        _write_score(workspace, score, details)
        return

    # 3. JSON 合法性 (10分)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        score += 10
        details.append({"item": "JSON is valid", "score": 10, "max_score": 10, "passed": True, "reason": "valid JSON"})
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": f"invalid JSON: {e}"})
        _write_score(workspace, score, details)
        return

    # 4. 根结构是 dict 并包含 items 和 total_amount (20分)
    if not isinstance(data, dict):
        details.append({"item": "root is dict", "score": 0, "max_score": 20, "passed": False, "reason": "root is not a dict"})
        _write_score(workspace, score, details)
        return
    if "items" not in data or "total_amount" not in data:
        details.append({"item": "required fields present", "score": 0, "max_score": 20, "passed": False, "reason": "missing items or total_amount"})
        _write_score(workspace, score, details)
        return
    if not isinstance(data["items"], list):
        details.append({"item": "items is list", "score": 0, "max_score": 20, "passed": False, "reason": "items is not a list"})
        _write_score(workspace, score, details)
        return
    if not isinstance(data["total_amount"], (int, float)):
        details.append({"item": "total_amount is numeric", "score": 0, "max_score": 20, "passed": False, "reason": "total_amount not numeric"})
        _write_score(workspace, score, details)
        return
    # 字段存在且类型正确
    score += 20
    details.append({"item": "root structure and field types", "score": 20, "max_score": 20, "passed": True, "reason": "dict with items list and numeric total_amount"})

    # 5. items 数量 (20分)
    if len(data["items"]) == 2:
        score += 20
        details.append({"item": "items count", "score": 20, "max_score": 20, "passed": True, "reason": "exactly 2 items"})
    else:
        details.append({"item": "items count", "score": 0, "max_score": 20, "passed": False, "reason": f"expected 2, got {len(data['items'])}"})
        _write_score(workspace, score, details)
        return

    # 6. 每个 item 的 email_id 和 amount 正确 (40分，各20)
    expected = [{"email_id": "em_002", "amount": 150.0},
                {"email_id": "em_005", "amount": 200.0}]
    item_correct = 0
    for exp in expected:
        found = any(item.get("email_id") == exp["email_id"] and item.get("amount") == exp["amount"] for item in data["items"])
        if found:
            item_correct += 1
    if item_correct == 2:
        score += 40
        details.append({"item": "items content (email_id & amount)", "score": 40, "max_score": 40, "passed": True, "reason": "both items match expected values"})
    else:
        details.append({"item": "items content (email_id & amount)", "score": 0, "max_score": 40, "passed": False, "reason": f"expected {expected}, got {data['items']}"})
        _write_score(workspace, score, details)
        return

    # 7. total_amount (20分)
    expected_total = 350.0
    if data["total_amount"] == expected_total:
        score += 20
        details.append({"item": "total_amount", "score": 20, "max_score": 20, "passed": True, "reason": f"total_amount is {expected_total}"})
    else:
        details.append({"item": "total_amount", "score": 0, "max_score": 20, "passed": False, "reason": f"expected {expected_total}, got {data['total_amount']}"})
        _write_score(workspace, score, details)
        return

    _write_score(workspace, score, details)

def _write_score(workspace, total, details):
    result = {"total_score": total, "details": details}
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
