import json
import os
import sys

def verify(workspace: str):
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查 ops/deny_list.json 是否存在 (10分)
    target_file = os.path.join(workspace, "ops", "deny_list.json")
    if os.path.exists(target_file):
        details.append({
            "item": "ops/deny_list.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10
    else:
        details.append({
            "item": "ops/deny_list.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 后续检查无法进行，直接返回
        _write_score(details, total_score, max_total)
        return

    # 2. 检查 JSON 格式是否合法 (10分)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "解析成功"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {str(e)}"
        })
        _write_score(details, total_score, max_total)
        return

    # 3. 检查顶层结构：必须是一个列表 (10分)
    if isinstance(data, list):
        details.append({
            "item": "顶层为 JSON 数组",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "数组格式正确"
        })
        total_score += 10
    else:
        details.append({
            "item": "顶层为 JSON 数组",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望列表，实际是 {type(data).__name__}"
        })
        # 后续无法继续，但可以尝试继续
        # 为避免后面报错，设置 data 为空列表
        data = []

    # 4. 检查每个元素是否为字符串 (5分)
    all_str = all(isinstance(item, str) for item in data)
    if all_str:
        details.append({
            "item": "数组元素均为字符串",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "所有元素类型正确"
        })
        total_score += 5
    else:
        details.append({
            "item": "数组元素均为字符串",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "存在非字符串元素"
        })

    # 5. 核心：检查 ID 集合是否与预期完全一致 (60分)
    expected_ids = {"req-001", "req-002", "req-005"}
    actual_ids = set(data)
    if actual_ids == expected_ids:
        details.append({
            "item": "拒绝列表包含正确的请求 ID",
            "score": 60,
            "max_score": 60,
            "passed": True,
            "reason": f"实际集合 {actual_ids} 与预期完全一致"
        })
        total_score += 60
    elif actual_ids == expected_ids:
        # 不会执行
        pass
    else:
        # 计算部分正确分：正确命中的比例 * 60
        correct = len(actual_ids & expected_ids)
        total_expected = len(expected_ids)
        if total_expected > 0:
            ratio = correct / total_expected
        else:
            ratio = 0
        extra = actual_ids - expected_ids
        reason = f"正确 ID: {actual_ids & expected_ids}, 缺失: {expected_ids - actual_ids}, 多余: {extra}"
        score = int(ratio * 60)
        details.append({
            "item": "拒绝列表包含正确的请求 ID",
            "score": score,
            "max_score": 60,
            "passed": False,
            "reason": reason
        })
        total_score += score

    # 6. 检查无多余 ID（附加扣分项，最多5分，但已有分数上限，我们作为独立项给5分）
    # 如果前面已经扣分，这里可以再检查多余情况
    extra_ids = actual_ids - expected_ids
    if len(extra_ids) == 0:
        details.append({
            "item": "没有多余的请求 ID",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "无多余 ID"
        })
        total_score += 5
    else:
        details.append({
            "item": "没有多余的请求 ID",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"存在多余 ID: {extra_ids}"
        })

    # 确保总分不超过100
    total_score = min(total_score, 100)

    _write_score(details, total_score, max_total)

def _write_score(details, total_score, max_total):
    score_data = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(score_data, f, indent=2)
    print(f"Verification complete. Score: {total_score}/{max_total}")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
