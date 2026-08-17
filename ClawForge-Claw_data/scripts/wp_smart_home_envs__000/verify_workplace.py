import sys
import os
import json

def write_score(workspace, total, details):
    result = {"total_score": total, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 目录结构 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ found"})
        score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ not found"})
        write_score(workspace, score, details)
        return

    # 2. 推荐文件存在且合法 (10分)
    rec_file = os.path.join(ops_dir, "recommendations.json")
    if not os.path.isfile(rec_file):
        details.append({"item": "recommendations.json exists and valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        write_score(workspace, score, details)
        return
    try:
        with open(rec_file, "r") as f:
            rec = json.load(f)
    except json.JSONDecodeError:
        details.append({"item": "recommendations.json exists and valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "invalid JSON"})
        write_score(workspace, score, details)
        return
    details.append({"item": "recommendations.json exists and valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "valid JSON"})
    score += 10

    # 3. 推荐列表非空 (10分)
    items = rec.get("recommendations", rec.get("adjustments", rec.get("actions", [])))
    if not isinstance(items, list) or len(items) == 0:
        details.append({"item": "recommendations list non-empty", "score": 0, "max_score": 10, "passed": False, "reason": "no recommendations found"})
        write_score(workspace, score, details)
        return
    details.append({"item": "recommendations list non-empty", "score": 10, "max_score": 10, "passed": True, "reason": f"found {len(items)} items"})
    score += 10

    # 4. 正确设备数量 (20分)
    expected_count = 2
    if len(items) == expected_count:
        details.append({"item": "correct number of devices to adjust", "score": 20, "max_score": 20, "passed": True, "reason": f"exactly {expected_count}"})
        score += 20
    else:
        details.append({"item": "correct number of devices to adjust", "score": 0, "max_score": 20, "passed": False, "reason": f"expected {expected_count}, got {len(items)}"})

    # 5. 具体操作 (40分，每个20)
    expected = {
        "humid_bedroom_01": {"action": "turn_on", "new_setting": {"humidity": 55}},
        "ac_living_01": {"action": "adjust_setting", "new_setting": {"temperature": 24}}
    }
    for dev_id, exp in expected.items():
        found = False
        correct = False
        for item in items:
            if item.get("device_id", "") == dev_id:
                found = True
                act = item.get("action", "").lower()
                setting = item.get("new_setting", item.get("setting", {}))
                if act == exp["action"] and setting == exp["new_setting"]:
                    correct = True
                break
        if found and correct:
            details.append({"item": f"Correct action for {dev_id}", "score": 20, "max_score": 20, "passed": True, "reason": f"matched {exp}"})
            score += 20
        elif found and not correct:
            details.append({"item": f"Correct action for {dev_id}", "score": 0, "max_score": 20, "passed": False, "reason": f"device found but action/setting mismatch"})
        else:
            details.append({"item": f"Correct action for {dev_id}", "score": 0, "max_score": 20, "passed": False, "reason": "device not found in recommendations"})

    # 6. 额外扣分：如果推荐了不应调整的设备（如 TV Smart Plug），扣10分
    undesired_ids = {"plug_tv_01", "plug_desk_01", "plug_floor_lamp_01", "ac_bedroom_01", "humid_living_01"}
    for item in items:
        dev_id = item.get("device_id", "")
        if dev_id in undesired_ids:
            details.append({"item": "No unnecessary devices recommended", "score": -10, "max_score": 0, "passed": False, "reason": f"unnecessary device {dev_id} included"})
            score += -10  # 注意：扣分后最低0？可以限制不扣到负分，但这里保持简单
            break

    # 确保总分在0-100
    total = max(0, min(100, score))
    write_score(workspace, total, details)

if __name__ == "__main__":
    main()
