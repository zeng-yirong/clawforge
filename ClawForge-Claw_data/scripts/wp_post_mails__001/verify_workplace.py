import sys
import os
import json

def verify(workspace):
    details = []
    total_score = 0

    # 1) 检查 launch 目录是否存在 (10分)
    launch_dir = os.path.join(workspace, "launch")
    dir_ok = os.path.isdir(launch_dir)
    details.append({
        "item": "launch 目录存在",
        "score": 10 if dir_ok else 0,
        "max_score": 10,
        "passed": dir_ok,
        "reason": "目录存在" if dir_ok else "launch 目录缺失"
    })
    if dir_ok:
        total_score += 10

    # 2) 检查 draft.json 文件是否存在 (10分)
    draft_path = os.path.join(launch_dir, "draft.json")
    file_ok = os.path.isfile(draft_path)
    details.append({
        "item": "draft.json 文件存在",
        "score": 10 if file_ok else 0,
        "max_score": 10,
        "passed": file_ok,
        "reason": "文件存在" if file_ok else "draft.json 缺失"
    })
    if file_ok:
        total_score += 10
    else:
        # 文件不存在，后续检查跳过
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return total_score

    # 3) 检查 JSON 合法性 (10分)
    try:
        with open(draft_path, "r") as f:
            data = json.load(f)
        json_ok = True
        details.append({
            "item": "draft.json 是合法 JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON 解析成功"
        })
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        json_ok = False
        data = None
        details.append({
            "item": "draft.json 是合法 JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {e}"
        })

    # 4) 字段完整性 (20分)
    if json_ok and isinstance(data, dict):
        required_keys = ["mission", "date", "approver"]
        missing = [k for k in required_keys if k not in data]
        extra = [k for k in data if k not in required_keys]
        completeness_score = 0
        # 每个必要字段存在得 5 分，共 15
        for k in required_keys:
            if k in data:
                completeness_score += 5
        # 无多余字段得 5 分
        if not extra:
            completeness_score += 5
        else:
            # 有额外字段，该项不得分
            pass
        passed = len(missing) == 0 and len(extra) == 0
        reason_parts = []
        if missing:
            reason_parts.append(f"缺失字段: {missing}")
        if extra:
            reason_parts.append(f"多余字段: {extra}")
        details.append({
            "item": "字段完整性（含 mission, date, approver，且无多余字段）",
            "score": completeness_score,
            "max_score": 20,
            "passed": passed,
            "reason": "; ".join(reason_parts) if reason_parts else "所有必要字段存在且无多余"
        })
        total_score += completeness_score

        # 5) 字段值正确性 (40分)
        expected = {
            "mission": "Orbital Aurora",
            "date": "2025-07-20",
            "approver": "Mira Chen"
        }
        value_score = 0
        field_details = []
        # mission 15分
        if data.get("mission") == expected["mission"]:
            value_score += 15
            field_details.append("mission 正确")
        else:
            field_details.append(f"mission 应为 '{expected['mission']}'，实际为 '{data.get('mission')}'")
        # date 15分
        if data.get("date") == expected["date"]:
            value_score += 15
            field_details.append("date 正确")
        else:
            field_details.append(f"date 应为 '{expected['date']}'，实际为 '{data.get('date')}'")
        # approver 10分
        if data.get("approver") == expected["approver"]:
            value_score += 10
            field_details.append("approver 正确")
        else:
            field_details.append(f"approver 应为 '{expected['approver']}'，实际为 '{data.get('approver')}'")
        all_correct = value_score == 40
        details.append({
            "item": "字段值正确性",
            "score": value_score,
            "max_score": 40,
            "passed": all_correct,
            "reason": "; ".join(field_details)
        })
        total_score += value_score
    else:
        # JSON 不合法或不是字典，字段检查得 0 分
        details.append({
            "item": "字段完整性及值正确性",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": "JSON 不合法或不是对象"
        })

    # 6) 检查 launch 目录下是否只有 draft.json (10分)
    extra_files = []
    if os.path.isdir(launch_dir):
        all_files = [f for f in os.listdir(launch_dir) if os.path.isfile(os.path.join(launch_dir, f))]
        extra_files = [f for f in all_files if f != "draft.json"]
    clean = len(extra_files) == 0
    details.append({
        "item": "launch 目录没有多余文件",
        "score": 10 if clean else 0,
        "max_score": 10,
        "passed": clean,
        "reason": "目录干净" if clean else f"多余文件: {extra_files}"
    })
    if clean:
        total_score += 10

    # 确保总分不超过 100
    total_score = min(total_score, 100)

    # 写入结果
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    return total_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
