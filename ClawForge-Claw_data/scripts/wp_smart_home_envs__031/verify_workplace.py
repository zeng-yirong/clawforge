import sys
import os
import json
import math
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    base = Path(workspace)
    score = 0
    details = []

    # 1. 检查ops目录 (5分)
    ops_dir = base / "ops"
    if ops_dir.is_dir():
        details.append({
            "item": "ops directory exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Directory ops exists"
        })
        score += 5
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "Directory ops not found"
        })
        write_score(details, score)
        return

    # 2. 检查产物文件存在 (10分)
    out_file = ops_dir / "health_adjustments.json"
    if out_file.is_file():
        details.append({
            "item": "health_adjustments.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File exists"
        })
        score += 10
    else:
        details.append({
            "item": "health_adjustments.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        write_score(details, score)
        return

    # 3. JSON合法性 (10分)
    try:
        with open(out_file, "r") as f:
            output = json.load(f)
        details.append({
            "item": "JSON valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Valid JSON"
        })
        score += 10
    except Exception as e:
        details.append({
            "item": "JSON valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        write_score(details, score)
        return

    # 4. 字段结构检查 (10分)
    if not isinstance(output, list):
        details.append({
            "item": "Output is a list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Output is not a list"
        })
        write_score(details, score)
        return
    structure_ok = True
    for item in output:
        if not isinstance(item, dict) or "device_id" not in item or "recommended_setting" not in item:
            structure_ok = False
            break
    if structure_ok:
        details.append({
            "item": "Output items have required fields",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Each item has device_id and recommended_setting"
        })
        score += 10
    else:
        details.append({
            "item": "Output items have required fields",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing required fields in some items"
        })
        write_score(details, score)
        return

    # 5. 读取初始数据计算预期结果
    try:
        with open(base / "data/health/health.json") as f:
            health_data = json.load(f)["users"]
        with open(base / "data/devices/devices.json") as f:
            devices_data = json.load(f)["devices"]
        with open(base / "data/devices/state.json") as f:
            state_data = json.load(f)
    except Exception as e:
        details.append({
            "item": "Read source data",
            "score": 0,
            "max_score": 0,
            "passed": False,
            "reason": f"Error reading source files: {e}"
        })
        write_score(details, score)
        return

    # 建立用户 location->user 映射
    user_by_location = {}
    for u in health_data:
        loc = u.get("location")
        if loc:
            user_by_location[loc] = u

    # 建立设备 id->info 映射
    device_info = {}
    for d in devices_data:
        device_info[d["device_id"]] = d

    # 建立设备 id->current setting 映射
    current_settings = {}
    for s in state_data:
        current_settings[s["device_id"]] = s["setting"]

    # 计算预期调整列表
    expected = []
    for dev_id, info in device_info.items():
        loc = info.get("location")
        if loc not in user_by_location:
            continue
        if info["type"] not in ("air_conditioner", "humidifier"):
            continue
        user = user_by_location[loc]
        setting = current_settings.get(dev_id)
        if setting is None:
            continue
        if info["type"] == "air_conditioner":
            current_val = setting.get("temperature")
            pref = user["temperature_preference"]
        else:  # humidifier
            current_val = setting.get("humidity")
            pref = user["humidity_preference"]
        if current_val is None:
            continue
        min_val = pref["min"]
        max_val = pref["max"]
        if current_val < min_val:
            recommended = min_val
        elif current_val > max_val:
            recommended = max_val
        else:
            continue  # 在范围内，不需要调整
        expected.append({"device_id": dev_id, "recommended_setting": recommended})

    expected.sort(key=lambda x: x["device_id"])
    output.sort(key=lambda x: x["device_id"])

    # 6. 数量正确性 (15分)
    if len(output) == len(expected):
        details.append({
            "item": "Correct number of devices",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"Expected {len(expected)} adjustments, got {len(output)}"
        })
        score += 15
    else:
        details.append({
            "item": "Correct number of devices",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Expected {len(expected)} adjustments, got {len(output)}"
        })

    # 7. 推荐值准确性 (20分, 每个5分)
    rec_correct = 0
    max_rec_score = 20
    for exp, out_item in zip(expected, output):
        if exp["device_id"] == out_item["device_id"] and math.isclose(exp["recommended_setting"], out_item["recommended_setting"]):
            rec_correct += 1
    rec_score = (rec_correct / max(len(expected), 1)) * max_rec_score
    details.append({
        "item": "Recommended values accuracy",
        "score": rec_score,
        "max_score": max_rec_score,
        "passed": rec_correct == len(expected),
        "reason": f"{rec_correct}/{len(expected)} correct"
    })
    score += rec_score

    # 8. 无多余设备 (10分)
    extra = [o for o in output if o["device_id"] not in {e["device_id"] for e in expected}]
    if len(extra) == 0:
        details.append({
            "item": "No extra devices",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "No unexpected devices in output"
        })
        score += 10
    else:
        details.append({
            "item": "No extra devices",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Extra devices found: {[e['device_id'] for e in extra]}"
        })

    # 9. 忽略非气候设备（smart_plug） (5分)
    plugs_in_output = [o for o in output if any(plug_id in o['device_id'] for plug_id in ['desk_plug', 'floor_plug'])]
    if len(plugs_in_output) == 0:
        details.append({
            "item": "Ignore non-climate devices",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "No smart plugs in output"
        })
        score += 5
    else:
        details.append({
            "item": "Ignore non-climate devices",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "Smart plugs found in output"
        })

    # 10. 忽略无用户location的设备 (study_ac) (5分)
    study_in_output = [o for o in output if o['device_id'] == 'study_ac']
    if len(study_in_output) == 0:
        details.append({
            "item": "Ignore devices without user",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "No study_ac in output"
        })
        score += 5
    else:
        details.append({
            "item": "Ignore devices without user",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "study_ac found in output"
        })

    total_score = min(score, 100)
    write_score(details, total_score)


def write_score(details, total):
    result = {"total_score": int(total), "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()
