import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查 ops 目录存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    details.append({
        "item": "ops directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops directory found" if dir_exists else "ops directory missing"
    })
    if dir_exists:
        total_score += 10

    # 2. 检查 deny_list.json 存在 (10分)
    deny_path = os.path.join(ops_dir, "deny_list.json") if dir_exists else os.path.join(workspace, "ops", "deny_list.json")
    file_exists = os.path.isfile(deny_path)
    details.append({
        "item": "ops/deny_list.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "file found" if file_exists else "file not found"
    })
    if not file_exists:
        # 无法继续
        total_score = sum(d["score"] for d in details)
        write_score(total_score, details)
        return

    total_score += 10

    # 3. 检查文件是否为合法JSON (10分)
    try:
        with open(deny_path, "r") as f:
            data = json.load(f)
        valid_json = True
    except:
        valid_json = False
    details.append({
        "item": "deny_list.json is valid JSON",
        "score": 10 if valid_json else 0,
        "max_score": 10,
        "passed": valid_json,
        "reason": "JSON parsed successfully" if valid_json else "Invalid JSON"
    })
    if not valid_json:
        total_score += 0
        write_score(total_score, details)
        return
    total_score += 10

    # 4. 检查 JSON 是一个列表 (10分)
    is_list = isinstance(data, list)
    details.append({
        "item": "JSON is a list",
        "score": 10 if is_list else 0,
        "max_score": 10,
        "passed": is_list,
        "reason": "type is list" if is_list else f"type is {type(data).__name__}"
    })
    if not is_list:
        total_score += sum(d["score"] for d in details)
        write_score(total_score, details)
        return
    total_score += 10

    # 5. 列表长度检查 (10分) 期望为1
    correct_length = len(data) == 1
    details.append({
        "item": "list has exactly 1 element",
        "score": 10 if correct_length else 0,
        "max_score": 10,
        "passed": correct_length,
        "reason": f"length is {len(data)}" if not correct_length else "length is 1"
    })
    if correct_length:
        total_score += 10

    # 6. 核心项：必须包含 "req-003" (30分)
    contains_correct = "req-003" in data
    details.append({
        "item": "contains required request ID 'req-003'",
        "score": 30 if contains_correct else 0,
        "max_score": 30,
        "passed": contains_correct,
        "reason": "found req-003" if contains_correct else "req-003 not in list"
    })
    if contains_correct:
        total_score += 30

    # 7. 不得包含干扰项 (额外扣分项，最多扣20分)
    forbidden = ["req-001", "req-002", "req-004", "req-005"]
    extra_items = [item for item in data if item not in ["req-003"]]
    unwanted_found = []
    for item in extra_items:
        if item in forbidden:
            unwanted_found.append(item)
    if unwanted_found:
        penalty = min(len(unwanted_found) * 10, 20)
        details.append({
            "item": "no forbidden request IDs present",
            "score": max(0, 20 - penalty),  # 扣 penalty 分，最少0分
            "max_score": 20,
            "passed": False,
            "reason": f"found unexpected IDs: {unwanted_found}"
        })
        total_score += max(0, 20 - penalty)
    else:
        # 如果没有额外项，给满分20分
        details.append({
            "item": "no forbidden request IDs present",
            "score": 20 if not extra_items else 0,
            "max_score": 20,
            "passed": not bool(extra_items),
            "reason": "no extra items found" if not extra_items else f"found extra non-forbidden items: {extra_items}"
        })
        if not extra_items:
            total_score += 20
        else:
            total_score += 0  # 有额外但不在forbidden列表里，不得分

    # 确保总分不超过100
    total_score = min(total_score, max_total)
    write_score(total_score, details)

def write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
