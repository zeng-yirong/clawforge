import os
import sys
import json
import math

def verify(workspace: str):
    errors = []
    details = []
    total_score = 0

    # 1. 检查 ops 目录存在 (10)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops directory found"
        })
        total_score += 10
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops directory missing"
        })

    # 2. 检查 output 文件存在 (10)
    output_path = os.path.join(workspace, "ops", "competitor_summary.json")
    if os.path.isfile(output_path):
        details.append({
            "item": "output file ops/competitor_summary.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "file found"
        })
        total_score += 10
    else:
        details.append({
            "item": "output file ops/competitor_summary.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "file missing"
        })
        # 如果文件不存在，后续无法检查，直接返回
        _finalize(workspace, total_score, details)
        return

    # 3. JSON 合法性 (10)
    try:
        with open(output_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "output file is valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "valid JSON"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "output file is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        _finalize(workspace, total_score, details)
        return

    # 4. 字段完整性 (检查四个必要键) (10)
    required_keys = ["total_market_cap", "avg_growth_rate", "top_competitor_name", "top_competitor_users"]
    missing_keys = [k for k in required_keys if k not in data]
    extra_keys = set(data.keys()) - set(required_keys)
    if not missing_keys:
        details.append({
            "item": "output contains all required fields",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "all keys present"
        })
        total_score += 10
    else:
        details.append({
            "item": "output contains all required fields",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"missing keys: {missing_keys}"
        })
        # 即使缺少键，可以尝试部分检查，但为了简单，先给0分后不继续对缺失键判分
    if extra_keys:
        details.append({
            "item": "no extra fields in output",
            "score": 0,
            "max_score": 0,
            "passed": False,
            "reason": f"extra keys found: {extra_keys} (not penalized but noted)"
        })

    # 5. 计算检查 (每个20分，共60分)
    # 预设正确值
    expected_total_market_cap = 5000 + 3200 + 1800 + 7000  # 17000
    expected_avg_growth_rate = (0.15 + 0.22 + 0.08 + 0.18) / 4  # 0.1575
    expected_top_competitor_name = "TechCorp"
    expected_top_competitor_users = 6

    # 5a total_market_cap (20)
    cap_score = 0
    cap_passed = False
    cap_reason = ""
    if "total_market_cap" in data:
        val = data["total_market_cap"]
        if isinstance(val, (int, float)) and math.isclose(val, expected_total_market_cap, rel_tol=1e-9):
            cap_score = 20
            cap_passed = True
            cap_reason = f"correct value {val}"
        else:
            cap_reason = f"expected {expected_total_market_cap}, got {val}"
    else:
        cap_reason = "field missing"
    details.append({
        "item": "total_market_cap correct",
        "score": cap_score,
        "max_score": 20,
        "passed": cap_passed,
        "reason": cap_reason
    })
    total_score += cap_score

    # 5b avg_growth_rate (20)
    gr_score = 0
    gr_passed = False
    gr_reason = ""
    if "avg_growth_rate" in data:
        val = data["avg_growth_rate"]
        if isinstance(val, (int, float)) and math.isclose(val, expected_avg_growth_rate, rel_tol=1e-9):
            gr_score = 20
            gr_passed = True
            gr_reason = f"correct value {val}"
        else:
            gr_reason = f"expected {expected_avg_growth_rate}, got {val}"
    else:
        gr_reason = "field missing"
    details.append({
        "item": "avg_growth_rate correct",
        "score": gr_score,
        "max_score": 20,
        "passed": gr_passed,
        "reason": gr_reason
    })
    total_score += gr_score

    # 5c top_competitor_name (20)
    name_score = 0
    name_passed = False
    name_reason = ""
    if "top_competitor_name" in data:
        val = data["top_competitor_name"]
        if isinstance(val, str) and val == expected_top_competitor_name:
            name_score = 20
            name_passed = True
            name_reason = f"correct name '{val}'"
        else:
            name_reason = f"expected '{expected_top_competitor_name}', got '{val}'"
    else:
        name_reason = "field missing"
    details.append({
        "item": "top_competitor_name correct",
        "score": name_score,
        "max_score": 20,
        "passed": name_passed,
        "reason": name_reason
    })
    total_score += name_score

    # 5d top_competitor_users (20)
    users_score = 0
    users_passed = False
    users_reason = ""
    if "top_competitor_users" in data:
        val = data["top_competitor_users"]
        if isinstance(val, int) and val == expected_top_competitor_users:
            users_score = 20
            users_passed = True
            users_reason = f"correct count {val}"
        else:
            users_reason = f"expected {expected_top_competitor_users}, got {val}"
    else:
        users_reason = "field missing"
    details.append({
        "item": "top_competitor_users correct",
        "score": users_score,
        "max_score": 20,
        "passed": users_passed,
        "reason": users_reason
    })
    total_score += users_score

    # 汇总总分 (满分100，上面已累计)
    _finalize(workspace, total_score, details)

def _finalize(workspace, score, details):
    # 确保总分为整数
    score = min(100, max(0, int(round(score))))
    result = {
        "total_score": score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Score: {score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
