import json
import os
import sys

def verify(workspace: str):
    workspace = os.path.abspath(workspace)
    details = []
    total_score = 0

    # 1. 检查 conflict_report.json 是否存在 (10分)
    report_path = os.path.join(workspace, "conflict_report.json")
    if os.path.isfile(report_path):
        details.append({
            "item": "conflict_report.json 文件存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10
    else:
        details.append({
            "item": "conflict_report.json 文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "未找到 conflict_report.json"
        })
        # 如果文件不存在，后续无法检查，直接输出结果
        _write_score(workspace, total_score, details)
        return

    # 2. 检查 JSON 合法性 (10分)
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "解析成功"
        })
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {e}"
        })
        _write_score(workspace, total_score, details)
        return

    # 3. 检查字段完整性 (20分)
    required_fields = {"time", "device1", "device2"}
    actual_fields = set(data.keys())
    if actual_fields == required_fields:
        details.append({
            "item": "字段完整性",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"字段正确: {sorted(actual_fields)}"
        })
        total_score += 20
    else:
        missing = required_fields - actual_fields
        extra = actual_fields - required_fields
        reason = ""
        if missing:
            reason += f"缺少字段: {missing}; "
        if extra:
            reason += f"多余字段: {extra}; "
        details.append({
            "item": "字段完整性",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": reason
        })
        # 仍继续检查已有字段的值（如果缺少关键字段，后面的值检查会失败）

    # 4. 检查 time 值 (20分)
    expected_time = "22:00-23:00"
    actual_time = data.get("time", "") if isinstance(data, dict) else ""
    if actual_time == expected_time:
        details.append({
            "item": "time 值正确",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"time 为 {expected_time}"
        })
        total_score += 20
    else:
        details.append({
            "item": "time 值正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"期望 {expected_time}, 实际 {actual_time}"
        })

    # 5. 检查 device1 值 (20分)
    expected_d1 = "living_room_ac_01"
    actual_d1 = data.get("device1", "") if isinstance(data, dict) else ""
    if actual_d1 == expected_d1:
        details.append({
            "item": "device1 值正确",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"device1 为 {expected_d1}"
        })
        total_score += 20
    else:
        details.append({
            "item": "device1 值正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"期望 {expected_d1}, 实际 {actual_d1}"
        })

    # 6. 检查 device2 值 (20分)
    expected_d2 = "bedroom_humidifier_01"
    actual_d2 = data.get("device2", "") if isinstance(data, dict) else ""
    if actual_d2 == expected_d2:
        details.append({
            "item": "device2 值正确",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"device2 为 {expected_d2}"
        })
        total_score += 20
    else:
        details.append({
            "item": "device2 值正确",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"期望 {expected_d2}, 实际 {actual_d2}"
        })

    # 额外扣分：多余字段（已在字段完整性中处理，这里不再重复扣）
    # 确保总分不超过100
    total_score = min(total_score, 100)

    _write_score(workspace, total_score, details)

def _write_score(workspace, total_score, details):
    output = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
