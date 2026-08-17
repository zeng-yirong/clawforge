import sys
import os
import json
import math

def verify(workspace: str):
    scores = []
    total_score = 0

    # 1. ops 目录存在
    ops_path = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_path)
    scores.append({
        "item": "ops directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops directory found" if dir_exists else "ops directory missing"
    })
    if dir_exists:
        total_score += 10

    # 2. diff_record.json 存在
    json_path = os.path.join(ops_path, "diff_record.json")
    file_exists = os.path.isfile(json_path)
    scores.append({
        "item": "diff_record.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "file found" if file_exists else "file missing"
    })
    if file_exists:
        total_score += 10

    # 3. JSON 格式合法
    format_ok = False
    data = None
    if file_exists:
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
            format_ok = True
        except (json.JSONDecodeError, Exception):
            pass
    scores.append({
        "item": "JSON format valid",
        "score": 10 if format_ok else 0,
        "max_score": 10,
        "passed": format_ok,
        "reason": "valid JSON" if format_ok else "invalid JSON or parse error"
    })
    if format_ok:
        total_score += 10
    else:
        # 若格式错误，后续检查无法进行，直接返回
        _write_score(total_score, scores)
        return

    # 4. 必须包含 batch_a, batch_b, metrics_diff 三个顶层字段
    required_top = {"batch_a", "batch_b", "metrics_diff"}
    present_top = set(data.keys()) if isinstance(data, dict) else set()
    top_ok = required_top.issubset(present_top)
    top_score = 15 if top_ok else 0
    scores.append({
        "item": "top-level fields (batch_a, batch_b, metrics_diff)",
        "score": top_score,
        "max_score": 15,
        "passed": top_ok,
        "reason": f"fields present: {present_top}" if top_ok else f"missing: {required_top - present_top}"
    })
    if top_ok:
        total_score += top_score

    # 5. batch_a / batch_b 值正确
    batch_ok = (data.get("batch_a") == "batch_v2" and data.get("batch_b") == "batch_v3")
    scores.append({
        "item": "batch IDs (batch_v2, batch_v3)",
        "score": 10 if batch_ok else 0,
        "max_score": 10,
        "passed": batch_ok,
        "reason": f"got {data.get('batch_a')}, {data.get('batch_b')}" if not batch_ok else "correct IDs"
    })
    if batch_ok:
        total_score += 10

    # 6. metrics_diff 包含 accuracy, latency_ms, cost_usd
    metrics_diff = data.get("metrics_diff", {})
    required_metrics = {"accuracy", "latency_ms", "cost_usd"}
    present_metrics = set(metrics_diff.keys()) if isinstance(metrics_diff, dict) else set()
    metrics_ok = required_metrics.issubset(present_metrics)
    scores.append({
        "item": "metrics_diff contains accuracy, latency_ms, cost_usd",
        "score": 5 if metrics_ok else 0,
        "max_score": 5,
        "passed": metrics_ok,
        "reason": f"metrics present: {present_metrics}" if metrics_ok else f"missing: {required_metrics - present_metrics}"
    })
    if metrics_ok:
        total_score += 5

    # 7. 数值精确计算（允许浮点误差 1e-9）
    # 预期值：accuracy = 0.89 - 0.85 = 0.04, latency_ms = 110 - 120 = -10.0, cost_usd = 0.52 - 0.50 = 0.02
    expected = {
        "accuracy": 0.04,
        "latency_ms": -10.0,
        "cost_usd": 0.02
    }
    calc_ok = True
    reasons = []
    for metric, exp_val in expected.items():
        if metric not in metrics_diff:
            calc_ok = False
            reasons.append(f"{metric} missing")
            continue
        val = metrics_diff[metric]
        if not isinstance(val, (int, float)):
            calc_ok = False
            reasons.append(f"{metric} not numeric")
            continue
        if not math.isclose(val, exp_val, rel_tol=1e-9):
            calc_ok = False
            reasons.append(f"{metric} expected {exp_val}, got {val}")
        else:
            reasons.append(f"{metric} correct ({val})")
    calc_score = 40 if calc_ok else 0
    patterns_ok = all(math.isclose(metrics_diff.get(m, 0), expected[m], rel_tol=1e-9) for m in expected)
    scores.append({
        "item": "diff calculation (accuracy, latency_ms, cost_usd)",
        "score": calc_score,
        "max_score": 40,
        "passed": calc_ok,
        "reason": "; ".join(reasons)
    })
    if calc_ok:
        total_score += calc_score

    _write_score(total_score, scores)

def _write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
