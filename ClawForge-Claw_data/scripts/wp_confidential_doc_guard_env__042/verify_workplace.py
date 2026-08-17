import json
import os
import sys

def check_workplace(workspace):
    details = []
    total_score = 0

    # 1. ops 目录存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ found"})
        total_score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ not found"})

    # 2. ops/deny_targets.json 存在 (10分)
    target_file = os.path.join(workspace, "ops", "deny_targets.json")
    if os.path.isfile(target_file):
        details.append({"item": "deny_targets.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
        total_score += 10
    else:
        details.append({"item": "deny_targets.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        # 如果文件不存在，后续检查无法进行，直接返回
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. JSON 格式合法 (10分)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON format valid", "score": 10, "max_score": 10, "passed": True, "reason": "valid JSON"})
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON format valid", "score": 0, "max_score": 10, "passed": False, "reason": f"invalid JSON: {str(e)}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 4. 数据结构合法：必须是一个列表，且每个元素是字符串 (10分)
    if not isinstance(data, list):
        details.append({"item": "data is a list of strings", "score": 0, "max_score": 10, "passed": False, "reason": "root element is not a list"})
    elif not all(isinstance(x, str) for x in data):
        details.append({"item": "data is a list of strings", "score": 0, "max_score": 10, "passed": False, "reason": "list contains non-string elements"})
    else:
        details.append({"item": "data is a list of strings", "score": 10, "max_score": 10, "passed": True, "reason": "valid list of strings"})
        total_score += 10

    # 5. 正确的拒绝ID集合 (60分)
    # 预期：R002 和 R004 应该被拒绝
    expected = {"R002", "R004"}
    actual = set(data)
    if actual == expected:
        details.append({"item": "correct denied request IDs", "score": 60, "max_score": 60, "passed": True, "reason": "exactly R002 and R004"})
        total_score += 60
    else:
        # 计算分数：每个正确ID得30分，每个多余或缺失的ID扣10分，最低0分
        correct = len(actual & expected) * 30
        incorrect = len(actual - expected) + len(expected - actual)
        penalty = min(incorrect * 10, correct)  # 最多扣到0
        score = max(0, correct - penalty)
        reasons = []
        missing = expected - actual
        extra = actual - expected
        if missing:
            reasons.append(f"missing: {missing}")
        if extra:
            reasons.append(f"extra: {extra}")
        details.append({"item": "correct denied request IDs", "score": score, "max_score": 60, "passed": score >= 30,
                        "reason": "; ".join(reasons) if reasons else "partial match"})
        total_score += score

    # 写入最终评分
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    check_workplace(workspace)
