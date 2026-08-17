import sys
import os
import json

def verify(workspace: str) -> dict:
    details = []
    total_score = 0

    # 1. 检查目录结构 (权重10)
    dirs_passed = True
    required_dirs = ["ops", "policy", "requests", "attachments"]
    for d in required_dirs:
        if not os.path.isdir(os.path.join(workspace, d)):
            dirs_passed = False
            break
    if dirs_passed:
        details.append({"item": "Required directory structure present", "score": 10, "max_score": 10, "passed": True, "reason": "All required directories exist."})
        total_score += 10
    else:
        details.append({"item": "Required directory structure present", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing one or more directories: {required_dirs}"})

    # 2. 检查目标文件存在性 (权重10)
    output_path = os.path.join(workspace, "ops", "denied_requests.json")
    if not os.path.isfile(output_path):
        details.append({"item": "Output file exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/denied_requests.json not found."})
        return {"total_score": 0, "details": details}
    else:
        details.append({"item": "Output file exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/denied_requests.json found."})
        total_score += 10

    # 3. 解析 JSON 合法性 (权重10)
    try:
        with open(output_path, "r") as f:
            denied_list = json.load(f)
    except (json.JSONDecodeError, ValueError) as e:
        details.append({"item": "JSON format valid", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        return {"total_score": total_score, "details": details}
    if not isinstance(denied_list, list):
        details.append({"item": "JSON format valid", "score": 0, "max_score": 10, "passed": False, "reason": "Top-level element is not a list."})
        return {"total_score": total_score, "details": details}
    details.append({"item": "JSON format valid", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON list."})
    total_score += 10

    # 4. 检查列表内容是否正确 (权重70)
    # 正确答案：只有两个外部审计/渗透测试请求应被拒绝
    expected_denied = {"req_external_001", "req_pen_test_002"}
    actual_ids = set(denied_list)

    # 检查是否有遗漏
    missing = expected_denied - actual_ids
    extra = actual_ids - expected_denied

    if missing:
        details.append({"item": "Contains correct denied request IDs", "score": 0, "max_score": 70, "passed": False,
                        "reason": f"Missing required IDs: {missing}. Also extra: {extra}"})
        total_score += 0
    elif extra:
        # 有额外ID，扣一半分数
        details.append({"item": "Contains correct denied request IDs", "score": 35, "max_score": 70, "passed": False,
                        "reason": f"Contains extra IDs: {extra}. Should only contain: {expected_denied}"})
        total_score += 35
    elif actual_ids == expected_denied:
        details.append({"item": "Contains correct denied request IDs", "score": 70, "max_score": 70, "passed": True,
                        "reason": f"Exactly matches expected denied requests: {expected_denied}"})
        total_score += 70
    else:
        # 理论上不会到这里
        details.append({"item": "Contains correct denied request IDs", "score": 0, "max_score": 70, "passed": False,
                        "reason": f"Unexpected set: {actual_ids}"})

    # 输出结果
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    return result

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
