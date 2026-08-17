import os
import sys
import json
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total = 0

    # 1. 检查 ops/ 目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        score_details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ found"
        })
        total += 10
    else:
        score_details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory missing"
        })
        # 如果 ops 不存在，后续检查无意义，直接输出分数
        finalize(score_details, total)
        return

    # 2. 检查 deny_result.json 存在 (20分)
    result_path = os.path.join(workspace, "ops", "deny_result.json")
    if os.path.isfile(result_path):
        score_details.append({
            "item": "deny_result.json file exists",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "file found"
        })
        total += 20
    else:
        score_details.append({
            "item": "deny_result.json file exists",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "file missing"
        })
        finalize(score_details, total)
        return

    # 3. 文件格式合法 (JSON可解析) (10分)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "JSON format valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "valid JSON"
        })
        total += 10
    except Exception as e:
        score_details.append({
            "item": "JSON format valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"parse error: {e}"
        })
        finalize(score_details, total)
        return

    # 4. 字段完整性 (30分)
    required_fields = ["request_id", "action", "reason"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        score_details.append({
            "item": "required fields present",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"missing fields: {missing}"
        })
        finalize(score_details, total)
        return
    else:
        score_details.append({
            "item": "required fields present",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": "all required fields found"
        })
        total += 30

    # 5. 关键值正确性 (40分)
    sub_score = 0
    reasons = []
    # 5.1 request_id
    if data["request_id"] == "req-2025-03-17-abcd":
        sub_score += 20
        reasons.append("request_id correct")
    else:
        reasons.append(f"request_id expected 'req-2025-03-17-abcd', got '{data['request_id']}'")
    # 5.2 action == "deny"
    if data["action"] == "deny":
        sub_score += 10
        reasons.append("action=deny")
    else:
        reasons.append(f"action expected 'deny', got '{data['action']}'")
    # 5.3 reason 精确匹配
    expected_reason = "Export exceeds account access level: customer data not permitted."
    if data.get("reason") == expected_reason:
        sub_score += 10
        reasons.append("reason exact match")
    else:
        reasons.append(f"reason mismatch: expected exact string")

    score_details.append({
        "item": "key values correctness",
        "score": sub_score,
        "max_score": 40,
        "passed": sub_score == 40,
        "reason": "; ".join(reasons)
    })
    total += sub_score

    finalize(score_details, total)

def finalize(details, total):
    # 输出分数到文件
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    # 打印结果（可选）
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
