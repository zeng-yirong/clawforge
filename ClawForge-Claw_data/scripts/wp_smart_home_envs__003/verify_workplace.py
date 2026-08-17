import sys
import json
import os

def verify(workspace):
    details = []
    total_score = 0

    # 1. 检查 ops 目录存在 (10分)
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        details.append({"item": "ops directory", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ exists"})
        total_score += 10
    else:
        details.append({"item": "ops directory", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ not found"})

    # 2. 检查输出文件存在 (10分)
    output_file = os.path.join(ops_path, "device_adjustments.json")
    if os.path.isfile(output_file):
        details.append({"item": "output file", "score": 10, "max_score": 10, "passed": True, "reason": "ops/device_adjustments.json exists"})
        total_score += 10
    else:
        details.append({"item": "output file", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        # 无法继续检查内容，直接写入分数退出
        score_data = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_data, f, indent=2)
        return

    # 3. 解析 JSON 合法性 (10分)
    try:
        with open(output_file, "r") as f:
            data = json.load(f)
        adjustments = data.get("adjustments", [])
        if not isinstance(adjustments, list):
            raise ValueError("adjustments is not a list")
        details.append({"item": "JSON valid & adjustments list", "score": 10, "max_score": 10, "passed": True, "reason": "valid JSON with adjustments array"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON valid & adjustments list", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        score_data = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_data, f, indent=2)
        return

    # 4. 检查是否包含了 bedroom AC 的调整 (20分)
    ac_device = "ac_bedroom_01"
    ac_adjustment = None
    for adj in adjustments:
        if adj.get("device_id") == ac_device:
            ac_adjustment = adj
            break
    if ac_adjustment:
        details.append({"item": "bedroom AC adjustment present", "score": 20, "max_score": 20, "passed": True, "reason": "ac_bedroom_01 found"})
        total_score += 20
    else:
        details.append({"item": "bedroom AC adjustment present", "score": 0, "max_score": 20, "passed": False, "reason": "missing adjustment for ac_bedroom_01"})

    # 5. 检查 bedroom AC 新温度是否在偏好范围 (20分)
    temperature_ok = False
    if ac_adjustment:
        new_temp = ac_adjustment.get("setting", {}).get("temperature")
        if new_temp is not None and 20 <= new_temp <= 24:
            temperature_ok = True
            details.append({"item": "bedroom AC temperature in 20-24 range", "score": 20, "max_score": 20, "passed": True, "reason": f"temperature={new_temp} within preference"})
            total_score += 20
        else:
            details.append({"item": "bedroom AC temperature in 20-24 range", "score": 0, "max_score": 20, "passed": False, "reason": f"temperature {new_temp} out of range"})
    else:
        details.append({"item": "bedroom AC temperature in 20-24 range", "score": 0, "max_score": 20, "passed": False, "reason": "no ac_adjustment to evaluate"})

    # 6. 检查是否包含了卧室加湿器的调整 (20分)
    humidifier_device = "humidifier_bedroom_01"
    humidifier_adjustment = None
    for adj in adjustments:
        if adj.get("device_id") == humidifier_device:
            humidifier_adjustment = adj
            break
    if humidifier_adjustment:
        details.append({"item": "bedroom humidifier adjustment present", "score": 20, "max_score": 20, "passed": True, "reason": "humidifier_bedroom_01 found"})
        total_score += 20
    else:
        details.append({"item": "bedroom humidifier adjustment present", "score": 0, "max_score": 20, "passed": False, "reason": "missing adjustment for humidifier_bedroom_01"})

    # 7. 检查加湿器新湿度不高于60% (20分) —— 因为 humidity_preference max=60
    humidity_ok = False
    if humidifier_adjustment:
        new_humidity = humidifier_adjustment.get("setting", {}).get("humidity")
        if new_humidity is not None and new_humidity <= 60:
            humidity_ok = True
            details.append({"item": "bedroom humidifier humidity <=60%", "score": 20, "max_score": 20, "passed": True, "reason": f"humidity={new_humidity} within preference"})
            total_score += 20
        else:
            details.append({"item": "bedroom humidifier humidity <=60%", "score": 0, "max_score": 20, "passed": False, "reason": f"humidity {new_humidity} out of range"})
    else:
        details.append({"item": "bedroom humidifier humidity <=60%", "score": 0, "max_score": 20, "passed": False, "reason": "no humidifier adjustment to evaluate"})

    # 8. 检查是否有多余的无关设备调整（超额扣分，最多扣20分）
    expected_ids = {ac_device, humidifier_device}
    actual_ids = {adj.get("device_id") for adj in adjustments}
    extra = actual_ids - expected_ids
    if extra:
        extra_score = max(-20, -len(extra) * 10)  # 每个多余扣10，最多扣20
        details.append({"item": "no extra device adjustments", "score": extra_score, "max_score": 20, "passed": False, "reason": f"unexpected devices: {extra}"})
        total_score += extra_score
    else:
        details.append({"item": "no extra device adjustments", "score": 20, "max_score": 20, "passed": True, "reason": "no extra adjustments"})
        total_score += 20

    # 总分上限 clamp 0-100
    total_score = max(0, min(100, total_score))
    score_data = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score_data, f, indent=2)

if __name__ == "__main__":
    ws = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(ws)
