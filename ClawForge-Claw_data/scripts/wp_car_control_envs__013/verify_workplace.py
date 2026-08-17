import os, sys, json

def verify(workspace: str):
    total = 0
    details = []

    # 1. 检查 ops 目录是否存在（10分）
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        total += 10
        details.append({
            "item": "ops/ 目录存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops 目录已创建"
        })
    else:
        details.append({
            "item": "ops/ 目录存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops 目录不存在"
        })

    # 2. 检查 reset_fan.json 文件是否存在（20分）
    json_path = os.path.join(workspace, "ops", "reset_fan.json")
    if os.path.isfile(json_path):
        total += 20
        details.append({
            "item": "ops/reset_fan.json 文件存在",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "目标文件已生成"
        })
    else:
        details.append({
            "item": "ops/reset_fan.json 文件存在",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "文件不存在"
        })
        # 如果文件不存在，后续检查跳过
        score = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score, f, indent=2)
        return

    # 3. 文件内容是否为合法 JSON（20分）
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        total += 20
        details.append({
            "item": "JSON 格式合法",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "可正常解析为 JSON"
        })
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        score = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score, f, indent=2)
        return

    # 4. 检查 fan_speed 字段是否存在且值为 "auto"（50分）
    if isinstance(data, dict) and "fan_speed" in data:
        actual_value = data["fan_speed"]
        if actual_value == "auto":
            total += 50
            details.append({
                "item": "fan_speed 字段值正确",
                "score": 50,
                "max_score": 50,
                "passed": True,
                "reason": f"期望 'auto'，实际 '{actual_value}'"
            })
        else:
            details.append({
                "item": "fan_speed 字段值正确",
                "score": 0,
                "max_score": 50,
                "passed": False,
                "reason": f"期望 'auto'，实际 '{actual_value}'"
            })
    else:
        details.append({
            "item": "fan_speed 字段值正确",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": "缺少 fan_speed 字段或 JSON 不是字典"
        })

    # 写入评分
    final_score = {"total_score": total, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final_score, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
