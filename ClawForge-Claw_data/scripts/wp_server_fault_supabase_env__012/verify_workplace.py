import sys
import os
import json

def verify(workspace: str):
    details = []
    total_score = 0
    max_total = 100

    # 1. ops 目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    details.append({
        "item": "ops directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops/ found" if dir_exists else "ops/ missing"
    })
    if dir_exists:
        total_score += 10

    # 2. kill_target.json 文件是否存在 (10分)
    target_path = os.path.join(ops_dir, "kill_target.json")
    file_exists = os.path.isfile(target_path)
    details.append({
        "item": "kill_target.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "file present" if file_exists else "file not found"
    })
    if file_exists:
        total_score += 10

    # 3. JSON 格式合法 (20分)
    valid_json = False
    data = None
    if file_exists:
        try:
            with open(target_path, "r") as f:
                data = json.load(f)
            valid_json = True
        except (json.JSONDecodeError, Exception):
            valid_json = False
    details.append({
        "item": "valid JSON",
        "score": 20 if valid_json else 0,
        "max_score": 20,
        "passed": valid_json,
        "reason": "JSON parse ok" if valid_json else "invalid JSON or read error"
    })
    if valid_json:
        total_score += 20

    # 4. 包含 transaction_id 字段 (20分)
    has_field = False
    if valid_json and isinstance(data, dict) and "transaction_id" in data:
        has_field = True
        tx_val = data["transaction_id"]
    else:
        tx_val = None
    details.append({
        "item": "contains 'transaction_id' field",
        "score": 20 if has_field else 0,
        "max_score": 20,
        "passed": has_field,
        "reason": f"field found with value '{tx_val}'" if has_field else "field missing or not a dict"
    })
    if has_field:
        total_score += 20

    # 5. 事务 ID 是否正确 (40分)
    correct_id = False
    if has_field:
        correct_id = (tx_val == "Txn-9876")
    details.append({
        "item": "transaction_id value is Txn-9876",
        "score": 40 if correct_id else 0,
        "max_score": 40,
        "passed": correct_id,
        "reason": f"exact match: {tx_val}" if correct_id else f"got '{tx_val}', expected 'Txn-9876'"
    })
    if correct_id:
        total_score += 40

    # 写入评分结果
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Total score: {total_score}/100")
    return total_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
