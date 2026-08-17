import sys
import os
import json

def verify(workspace):
    score_details = []
    total_score = 0

    # 1. 检查目录结构：必须存在 ops/ 目录（10分）
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        score_details.append({
            "item": "ops/ directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ directory found"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "ops/ directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory not found"
        })

    # 2. 检查目标文件 ops/kill_target.json 是否存在（10分）
    target_file = os.path.join(workspace, "ops", "kill_target.json")
    if os.path.isfile(target_file):
        score_details.append({
            "item": "ops/kill_target.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File present"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "ops/kill_target.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # 如果文件不存在，后续检查无法进行，直接输出结果
        result = {
            "total_score": total_score,
            "details": score_details
        }
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 检查文件内容是否为有效 JSON（10分）
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "ops/kill_target.json is valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON parsed successfully"
        })
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        score_details.append({
            "item": "ops/kill_target.json is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        result = {
            "total_score": total_score,
            "details": score_details
        }
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 4. 检查是否包含必需的 "transaction_id" 字段（20分）
    if isinstance(data, dict) and "transaction_id" in data:
        tid = data["transaction_id"]
        score_details.append({
            "item": "Contains 'transaction_id' field",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"Field present with value: {tid}"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "Contains 'transaction_id' field",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "Missing 'transaction_id' key or data is not a dict"
        })
        # 字段缺失，后续不再检查值，直接输出
        result = {
            "total_score": total_score,
            "details": score_details
        }
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 5. 检查 transaction_id 的值是否完全等于 "TX-20240315-001"（50分）
    expected_id = "TX-20240315-001"
    if tid == expected_id:
        score_details.append({
            "item": "transaction_id matches expected value",
            "score": 50,
            "max_score": 50,
            "passed": True,
            "reason": f"Value exactly '{expected_id}'"
        })
        total_score += 50
    else:
        score_details.append({
            "item": "transaction_id matches expected value",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": f"Value is '{tid}', expected '{expected_id}'"
        })

    # 6. 检查是否包含多余的键（扣分项：非严格要求，但越简洁越好，这里不扣分仅记录）
    extra_keys = [k for k in data.keys() if k != "transaction_id"]
    if extra_keys:
        score_details.append({
            "item": "No extra fields beyond 'transaction_id'",
            "score": 0,
            "max_score": 0,  # 不扣分，仅提醒
            "passed": False,
            "reason": f"Unexpected keys: {extra_keys}. Task explicitly asked for only the ID."
        })
    else:
        score_details.append({
            "item": "No extra fields beyond 'transaction_id'",
            "score": 0,
            "max_score": 0,
            "passed": True,
            "reason": "Only expected key present"
        })

    # 组合结果
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

    print(f"Verification complete. Total score: {total_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
