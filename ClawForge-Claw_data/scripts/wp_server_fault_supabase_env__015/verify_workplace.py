import os
import sys
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 目录结构检查 (10分)
    required_dirs = ["logs", "ops"]
    missing_dirs = []
    for d in required_dirs:
        full_path = os.path.join(workspace, d)
        if not os.path.isdir(full_path):
            missing_dirs.append(d)
    if missing_dirs:
        score_details.append({
            "item": "Directory structure",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Missing directories: {', '.join(missing_dirs)}"
        })
    else:
        score_details.append({
            "item": "Directory structure",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All required directories exist"
        })

    # 2. kill_target.json 存在 (10分)
    target_path = os.path.join(workspace, "ops", "kill_target.json")
    if not os.path.isfile(target_path):
        score_details.append({
            "item": "File existence: ops/kill_target.json",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # 后续检查无法进行，写入总分并退出
        total_score = sum(d["score"] for d in score_details)
        _write_score(score_details, total_score)
        return
    else:
        score_details.append({
            "item": "File existence: ops/kill_target.json",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File exists"
        })

    # 3. JSON 合法性 (20分)
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("Not a JSON object")
        score_details.append({
            "item": "JSON format",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Valid JSON object"
        })
    except Exception as e:
        score_details.append({
            "item": "JSON format",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        total_score = sum(d["score"] for d in score_details)
        _write_score(score_details, total_score)
        return

    # 4. 必须包含 transaction_id 字段 (20分)
    if "transaction_id" not in data:
        score_details.append({
            "item": "Field 'transaction_id' exists",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "Missing key 'transaction_id'"
        })
        total_score = sum(d["score"] for d in score_details)
        _write_score(score_details, total_score)
        return
    else:
        score_details.append({
            "item": "Field 'transaction_id' exists",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Key present"
        })

    # 5. transaction_id 的值必须为 tx_42 (40分)
    expected_id = "tx_42"
    actual_id = data["transaction_id"]
    if actual_id == expected_id:
        score_details.append({
            "item": "Correct transaction_id value",
            "score": 40,
            "max_score": 40,
            "passed": True,
            "reason": f"transaction_id is '{expected_id}'"
        })
    else:
        score_details.append({
            "item": "Correct transaction_id value",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": f"Expected '{expected_id}', got '{actual_id}'"
        })

    # 6. 无多余键 (防止作弊) 5分
    allowed_keys = {"transaction_id"}
    actual_keys = set(data.keys())
    extra = actual_keys - allowed_keys
    if extra:
        score_details.append({
            "item": "No unexpected keys",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Extra keys: {extra}"
        })
    else:
        score_details.append({
            "item": "No unexpected keys",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Only expected keys"
        })

    # 7. 检查 agent 是否修改了原始日志 (可选, 5分)
    # 检查 slow_queries.log 内容是否完整包含 "Lock_time: 8.000"
    log_path = os.path.join(workspace, "logs", "slow_queries.log")
    try:
        with open(log_path, "r") as f:
            content = f.read()
        if "Lock_time: 8.000" in content:
            score_details.append({
                "item": "Original log integrity",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "Log file unchanged"
            })
        else:
            score_details.append({
                "item": "Original log integrity",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": "Log file modified or missing expected pattern"
            })
    except FileNotFoundError:
        score_details.append({
            "item": "Original log integrity",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "slow_queries.log not found"
        })

    # 计算总分
    total_score = sum(d["score"] for d in score_details)
    _write_score(score_details, total_score)

def _write_score(details, total):
    results = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
