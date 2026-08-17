import sys
import os
import json
import re

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    max_possible = 100

    # 1. 目录结构检查 （10分）
    required_dirs = ["ops", "data/devices/status", "data/electricity", "data/health", "data/weather"]
    dirs_ok = True
    for d in required_dirs:
        if not os.path.isdir(os.path.join(workspace, d)):
            dirs_ok = False
            score_details.append({"item": "Directory structure", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing directory: {d}"})
            break
    if dirs_ok:
        score_details.append({"item": "Directory structure", "score": 10, "max_score": 10, "passed": True, "reason": "All required directories exist"})
        total_score += 10

    # 2. 产物文件存在性 （20分）
    plan_path = os.path.join(workspace, "ops", "optimization_plan.json")
    if not os.path.isfile(plan_path):
        score_details.append({"item": "Output file existence", "score": 0, "max_score": 20, "passed": False, "reason": "ops/optimization_plan.json not found"})
        # 直接返回，无法继续
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return
    else:
        score_details.append({"item": "Output file existence", "score": 20, "max_score": 20, "passed": True, "reason": "File exists"})
        total_score += 20

    # 3. JSON 格式与结构 （10分）
    try:
        with open(plan_path, "r") as f:
            plan = json.load(f)
        if not isinstance(plan, dict) or "actions" not in plan:
            raise ValueError("Missing 'actions' key")
        if not isinstance(plan["actions"], list):
            raise ValueError("'actions' is not a list")
        score_details.append({"item": "JSON format & structure", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON with actions list"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "JSON format & structure", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        # 无法继续
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 4. 动作数量 （10分） 期望恰好2个动作（bedroom_ac 和 bedroom_humidifier）
    actions = plan["actions"]
    if len(actions) == 2:
        score_details.append({"item": "Number of actions", "score": 10, "max_score": 10, "passed": True, "reason": "Exactly 2 actions"})
        total_score += 10
    else:
        score_details.append({"item": "Number of actions", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected 2 actions, got {len(actions)}"})

    # 5. 设备ID正确性 （20分） 必须包含 bedroom_ac 和 bedroom_humidifier
    device_ids = {a.get("device_id") for a in actions}
    expected_ids = {"bedroom_ac", "bedroom_humidifier"}
    if device_ids == expected_ids:
        score_details.append({"item": "Device IDs", "score": 20, "max_score": 20, "passed": True, "reason": "Correct device IDs"})
        total_score += 20
    else:
        missing = expected_ids - device_ids
        extra = device_ids - expected_ids
        reason_parts = []
        if missing:
            reason_parts.append(f"Missing: {missing}")
        if extra:
            reason_parts.append(f"Unexpected: {extra}")
        score_details.append({"item": "Device IDs", "score": 0, "max_score": 20, "passed": False, "reason": "; ".join(reason_parts)})

    # 6. 动作参数准确性 （30分） 需检查每个设备的关键参数
    params_ok = True
    param_errors = []
    for action in actions:
        did = action.get("device_id")
        if did == "bedroom_ac":
            # 期望 action: turn_on, set_temperature: 25 (Jane偏好中值)
            if action.get("action") != "turn_on":
                param_errors.append(f"bedroom_ac action should be 'turn_on', got '{action.get('action')}'")
                params_ok = False
            # set_temperature 可接受24-26之间的整数，但唯一答案是25
            if action.get("set_temperature") != 25:
                param_errors.append(f"bedroom_ac set_temperature should be 25, got {action.get('set_temperature')}")
                params_ok = False
        elif did == "bedroom_humidifier":
            if action.get("action") != "turn_on":
                param_errors.append(f"bedroom_humidifier action should be 'turn_on', got '{action.get('action')}'")
                params_ok = False
            if action.get("target_humidity") != 50:
                param_errors.append(f"bedroom_humidifier target_humidity should be 50, got {action.get('target_humidity')}")
                params_ok = False

    if params_ok:
        score_details.append({"item": "Action parameters", "score": 30, "max_score": 30, "passed": True, "reason": "All parameters match expected values"})
        total_score += 30
    else:
        score_details.append({"item": "Action parameters", "score": 0, "max_score": 30, "passed": False, "reason": "; ".join(param_errors)})

    # 7. 无多余字段 （作为额外质量检查，扣分项已包含在结构检查里）
    # 最终分数
    total_score = min(total_score, 100)
    result = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
