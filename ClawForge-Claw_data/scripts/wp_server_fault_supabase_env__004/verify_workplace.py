import sys, os, json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0

    # 1. 检查 ops 目录是否存在
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    results.append({
        "item": "ops directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops directory found" if dir_exists else "ops directory missing"
    })
    if dir_exists:
        total_score += 10

    # 2. 检查 kill_target.json 是否存在
    target_path = os.path.join(workspace, "ops", "kill_target.json")
    file_exists = os.path.isfile(target_path)
    results.append({
        "item": "ops/kill_target.json exists",
        "score": 20 if file_exists else 0,
        "max_score": 20,
        "passed": file_exists,
        "reason": "file found" if file_exists else "file not found"
    })
    if file_exists:
        total_score += 20

    # 3. 检查 JSON 是否合法
    data = None
    json_valid = False
    if file_exists:
        try:
            with open(target_path, "r") as f:
                data = json.load(f)
            json_valid = True
        except (json.JSONDecodeError, Exception):
            json_valid = False
    results.append({
        "item": "JSON is valid",
        "score": 10 if json_valid else 0,
        "max_score": 10,
        "passed": json_valid,
        "reason": "valid JSON" if json_valid else "invalid or unparseable JSON"
    })
    if json_valid:
        total_score += 10

    # 4. 检查是否包含 transaction_id 字段
    has_field = False
    if json_valid and isinstance(data, dict):
        has_field = "transaction_id" in data
    results.append({
        "item": "contains 'transaction_id' field",
        "score": 20 if has_field else 0,
        "max_score": 20,
        "passed": has_field,
        "reason": "field present" if has_field else "field missing"
    })
    if has_field:
        total_score += 20

    # 5. 检查 transaction_id 的值是否正确
    correct_value = "txn_a1b2c3d4"
    value_correct = False
    if has_field:
        value_correct = data["transaction_id"] == correct_value
    results.append({
        "item": f"transaction_id equals '{correct_value}'",
        "score": 30 if value_correct else 0,
        "max_score": 30,
        "passed": value_correct,
        "reason": f"correct value: {data.get('transaction_id')}" if value_correct else f"expected '{correct_value}', got '{data.get('transaction_id')}'"
    })
    if value_correct:
        total_score += 30

    # 6. 检查是否有多余字段（鼓励干净输出）
    allowed_keys = {"transaction_id"}
    no_extra = False
    if has_field and isinstance(data, dict):
        extra = set(data.keys()) - allowed_keys
        no_extra = len(extra) == 0
    results.append({
        "item": "no extra fields in JSON",
        "score": 10 if no_extra else 0,
        "max_score": 10,
        "passed": no_extra,
        "reason": "only expected fields" if no_extra else f"unexpected fields: {extra}"
    })
    if no_extra:
        total_score += 10

    # 输出总分
    final_score = min(100, total_score)  # 确保不超过100
    summary = {
        "total_score": final_score,
        "details": results
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Score written to {score_path}: {final_score}/100")

if __name__ == "__main__":
    main()
