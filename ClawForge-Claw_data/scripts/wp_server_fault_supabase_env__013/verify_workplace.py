import os
import sys
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0

    # 1. ops 目录存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        results.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ directory found."
        })
        total_score += 10
    else:
        results.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory not found."
        })

    # 2. kill_target.json 存在 (10分)
    target_path = os.path.join(workspace, "ops", "kill_target.json")
    if os.path.isfile(target_path):
        results.append({
            "item": "kill_target.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File ops/kill_target.json found."
        })
        total_score += 10
    else:
        results.append({
            "item": "kill_target.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File ops/kill_target.json not found."
        })
        # 后续检查不执行，直接输出
        _write_score(results, total_score, workspace)
        return

    # 3. 合法 JSON (10分)
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        results.append({
            "item": "valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File parses as valid JSON."
        })
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        results.append({
            "item": "valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        _write_score(results, total_score, workspace)
        return

    # 4. 内容是列表 (10分)
    if isinstance(data, list):
        results.append({
            "item": "top-level list",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Content is a JSON array."
        })
        total_score += 10
    else:
        results.append({
            "item": "top-level list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected list, got {type(data).__name__}."
        })
        _write_score(results, total_score, workspace)
        return

    # 5. 必须包含且仅包含目标ID (50+10=60分)
    expected_ids = {"INC-2026-04-12-001", "INC-2026-04-12-002"}
    actual_set = set(item if isinstance(item, str) else str(item) for item in data)
    missing = expected_ids - actual_set
    extra = actual_set - expected_ids

    # 精确匹配基础分30，无缺失+10，无多余+10，排序正确加10 (但排序不重要，改为精确匹配多10)
    # 简化：完全匹配得60，否则按缺失/多余扣分
    if not missing and not extra and len(actual_set) == 2:
        results.append({
            "item": "target IDs exactly correct",
            "score": 60,
            "max_score": 60,
            "passed": True,
            "reason": f"Contains exactly {sorted(expected_ids)}."
        })
        total_score += 60
    else:
        # 扣分逻辑：每个missing扣30，每个extra扣20，但不超过60
        score = 60
        deductions = []
        if missing:
            deductions.append(f"missing {sorted(missing)}")
            score -= min(len(missing) * 30, 60)
        if extra:
            deductions.append(f"extra {sorted(extra)}")
            score -= min(len(extra) * 20, 60)
        score = max(score, 0)
        results.append({
            "item": "target IDs exactly correct",
            "score": score,
            "max_score": 60,
            "passed": score == 60,
            "reason": f"Issues: {'; '.join(deductions)}."
        })
        total_score += score

    # 写最终结果
    _write_score(results, total_score, workspace)

def _write_score(results, total_score, workspace):
    score_data = {
        "total_score": min(total_score, 100),
        "details": results
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(score_data, f, indent=2)
    print(f"Score written: {score_data['total_score']}/100")

if __name__ == "__main__":
    main()
