import json, os, sys

def verify_workplace(workspace: str) -> dict:
    details = []
    total = 0

    # ---- 1. 检查产物文件是否存在 ----
    target_path = os.path.join(workspace, "ops", "kill_target.json")
    exists = os.path.isfile(target_path)
    if exists:
        total += 10
        details.append({
            "item": "产物文件 ops/kill_target.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件已创建"
        })
    else:
        details.append({
            "item": "产物文件 ops/kill_target.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 后续检查无法进行，直接返回
        return {"total_score": total, "details": details}

    # ---- 2. JSON 合法性 ----
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        total += 10
        details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "解析成功"
        })
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {str(e)}"
        })
        # 无法继续检查
        return {"total_score": total, "details": details}

    # ---- 3. 字段正确性（必须包含 target_id，且无多余字段） ----
    required_fields = {"target_id"}
    actual_fields = set(data.keys())
    if required_fields.issubset(actual_fields) and len(actual_fields) == 1:
        total += 20
        details.append({
            "item": "包含且仅包含 target_id 字段",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "字段数量正确"
        })
    elif required_fields.issubset(actual_fields):
        total += 10
        details.append({
            "item": "包含 target_id 字段",
            "score": 10,
            "max_score": 20,
            "passed": False,
            "reason": f"存在多余字段: {actual_fields - required_fields}"
        })
    else:
        details.append({
            "item": "包含 target_id 字段",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"缺少 target_id 字段；实际字段: {actual_fields}"
        })
        return {"total_score": total, "details": details}

    # ---- 4. target_id 值必须为 "sensor_004" ----
    expected_id = "sensor_004"
    provided_id = data.get("target_id", "")
    if provided_id == expected_id:
        total += 60
        details.append({
            "item": "target_id 值正确",
            "score": 60,
            "max_score": 60,
            "passed": True,
            "reason": f"ID 为 {expected_id}"
        })
    else:
        total += 0
        details.append({
            "item": "target_id 值正确",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": f"期望 {expected_id}，实际 {provided_id}"
        })

    return {"total_score": total, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify_workplace(workspace)
    # 写入评分文件
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
