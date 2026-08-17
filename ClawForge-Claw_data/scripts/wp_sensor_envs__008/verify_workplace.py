import sys, os, json, math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. 目录检查 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops/ 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops 目录存在"})
        total_score += 10
    else:
        details.append({"item": "ops/ 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops 目录不存在"})

    # 2. 文件存在性 (10分)
    target_path = os.path.join(workspace, "ops/adjustments.json")
    if os.path.isfile(target_path):
        details.append({"item": "ops/adjustments.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "目标文件存在"})
        total_score += 10
    else:
        details.append({"item": "ops/adjustments.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 后续检查无法进行，直接返回
        write_score(details, total_score, workspace)
        return

    # 3. JSON 合法性 (10分)
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "可正常解析"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        write_score(details, total_score, workspace)
        return

    # 4. 字段完整性 (10分)
    required_fields = {"sensor_id", "new_low", "new_high"}
    if set(data.keys()) == required_fields:
        details.append({"item": "字段完整性", "score": 10, "max_score": 10, "passed": True, "reason": "包含且仅包含 sensor_id, new_low, new_high"})
        total_score += 10
    else:
        extra = set(data.keys()) - required_fields
        missing = required_fields - set(data.keys())
        reason_parts = []
        if extra: reason_parts.append(f"多余字段: {extra}")
        if missing: reason_parts.append(f"缺少字段: {missing}")
        details.append({"item": "字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": "; ".join(reason_parts)})

    # 5. sensor_id 正确 (20分)
    expected_sensor_id = "sens_006"
    if data.get("sensor_id") == expected_sensor_id:
        details.append({"item": "sensor_id 值正确", "score": 20, "max_score": 20, "passed": True, "reason": f"值为 {expected_sensor_id}"})
        total_score += 20
    else:
        details.append({"item": "sensor_id 值正确", "score": 0, "max_score": 20, "passed": False, "reason": f"期望 {expected_sensor_id}，得到 {data.get('sensor_id')}"})

    # 6. new_low 数值正确 (20分)
    expected_low = 63.5
    actual_low = data.get("new_low")
    if isinstance(actual_low, (int, float)) and math.isclose(actual_low, expected_low, rel_tol=1e-9):
        details.append({"item": "new_low 数值正确", "score": 20, "max_score": 20, "passed": True, "reason": f"值为 {actual_low}"})
        total_score += 20
    else:
        details.append({"item": "new_low 数值正确", "score": 0, "max_score": 20, "passed": False, "reason": f"期望 {expected_low}，得到 {actual_low}"})

    # 7. new_high 数值正确 (20分)
    expected_high = 73.5
    actual_high = data.get("new_high")
    if isinstance(actual_high, (int, float)) and math.isclose(actual_high, expected_high, rel_tol=1e-9):
        details.append({"item": "new_high 数值正确", "score": 20, "max_score": 20, "passed": True, "reason": f"值为 {actual_high}"})
        total_score += 20
    else:
        details.append({"item": "new_high 数值正确", "score": 0, "max_score": 20, "passed": False, "reason": f"期望 {expected_high}，得到 {actual_high}"})

    # 最终写入
    write_score(details, total_score, workspace)

def write_score(details, total, workspace):
    result = {"total_score": total, "details": details}
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    # 输出到 stdout 方便查看
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
