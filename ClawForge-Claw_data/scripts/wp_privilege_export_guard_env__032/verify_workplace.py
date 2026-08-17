import os
import sys
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0

    # 1. 检查 ops 目录是否存在 (10分)
    ops_path = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_path)
    if dir_exists:
        total_score += 10
        results.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "directory created"})
    else:
        results.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "missing ops directory"})

    # 2. 检查 denied_target.json 是否存在 (10分)
    target_path = os.path.join(workspace, "ops", "denied_target.json")
    file_exists = os.path.isfile(target_path)
    if file_exists:
        total_score += 10
        results.append({"item": "denied_target.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file present"})
    else:
        results.append({"item": "denied_target.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        # 后续检查跳过
        write_score(results, total_score)
        return

    # 3. JSON 格式合法 (10分)
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        total_score += 10
        results.append({"item": "valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "parsed successfully"})
    except (json.JSONDecodeError, Exception) as e:
        results.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        write_score(results, total_score)
        return

    # 4. 必要字段存在: request_id, reason, decided_by (各5分，共15分)
    fields_ok = True
    for field in ["request_id", "reason", "decided_by"]:
        if field in data:
            total_score += 5
            results.append({"item": f"field '{field}' present", "score": 5, "max_score": 5, "passed": True, "reason": "found"})
        else:
            fields_ok = False
            results.append({"item": f"field '{field}' present", "score": 0, "max_score": 5, "passed": False, "reason": "missing"})

    # 5. request_id 应为 "REQ-001" (20分)
    rid = data.get("request_id", "")
    if rid == "REQ-001":
        total_score += 20
        results.append({"item": "correct request_id", "score": 20, "max_score": 20, "passed": True, "reason": "matches expected"})
    else:
        results.append({"item": "correct request_id", "score": 0, "max_score": 20, "passed": False, "reason": f"got '{rid}', expected 'REQ-001'"})

    # 6. reason 应包含权限相关的关键词 (30分)
    reason = data.get("reason", "")
    keywords = ["access", "permission"]
    if all(kw.lower() in reason.lower() for kw in keywords):
        total_score += 30
        results.append({"item": "reason contains access/permission keywords", "score": 30, "max_score": 30, "passed": True, "reason": f"found in '{reason}'"})
    else:
        results.append({"item": "reason contains access/permission keywords", "score": 0, "max_score": 30, "passed": False, "reason": f"missing keywords in '{reason}'"})

    # 7. 没有错误地针对其他请求 (5分) —— 确保只有 REQ-001
    if rid == "REQ-001":
        total_score += 5
        results.append({"item": "no extra requests mentioned", "score": 5, "max_score": 5, "passed": True, "reason": "only REQ-001"})
    else:
        results.append({"item": "no extra requests mentioned", "score": 0, "max_score": 5, "passed": False, "reason": "unexpected request_id"})

    write_score(results, total_score)

def write_score(details, total):
    output = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
