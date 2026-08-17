import os
import sys
import json
import math

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def verify(workspace):
    details = []
    total = 0

    # 1. 检查必要目录存在 (10分)
    dirs = ["data/flights", "data/policies", "data/platforms", "ops"]
    score = 0
    for d in dirs:
        if os.path.isdir(os.path.join(workspace, d)):
            score += 2.5
    details.append({
        "item": "Required directories exist",
        "score": score,
        "max_score": 10,
        "passed": score == 10,
        "reason": f"Found {score//2.5} of 4 directories"
    })
    total += score

    # 2. 检查关键源文件存在 (10分)
    required_files = [
        "data/flights/SB-20260615-001.json",
        "data/policies/acme_business_2026.json",
        "data/platforms/skybook.json"
    ]
    score = 0
    for rf in required_files:
        if os.path.isfile(os.path.join(workspace, rf)):
            score += 10/3
    # 允许小误差取整
    score = round(score, 1)
    details.append({
        "item": "Source data files exist",
        "score": score,
        "max_score": 10,
        "passed": score >= 9.9,
        "reason": f"Found {int(score//(10/3))} of 3"
    })
    total += score

    # 3. 检查 ops/best_option.json 存在且合法 (10分)
    target_path = os.path.join(workspace, "ops", "best_option.json")
    if not os.path.isfile(target_path):
        details.append({
            "item": "ops/best_option.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        total += 0
        # 无法继续检查，直接返回
        _write_score(total, details, workspace)
        return total

    try:
        result = load_json(target_path)
        format_ok = isinstance(result, dict) and all(k in result for k in ("flight_id", "price", "platform", "reason"))
    except Exception:
        format_ok = False

    if format_ok:
        details.append({
            "item": "ops/best_option.json valid JSON with required fields",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Fields present: flight_id, price, platform, reason"
        })
        total += 10
    else:
        details.append({
            "item": "ops/best_option.json valid JSON with required fields",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing or malformed fields"
        })
        total += 0
        # 仍然可以检查其他项，但后面依赖字段的部分可能会出错，我们跳过
        _write_score(total, details, workspace)
        return total

    # 4. flight_id 正确 (20分)
    expected_flight_id = "SB-20260615-001"
    if result.get("flight_id") == expected_flight_id:
        details.append({
            "item": "flight_id correct",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"Match: {expected_flight_id}"
        })
        total += 20
    else:
        details.append({
            "item": "flight_id correct",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Got '{result.get('flight_id')}', expected '{expected_flight_id}'"
        })

    # 5. price 正确 (20分)
    expected_price = 1800.0
    price = result.get("price")
    if isinstance(price, (int, float)) and math.isclose(price, expected_price, rel_tol=1e-9):
        details.append({
            "item": "price correct",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"Value: {price}"
        })
        total += 20
    else:
        details.append({
            "item": "price correct",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Got {price}, expected {expected_price}"
        })

    # 6. platform 正确 (20分)
    expected_platform = "skybook"
    if result.get("platform") == expected_platform:
        details.append({
            "item": "platform correct",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"Match: {expected_platform}"
        })
        total += 20
    else:
        details.append({
            "item": "platform correct",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Got '{result.get('platform')}', expected '{expected_platform}'"
        })

    # 7. reason 非空 (10分)
    reason = result.get("reason", "")
    if isinstance(reason, str) and reason.strip():
        details.append({
            "item": "reason is non-empty string",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Reason provided"
        })
        total += 10
    else:
        details.append({
            "item": "reason is non-empty string",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing or empty"
        })

    _write_score(total, details, workspace)
    return total

def _write_score(total, details, workspace):
    out = {
        "total_score": min(100, int(round(total))),
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    ws = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(ws)
