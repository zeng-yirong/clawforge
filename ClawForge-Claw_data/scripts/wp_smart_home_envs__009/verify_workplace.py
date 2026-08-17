import json
import os
import sys

def verify(workspace: str):
    details = []
    total_score = 0

    # 1. 目录结构检查（10分）
    req_dirs = ["ops", "data", "data/devices", "data/health", "data/electricity", "data/weather"]
    dirs_ok = all(os.path.isdir(os.path.join(workspace, d)) for d in req_dirs)
    details.append({
        "item": "Required directories exist",
        "score": 10 if dirs_ok else 0,
        "max_score": 10,
        "passed": dirs_ok,
        "reason": "All standard directories found" if dirs_ok else "Missing one or more directories"
    })
    if dirs_ok:
        total_score += 10

    # 2. 目标文件存在（10分）
    target = os.path.join(workspace, "ops", "peak_hour_disable.json")
    file_exists = os.path.isfile(target)
    details.append({
        "item": "Target file ops/peak_hour_disable.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "File found" if file_exists else "File not found"
    })
    if file_exists:
        total_score += 10

    # 3. JSON 合法性（10分）
    content = None
    json_valid = False
    if file_exists:
        try:
            with open(target, "r") as f:
                content = json.load(f)
            json_valid = True
        except (json.JSONDecodeError, Exception):
            json_valid = False
    details.append({
        "item": "Target file is valid JSON",
        "score": 10 if json_valid else 0,
        "max_score": 10,
        "passed": json_valid,
        "reason": "Valid JSON" if json_valid else "Invalid or unreadable JSON"
    })
    if json_valid:
        total_score += 10

    # 4. 内容准确性（70分）
    content_ok = False
    if json_valid and isinstance(content, list):
        expected = ["ac_living_room"]
        # 顺序无关，去重检查
        content_set = set(content)
        expected_set = set(expected)
        if content_set == expected_set:
            content_ok = True
            score = 70
            reason = f"Exactly correct devices: {sorted(content_set)}"
        elif content_set < expected_set:
            # 缺少部分设备
            missing = expected_set - content_set
            score = 30
            reason = f"Missing devices: {missing}"
        elif content_set > expected_set:
            extra = content_set - expected_set
            score = 30
            reason = f"Extra devices: {extra}"
        else:
            score = 0
            reason = "Unexpected content"
    else:
        score = 0
        reason = "Content is not a list"
    details.append({
        "item": "Content matches expected device list",
        "score": score,
        "max_score": 70,
        "passed": content_ok,
        "reason": reason
    })
    total_score += score

    # 最终总分
    total = min(total_score, 100)
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    return result

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
