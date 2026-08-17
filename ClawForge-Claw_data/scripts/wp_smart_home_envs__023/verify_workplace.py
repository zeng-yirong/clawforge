import sys
import os
import json

def verify(workspace: str):
    # 初始化得分
    total_score = 0
    max_total = 100
    details = []

    def add_detail(item, score, max_score, passed, reason):
        details.append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        nonlocal total_score
        total_score += score

    # 检查必要目录
    required_dirs = ["data", "data/devices", "data/health", "ops"]
    for d in required_dirs:
        full = os.path.join(workspace, d)
        if os.path.isdir(full):
            add_detail(f"目录 {d} 存在", 5, 5, True, "")
        else:
            add_detail(f"目录 {d} 存在", 0, 5, False, f"缺少目录 {d}")

    # 检查必要源文件
    required_files = [
        "data/devices/devices.json",
        "data/health/health.json"
    ]
    for f in required_files:
        full = os.path.join(workspace, f)
        if os.path.isfile(full):
            add_detail(f"源文件 {f} 存在", 5, 5, True, "")
        else:
            add_detail(f"源文件 {f} 存在", 0, 5, False, f"缺少文件 {f}")

    # 检查输出文件 ops/health_conflicts.json
    output_file = os.path.join(workspace, "ops", "health_conflicts.json")
    if not os.path.isfile(output_file):
        add_detail("输出文件 ops/health_conflicts.json 存在", 0, 20, False, "文件不存在")
        # 无法继续，直接返回当前分数
        add_detail("冲突内容验证", 0, 60, False, "输出文件缺失，跳过验证")
        # 写分数
        score = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score, f, indent=2)
        return

    add_detail("输出文件 ops/health_conflicts.json 存在", 20, 20, True, "")

    # 解析输出文件
    try:
        with open(output_file, "r") as f:
            conflicts = json.load(f)
    except json.JSONDecodeError:
        add_detail("输出文件为合法 JSON", 0, 10, False, "JSON 解析失败")
        add_detail("冲突内容验证", 0, 50, False, "JSON 非法，跳过内容验证")
        score = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score, f, indent=2)
        return

    add_detail("输出文件为合法 JSON", 10, 10, True, "")

    # 检查冲突列表应为数组
    if not isinstance(conflicts, list):
        add_detail("冲突列表为数组", 0, 5, False, "根元素不是数组")
        add_detail("冲突内容验证", 0, 45, False, "格式错误，跳过")
        score = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score, f, indent=2)
        return

    add_detail("冲突列表为数组", 5, 5, True, "")

    # 期望唯一冲突：客厅加湿器湿度冲突
    expected_conflict = {
        "device_id": "LR-HM-002",
        "user_id": "JANE001",
        "conflict_type": "humidity",
        "current_value": 60,
        "preferred_min": 40,
        "preferred_max": 50
    }

    # 允许额外字段，但必须包含这些字段
    matched = False
    extra_conflicts = False
    for c in conflicts:
        # 检查必要字段存在
        required_fields = ["device_id", "user_id", "conflict_type", "current_value", "preferred_min", "preferred_max"]
        if all(f in c for f in required_fields):
            if (c["device_id"] == expected_conflict["device_id"] and
                c["user_id"] == expected_conflict["user_id"] and
                c["conflict_type"] == expected_conflict["conflict_type"] and
                c["current_value"] == expected_conflict["current_value"] and
                c["preferred_min"] == expected_conflict["preferred_min"] and
                c["preferred_max"] == expected_conflict["preferred_max"]):
                matched = True
            else:
                extra_conflicts = True
        else:
            extra_conflicts = True  # 缺少字段视为错误

    if not matched:
        add_detail("包含正确的冲突条目", 0, 35, False, "未找到与预期完全匹配的冲突")
    elif extra_conflicts:
        add_detail("包含正确的冲突条目", 20, 35, False, "找到了正确条目，但存在多余或格式错误的条目")
    else:
        add_detail("包含正确的冲突条目且无多余冲突", 35, 35, True, "仅一个冲突，字段完全匹配")

    # 检查不应包含的冲突：例如空调，因其设置均在 Jane 偏好内，且 John 不冲突
    # 如果有空调冲突（如错误地认为 BD-AC-001 的 20°C 在 Jane 的 20-22 内，不会冲突），但若出现则扣分
    for c in conflicts:
        if c.get("conflict_type") == "temperature" and c.get("device_id") in ["BD-AC-001", "LR-AC-004"]:
            add_detail("无错误温度冲突", 0, 10, False, f"不应报告温度冲突，设备 {c['device_id']} 设置正常")
            break
    else:
        add_detail("无错误温度冲突", 10, 10, True, "未报告多余的温度冲突")

    # 最终计算总分（已有累积）
    # 写分数
    score = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
