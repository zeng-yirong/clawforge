import json
import os
import sys

def verify(workspace):
    details = []
    total_score = 0

    # 1. 目录 ops 是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    details.append({
        "item": "ops directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops/ found" if dir_exists else "ops/ not found"
    })
    if dir_exists:
        total_score += 10

    # 2. 文件 ops/blocked_exports.json 是否存在 (10分)
    result_path = os.path.join(ops_dir, "blocked_exports.json")
    file_exists = os.path.isfile(result_path)
    details.append({
        "item": "blocked_exports.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "file found" if file_exists else "file missing"
    })
    if file_exists:
        total_score += 10

    # 3. JSON 格式合法性 (10分)
    json_valid = False
    parsed = None
    if file_exists:
        try:
            with open(result_path, "r") as f:
                parsed = json.load(f)
            json_valid = True
            reason = "valid JSON"
        except (json.JSONDecodeError, Exception) as e:
            reason = f"invalid JSON: {e}"
    else:
        reason = "file not present, skipped"
    details.append({
        "item": "JSON is valid",
        "score": 10 if json_valid else 0,
        "max_score": 10,
        "passed": json_valid,
        "reason": reason
    })
    if json_valid:
        total_score += 10

    # 4. 包含键 "request_ids" (10分)
    has_key = json_valid and isinstance(parsed, dict) and "request_ids" in parsed
    details.append({
        "item": "key 'request_ids' exists",
        "score": 10 if has_key else 0,
        "max_score": 10,
        "passed": has_key,
        "reason": "key present" if has_key else "key missing or wrong type"
    })
    if has_key:
        total_score += 10

    # 5. request_ids 是列表 (10分)
    is_list = has_key and isinstance(parsed["request_ids"], list)
    details.append({
        "item": "request_ids is a list",
        "score": 10 if is_list else 0,
        "max_score": 10,
        "passed": is_list,
        "reason": "type is list" if is_list else f"type is {type(parsed['request_ids']).__name__}"
    })
    if is_list:
        total_score += 10

    # 6. 列表长度为2 (10分)
    correct_length = is_list and len(parsed["request_ids"]) == 2
    details.append({
        "item": "list contains exactly 2 request IDs",
        "score": 10 if correct_length else 0,
        "max_score": 10,
        "passed": correct_length,
        "reason": f"length = {len(parsed['request_ids'])}" if is_list else "n/a"
    })
    if correct_length:
        total_score += 10

    # 7. 包含 req-002 (15分)
    has_req002 = is_list and "req-002" in parsed["request_ids"]
    details.append({
        "item": "contains 'req-002'",
        "score": 15 if has_req002 else 0,
        "max_score": 15,
        "passed": has_req002,
        "reason": "present" if has_req002 else "missing"
    })
    if has_req002:
        total_score += 15

    # 8. 包含 req-003 (15分)
    has_req003 = is_list and "req-003" in parsed["request_ids"]
    details.append({
        "item": "contains 'req-003'",
        "score": 15 if has_req003 else 0,
        "max_score": 15,
        "passed": has_req003,
        "reason": "present" if has_req003 else "missing"
    })
    if has_req003:
        total_score += 15

    # 9. 不包含额外 ID (10分) —— 只允许 req-002 和 req-003
    extra_ids = []
    if is_list:
        allowed = {"req-002", "req-003"}
        for rid in parsed["request_ids"]:
            if rid not in allowed:
                extra_ids.append(rid)
    no_extra = is_list and len(extra_ids) == 0
    details.append({
        "item": "no extra request IDs",
        "score": 10 if no_extra else 0,
        "max_score": 10,
        "passed": no_extra,
        "reason": "clean" if no_extra else f"extra: {extra_ids}"
    })
    if no_extra:
        total_score += 10

    # 汇总
    total_score = min(total_score, 100)  # 保险
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
