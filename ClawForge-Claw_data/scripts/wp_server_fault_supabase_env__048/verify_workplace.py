import sys
import os
import json

def check_environment(workspace):
    result = {"total_score": 0, "details": []}
    # 1. 目录结构检查 (10分)
    dirs_ok = True
    for d in ["db_dumps", "ops"]:
        if os.path.isdir(os.path.join(workspace, d)):
            result["details"].append({
                "item": f"Directory '{d}' exists",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": ""
            })
        else:
            result["details"].append({
                "item": f"Directory '{d}' exists",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Missing directory: {d}"
            })
            dirs_ok = False

    # 2. 目标文件是否存在 (10分)
    target_path = os.path.join(workspace, "ops", "kill_target.json")
    if os.path.isfile(target_path):
        result["details"].append({
            "item": "File 'ops/kill_target.json' exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": ""
        })
    else:
        result["details"].append({
            "item": "File 'ops/kill_target.json' exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # 如果文件不存在，直接返回，避免后面解析报错
        result["total_score"] = sum(d["score"] for d in result["details"])
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f)
        return result

    # 3. JSON 合法性 (10分)
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        result["details"].append({
            "item": "JSON is parseable",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": ""
        })
    except (json.JSONDecodeError, Exception) as e:
        result["details"].append({
            "item": "JSON is parseable",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        result["total_score"] = sum(d["score"] for d in result["details"])
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f)
        return result

    # 4. 键 'session_id' 存在 (10分)
    if "session_id" in data:
        result["details"].append({
            "item": "Key 'session_id' exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": ""
        })
    else:
        result["details"].append({
            "item": "Key 'session_id' exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Key not found. Keys: {list(data.keys())}"
        })

    # 5. 'session_id' 是整数 (10分)
    sid = data.get("session_id")
    if isinstance(sid, int):
        result["details"].append({
            "item": "'session_id' is integer type",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": ""
        })
    else:
        result["details"].append({
            "item": "'session_id' is integer type",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Value {sid} has type {type(sid).__name__}"
        })

    # 6. 值正确为 12345 (40分)
    expected_id = 12345
    if sid == expected_id:
        result["details"].append({
            "item": "session_id value is correct (12345)",
            "score": 40,
            "max_score": 40,
            "passed": True,
            "reason": ""
        })
    else:
        result["details"].append({
            "item": "session_id value is correct (12345)",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": f"Got {sid}, expected {expected_id}"
        })

    # 7. 没有多余键 (10分)
    expected_keys = {"session_id"}
    actual_keys = set(data.keys())
    if actual_keys == expected_keys:
        result["details"].append({
            "item": "No extra keys in JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": ""
        })
    else:
        extra = actual_keys - expected_keys
        missing = expected_keys - actual_keys
        result["details"].append({
            "item": "No extra keys in JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Extra keys: {extra}, Missing keys: {missing}"
        })

    # 计算总分
    result["total_score"] = sum(d["score"] for d in result["details"])
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    return result

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    check_environment(workspace)
