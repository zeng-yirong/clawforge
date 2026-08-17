import sys
import os
import json
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    details = []
    total_score = 0
    max_total_score = 100

    # 1. 检查 ops 目录是否存在 (10分)
    score = 0
    max_score = 10
    passed = False
    reason = ""
    if os.path.isdir("ops"):
        score = max_score
        passed = True
        reason = "ops directory exists"
    else:
        reason = "ops directory missing"
    details.append({"item": "ops directory", "score": score, "max_score": max_score, "passed": passed, "reason": reason})
    total_score += score

    # 2. 检查目标文件是否存在 (10分)
    score = 0
    max_score = 10
    passed = False
    reason = ""
    target_file = "ops/nxtc_earnings_summary.json"
    if os.path.isfile(target_file):
        score = max_score
        passed = True
        reason = "target file exists"
    else:
        reason = f"file {target_file} not found"
    details.append({"item": "target file existence", "score": score, "max_score": max_score, "passed": passed, "reason": reason})
    total_score += score

    # 3. 文件格式合法性 (JSON可解析) (10分)
    score = 0
    max_score = 10
    passed = False
    reason = ""
    data = None
    if os.path.isfile(target_file):
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
            score = max_score
            passed = True
            reason = "valid JSON"
        except json.JSONDecodeError as e:
            reason = f"invalid JSON: {e}"
    else:
        reason = "file not found, cannot check format"
    details.append({"item": "JSON format validity", "score": score, "max_score": max_score, "passed": passed, "reason": reason})
    total_score += score

    # 4. 字段完整性 (必须包含：quarter, revenue_actual, revenue_estimate, eps_actual, eps_estimate, revenue_beat_pct, eps_beat_pct, stock_change_pct) (30分)
    required_fields = ["quarter", "revenue_actual", "revenue_estimate", "eps_actual", "eps_estimate", "revenue_beat_pct", "eps_beat_pct", "stock_change_pct"]
    score = 0
    max_score = 30
    passed = False
    reason = ""
    if data is not None and isinstance(data, dict):
        missing = [f for f in required_fields if f not in data]
        if not missing:
            score = max_score
            passed = True
            reason = "all required fields present"
        else:
            reason = f"missing fields: {missing}"
    else:
        reason = "data is not a dictionary"
    details.append({"item": "field completeness", "score": score, "max_score": max_score, "passed": passed, "reason": reason})
    total_score += score

    # 5. 核心数值正确性 (40分) — 根据内部真相精确比对
    score_block = 0
    max_block = 40
    block_breakdown = {}
    reason_block = []

    # 预置真相 (env_builder 产生的唯一答案)
    expected = {
        "quarter": "Q2 2026",
        "revenue_actual": 1250,          # 单位: 百万
        "revenue_estimate": 1200,
        "eps_actual": 2.8,
        "eps_estimate": 2.5,
        "revenue_beat_pct": 4.17,        # (1250-1200)/1200*100 ≈ 4.1667 -> 4.17
        "eps_beat_pct": 12.00,           # (2.8-2.5)/2.5*100 = 12.0
        "stock_change_pct": 2.94          # 从stocks.json NXTC 的 change_pct
    }

    if data is not None and isinstance(data, dict):
        def approx(a, b, tol=0.01):
            return abs(a - b) < tol

        check_list = [
            ("quarter", expected["quarter"], True),
            ("revenue_actual", expected["revenue_actual"], True),
            ("revenue_estimate", expected["revenue_estimate"], True),
            ("eps_actual", expected["eps_actual"], True),
            ("eps_estimate", expected["eps_estimate"], True),
            ("revenue_beat_pct", expected["revenue_beat_pct"], True),
            ("eps_beat_pct", expected["eps_beat_pct"], True),
            ("stock_change_pct", expected["stock_change_pct"], True)
        ]
        for field, expected_val, is_numeric in check_list:
            if field in data:
                actual = data[field]
                if is_numeric:
                    if isinstance(actual, (int, float)):
                        if approx(actual, expected_val):
                            block_breakdown[field] = "correct"
                            score_block += 5  # 每个字段5分
                        else:
                            block_breakdown[field] = f"wrong value: got {actual}, expected {expected_val}"
                    else:
                        block_breakdown[field] = f"not numeric: {actual}"
                else:
                    if actual == expected_val:
                        block_breakdown[field] = "correct"
                        score_block += 5
                    else:
                        block_breakdown[field] = f"wrong string: got {actual}, expected {expected_val}"
            else:
                block_breakdown[field] = "missing field"

        # 额外检查：不能有多余的字段？不强制，但可以检查是否包含干扰字段（比如来自旧版本的键）
        # 根据业务，可以接受额外字段，但至少所有required正确即可。
        # 另外，确保revenue_beat和eps_beat布尔值可能不需要，但如果有则检查一致性？
        # 不做额外约束，只检查上述8个字段。
        # 注意quarter必须是字符串"Q2 2026"
    else:
        reason_block.append("data unavailable")

    # 汇总 block 得分
    if data is None:
        reason_block.append("Cannot verify values - no data")
    else:
        reason_block.append("; ".join([f"{k}: {v}" for k,v in block_breakdown.items()]) if block_breakdown else "no breakdown")
    details.append({"item": "core values correctness (quarter, revenue, eps, beat %, stock change)", "score": score_block, "max_score": max_block, "passed": score_block == max_block, "reason": " | ".join(reason_block)})
    total_score += score_block

    # 确保总分在0-100
    total_score = min(total_score, max_total_score)
    total_score = max(total_score, 0)

    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    main()
