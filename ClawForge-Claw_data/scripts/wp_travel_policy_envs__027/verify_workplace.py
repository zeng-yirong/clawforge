import json
import os
import sys

def verify_workplace(workspace: str):
    result = {
        "total_score": 0,
        "details": []
    }

    # 辅助函数
    def check(description, max_score, passed, reason=""):
        score = max_score if passed else 0
        result["details"].append({
            "item": description,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        return score

    score = 0

    # 1. 检查 ops 目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    ops_exists = os.path.isdir(ops_dir)
    score += check("Directory 'ops/' exists", 10, ops_exists, "Missing ops directory" if not ops_exists else "")

    # 2. 检查目标文件是否存在 (10分)
    target_file = os.path.join(ops_dir, "approval_required.json")
    file_exists = os.path.isfile(target_file)
    score += check("File 'ops/approval_required.json' exists", 10, file_exists, "File not found" if not file_exists else "")

    if not file_exists:
        result["total_score"] = score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 检查 JSON 格式是否合法 (10分)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        valid_json = True
    except (json.JSONDecodeError, Exception):
        valid_json = False
    score += check("JSON is valid", 10, valid_json, "Failed to parse JSON" if not valid_json else "")

    if not valid_json:
        result["total_score"] = score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 4. 检查顶层字段 "approvals" 是否存在且为 list (10分)
    has_approvals = isinstance(data, dict) and "approvals" in data
    is_list = has_approvals and isinstance(data["approvals"], list)
    score += check("Contains key 'approvals' of type list", 10, has_approvals and is_list,
                   "Missing or wrong type" if not (has_approvals and is_list) else "")

    if not (has_approvals and is_list):
        result["total_score"] = score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    approvals = data["approvals"]

    # 5. 检查数量是否正确 (20分)
    expected_count = 3
    count_ok = len(approvals) == expected_count
    score += check(f"Number of approvals is {expected_count}", 20, count_ok,
                   f"Expected {expected_count}, got {len(approvals)}" if not count_ok else "")

    # 6. 检查每个元素必须包含 booking_id, total_cost, policy_id, approver (10分)
    fields = {"booking_id", "total_cost", "policy_id", "approver"}
    all_have_fields = all(
        isinstance(item, dict) and fields.issubset(item.keys())
        for item in approvals
    )
    score += check("Each approval has required fields (booking_id, total_cost, policy_id, approver)", 10,
                   all_have_fields, "Missing fields in one or more entries" if not all_have_fields else "")

    # 7. 精确匹配每个预期的审批记录 (30分，每个10分)
    # 预期答案：根据 env_builder 数据计算
    expected = {
        "booking_001": {"total_cost": 2500, "policy_id": "acme_business_v2", "approver": "Alice Smith"},
        "booking_003": {"total_cost": 8000, "policy_id": "acme_exec_v1", "approver": "Charlie Davis"},
        "booking_005": {"total_cost": 3000, "policy_id": "acme_business_v2", "approver": "Charlie Davis"}
    }

    # 构建映射：booking_id -> item
    actual_map = {}
    for item in approvals:
        bid = item.get("booking_id")
        if bid:
            actual_map[bid] = item

    correct_count = 0
    for bid, exp in expected.items():
        if bid in actual_map:
            item = actual_map[bid]
            match = (
                item.get("total_cost") == exp["total_cost"] and
                item.get("policy_id") == exp["policy_id"] and
                item.get("approver") == exp["approver"]
            )
            if match:
                correct_count += 1
    score += check("Each expected booking correct (3 items, 10 each)", 30, correct_count == 3,
                   f"Correct items: {correct_count}/3" if correct_count != 3 else "")

    # 额外检查：没有多余的不符合条件的预订
    unexpected = [bid for bid in actual_map if bid not in expected]
    if unexpected:
        score += check("No extra unexpected bookings", 0, False,
                       f"Unexpected booking_ids: {unexpected}")
        # 扣分？但我们已经设了满分100，这里只是记录。也可以不扣分，但为了严格，我们设一个检查项但没分，或者并到上面。
        # 由于上面已经扣了字段检查分，这里不再重复，但我们可以记录。
        # 为了简洁，不额外扣分。

    result["total_score"] = score
    result["details"].append({
        "item": "No unexpected extra bookings (informational)",
        "score": 0,
        "max_score": 0,
        "passed": len(unexpected) == 0,
        "reason": f"Found extra: {unexpected}" if unexpected else ""
    })

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
