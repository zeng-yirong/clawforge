import sys
import os
import json

def grade() -> dict:
    # 获取工作区路径
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "ops", "conflict_report.json")

    details = []
    total_score = 0

    # 1. 检查目录结构 (ops/ 存在)
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    details.append({
        "item": "ops/ directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "op directory found" if dir_exists else "ops/ directory missing"
    })
    if dir_exists:
        total_score += 10

    # 2. 检查报告文件是否存在
    file_exists = os.path.isfile(report_path)
    details.append({
        "item": "conflict_report.json exists",
        "score": 20 if file_exists else 0,
        "max_score": 20,
        "passed": file_exists,
        "reason": "report file found" if file_exists else "conflict_report.json not found"
    })
    if file_exists:
        total_score += 20
    else:
        # 提前结束，无法继续
        return {
            "total_score": total_score,
            "details": details
        }

    # 3. JSON 合法性
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        json_valid = True
    except (json.JSONDecodeError, Exception) as e:
        json_valid = False
        details.append({
            "item": "Valid JSON",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        # 停在这里，无法再检查字段
        return {"total_score": total_score, "details": details}

    details.append({
        "item": "Valid JSON",
        "score": 20,
        "max_score": 20,
        "passed": True,
        "reason": "File is valid JSON"
    })
    total_score += 20

    # 4. 必须包含 schedule_id 字段
    has_schedule_id = "schedule_id" in data and isinstance(data["schedule_id"], str)
    details.append({
        "item": "schedule_id field present and string",
        "score": 10 if has_schedule_id else 0,
        "max_score": 10,
        "passed": has_schedule_id,
        "reason": f"schedule_id = {data.get('schedule_id')!r}" if has_schedule_id else "schedule_id missing or not a string"
    })
    if has_schedule_id:
        total_score += 10

    # 5. 必须包含 device_id 字段
    has_device_id = "device_id" in data and isinstance(data["device_id"], str)
    details.append({
        "item": "device_id field present and string",
        "score": 10 if has_device_id else 0,
        "max_score": 10,
        "passed": has_device_id,
        "reason": f"device_id = {data.get('device_id')!r}" if has_device_id else "device_id missing or not a string"
    })
    if has_device_id:
        total_score += 10

    # 6. 必须包含 reason 字段（非空字符串）
    has_reason = "reason" in data and isinstance(data["reason"], str) and len(data["reason"].strip()) > 0
    details.append({
        "item": "reason field present and non-empty",
        "score": 10 if has_reason else 0,
        "max_score": 10,
        "passed": has_reason,
        "reason": f"reason = {data.get('reason')!r}" if has_reason else "reason missing or empty"
    })
    if has_reason:
        total_score += 10

    # 7. 关键值匹配：schedule_id 必须是 "sch-003"
    sid_correct = has_schedule_id and data["schedule_id"] == "sch-003"
    details.append({
        "item": "schedule_id equals 'sch-003'",
        "score": 20 if sid_correct else 0,
        "max_score": 20,
        "passed": sid_correct,
        "reason": f"schedule_id = {data.get('schedule_id')!r}" if sid_correct else f"expected 'sch-003', got {data.get('schedule_id')!r}"
    })
    if sid_correct:
        total_score += 20

    # 8. 关键值匹配：device_id 必须是 "ac-001"
    did_correct = has_device_id and data["device_id"] == "ac-001"
    details.append({
        "item": "device_id equals 'ac-001'",
        "score": 20 if did_correct else 0,
        "max_score": 20,
        "passed": did_correct,
        "reason": f"device_id = {data.get('device_id')!r}" if did_correct else f"expected 'ac-001', got {data.get('device_id')!r}"
    })
    if did_correct:
        total_score += 20

    # 总分不能超过 100（调整最大值，实际总分可能超过100，这里我们限制为100）
    final_total = min(total_score, 100)
    # 调整细节中的分数使其和不超过100？不必，total_score 显示实际得分，但最终输出取 min
    # 为了符合规范，我们按实际权重，再调整最后总分
    # 我们动态重算：实际满分是10+20+20+10+10+10+20+20 = 120，但题目要求0-100。
    # 所以按比例缩放。
    max_possible = 120
    scaled_total = round((total_score / max_possible) * 100)
    # 但保留细节原始分数，只修改 total_score 为缩放后值
    result = {
        "total_score": scaled_total,
        "details": details
    }
    return result

if __name__ == "__main__":
    result = grade()
    # 写入 workplace_score.json
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
