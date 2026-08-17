import sys
import os
import json
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)  # 切换到工作区

    details = []
    total_score = 0

    # 1. 目录结构检查 (10分)
    required_dirs = ["ops", "data/requests"]
    dir_score = 0
    for d in required_dirs:
        if os.path.isdir(d):
            dir_score += 5
        else:
            details.append({"item": f"目录 {d} 存在", "score": 0, "max_score": 5, "passed": False, "reason": f"目录 {d} 不存在"})
    if dir_score == 10:
        details.append({"item": "目录结构完整", "score": 10, "max_score": 10, "passed": True, "reason": "所有必需目录存在"})
    else:
        # 如果前面已经记录缺失，这里不再重复，但确保细节列表有项
        if not any(d["item"] == "目录结构完整" for d in details):
            details.append({"item": "目录结构完整", "score": dir_score, "max_score": 10, "passed": dir_score==10, "reason": f"只有 {dir_score} 分"})
    total_score += dir_score

    # 2. 检查产物文件 ops/deny_list.json (10分)
    deny_path = "ops/deny_list.json"
    if not os.path.isfile(deny_path):
        details.append({"item": "产物文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops/deny_list.json 不存在"})
        total_score += 0
        # 后续无法检查，直接输出结果
        finish(details, total_score)
        return

    details.append({"item": "产物文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
    total_score += 10

    # 3. JSON 合法性 (10分)
    try:
        with open(deny_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON 语法合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON 语法合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        finish(details, total_score)
        return

    # 4. 内容检查：必须是一个列表 (10分)
    if not isinstance(data, list):
        details.append({"item": "内容是 JSON 数组", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 list，实际 {type(data).__name__}"})
        finish(details, total_score)
        return
    details.append({"item": "内容是 JSON 数组", "score": 10, "max_score": 10, "passed": True, "reason": "数据类型正确"})
    total_score += 10

    # 5. 元素检查：必须包含且仅包含 ['req_001', 'req_004'] (60分)
    expected_ids = {"req_001", "req_004"}
    actual_ids = set(data)
    if actual_ids == expected_ids:
        details.append({"item": "拒绝请求 ID 完全正确", "score": 60, "max_score": 60, "passed": True, "reason": f"包含正确的 ID: {expected_ids}"})
        total_score += 60
    elif actual_ids.issuperset(expected_ids):
        # 有多余ID
        extra = actual_ids - expected_ids
        details.append({"item": "拒绝请求 ID 正确但有额外", "score": 30, "max_score": 60, "passed": False, "reason": f"缺少 {expected_ids - actual_ids} 或有多余 {extra}"})
        total_score += 30
    elif actual_ids.issubset(expected_ids):
        missing = expected_ids - actual_ids
        details.append({"item": "拒绝请求 ID 部分缺失", "score": 20, "max_score": 60, "passed": False, "reason": f"缺少 {missing}"})
        total_score += 20
    else:
        details.append({"item": "拒绝请求 ID 错误", "score": 0, "max_score": 60, "passed": False, "reason": f"实际ID: {actual_ids}，期望: {expected_ids}"})
        total_score += 0

    finish(details, total_score)

def finish(details, total_score):
    # 确保总分为整数且不超过100
    total_score = min(100, max(0, int(total_score)))
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total_score}")

if __name__ == "__main__":
    main()
