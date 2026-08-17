import sys
import json
import os

def verify(workspace):
    score_details = []
    total = 0

    # 1. 检查必要目录 (10分)
    required_dirs = ["data/requests", "data/assets", "ops"]
    dir_score = 0
    for d in required_dirs:
        if os.path.isdir(os.path.join(workspace, d)):
            dir_score += 1
    if dir_score == 3:
        score_details.append({"item": "Required directories exist", "score": 10, "max_score": 10, "passed": True, "reason": "All three required dirs present."})
        total += 10
    else:
        score_details.append({"item": "Required directories exist", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing dirs: {[d for d in required_dirs if not os.path.isdir(os.path.join(workspace, d))]}"})

    # 2. 检查ops/block_targets.json是否存在 (10分)
    target_file = os.path.join(workspace, "ops/block_targets.json")
    if not os.path.isfile(target_file):
        score_details.append({"item": "Output file ops/block_targets.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found."})
        # 提前返回? 但继续执行其他检查可能无意义，但为了完整性继续
        print(json.dumps({"total_score": total, "details": score_details}))
        return

    # 3. JSON合法性 (10分)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            score_details.append({"item": "JSON is a list", "score": 0, "max_score": 10, "passed": False, "reason": "Root element is not list."})
        else:
            score_details.append({"item": "JSON is a list", "score": 10, "max_score": 10, "passed": True, "reason": "Valid list."})
            total += 10
    except (json.JSONDecodeError, Exception) as e:
        score_details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": f"Parse error: {str(e)}"})
        print(json.dumps({"total_score": total, "details": score_details}))
        return

    # 4. 检查列表内容 – 必须包含且只包含req-001 (60分)
    expected_id = "req-001"
    # 读取原始请求，验证env_builder是否生成了正确数据（辅助检查，但核心是列表）
    # 先确保没有多余id
    unique_ids = set(data)
    if len(unique_ids) != len(data):
        score_details.append({"item": "No duplicate IDs", "score": 0, "max_score": 10, "passed": False, "reason": "List contains duplicate request IDs."})
    else:
        score_details.append({"item": "No duplicate IDs", "score": 10, "max_score": 10, "passed": True, "reason": "All IDs unique."})
        total += 10

    # 检查是否包含expected_id
    if expected_id in data:
        # 检查是否有多余的id
        other_ids = [i for i in data if i != expected_id]
        if other_ids:
            # 扣分：多拦截了
            score_details.append({"item": "Only the correct ID is included", "score": 0, "max_score": 50, "passed": False, "reason": f"Extra IDs found: {other_ids}. Should only contain '{expected_id}'."})
        else:
            score_details.append({"item": "Only the correct ID is included", "score": 50, "max_score": 50, "passed": True, "reason": f"Exactly contains '{expected_id}'."})
            total += 50
    else:
        score_details.append({"item": "Only the correct ID is included", "score": 0, "max_score": 50, "passed": False, "reason": f"Missing required ID '{expected_id}'. Found IDs: {data}"})

    # 5. 额外检查：结果列表不应为空 (10分)
    if len(data) == 0:
        score_details.append({"item": "List is not empty", "score": 0, "max_score": 10, "passed": False, "reason": "Empty list."})
    else:
        score_details.append({"item": "List is not empty", "score": 10, "max_score": 10, "passed": True, "reason": f"Contains {len(data)} item(s)."})
        total += 10

    # 如果总分数超过100，截断（不应发生）
    total = min(total, 100)
    result = {
        "total_score": total,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result))

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
