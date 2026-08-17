import sys
import os
import json
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    score = 0
    max_total = 100
    details = []

    # 1. 检查 reports/ 目录存在 (10分)
    if os.path.isdir("reports"):
        details.append({"item": "reports/ directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found reports/ directory"})
        score += 10
    else:
        details.append({"item": "reports/ directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Missing reports/ directory"})

    # 2. 检查 diff_v1_v2.json 文件存在 (10分)
    target = "reports/diff_v1_v2.json"
    if os.path.isfile(target):
        details.append({"item": f"File {target} exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found diff_v1_v2.json"})
        score += 10
    else:
        details.append({"item": f"File {target} exists", "score": 0, "max_score": 10, "passed": False, "reason": "Missing diff_v1_v2.json"})
        print(json.dumps({"total_score": score, "details": details}, indent=2))
        # 如果文件都不存在，后续无法验证，直接返回
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        return

    # 3. 解析 JSON 合法性 (10分)
    try:
        with open(target, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON parsable", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON"})
        score += 10
    except Exception as e:
        details.append({"item": "JSON parsable", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {str(e)}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        return

    # 4. 检查必填字段 (每项5分，共30分)
    field_score = 0
    # 4a. batch_1
    if "batch_1" in data and data["batch_1"] == "batch_v1":
        field_score += 10
        details.append({"item": "Field batch_1 == 'batch_v1'", "score": 10, "max_score": 10, "passed": True, "reason": "Correct baseline identifier"})
    else:
        details.append({"item": "Field batch_1 == 'batch_v1'", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected 'batch_v1', got {data.get('batch_1')}"})
    # 4b. batch_2
    if "batch_2" in data and data["batch_2"] == "batch_v2":
        field_score += 10
        details.append({"item": "Field batch_2 == 'batch_v2'", "score": 10, "max_score": 10, "passed": True, "reason": "Correct treatment identifier"})
    else:
        details.append({"item": "Field batch_2 == 'batch_v2'", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected 'batch_v2', got {data.get('batch_2')}"})
    # 4c. metrics_diff 存在且为dict
    if "metrics_diff" in data and isinstance(data["metrics_diff"], dict):
        field_score += 10
        details.append({"item": "Field metrics_diff is a dict", "score": 10, "max_score": 10, "passed": True, "reason": "metrics_diff present and is object"})
    else:
        details.append({"item": "Field metrics_diff is a dict", "score": 0, "max_score": 10, "passed": False, "reason": "Missing or non-dict metrics_diff"})
    score += field_score

    # 5. 检查 metrics_diff 内数值 (共40分)
    if isinstance(data.get("metrics_diff"), dict):
        md = data["metrics_diff"]
        # 期望值
        expected = {
            "accuracy": 0.02,          # (0.88+0.91+0.88)/3 - (0.85+0.90+0.86)/3 = 0.89 - 0.87 = 0.02
            "latency_ms": -5.0,        # 105 - 110 = -5
            "cost_usd": 1.0            # 12 - 11 = 1
        }
        accepted_tolerance = 1e-9
        num_fields = 0
        for key, exp_val in expected.items():
            if key in md:
                try:
                    actual = float(md[key])
                except:
                    actual = None
                if actual is not None and math.isclose(actual, exp_val, abs_tol=accepted_tolerance):
                    num_fields += 1
                    details.append({"item": f"metrics_diff.{key} == {exp_val}", "score": 15, "max_score": 15, "passed": True, "reason": f"Got {actual}"})
                else:
                    details.append({"item": f"metrics_diff.{key} == {exp_val}", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected {exp_val}, got {actual}"})
            else:
                details.append({"item": f"metrics_diff.{key} == {exp_val}", "score": 0, "max_score": 15, "passed": False, "reason": "Key missing"})
        # 额外检查是否有多余的 key（扣分机制：每多一个非期望 key 扣5分，最多扣10分）
        extra_keys = set(md.keys()) - set(expected.keys())
        if extra_keys:
            penalty = min(len(extra_keys) * 5, 10)
            details.append({"item": "No extra keys in metrics_diff", "score": -penalty, "max_score": 0, "passed": False, "reason": f"Unexpected keys: {extra_keys}"})
            score = max(0, score - penalty)
        score += num_fields * 15  # 每个15分，共最多45分，但上面已加过score，这里累计到总分
        # 实际上上面细节已经加了分，我们再调整分数
        # 重新计算：我们手动加
    else:
        details.append({"item": "metrics_diff values", "score": 0, "max_score": 45, "passed": False, "reason": "metrics_diff not a dict, skipping"})

    # 由于上面细节中已经包含了每个项的分数，我们需要重新汇总总分
    # 重新计算总分：从 details 中 sum score
    total_score = sum(item['score'] for item in details if item['score'] >= 0)  # 惩罚是负分，也纳入
    # 但注意我们之前将 score 累加，可能有重复，我们重新计算干净：
    # 简化：直接用 total_score
    # 重算
    total_score = 0
    for item in details:
        total_score += item['score']
    total_score = max(0, total_score)  # 不低于0

    # 确保总分不超过100
    total_score = min(total_score, 100)

    # 输出结果
    output = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Verification complete. Total score: {total_score}")

if __name__ == "__main__":
    main()
