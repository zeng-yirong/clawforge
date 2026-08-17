import sys
import os
import json
import math

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    score = 0
    details = []

    # 1. 检查 ops 目录是否存在 (10 分)
    if os.path.isdir("ops"):
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops dir found"})
        score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops dir missing"})

    # 2. 检查 ops/top_performers.json 是否存在 (10 分)
    target = "ops/top_performers.json"
    if os.path.isfile(target):
        details.append({"item": "top_performers.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
        score += 10
    else:
        details.append({"item": "top_performers.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        # 如果文件不存在，直接结束，因为后续无法解析
        result = {"total_score": score, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 文件是否为合法 JSON (10 分)
    try:
        data = load_json(target)
        details.append({"item": "valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON parse successful"})
        score += 10
    except Exception as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse failed: {e}"})
        # 不能继续，但还要写结果
        result = {"total_score": score, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 4. 必须是数组 (10 分)
    if isinstance(data, list):
        details.append({"item": "is array", "score": 10, "max_score": 10, "passed": True, "reason": "top-level is list"})
        score += 10
    else:
        details.append({"item": "is array", "score": 0, "max_score": 10, "passed": False, "reason": f"expected list, got {type(data).__name__}"})
        result = {"total_score": score, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 5. 数组长度必须为 5 (10 分)
    if len(data) == 5:
        details.append({"item": "array length = 5", "score": 10, "max_score": 10, "passed": True, "reason": "found 5 entries"})
        score += 10
    else:
        details.append({"item": "array length = 5", "score": 0, "max_score": 10, "passed": False, "reason": f"expected 5, got {len(data)}"})

    # 6. 每个元素必须有 ticker 和 revenue_beat_pct，且类型正确 (20 分)
    passed_field = True
    field_errors = []
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            field_errors.append(f"entry {i} is not dict")
            passed_field = False
            continue
        if "ticker" not in entry:
            field_errors.append(f"entry {i} missing 'ticker'")
            passed_field = False
        elif not isinstance(entry["ticker"], str):
            field_errors.append(f"entry {i} 'ticker' not string")
            passed_field = False

        if "revenue_beat_pct" not in entry:
            field_errors.append(f"entry {i} missing 'revenue_beat_pct'")
            passed_field = False
        elif not isinstance(entry["revenue_beat_pct"], (int, float)):
            field_errors.append(f"entry {i} 'revenue_beat_pct' not numeric")
            passed_field = False

        # 不允许额外字段
        if set(entry.keys()) != {"ticker", "revenue_beat_pct"}:
            field_errors.append(f"entry {i} has extra keys: {set(entry.keys()) - {'ticker','revenue_beat_pct'}}")
            passed_field = False

    if passed_field:
        details.append({"item": "field structure", "score": 20, "max_score": 20, "passed": True, "reason": "all entries have correct fields"})
        score += 20
    else:
        details.append({"item": "field structure", "score": 0, "max_score": 20, "passed": False, "reason": "; ".join(field_errors)})

    # 7. 检查 ticker 是否在预期集合中 (10 分)
    expected_tickers = {"TECH", "NXTC", "MFST", "GLBL", "HLTH"}
    actual_tickers = {entry["ticker"] for entry in data}
    if actual_tickers == expected_tickers:
        details.append({"item": "ticker set correctness", "score": 10, "max_score": 10, "passed": True, "reason": "tickers match expected"})
        score += 10
    else:
        missing = expected_tickers - actual_tickers
        extra = actual_tickers - expected_tickers
        reason_parts = []
        if missing:
            reason_parts.append(f"missing: {missing}")
        if extra:
            reason_parts.append(f"extra: {extra}")
        details.append({"item": "ticker set correctness", "score": 0, "max_score": 10, "passed": False, "reason": "; ".join(reason_parts)})

    # 8. 检查 revenue_beat_pct 是否按降序排列，且数值精确 (20 分)
    expected_order = [12.5, 9.8, 7.2, 5.1, 3.6]
    order_correct = True
    order_reason = []
    for i, entry in enumerate(data):
        expected_val = expected_order[i]
        actual_val = entry["revenue_beat_pct"]
        # 允许很小的浮点误差，但精确比较到小数点后1位（因为输入是固定小数）
        if abs(actual_val - expected_val) > 0.001:
            order_correct = False
            order_reason.append(f"position {i}: expected {expected_val}, got {actual_val}")
    if order_correct:
        details.append({"item": "correct order and values", "score": 20, "max_score": 20, "passed": True, "reason": "descending order and exact values"})
        score += 20
    else:
        details.append({"item": "correct order and values", "score": 0, "max_score": 20, "passed": False, "reason": "; ".join(order_reason)})

    # 9. 存在额外干扰文件但agent没有误用? 不扣分，只检查正确性。
    # 汇总
    total_score = score
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
