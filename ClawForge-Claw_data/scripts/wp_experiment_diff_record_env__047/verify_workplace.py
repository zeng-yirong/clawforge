import sys
import os
import json
import math

def verify(workspace):
    score = 0
    details = []
    total_max = 100

    # 1. 检查 ops/diff_record.json 是否存在 (10分)
    expected_path = os.path.join(workspace, "ops", "diff_record.json")
    if os.path.isfile(expected_path):
        details.append({"item": "ops/diff_record.json 文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        score += 10
    else:
        details.append({"item": "ops/diff_record.json 文件存在", "score": 0, "max_score": 10, "passed": False, "reason": f"文件 {expected_path} 不存在"})
        # 无法继续检查，直接返回
        result = {"total_score": score, "details": details}
        write_score(workspace, result)
        return

    # 2. JSON 合法性 (10分)
    try:
        with open(expected_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析为 JSON"})
        score += 10
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        result = {"total_score": score, "details": details}
        write_score(workspace, result)
        return

    # 3. 结构检查：根键只允许 "batch_001_vs_002" (10分)
    expected_root_key = "batch_001_vs_002"
    if list(data.keys()) == [expected_root_key]:
        details.append({"item": "根级别只包含预期的键 batch_001_vs_002", "score": 10, "max_score": 10, "passed": True, "reason": "结构正确"})
        score += 10
    else:
        details.append({"item": "根级别只包含预期的键 batch_001_vs_002", "score": 0, "max_score": 10, "passed": False, "reason": f"实际键列表: {list(data.keys())}"})

    record = data.get(expected_root_key, {})
    # 4. 检查子键 control 和 variant (10分)
    expected_groups = ["control", "variant"]
    if sorted(record.keys()) == expected_groups:
        details.append({"item": "包含 control 和 variant 两个分组", "score": 10, "max_score": 10, "passed": True, "reason": "分组键正确"})
        score += 10
    else:
        details.append({"item": "包含 control 和 variant 两个分组", "score": 0, "max_score": 10, "passed": False, "reason": f"实际分组键: {sorted(record.keys())}"})

    # 5. 每个分组下只允许键 "accuracy_diff" (10分)
    for group in expected_groups:
        subgroup = record.get(group, {})
        keys = list(subgroup.keys())
        if keys == ["accuracy_diff"]:
            details.append({"item": f"{group} 下只包含 accuracy_diff", "score": 5, "max_score": 5, "passed": True, "reason": "键正确"})
            score += 5
        else:
            details.append({"item": f"{group} 下只包含 accuracy_diff", "score": 0, "max_score": 5, "passed": False, "reason": f"实际键: {keys}"})

    # 6. 数值精确性校验 (剩余50分，每组25分)
    expected_control_diff = -0.0191  # 0.8321 - 0.8512 = -0.0191
    expected_variant_diff = 0.0222   # 0.9456 - 0.9234 = 0.0222

    control_diff = record.get("control", {}).get("accuracy_diff")
    variant_diff = record.get("variant", {}).get("accuracy_diff")

    # 控制组
    if control_diff is not None and isinstance(control_diff, (int, float)):
        if math.isclose(round(control_diff, 4), expected_control_diff, abs_tol=1e-6):
            details.append({"item": "control 组 accuracy_diff 数值正确", "score": 25, "max_score": 25, "passed": True, "reason": f"值为 {control_diff}"})
            score += 25
        else:
            details.append({"item": "control 组 accuracy_diff 数值正确", "score": 0, "max_score": 25, "passed": False, "reason": f"预期 {expected_control_diff}，实际 {control_diff}"})
    else:
        details.append({"item": "control 组 accuracy_diff 数值正确", "score": 0, "max_score": 25, "passed": False, "reason": "缺失或非数值"})

    # 变体组
    if variant_diff is not None and isinstance(variant_diff, (int, float)):
        if math.isclose(round(variant_diff, 4), expected_variant_diff, abs_tol=1e-6):
            details.append({"item": "variant 组 accuracy_diff 数值正确", "score": 25, "max_score": 25, "passed": True, "reason": f"值为 {variant_diff}"})
            score += 25
        else:
            details.append({"item": "variant 组 accuracy_diff 数值正确", "score": 0, "max_score": 25, "passed": False, "reason": f"预期 {expected_variant_diff}，实际 {variant_diff}"})
    else:
        details.append({"item": "variant 组 accuracy_diff 数值正确", "score": 0, "max_score": 25, "passed": False, "reason": "缺失或非数值"})

    # 写入结果
    result = {"total_score": score, "details": details}
    write_score(workspace, result)


def write_score(workspace, result):
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
