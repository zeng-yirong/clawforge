import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result_path = os.path.join(workspace, "ops", "flight_decision.json")

    details = []
    # 1. 文件存在性 (10分)
    if os.path.exists(result_path):
        details.append({"item": "result file exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/flight_decision.json found"})
    else:
        details.append({"item": "result file exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/flight_decision.json not found"})
        # 如果文件不存在，后续评分直接 fail 但继续收集
        total_score = 0
        write_score(details, total_score, workspace)
        return

    # 2. JSON 合法性 (10分)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append({"item": "valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON"})
    except Exception as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        total_score = sum(d["score"] for d in details)
        write_score(details, total_score, workspace)
        return

    # 3. 必需字段 (20分)
    required_fields = ["platform_id", "flight_id", "price", "cabin_class", "policy_id"]
    missing = [f for f in required_fields if f not in data]
    if not missing:
        details.append({"item": "required fields present", "score": 20, "max_score": 20, "passed": True, "reason": "All required fields present"})
    else:
        details.append({"item": "required fields present", "score": 0, "max_score": 20, "passed": False, "reason": f"Missing fields: {missing}"})
        # 缺失字段导致后续无法检查，剩余分数设为 0
        write_score(details, sum(d["score"] for d in details), workspace)
        return

    # 4. policy_id 正确 (10分)
    if data["policy_id"] == "travel_policy_v2":
        details.append({"item": "policy_id correct", "score": 10, "max_score": 10, "passed": True, "reason": "policy_id is travel_policy_v2"})
    else:
        details.append({"item": "policy_id correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected travel_policy_v2, got {data['policy_id']}"})

    # 5. platform_id 正确 (10分)
    if data["platform_id"] == "aero_cheap":
        details.append({"item": "platform_id correct", "score": 10, "max_score": 10, "passed": True, "reason": "platform_id is aero_cheap"})
    else:
        details.append({"item": "platform_id correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected aero_cheap, got {data['platform_id']}"})

    # 6. flight_id 正确 (10分)
    if data["flight_id"] == "AC-1234":
        details.append({"item": "flight_id correct", "score": 10, "max_score": 10, "passed": True, "reason": "flight_id is AC-1234"})
    else:
        details.append({"item": "flight_id correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected AC-1234, got {data['flight_id']}"})

    # 7. cabin_class 正确 (10分)
    if data["cabin_class"] == "economy":
        details.append({"item": "cabin_class correct", "score": 10, "max_score": 10, "passed": True, "reason": "cabin_class is economy"})
    else:
        details.append({"item": "cabin_class correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected economy, got {data['cabin_class']}"})

    # 8. price 正确 (10分)
    if isinstance(data["price"], (int, float)) and data["price"] == 1800:
        details.append({"item": "price correct", "score": 10, "max_score": 10, "passed": True, "reason": "price is 1800"})
    else:
        details.append({"item": "price correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected 1800, got {data['price']}"})

    # 9. 无非法值/多余字段 (10分) — 只允许额外字段，但不允许字段值为空或类型错误
    bad_fields = []
    for field in required_fields:
        val = data[field]
        if val is None or (isinstance(val, str) and val.strip() == ""):
            bad_fields.append(f"{field} is empty")
    if not bad_fields:
        details.append({"item": "no illegal values", "score": 10, "max_score": 10, "passed": True, "reason": "All required fields have non-empty values"})
    else:
        details.append({"item": "no illegal values", "score": 0, "max_score": 10, "passed": False, "reason": "Empty/null values: " + "; ".join(bad_fields)})

    total_score = sum(d["score"] for d in details)
    write_score(details, total_score, workspace)

def write_score(details, total_score, workspace):
    score_path = os.path.join(workspace, "workplace_score.json")
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
