import json, os, sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 检查 ops 目录是否存在
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ exists"})
        score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ missing"})

    # 2. 检查 output 文件是否存在
    output_file = os.path.join(ops_dir, "updates.json")
    if not os.path.isfile(output_file):
        details.append({"item": "updates.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        details.append({"item": "JSON valid", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        details.append({"item": "output structure", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        details.append({"item": "correct count", "score": 0, "max_score": 20, "passed": False, "reason": "file missing"})
        details.append({"item": "correct contact IDs", "score": 0, "max_score": 30, "passed": False, "reason": "file missing"})
        details.append({"item": "tags correctness", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        details.append({"item": "no extra contacts", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        finalize(score, details)
        return

    details.append({"item": "updates.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file exists"})
    score += 10

    # 3. 解析 JSON
    try:
        with open(output_file, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON valid", "score": 10, "max_score": 10, "passed": True, "reason": "valid JSON"})
        score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON valid", "score": 0, "max_score": 10, "passed": False, "reason": f"parse error: {e}"})
        finalize(score, details)
        return

    # 4. 结构检查：必须是 list，每个元素有 contact_id 和 new_tags
    if not isinstance(data, list):
        details.append({"item": "output structure", "score": 0, "max_score": 10, "passed": False, "reason": "root not a list"})
        finalize(score, details)
        return
    for entry in data:
        if not isinstance(entry, dict) or "contact_id" not in entry or "new_tags" not in entry:
            details.append({"item": "output structure", "score": 0, "max_score": 10, "passed": False, "reason": "entry missing contact_id or new_tags"})
            finalize(score, details)
            return
    details.append({"item": "output structure", "score": 10, "max_score": 10, "passed": True, "reason": "valid list of contact_id+new_tags"})
    score += 10

    # 5. 预期结果（唯一答案）
    expected = ["c002", "c003", "c006"]
    expected_tags = ["business", "vip"]
    actual_ids = sorted([entry["contact_id"] for entry in data])

    # 数量
    if len(actual_ids) == 3:
        details.append({"item": "correct count", "score": 20, "max_score": 20, "passed": True, "reason": "exactly 3 contacts"})
        score += 20
    else:
        details.append({"item": "correct count", "score": 0, "max_score": 20, "passed": False, "reason": f"expected 3, got {len(actual_ids)}"})

    # ID 正确性
    if actual_ids == sorted(expected):
        details.append({"item": "correct contact IDs", "score": 30, "max_score": 30, "passed": True, "reason": "IDs match exactly"})
        score += 30
    else:
        details.append({"item": "correct contact IDs", "score": 0, "max_score": 30, "passed": False, "reason": f"got {actual_ids}, expected {sorted(expected)}"})

    # tags 正确性
    all_tags_ok = all(
        sorted(entry.get("new_tags", [])) == sorted(expected_tags) for entry in data
    )
    if all_tags_ok:
        details.append({"item": "tags correctness", "score": 10, "max_score": 10, "passed": True, "reason": "all new_tags are business and vip"})
        score += 10
    else:
        details.append({"item": "tags correctness", "score": 0, "max_score": 10, "passed": False, "reason": "some entries have wrong tags"})

    # 没有多余联系人
    if set(actual_ids) == set(expected):
        details.append({"item": "no extra contacts", "score": 10, "max_score": 10, "passed": True, "reason": "no extra contacts included"})
        score += 10
    else:
        details.append({"item": "no extra contacts", "score": 0, "max_score": 10, "passed": False, "reason": "unexpected contact IDs present"})

    finalize(score, details)

def finalize(score, details):
    result = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {score}/100")

if __name__ == "__main__":
    main()
