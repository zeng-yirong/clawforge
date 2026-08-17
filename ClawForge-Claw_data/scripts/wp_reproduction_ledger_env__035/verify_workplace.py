import sys, os, json, pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = pathlib.Path(workspace).resolve()
    details = []
    total_score = 0

    # 1. 检查 ops/reproducibility_score.json 是否存在 (10分)
    score_path = ws / "ops" / "reproducibility_score.json"
    if score_path.exists():
        details.append({
            "item": "Output file exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"File found at {score_path}"
        })
        total_score += 10
    else:
        details.append({
            "item": "Output file exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File ops/reproducibility_score.json not found"
        })
        # 如果不存在，后续无法检查，直接输出结果
        output_result(ws, total_score, details)
        return

    # 2. 检查 JSON 合法性 (10分)
    try:
        with open(score_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON syntax valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File can be parsed as valid JSON"
        })
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON syntax valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON decode error: {e}"
        })
        output_result(ws, total_score, details)
        return

    # 3. 检查字段存在性 (20分)
    required_fields = ["total_steps", "contributing_docs"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        details.append({
            "item": "Required fields present",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Missing fields: {missing}"
        })
        output_result(ws, total_score, details)
        return
    else:
        details.append({
            "item": "Required fields present",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"Fields {required_fields} present"
        })
        total_score += 20

    # 4. 数值精确性 (60分)
    # 预期结果：根据env_builder，有效文档为：setup_env(7), unit_tests(5), integration(12), benchmark(8), cleanup(3) -> total=35, count=5
    # 注意：legacy.md可重复性false不计；missing.md不存在不计；negative.md steps负数不计（不是正整数）；no_steps.md缺少steps不计；strange.md steps是字符串"?"不计
    expected_total = 35
    expected_count = 5

    actual_total = data.get("total_steps")
    actual_count = data.get("contributing_docs")

    item_score = 0
    item_max = 60
    reasons = []

    # 检查total_steps
    if actual_total == expected_total:
        item_score += 30
        reasons.append(f"total_steps correct ({actual_total})")
    else:
        reasons.append(f"total_steps expected {expected_total}, got {actual_total}")

    # 检查contributing_docs
    if actual_count == expected_count:
        item_score += 30
        reasons.append(f"contributing_docs correct ({actual_count})")
    else:
        reasons.append(f"contributing_docs expected {expected_count}, got {actual_count}")

    passed = (actual_total == expected_total) and (actual_count == expected_count)
    details.append({
        "item": "Core values accuracy",
        "score": item_score,
        "max_score": item_max,
        "passed": passed,
        "reason": "; ".join(reasons)
    })
    total_score += item_score

    # 输出最终结果
    output_result(ws, total_score, details)

def output_result(ws, total_score, details):
    result = {"total_score": total_score, "details": details}
    out_path = ws / "workplace_score.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Total score: {total_score}/100")

if __name__ == "__main__":
    main()
