import json
import os
import sys

def verify_workplace(workspace: str):
    details = []
    total_score = 0

    # 1. 检查 ops 目录是否存在 (权重 5)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({
            "item": "ops 目录存在",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "ops/ 目录已创建"
        })
        total_score += 5
    else:
        details.append({
            "item": "ops 目录存在",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "未找到 ops/ 目录"
        })

    # 2. 检查 ops/fan_check.json 文件是否存在 (权重 10)
    fan_check_path = os.path.join(workspace, "ops", "fan_check.json")
    if os.path.isfile(fan_check_path):
        details.append({
            "item": "fan_check.json 文件存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "目标文件已生成"
        })
        total_score += 10
    else:
        details.append({
            "item": "fan_check.json 文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "未找到 ops/fan_check.json"
        })
        # 无法继续，直接返回
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)
        return total_score

    # 3. 检查文件是否为合法 JSON (权重 10)
    try:
        with open(fan_check_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({
            "item": "fan_check.json 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "成功解析为 JSON"
        })
        total_score += 10
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({
            "item": "fan_check.json 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {str(e)}"
        })
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)
        return total_score

    # 4. 检查是否包含预设的两个字段 (权重 15)
    has_preset_id = "preset_id" in data
    has_fan_speed = "fan_speed" in data
    if has_preset_id and has_fan_speed:
        details.append({
            "item": "包含 preset_id 和 fan_speed 字段",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "两个必需字段均存在"
        })
        total_score += 15
    else:
        missing = []
        if not has_preset_id:
            missing.append("preset_id")
        if not has_fan_speed:
            missing.append("fan_speed")
        details.append({
            "item": "包含 preset_id 和 fan_speed 字段",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"缺少字段: {', '.join(missing)}"
        })

    # 5. 检查 preset_id 是否等于 "preset_004" (权重 30)
    expected_preset_id = "preset_004"
    actual_preset_id = data.get("preset_id", "")
    if actual_preset_id == expected_preset_id:
        details.append({
            "item": "preset_id 正确",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"预设 ID 为 {expected_preset_id}"
        })
        total_score += 30
    else:
        details.append({
            "item": "preset_id 正确",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"期望 {expected_preset_id}，实际得到 {actual_preset_id}"
        })

    # 6. 检查 fan_speed 是否等于 "high" (权重 30)
    expected_fan_speed = "high"
    actual_fan_speed = data.get("fan_speed", "")
    if actual_fan_speed == expected_fan_speed:
        details.append({
            "item": "fan_speed 正确",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"风扇速度为 {expected_fan_speed}"
        })
        total_score += 30
    else:
        details.append({
            "item": "fan_speed 正确",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": f"期望 {expected_fan_speed}，实际得到 {actual_fan_speed}"
        })

    # 总分写入文件
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)
    return total_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
