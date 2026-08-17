import sys
import os
import json
import math

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 文件存在性 (10分)
    target_file = os.path.join(workspace, "ops/ac_adjustment.json")
    if os.path.isfile(target_file):
        score_details.append({
            "item": "ops/ac_adjustment.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Target file found"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "ops/ac_adjustment.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # 后续检查无法进行，直接输出结果
        output = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(output, f, indent=2)
        return

    # 2. JSON 合法性 (10分)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "Valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON parsed successfully"
        })
        total_score += 10
    except Exception as e:
        score_details.append({
            "item": "Valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        output = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(output, f, indent=2)
        return

    # 3. 必要字段存在 (10分)
    required_keys = ["device_id", "target_temperature", "schedule"]
    missing_keys = [k for k in required_keys if k not in data]
    if not missing_keys:
        score_details.append({
            "item": "Required fields present",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"All keys present: {required_keys}"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "Required fields present",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Missing keys: {missing_keys}"
        })
        output = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(output, f, indent=2)
        return

    # 4. device_id 正确性 (15分)
    if data["device_id"] == "AC_001":
        score_details.append({
            "item": "device_id == AC_001",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "Correct bedroom AC identifier"
        })
        total_score += 15
    else:
        score_details.append({
            "item": "device_id == AC_001",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Got {data['device_id']}, expected AC_001"
        })

    # 5. target_temperature 正确性 (20分)
    if data["target_temperature"] == 23:
        score_details.append({
            "item": "target_temperature == 23",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Correct ideal temperature for Jane"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "target_temperature == 23",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Got {data['target_temperature']}, expected 23"
        })

    # 6. schedule 包含正确的睡眠时段 (20分)
    schedule = data.get("schedule", [])
    # 期望至少有一个元素：start_hour=22, end_hour=6 (覆盖22:00-06:00)
    found_slot = False
    for slot in schedule:
        if not isinstance(slot, dict):
            continue
        sh = slot.get("start_hour")
        eh = slot.get("end_hour")
        if sh == 22 and eh == 6:
            found_slot = True
            break
    if found_slot:
        score_details.append({
            "item": "schedule contains slot (22,6)",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Sleeping period adjustment slot found"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "schedule contains slot (22,6)",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"No slot with start_hour=22 and end_hour=6 in schedule: {schedule}"
        })

    # 7. 没有多余无关设备调整 (15分)
    # 要求 schedule 中所有 slot 的 end_hour 和 start_hour 都在 0-24 范围内，且只针对单个设备
    # 简单的额外检查：确保没有出现其他 device_id 或目标温度不一致的槽
    # 这里仅检查输出中没有意外的键（如 device2）
    extra_keys = [k for k in data.keys() if k not in ("device_id", "target_temperature", "schedule")]
    if not extra_keys:
        score_details.append({
            "item": "No extra top-level keys",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Only the three expected keys present"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "No extra top-level keys",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Unexpected keys: {extra_keys}"
        })

    # 附加：检查 schedule 中每个槽的 target_temperature 是否等于 23（可选，不扣分）
    schedule_temp_ok = all(
        slot.get("target_temperature") in (23, None) for slot in schedule
    )
    if not schedule_temp_ok:
        # 轻微扣分，但满分15，只扣5
        score_details.append({
            "item": "Schedule slot temperatures consistent",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "Some slot has target_temperature != 23"
        })
    else:
        score_details.append({
            "item": "Schedule slot temperatures consistent",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "All slots target 23 or not specified"
        })
        total_score += 5

    # 总分汇总（可能超出100，但确保最高100）
    total_score = min(total_score, 100)
    output = {
        "total_score": total_score,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    verify()
