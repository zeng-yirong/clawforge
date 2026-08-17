import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. 检查 ops 目录是否存在 (10分)
    ops_path = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_path)
    details.append({
        "item": "ops/ 目录存在",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "目录存在" if dir_exists else "缺少 ops/ 目录"
    })
    if dir_exists:
        total_score += 10

    # 2. 检查 fix_afternoon_ac.json 文件是否存在 (10分)
    target_file = os.path.join(ops_path, "fix_afternoon_ac.json")
    file_exists = os.path.isfile(target_file)
    details.append({
        "item": "fix_afternoon_ac.json 存在",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "文件存在" if file_exists else "缺少目标文件"
    })
    if file_exists:
        total_score += 10

    # 3. 文件是否为合法 JSON (10分)
    if file_exists:
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
            json_valid = True
            reason = "JSON 格式正确"
        except Exception as e:
            json_valid = False
            reason = f"JSON 解析失败: {e}"
    else:
        json_valid = False
        reason = "文件不存在，跳过"
    details.append({
        "item": "JSON 格式合法",
        "score": 10 if json_valid else 0,
        "max_score": 10,
        "passed": json_valid,
        "reason": reason
    })
    if json_valid:
        total_score += 10

    # 如果 JSON 合法，检查关键字段和数值
    field_checks = []
    if json_valid and isinstance(data, dict):
        # 4. 必须包含 device_id 字段 (10分)
        device_id_ok = "device_id" in data and data["device_id"] == "ac_001"
        field_checks.append(("device_id 为 'ac_001'", device_id_ok, 10))
        # 5. 必须包含 time_range 且为 "14:00-17:00" (20分)
        time_ok = "time_range" in data and data["time_range"] == "14:00-17:00"
        field_checks.append(("time_range 为 '14:00-17:00'", time_ok, 20))
        # 6. 必须包含 temperature 且为 24 (20分)
        temp_ok = "temperature" in data and data["temperature"] == 24
        field_checks.append(("temperature 为 24", temp_ok, 20))
        # 7. 必须包含 action 且为 "turn_on" (10分)
        action_ok = "action" in data and data["action"] == "turn_on"
        field_checks.append(("action 为 'turn_on'", action_ok, 10))
        # 8. 额外：不应包含错误调度的痕迹（比如温度26）作为加分扣分？但无需检查
        # 9. 检查是否有多余的字段导致歧义（可选，但不扣分）

        for label, ok, weight in field_checks:
            score = weight if ok else 0
            details.append({
                "item": label,
                "score": score,
                "max_score": weight,
                "passed": ok,
                "reason": "符合预期" if ok else "数值或字段错误"
            })
            total_score += score
    elif json_valid:
        # JSON 不是 dict
        details.append({
            "item": "JSON 顶层为对象",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "顶层不是 JSON 对象"
        })

    # 确保总分不超过100
    total_score = min(total_score, 100)

    # 写入评分文件
    result = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"评分完成：{total_score}/100")

if __name__ == "__main__":
    main()
