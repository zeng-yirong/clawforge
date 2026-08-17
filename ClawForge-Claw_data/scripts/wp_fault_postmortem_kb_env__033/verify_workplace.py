import os
import sys
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    max_total = 100

    # 1. 检查 ops 目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        results.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ directory found"
        })
        total_score += 10
    else:
        results.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory missing"
        })

    # 2. 检查 ops/kill_target.json 是否存在且合法 JSON (20分)
    target_file = os.path.join(workspace, "ops", "kill_target.json")
    file_exists = os.path.isfile(target_file)
    json_valid = False
    data = None
    if file_exists:
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
            json_valid = True
            results.append({
                "item": "kill_target.json exists and is valid JSON",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "File found and parsed successfully"
            })
            total_score += 20
        except (json.JSONDecodeError, ValueError):
            results.append({
                "item": "kill_target.json exists and is valid JSON",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "File exists but is not valid JSON"
            })
    else:
        results.append({
            "item": "kill_target.json exists and is valid JSON",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "kill_target.json not found"
        })

    # 3. 检查是否包含 transaction_id 字段且为整数 (20分)
    if data is not None and isinstance(data, dict):
        if "transaction_id" in data:
            tid = data["transaction_id"]
            if isinstance(tid, int):
                results.append({
                    "item": "transaction_id field present and is integer",
                    "score": 20,
                    "max_score": 20,
                    "passed": True,
                    "reason": f"transaction_id = {tid} (int)"
                })
                total_score += 20
            else:
                results.append({
                    "item": "transaction_id field present and is integer",
                    "score": 0,
                    "max_score": 20,
                    "passed": False,
                    "reason": f"transaction_id exists but type is {type(tid).__name__}, expected int"
                })
        else:
            results.append({
                "item": "transaction_id field present and is integer",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "No 'transaction_id' key in JSON object"
            })
    else:
        # 如果之前 JSON 无效，直接给 0
        results.append({
            "item": "transaction_id field present and is integer",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "Cannot check transaction_id because JSON invalid or missing"
        })

    # 4. 检查 transaction_id 值是否为 7331 (40分) — 核心验证
    if data is not None and isinstance(data, dict):
        tid = data.get("transaction_id")
        if tid == 7331:
            results.append({
                "item": "transaction_id value is correct (7331)",
                "score": 40,
                "max_score": 40,
                "passed": True,
                "reason": "Expected 7331, got 7331"
            })
            total_score += 40
        else:
            results.append({
                "item": "transaction_id value is correct (7331)",
                "score": 0,
                "max_score": 40,
                "passed": False,
                "reason": f"Expected 7331, got {tid}" if tid is not None else "No value"
            })
    else:
        results.append({
            "item": "transaction_id value is correct (7331)",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": "Cannot verify value due to missing/invalid data"
        })

    # 5. 检查是否有多余字段（可选，扣分项，但这里用加分项：没有多余字段得 10 分）
    extra_fields_penalty = False
    if data is not None and isinstance(data, dict):
        allowed_keys = {"transaction_id"}
        extra_keys = set(data.keys()) - allowed_keys
        if not extra_keys:
            results.append({
                "item": "No extra fields in kill_target.json",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Only expected keys present"
            })
            total_score += 10
        else:
            results.append({
                "item": "No extra fields in kill_target.json",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Unexpected keys: {extra_keys}"
            })
    else:
        results.append({
            "item": "No extra fields in kill_target.json",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Cannot check extra fields due to invalid/missing data"
        })

    # 输出结果
    score_summary = {
        "total_score": min(total_score, max_total),
        "details": results
    }
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(score_summary, f, indent=2)

    print(f"Verification complete. Total score: {score_summary['total_score']}/{max_total}")
    sys.exit(0 if score_summary['total_score'] >= 0 else 1)

if __name__ == "__main__":
    main()
